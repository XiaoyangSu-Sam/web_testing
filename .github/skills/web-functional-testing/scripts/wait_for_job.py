"""Bounded polling for a known read-only JSON status endpoint."""

from collections import deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from math import ceil, isfinite
from pathlib import Path
from time import monotonic, sleep
from urllib.parse import urlsplit
import json

from playwright.sync_api import APIRequestContext, Error, TimeoutError as PlaywrightTimeout


class JobWaitError(RuntimeError):
    def __init__(self, outcome, detail, evidence):
        super().__init__(f"{outcome}: {detail} ({evidence['attempts']} reads, {evidence['elapsed_seconds']:.3f}s)")
        self.outcome = outcome
        self.evidence = evidence


def retry_delay(header):
    if not header:
        return 0.0
    if header.isascii() and header.isdigit():
        return float(header) if len(header) < 12 else float("inf")
    try:
        when = parsedate_to_datetime(header)
        return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())
    except (ValueError, TypeError, OverflowError):
        return 0.0


def wait_for_job(
    client: APIRequestContext,
    status_url: str,
    *,
    job_id: str,
    pending_states: tuple[str, ...],
    success_states: tuple[str, ...],
    failure_states: tuple[str, ...],
    timeout_s: float = 60,
    interval_s: float = 1,
    request_timeout_s: float = 5,
    id_key: str = "id",
    state_key: str = "status",
    retry_statuses: tuple[int, ...] = (),
    evidence_path: Path | None = None,
) -> dict:
    """Return the correlated success payload. Raise JobWaitError for other outcomes.

    For requests, retry only explicitly allowed HTTP statuses. The same GET is
    observed repeatedly. Specify the immutable job ID returned by submission.
    """
    parsed = urlsplit(status_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Use an absolute HTTP(S) status URL without credentials or fragments")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("Provide the exact job ID from the accepted submission as a string")
    if any(not isfinite(value) or value <= 0 for value in (timeout_s, interval_s, request_timeout_s)):
        raise ValueError("Timeouts and polling interval must be finite and positive")
    state_map = {}
    for outcome, states in (("pending", pending_states), ("completed", success_states), ("failed", failure_states)):
        if not states:
            raise ValueError(f"Provide documented {outcome} states")
        for state in states:
            if not isinstance(state, str) or not state.strip() or state in state_map:
                raise ValueError("Status values must be distinct, nonempty strings")
            state_map[state] = outcome
    if any(not isinstance(status, int) or status < 400 or status > 599 or status in {401, 403} for status in retry_statuses):
        raise ValueError("Retry statuses must be documented transient HTTP errors. Authentication errors stop immediately.")
    evidence_path = Path(evidence_path) if evidence_path else None
    if evidence_path:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        # Reserve the file before making requests so a prior run stays intact.
        with evidence_path.open("x", encoding="utf-8") as stream:
            stream.write("{}\n")

    start = monotonic()
    deadline = start + timeout_s
    timeline = deque(maxlen=100)
    attempts = 0
    outcome = "observation_error"
    detail = "Status observation interrupted"
    last_state = None
    last_http_status = None

    def evidence():
        return {
            "outcome": outcome,
            "detail": detail,
            "timeout_seconds": timeout_s,
            "elapsed_seconds": round(monotonic() - start, 4),
            "attempts": attempts,
            "last_http_status": last_http_status,
            "last_observed_state": last_state,
            "timeline": list(timeline),
            "earlier_entries_omitted": max(0, attempts - len(timeline)),
        }

    try:
        while (remaining := deadline - monotonic()) > 0:
            attempts += 1
            entry = {"attempt": attempts, "at_seconds": round(monotonic() - start, 4)}
            timeline.append(entry)
            try:
                response = client.get(
                    status_url, timeout=ceil(1000 * min(request_timeout_s, remaining)),
                    max_redirects=0, fail_on_status_code=False,
                )
            except PlaywrightTimeout:
                outcome = "timed_out" if monotonic() >= deadline else "observation_error"
                detail = "The status request exceeded its time budget"
                break
            except Error:
                detail = "The status request could not be completed"
                break

            pause = interval_s
            try:
                last_http_status = entry["http_status"] = response.status
                if response.status in retry_statuses:
                    entry["observation"] = "retryable_http_status"
                    pause = max(pause, retry_delay(response.headers.get("retry-after")))
                elif not response.ok:
                    detail = f"Unexpected HTTP {response.status} on status endpoint"
                    break
                else:
                    try:
                        payload = response.json()
                    except ValueError:
                        detail = "Status endpoint returned invalid JSON"
                        break
                    if not isinstance(payload, dict) or payload.get(id_key) != job_id:
                        detail = "Status payload belongs to a different job or lacks the expected job ID"
                        break
                    state = payload.get(state_key)
                    if not isinstance(state, str) or state not in state_map:
                        detail = "Status payload has an undocumented or missing state"
                        break
                    last_state = entry["state"] = state
                    if monotonic() >= deadline:
                        outcome, detail = "timed_out", "Status observation finished after the completion deadline"
                        break
                    if state_map[state] == "completed":
                        outcome, detail = "completed", "Correlated job reached a documented success state"
                        return payload
                    if state_map[state] == "failed":
                        outcome, detail = "failed", f"Correlated job reached terminal state {state}"
                        break
            finally:
                response.dispose()

            remaining = deadline - monotonic()
            if remaining > 0:
                sleep(min(pause, remaining))
        else:
            outcome, detail = "timed_out", "No terminal state was observed before the completion deadline"

        raise JobWaitError(outcome, detail, evidence())
    finally:
        if evidence_path:
            evidence_path.write_text(json.dumps(evidence(), indent=2) + "\n", encoding="utf-8")
