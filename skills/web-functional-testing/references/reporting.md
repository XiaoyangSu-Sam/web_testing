# Results and evidence

Use a new `reports/exploration/<run-id>/` per pass. Keep the report beside its machine-readable input and evidence so the links survive copying. Save only evidence suitable for the team's test-data rules. Link the runner output for this run's independent tests and keep `coverage.json` up to date as cases are planned and executed.

```text
reports/exploration/qa-001/
  coverage.json
  report.md
  pytest.html
  junit.xml
  evidence/
    DB-01-wait.json
    DB-01-screenshot.png
    DB-01-trace.zip
```

## Coverage schema version 1

Top level requires `schema_version` set to `1`, textual `run_id`, `target`, `environment`, `scope`, `cleanup`, and arrays `commands`, `next_steps`, `cases`. Record role and known test data in each relevant case. Use explicit commands for replay. If the run couldn't discover any cases, include the blocker or follow-up in `next_steps`.

Each case requires `id`, `feature`, `role`, `scenario`, `layer`, `status`, `expected`, `observed`. Layers are `smoke`, `unit`, `integration`, `gui`, `capacity`. Give every distinct scenario a unique ID. For executed cases, provide reproducible `steps` and set `test_ref` to the new test file or the recorded browser case for this run. Set `oracle` to the independently derived basis for each asserted expected result. Use `artifacts` as existing, forward-slash relative paths inside the run folder. Include screenshots, traces, timelines or relevant assertion evidence for failures/timeouts. Execution totals cover fresh cases that actually ran. Project test counts, discovery-only observations and unwritten tests do not establish a pass.

| `status` | Meaning | Additional fields |
|---|---|---|
| `passed` | Steps were executed and asserted against a known expectation | `steps`, `oracle` |
| `failed` | An observed check failed | `steps`, `cause`, `cause_detail`, `recommendation`, `verification`, `artifacts` |
| `timed_out` | The configured completion or observation budget elapsed | `steps`, `cause`, `cause_detail`, `recommendation`, `verification`, `artifacts` |
| `exercised_unverified` | The flow ran but some expected behavior lacks a valid oracle or confirmation | `steps`, `next_step` |
| `blocked` | Missing requirement, authorization, session or environment prevented execution | `next_step` |
| `not_run` | Discovered but not attempted within this pass | `next_step` |

For an async case, list `wait_evidence` in its `artifacts` and reference the same file in `wait_evidence`. The renderer reads the timeline summary and checks it against the case result. A successful-job pass defaults to `expected_wait_outcome: "completed"`. An intentional negative case can set `expected_wait_outcome: "failed"` and pass only after asserting the expected failure state and business effects separately. Always describe any final output or post-failure checks in `observed`.

For failures, set `cause` to `product`, `test`, `environment` or `unknown`. Use `cause_detail` to state the confirmed cause or explicitly label an evidence-based hypothesis. Use `recommendation` for a concrete fix or diagnostic and `verification` to say what to rerun. Where evidence supports it, identify a source file, function or responsible stage. Prioritize impact and actionable next steps.

For README-based testing, add `requirements`, a list of `id`, `claim`, `source`, and `implementation` objects. Reference those IDs in each case's `requirement_ids` array. Include uncovered requirements, including implementation or access gaps in `implementation`. For measured capacity, add a `capacity` array with `case_id` pointing to a `capacity` case, `input` such as bytes and row count, numeric `seconds`, `criterion`, and `output_check`. Record the highest passing and first failing tested size in the summary or follow-up when known. The [synthetic samples](../samples/README.md) include example input and a runnable demo.

Render from the workspace root with the existing Python:

```powershell
python .github/skills/web-functional-testing/scripts/render_report.py reports/exploration/qa-001/coverage.json
```

The report computes results from the cases, includes a case matrix and groups issue details, coverage gaps and verified outcomes. It checks artifact links and avoids accepting a success case with contradictory attached async evidence. “Exercised” counts executed cases among discovered cases, including failures and timeouts. It does not measure line, branch or undiscovered website coverage. Keep required facts in the run data so reruns remain comparable.
