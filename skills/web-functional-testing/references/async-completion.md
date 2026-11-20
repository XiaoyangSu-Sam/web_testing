# Wait for asynchronous work to finish

Give every slow functional check an explicit completion signal and finite timeout. Establish the timeout from the operation's SLA or observed QA behavior. Use separate budgets for navigation, actions, job completion and final UI propagation. A 60-second default in the helper is a starting value and may be overridden for a known long-running workflow.

| Signal | How to wait | What to check next |
|---|---|---|
| Final UI result identifies this run | Use `expect(scoped_locator).to_have_text(..., timeout=...)` or wait for a new result ID/version and result content | Exact cells, calculation, status label or file contents |
| One network response completes the operation | Arm `page.expect_response` before the click. Match the request origin, path and method, and correlate with this run | Response contract and the rendered or persisted result |
| Submission responds `202 Accepted` or returns a job ID | Save the accepted ID. Repeatedly read the documented status URL for that same ID until terminal success/failure or deadline | Read the actual output, handle UI propagation and confirm durability as appropriate |
| Existing polling, SSE or WebSocket drives the UI | Wait for a job-specific visible ready/error state, or an identified completion event registered before the action | User-visible result and persisted state |
| Export or popup | Arm `expect_download` or `expect_popup` before triggering | Parse the real file or assert on the new page |

An enabled button, disappearing spinner, successful submission HTTP code or browser network quiet period can precede actual completion. Scope final assertions to the record or new result version to prevent a previous result from passing the test. Use Playwright's [retrying UI assertions](https://playwright.dev/python/docs/actionability) and [response events](https://playwright.dev/python/docs/network) for those signals. Fixed sleeps do not confirm completion. A polling interval controls the rate of read-only status checks and works within the overall time budget.

## Python example for a documented job API

The example uses an illustrative contract. Substitute observed selectors and confirmed API paths and states. Import the helper from this skill's `scripts` folder or copy it with attribution into the project's testing helpers. Keep the status URL under the authorized app or documented API origin. A configurable endpoint should be validated against its expected origin before use.

```python
from urllib.parse import quote
from playwright.sync_api import expect
from wait_for_job import wait_for_job

with page.expect_response(
    lambda response: response.url == f"{api_origin}/jobs" and response.request.method == "POST",
    timeout=15_000,
) as accepted:
    page.get_by_role("button", name="Run report").click()

assert accepted.value.status == 202
job_id = accepted.value.json()["id"]
result = wait_for_job(
    page.request, f"{api_origin}/jobs/{quote(job_id, safe='')}",
    job_id=job_id,
    pending_states=("queued", "running"),
    success_states=("completed",),
    failure_states=("failed", "cancelled"),
    timeout_s=90, interval_s=1, request_timeout_s=5,
    retry_statuses=(429, 503),  # Only if the actual status contract allows these.
    evidence_path=run_dir / "CASE-01-wait.json",
)

# Verify the result of this job with an independent expected value.
assert result["row_count"] == expected_row_count
panel = page.get_by_test_id("report-result")
expect(panel).to_have_attribute("data-job-id", job_id, timeout=15_000)
expect(panel.get_by_test_id("row-count")).to_have_text(str(expected_row_count), timeout=15_000)
```

Use `page.request` when its authenticated context matches the documented status API. For bearer-authenticated APIs, use an approved test request context and pass credentials through existing test configuration. The helper makes GET requests only, disables redirects, requires a matching job ID, accepts configured JSON fields/states, and uses a monotonic deadline with per-request limits. It stops on malformed responses, unknown states, permission failures and mismatched IDs. Documented HTTP retries are opt-in and respect `Retry-After` within the time budget. Handle unusual schemas by adapting the observed contract, while retaining correlation and bounded waits.

`JobWaitError.outcome` reports `failed` for documented terminal failure, `timed_out` when the deadline expires, or `observation_error` when reliable status could not be obtained. Use the evidence timeline to report poll count, last observed state and elapsed time. A known terminal failure can be the expected outcome for a negative test. In that case record the expected terminal evidence explicitly without labelling the backend as successful. After success, use a separate UI assertion if result rendering or persistence lags. Record a completed job with an incorrect final output as a functional failure.

On timeout, retain the last status, case identifier, and relevant UI/trace artifacts. Check the existing submission before repeating an upload, approval, rejection or other write. A timeout can indicate queue delay, app latency, or an unreliable status signal. Classify the cause after reviewing evidence. Do not report a regression based on a guessed threshold.
