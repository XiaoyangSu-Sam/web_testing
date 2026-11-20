# Synthetic samples

The sample inputs are authored plain text. Run outputs belong under the target project's `reports/exploration/`. Keep site captures, traces, session data and company inputs in the project's approved storage.

## Render a report from local files

This walkthrough uses Python 3.10 or newer and local file reads and writes. It requires no package installation, browser or server. The sample describes planned tests, so its report records them as `not_run`.

Run from the target workspace after copying the Skill, or set `$skill` to `skills/web-functional-testing` in this collection's checkout.

```powershell
$skill = '.github/skills/web-functional-testing'
$run = Join-Path 'reports/exploration' ('sample-' + (New-Guid).Guid)
New-Item -ItemType Directory -Path $run | Out-Null
Copy-Item -LiteralPath "$skill/samples/coverage.example.json" -Destination "$run/coverage.json"
python "$skill/scripts/render_report.py" "$run/coverage.json"
python "$skill/scripts/make_csv_fixture.py" "$run/fixture.csv" --rows 4
```

Open `report.md` under `$run` for the requirement mapping and test plan. The generated CSV has four sequential IDs and an exact amount total of 1.25.

## Run the optional browser demo

Use this when the workstation permits an ephemeral loopback listener and has Python Playwright and Microsoft Edge already approved. The optional [hash-pinned requirements](../requirements-browser.lock) describe the validated Python dependencies for environments that manage them separately.

```powershell
python "$skill/scripts/run_async_demo.py"
```

The demo starts a temporary HTTP fixture on `127.0.0.1`, opens a fresh browser context, runs six job scenarios and writes a report under `reports/exploration/`. Screenshots and timing evidence are generated there if the demo runs. The fixture uses invented job IDs and data. Its intentional failures and timeout illustrate the difference between classification and a real application defect.

## Sample requirements

| ID | Requirement |
| --- | --- |
| DEMO-REQ-01 | The page shows its heading and an enabled Run report button. Each submission creates one job with a unique ID. Success shows the three expected rows for that job. A failed job shows a failure and preserves the previous result. |
| DEMO-REQ-02 | A synthetic CSV contains sequential IDs and cycles through the amounts -1.25, 0.00 and 3.75. Its metadata reports the exact byte count, row count and decimal total. |
