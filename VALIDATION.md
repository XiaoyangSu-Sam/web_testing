# Validation of the web functional testing Skill

The Skill format passed the skill-creator validator. Scripts were exercised on Windows with the existing Python 3.12 Playwright environment and installed Microsoft Edge. The previous add-on's validated page inspector is carried forward.

The included demo ran a real local HTTP service and Edge for six asynchronous scenarios. It checked normal completion, a documented failure, a job timeout, a mismatched job ID, a documented transient HTTP response with Retry-After, and a completed job containing an incorrect output. The harness verified one submission per scenario. The report retains per-job polling evidence and screenshots for the injected faults.

The demo also checked a small CSV fixture against an independently hand-calculated amount and then measured local reads of 100, 1,000 and 10,000 rows. Row order, count, bytes and exact decimal totals were checked. The largest sample was 1,123,349 bytes. This measurement describes only the sample reader on this machine.

The saved sample report contains 8 passes, 2 deliberately injected failures, 1 deliberate timeout and 1 unavailable-role case. The demo's acceptance checks passed and classified those outcomes as intended. The report validator was checked against contradictory async output, missing evidence and missing remediation. The company-managed Copilot end-to-end session and the target repository's README, source, app and workload limits still require actual access for validation.
