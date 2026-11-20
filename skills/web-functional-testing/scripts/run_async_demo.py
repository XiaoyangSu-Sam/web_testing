"""Run the skill against a synthetic job service in installed Edge and render the report."""

import argparse
from contextlib import contextmanager
import csv
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shlex
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from time import monotonic
from urllib.parse import urlsplit
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

from make_csv_fixture import make_csv
from render_report import render
from wait_for_job import JobWaitError, wait_for_job

HTML = b"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Functional testing fixture</title><h1>Asynchronous report fixture</h1>
<label>Fixture scenario <select id="scenario">
<option>success</option><option>failure</option><option>timeout</option>
<option>wrong-job</option><option>retry</option><option>bad-output</option>
</select></label><button id="run">Run report</button>
<p role="status" id="state">Ready</p>
<section data-testid="result" data-job-id="previous"><span data-testid="rows">3</span></section>
<script>
const state = document.querySelector('#state');
const result = document.querySelector('[data-testid=result]');
const rows = document.querySelector('[data-testid=rows]');
async function refreshJob(id) {
  const detail = await (await fetch('/published/' + id)).json();
  if (detail.status === 'failed') { state.textContent = 'Failed'; return; }
  if (detail.status !== 'completed') { setTimeout(() => refreshJob(id), 100); return; }
  state.textContent = 'Completed'; result.dataset.jobId = id;
  rows.textContent = detail.row_count;
}
document.querySelector('#run').onclick = async () => {
  const selection = document.querySelector('#scenario').value;
  const response = await fetch('/jobs', {method: 'POST', body: selection});
  const job = await response.json();
  state.textContent = 'Accepted';
  refreshJob(job.id);
};
</script></html>"""


@contextmanager
def fixture():
    jobs = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def reply(self, status, value, extra=None):
            raw = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            if extra:
                self.send_header(*extra)
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            scenario = self.rfile.read(int(self.headers["Content-Length"])).decode()
            job_id = uuid4().hex
            jobs[job_id] = {"scenario": scenario, "first_read": None, "reads": 0}
            self.reply(202, {"id": job_id})

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(HTML)))
                self.end_headers()
                self.wfile.write(HTML)
                return
            category, _, job_id = path.lstrip("/").partition("/")
            job = jobs.get(job_id)
            if not job or category not in {"jobs", "published"}:
                self.reply(404, {"status": "missing"})
                return
            scenario = job["scenario"]
            if category == "jobs":
                job["reads"] += 1
                if job["first_read"] is None:
                    job["first_read"] = monotonic()
                if scenario == "retry" and job["reads"] == 1:
                    self.reply(503, {"status": "unavailable"}, ("Retry-After", "1"))
                    return
            age = monotonic() - job["first_read"] if job["first_read"] is not None else 0
            delay = 0.25 if category == "jobs" else 0.75
            state = "running"
            if scenario != "timeout" and age >= delay:
                state = "failed" if scenario == "failure" else "completed"
            payload = {"id": "different-job" if scenario == "wrong-job" else job_id, "status": state}
            if state == "completed":
                payload["row_count"] = 2 if scenario == "bad-output" else 3
            self.reply(200, payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", jobs
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def run_case(browser, base, scenario, index, output):
    case_id = f"ASYNC-{index:02d}"
    timeline = f"evidence/{case_id}-wait.json"
    context = browser.new_context()
    try:
        page = context.new_page()
        page.goto(base)
        panel = page.get_by_test_id("result")
        expect(panel).to_have_attribute("data-job-id", "previous")
        expect(panel.get_by_test_id("rows")).to_have_text("3")
        page.get_by_label("Fixture scenario").select_option(scenario)
        with page.expect_response(lambda res: res.url == base + "/jobs" and res.request.method == "POST") as accepted:
            page.get_by_role("button", name="Run report").click()
        assert accepted.value.status == 202
        job_id = accepted.value.json()["id"]

        expected = "The new report publishes exactly 3 rows for its own job ID."
        case = {
            "id": case_id, "feature": "Asynchronous report", "role": "QA user",
            "layer": "gui", "requirement_ids": ["DEMO-REQ-01"], "test_ref": "run_async_demo.py / run_case",
            "scenario": scenario, "expected": expected, "oracle": "Synthetic fixture expects a 3-row result for the accepted ID.",
            "steps": [f"Select {scenario} on the synthetic report page.", "Submit once and capture the 202 response and job ID.", "Read the documented status and verify the result for the same job."],
            "artifacts": [timeline], "wait_evidence": timeline,
        }
        try:
            payload = wait_for_job(
                page.request, f"{base}/jobs/{job_id}", job_id=job_id,
                pending_states=("running",), success_states=("completed",), failure_states=("failed",),
                timeout_s=0.65 if scenario == "timeout" else 5, interval_s=0.1, request_timeout_s=1,
                retry_statuses=(503,) if scenario == "retry" else (), evidence_path=output / timeline,
            )
        except JobWaitError as error:
            if scenario == "failure":
                assert error.outcome == "failed"
                expect(page.get_by_role("status")).to_have_text("Failed", timeout=3_000)
                expect(panel).to_have_attribute("data-job-id", "previous")
                case.update(status="passed", expected_wait_outcome="failed",
                            expected="The documented terminal failure appears and preserves the previous published result.",
                            oracle="Synthetic negative fixture explicitly terminates as failed.",
                            observed="Terminal failure reached. UI displayed Failed and preserved the previous result.")
            elif scenario == "timeout":
                assert error.outcome == "timed_out"
                assert error.evidence["last_observed_state"] == "running"
                case.update(status="timed_out", cause="product", observed="The synthetic job stayed running beyond the configured deadline.",
                            cause_detail="The fixture deliberately keeps the state running.",
                            recommendation="Check whether the worker advances the job or emits a terminal failure when processing ends.",
                            verification="Rerun the job and confirm a terminal status within the agreed deadline, followed by correct output.")
            else:
                assert scenario == "wrong-job" and error.outcome == "observation_error"
                assert "different job" in str(error)
                case.update(status="failed", cause="product", observed="The injected status response carried a different job ID and was rejected.",
                            cause_detail="The fixture intentionally substitutes another job ID in the response.",
                            recommendation="Key status lookups and serialization by the submitted job ID.",
                            verification="Submit two independent jobs and assert each status payload matches its requested ID.")
        else:
            assert scenario in {"success", "retry", "bad-output"}
            expect(panel).to_have_attribute("data-job-id", job_id, timeout=3_000)
            rows = panel.get_by_test_id("rows")
            if scenario == "bad-output":
                assert payload["row_count"] == 2
                expect(rows).to_have_text("2")
                case.update(status="failed", cause="product", observed="The completed job and its new UI result contained 2 rows instead of the expected 3.",
                            cause_detail="The fixture injects an incorrect row count before publishing it.",
                            recommendation="Trace the discrepancy in the generated result before publication. Compare the payload with the independently expected row count.",
                            verification="Rerun with the same input and assert exact output in both the status result and browser.")
            else:
                assert payload["row_count"] == 3
                expect(rows).to_have_text("3")
                case.update(status="passed", observed="The correlated job finished. The new UI result displayed 3 rows after publication.")
                if scenario == "retry":
                    evidence = json.loads((output / timeline).read_text(encoding="utf-8"))
                    assert evidence["timeline"][0]["http_status"] == 503
                    assert evidence["timeline"][1]["at_seconds"] - evidence["timeline"][0]["at_seconds"] >= 0.95
        if case["status"] in {"failed", "timed_out"}:
            screenshot = f"evidence/{case_id}.png"
            page.screenshot(path=str(output / screenshot))
            case["artifacts"].append(screenshot)
        return case
    finally:
        context.close()


def csv_facts(path):
    total = Decimal(0)
    count = 0
    with path.open(newline="", encoding="ascii") as stream:
        for row in csv.DictReader(stream):
            count += 1
            assert int(row["id"]) == count
            total += Decimal(row["amount"])
    return count, total


def file_checks():
    with TemporaryDirectory() as folder:
        root = Path(folder)
        baseline = root / "unit.csv"
        fixture_info = make_csv(baseline, 4, 3, 1024)
        assert csv_facts(baseline) == (4, Decimal("1.25"))
        assert baseline.stat().st_size == fixture_info["bytes"]
        cases = [{"id": "UNIT-01", "layer": "unit", "feature": "Synthetic CSV", "role": "QA fixture",
                  "scenario": "Four-row fixture count and exact sum", "status": "passed",
                  "expected": "Four rows, summing to 1.25, with the declared byte count.",
                  "observed": "Row count, exact decimal total and disk size matched.",
                  "oracle": "Demo contract and manual addition of -1.25, 0.00, 3.75 and -1.25.",
                  "steps": ["Generate four fixture rows.", "Read CSV independently and verify count, sum and disk size."],
                  "requirement_ids": ["DEMO-REQ-02"], "test_ref": "run_async_demo.py / file_checks"}]
        trials = []
        for index, rows in enumerate((100, 1_000, 10_000), 1):
            path = root / f"capacity-{index}.csv"
            details = make_csv(path, rows, 100, 2_000_000)
            start = monotonic()
            count, total = csv_facts(path)
            elapsed = monotonic() - start
            assert count == rows and total == Decimal(details["amount_sum"])
            assert path.stat().st_size == details["bytes"]
            case_id = f"CAP-{index:02d}"
            cases.append({"id": case_id, "layer": "capacity", "feature": "Synthetic CSV readback", "role": "QA fixture",
                          "scenario": f"Parse {rows:,} synthetic rows serially", "status": "passed",
                          "expected": "Exact row count, sequential IDs and monetary total.",
                          "observed": f"Read {count:,} rows and verified IDs and {total:.2f} total.",
                          "oracle": "Expected count and amount metadata independently compared with CSV parsing.",
                          "steps": [f"Generate {rows} rows with a 100-byte note.", "Time the serial read and assert IDs, row count and sum."],
                          "requirement_ids": ["DEMO-REQ-02"], "test_ref": "run_async_demo.py / file_checks"})
            trials.append({"case_id": case_id, "input": f"{details['bytes']:,} bytes / {rows:,} rows",
                           "seconds": round(elapsed, 6), "criterion": "Correct output; no latency target for demo",
                           "output_check": "Row count, IDs and decimal sum matched"})
        return cases, trials


def replay_command():
    workspace = Path.cwd()
    script = Path(__file__).resolve()
    if script.is_relative_to(workspace):
        script = script.relative_to(workspace)
    arguments = [sys.executable, str(script)]
    if os.name == "nt":
        return "& " + " ".join("'" + item.replace("'", "''") + "'" for item in arguments)
    return shlex.join(arguments)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("reports/exploration/async-demo-" + uuid4().hex[:8]))
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    scenarios = ["success", "failure", "timeout", "wrong-job", "retry", "bad-output"]
    with fixture() as (base, jobs), sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge")
        try:
            edge_version = browser.version
            with browser.new_page() as baseline:
                baseline.goto(base)
                expect(baseline.get_by_role("heading")).to_have_text("Asynchronous report fixture")
                expect(baseline.get_by_role("button", name="Run report")).to_be_enabled()
            cases = [run_case(browser, base, scenario, index, output) for index, scenario in enumerate(scenarios, 1)]
            assert len(jobs) == len(cases), "A submission was repeated"
        finally:
            browser.close()
    assert [case["status"] for case in cases] == ["passed", "passed", "timed_out", "failed", "passed", "failed"]
    cases.append({"id": "ASYNC-07", "layer": "gui", "feature": "Role behavior", "role": "Approver", "scenario": "Approval publication",
                  "status": "blocked", "expected": "Check the published status for the approver's own test record.",
                  "observed": "The synthetic report fixture has no approver account or approval workflow.",
                  "next_step": "Run on an authorized QA application with the approver role."})
    csv_cases, trials = file_checks()
    report = {
        "schema_version": 1, "run_id": output.name, "target": "Synthetic localhost fixture with deliberate faults",
        "environment": f"Python Playwright using installed Microsoft Edge {edge_version}",
        "scope": "Synthetic async wait, unit and capacity examples. Intentional fixture faults illustrate reporting. Capacity measures local CSV reads only.",
        "cleanup": "The demo service stopped and discarded its in-memory jobs. Temporary CSV files were removed.",
        "commands": [replay_command()],
        "next_steps": ["The largest local CSV checked was 10,000 rows. No application capacity limit was established.",
                       "Use the target README, documented completion signals and independent data on the QA application."],
        "requirements": [
            {"id": "DEMO-REQ-01", "source": "samples/README.md / DEMO-REQ-01", "claim": "The UI publishes the correct result for the accepted job.",
             "implementation": "run_async_demo.py / fixture and refreshJob"},
            {"id": "DEMO-REQ-02", "source": "samples/README.md / DEMO-REQ-02", "claim": "Generate deterministic rows and exact amount metadata.",
             "implementation": "make_csv_fixture.py / make_csv"},
        ],
        "cases": [{"id": "SMOKE-01", "layer": "smoke", "feature": "Report page", "role": "QA user",
                   "scenario": "Report page starts", "status": "passed", "requirement_ids": ["DEMO-REQ-01"],
                   "expected": "The heading and report button are ready.", "observed": "Both UI checks passed.",
                   "oracle": "samples/README.md / DEMO-REQ-01", "steps": ["Open the synthetic home URL.", "Verify heading and enabled report button."],
                   "test_ref": "run_async_demo.py / main"}, *cases, *csv_cases],
        "capacity": trials,
    }
    (output / "coverage.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "report.md").write_text(render(report, output), encoding="utf-8")
    print(f"Demonstration checks passed. Intentional timeout and failure evidence is in {output / 'report.md'}")


if __name__ == "__main__":
    main()
