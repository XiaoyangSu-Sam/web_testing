# Measure file, dataset and query capacity

Start with ordinary business use. Test the small baseline and exact results first. Move to capacity only for paths with an established functional baseline and an authorized local or QA environment. A baseline failure is a finding to fix before escalation. Keep this workflow focused on normal input patterns and agreed operating limits.

1. **Choose one variable.** Examples are upload bytes, CSV or SQL-file records, query result rows, column count, pivot cardinality, export size or read-only concurrency. For a SQL workbench, separate database query duration, result transfer, grid rendering and export. Test supported file formats with schema-valid synthetic data. Use a dedicated read-only test database for query fixtures.
2. **Make the bounds explicit.** Record maximum workload size, request/job deadline, allowed concurrency, total duration, resource budget and environment. Default to serial operation. Example small-to-large steps for approved local file QA are 100 KiB, 1 MiB, 5 MiB, 10 MiB, up to the environment's approved ceiling. Follow actual supported limits and available capacity. Use sizes just below and above a documented product limit when in scope to verify graceful handling.
3. **Measure the same operation.** Measure submit/accept, time to terminal state, and time until the correct result appears. Record input bytes and row counts, samples, elapsed times and peak memory/CPU when instrumentation is available. Preserve raw measurements. Include latency percentiles only with enough samples and state the sample size. For a small run show individual samples or median and range.
4. **Validate each step.** Assert exact record counts, representative values, completeness/order, totals, no duplicate records and persistence as applicable. A successful HTTP status with missing rows fails the functional check. A correct rejection above a documented limit passes an input-limit behavior check. Capture actual rejection, timeout, crash, corrupted result or unavailable instrumentation distinctly.
5. **Stop escalation on the first failure or limit.** Save the highest tested size satisfying the stated criteria and the first tested size that did not. Use the observed interval to guide a narrower rerun if appropriate. A capacity ceiling is established only within the tested bounds, environment and acceptance criteria. Save cleanup state and avoid reissuing timed-out writes.

Generate a bounded `id,amount,note` fixture from the workspace root using the bundled CSV generator and existing Python:

```powershell
python .github/skills/web-functional-testing/scripts/make_csv_fixture.py reports/exploration/qa-001/fixtures/sample.csv --rows 10000 --note-bytes 100
```

The generator prints actual bytes, expected count and exact sum. Adapt the columns to the real test contract before uploading. The generator writes a local file and does not submit it to the application. Execute the approved browser or integration check at each size using the existing application adapter. Put the measurements in the report's `capacity` table and link logs or JSON with raw samples.

Recommendations should follow observations. A workbook that times out while rendering a correct export suggests examining client-side grid/render stages. Truncation at a fixed row count suggests checking default limits or pagination. High memory growth while reading larger files suggests measuring allocations before proposing streaming or chunking. Identify these as hypotheses until profiling supports them.
