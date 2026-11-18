# Copilot request for web functional testing

Use the `web-functional-testing` Skill in this workspace. I want you to own test discovery, test authoring, execution, diagnosis and reporting. Keep generated code and artifacts in English. Explain results to me in Chinese.

- Repository or local checkout: [GitHub URL or path]
- Test app URL and environment: [local or authorized QA URL]
- Available account roles: [role names or approved saved sessions]
- Known business rules or fixtures: [optional reference]
- Capacity test scope: [approved input sizes, concurrency, time or resource limits]

Read the repository README and its relevant referenced docs. Extract all in-scope testable claims, map each to source and a requirement ID, then create missing unit cases for identifiable logic and integration or GUI tests for the appropriate boundaries. Use the existing project runner where available. Discover selectors from actual UI. Start with the simplest baseline and prioritize wrong results, missing behavior, state mistakes, validation, and data integrity. Record unavailable or unverified claims with their causes.

For asynchronous work, capture the accepted job ID, wait for its documented terminal state within a finite budget, and then verify the actual output. Distinguish submission, job success, final UI propagation and persisted data. Use the Skill's polling helper when a known JSON status contract is available. Record event or polling evidence.

Once the relevant small functional baseline passes, measure bounded input capacity in the authorized test environment. Vary one dimension at a time. For a SQL or file tool, try progressively larger valid inputs or result sets. Record exact input size, sample count, time, output integrity and highest passing/first failing tested size. Stop escalating on a functional failure, time/resource limit or agreed ceiling. Also check graceful rejection around a documented input limit when in scope.

Do the work within the available environment. Preserve the test code, command output and relevant evidence. Create `coverage.json` and run the Skill's renderer to create `report.md`. For each tested feature show the linked requirement, test layer, actual method, expected and observed results, outcome and evidence. For each failure or timeout explain the cause or best-supported hypothesis, recommend a specific fix or diagnostic, and state which assertion to rerun. Stated fixes should match the evidence. Tell me what remains blocked or untested.

Prefer existing Edge with the Python 3.12 and uv kit. Use available app-native tooling for source-level tests. Keep this workflow free of new npm installation requirements. If access, an app runner, a business rule or an input limit is unresolved, continue independent checks and record the gap in the report.
