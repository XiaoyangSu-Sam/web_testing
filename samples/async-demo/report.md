# Web functional test report

Run **web-functional-v2-final-demo** against **Synthetic localhost fixture with deliberate faults**.

Environment — Python Playwright using installed Microsoft Edge 157.0.4341.60

Scope — Synthetic async wait, unit and capacity examples. Intentional fixture faults illustrate reporting. Capacity measures local CSV reads only.

## Coverage summary

**11 of 12 discovered cases exercised.**

| Outcome | Cases |
|---|---:|
| Passed | 8 |
| Failed | 2 |
| Timed out | 1 |
| Exercised, result unverified | 0 |
| Blocked | 1 |
| Not run | 0 |

## Requirements traced to tests

| Requirement | Documented behavior | Source | Implementation | Cases |
|---|---|---|---|---|
| DEMO-REQ-01 | The UI publishes the correct result for the accepted job. | Sample README / Async report | run\_async\_demo.py / fixture and refreshJob | SMOKE-01 \(Passed\), ASYNC-01 \(Passed\), ASYNC-02 \(Passed\), ASYNC-03 \(Timed out\), ASYNC-04 \(Failed\), ASYNC-05 \(Passed\), ASYNC-06 \(Failed\) |
| DEMO-REQ-02 | Generate deterministic rows and exact amount metadata. | Sample README / Synthetic CSV | make\_csv\_fixture.py / make\_csv | UNIT-01 \(Passed\), CAP-01 \(Passed\), CAP-02 \(Passed\), CAP-03 \(Passed\) |

## Case matrix

| Case | Layer | Feature | Role | Scenario | Result |
|---|---|---|---|---|---|
| SMOKE-01 | smoke | Report page | QA user | Report page starts | Passed |
| ASYNC-01 | gui | Asynchronous report | QA user | success | Passed |
| ASYNC-02 | gui | Asynchronous report | QA user | failure | Passed |
| ASYNC-03 | gui | Asynchronous report | QA user | timeout | Timed out |
| ASYNC-04 | gui | Asynchronous report | QA user | wrong-job | Failed |
| ASYNC-05 | gui | Asynchronous report | QA user | retry | Passed |
| ASYNC-06 | gui | Asynchronous report | QA user | bad-output | Failed |
| ASYNC-07 | gui | Role behavior | Approver | Approval publication | Blocked |
| UNIT-01 | unit | Synthetic CSV | QA fixture | Four-row fixture count and exact sum | Passed |
| CAP-01 | capacity | Synthetic CSV readback | QA fixture | Parse 100 synthetic rows serially | Passed |
| CAP-02 | capacity | Synthetic CSV readback | QA fixture | Parse 1,000 synthetic rows serially | Passed |
| CAP-03 | capacity | Synthetic CSV readback | QA fixture | Parse 10,000 synthetic rows serially | Passed |

## Capacity observations

| Case | Input | Seconds | Acceptance criterion | Output check | Result |
|---|---|---:|---|---|---|
| CAP-01 | 11,049 bytes / 100 rows | 0.016 | Correct output; no latency target for demo | Row count, IDs and decimal sum matched | Passed |
| CAP-02 | 111,349 bytes / 1,000 rows | 0.015 | Correct output; no latency target for demo | Row count, IDs and decimal sum matched | Passed |
| CAP-03 | 1,123,349 bytes / 10,000 rows | 0.016 | Correct output; no latency target for demo | Row count, IDs and decimal sum matched | Passed |

## Failures and timeouts

### ASYNC-03 — timeout

- Expected — The new report publishes exactly 3 rows for its own job ID.
- Observed — The synthetic job stayed running beyond the configured deadline.
- Basis — Synthetic fixture expects a 3-row result for the accepted ID.
- Cause classification — product
- Test implementation — run\_async\_demo.py / run\_case
- Why it failed — The fixture deliberately keeps the state running.
- Suggested fix or diagnostic — Check whether the worker advances the job or emits a terminal failure when processing ends.
- Verify the fix — Rerun the job and confirm a terminal status within the agreed deadline, followed by correct output.
- Job wait — timed\_out, 0.656s elapsed, 7 reads, last state running
- Evidence — [evidence/ASYNC-03-wait.json](evidence/ASYNC-03-wait.json), [evidence/ASYNC-03.png](evidence/ASYNC-03.png)

Reproduction steps

1. Select timeout on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.

### ASYNC-04 — wrong-job

- Expected — The new report publishes exactly 3 rows for its own job ID.
- Observed — The injected status response carried a different job ID and was rejected.
- Basis — Synthetic fixture expects a 3-row result for the accepted ID.
- Cause classification — product
- Test implementation — run\_async\_demo.py / run\_case
- Why it failed — The fixture intentionally substitutes another job ID in the response.
- Suggested fix or diagnostic — Key status lookups and serialization by the submitted job ID.
- Verify the fix — Submit two independent jobs and assert each status payload matches its requested ID.
- Job wait — observation\_error, 0.0s elapsed, 1 reads, last state none
- Evidence — [evidence/ASYNC-04-wait.json](evidence/ASYNC-04-wait.json), [evidence/ASYNC-04.png](evidence/ASYNC-04.png)

Reproduction steps

1. Select wrong-job on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.

### ASYNC-06 — bad-output

- Expected — The new report publishes exactly 3 rows for its own job ID.
- Observed — The completed job and its new UI result contained 2 rows instead of the expected 3.
- Basis — Synthetic fixture expects a 3-row result for the accepted ID.
- Cause classification — product
- Test implementation — run\_async\_demo.py / run\_case
- Why it failed — The fixture injects an incorrect row count before publishing it.
- Suggested fix or diagnostic — Trace the discrepancy in the generated result before publication. Compare the payload with the independently expected row count.
- Verify the fix — Rerun with the same input and assert exact output in both the status result and browser.
- Job wait — completed, 0.313s elapsed, 4 reads, last state completed
- Evidence — [evidence/ASYNC-06-wait.json](evidence/ASYNC-06-wait.json), [evidence/ASYNC-06.png](evidence/ASYNC-06.png)

Reproduction steps

1. Select bad-output on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.


## Coverage gaps

### ASYNC-07 — Approval publication

- Expected — Check the published status for the approver's own test record.
- Observed — The synthetic report fixture has no approver account or approval workflow.
- Follow-up — Run on an authorized QA application with the approver role.


## Verified outcomes

### SMOKE-01 — Report page starts

- Expected — The heading and report button are ready.
- Observed — Both UI checks passed.
- Basis — Sample README / Async report
- Test implementation — run\_async\_demo.py / main

Reproduction steps

1. Open the synthetic home URL.
2. Verify heading and enabled report button.

### ASYNC-01 — success

- Expected — The new report publishes exactly 3 rows for its own job ID.
- Observed — The correlated job finished. The new UI result displayed 3 rows after publication.
- Basis — Synthetic fixture expects a 3-row result for the accepted ID.
- Test implementation — run\_async\_demo.py / run\_case
- Job wait — completed, 0.329s elapsed, 4 reads, last state completed
- Evidence — [evidence/ASYNC-01-wait.json](evidence/ASYNC-01-wait.json)

Reproduction steps

1. Select success on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.

### ASYNC-02 — failure

- Expected — The documented terminal failure appears and preserves the previous published result.
- Observed — Terminal failure reached. UI displayed Failed and preserved the previous result.
- Basis — Synthetic negative fixture explicitly terminates as failed.
- Test implementation — run\_async\_demo.py / run\_case
- Job wait — failed, 0.313s elapsed, 4 reads, last state failed
- Evidence — [evidence/ASYNC-02-wait.json](evidence/ASYNC-02-wait.json)

Reproduction steps

1. Select failure on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.

### ASYNC-05 — retry

- Expected — The new report publishes exactly 3 rows for its own job ID.
- Observed — The correlated job finished. The new UI result displayed 3 rows after publication.
- Basis — Synthetic fixture expects a 3-row result for the accepted ID.
- Test implementation — run\_async\_demo.py / run\_case
- Job wait — completed, 1.015s elapsed, 2 reads, last state completed
- Evidence — [evidence/ASYNC-05-wait.json](evidence/ASYNC-05-wait.json)

Reproduction steps

1. Select retry on the synthetic report page.
2. Submit once and capture the 202 response and job ID.
3. Read the documented status and verify the result for the same job.

### UNIT-01 — Four-row fixture count and exact sum

- Expected — Four rows, summing to 1.25, with the declared byte count.
- Observed — Row count, exact decimal total and disk size matched.
- Basis — Demo contract and manual addition of -1.25, 0.00, 3.75 and -1.25.
- Test implementation — run\_async\_demo.py / file\_checks

Reproduction steps

1. Generate four fixture rows.
2. Read CSV independently and verify count, sum and disk size.

### CAP-01 — Parse 100 synthetic rows serially

- Expected — Exact row count, sequential IDs and monetary total.
- Observed — Read 100 rows and verified IDs and 81.25 total.
- Basis — Expected count and amount metadata independently compared with CSV parsing.
- Test implementation — run\_async\_demo.py / file\_checks

Reproduction steps

1. Generate 100 rows with a 100-byte note.
2. Time the serial read and assert IDs, row count and sum.

### CAP-02 — Parse 1,000 synthetic rows serially

- Expected — Exact row count, sequential IDs and monetary total.
- Observed — Read 1,000 rows and verified IDs and 831.25 total.
- Basis — Expected count and amount metadata independently compared with CSV parsing.
- Test implementation — run\_async\_demo.py / file\_checks

Reproduction steps

1. Generate 1000 rows with a 100-byte note.
2. Time the serial read and assert IDs, row count and sum.

### CAP-03 — Parse 10,000 synthetic rows serially

- Expected — Exact row count, sequential IDs and monetary total.
- Observed — Read 10,000 rows and verified IDs and 8331.25 total.
- Basis — Expected count and amount metadata independently compared with CSV parsing.
- Test implementation — run\_async\_demo.py / file\_checks

Reproduction steps

1. Generate 10000 rows with a 100-byte note.
2. Time the serial read and assert IDs, row count and sum.

## Rerun and cleanup

- Test data — The demo service stopped and discarded its in-memory jobs. Temporary CSV files were removed.
- Command — uv run --no-sync --offline python .github/skills/web-functional-testing/scripts/run\_async\_demo.py
- Next — The largest local CSV checked was 10,000 rows. No application capacity limit was established.
- Next — Use the target README, documented completion signals and independent data on the QA application.
