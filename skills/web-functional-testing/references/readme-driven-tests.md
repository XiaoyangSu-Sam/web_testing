# Derive tests from the repository README

Use the local checkout or the user-supplied GitHub repository. Read the primary README and directly referenced docs required to interpret its behavior. Record the actual revision and the README section for each claim. Inspect existing tests and application entry points before generating new tests. Use `rg` or target-specific source search to locate the implementation.

## Build the requirement and test map

1. Extract distinct, testable promises. Include examples, supported formats, parameter defaults, error behavior, user roles, sorting rules, limits and state transitions when specified. Group duplicates under one stable requirement ID. Distinguish current features, roadmap items, prerequisites and marketing text by evidence. Record conflicting docs separately.
2. Map each current promise to a callable, component, API, or visible workflow. Record implementation evidence or the reason a mapping was unavailable. A README can describe externally visible behavior while omitting internal branches. Inspect the actual code and existing tests for material boundaries, exceptions and state transitions.
3. Select the appropriate layer. Generate every meaningful unit case identified for an isolated contract, including normal, invalid, boundary and documented error handling. Use dependency fixtures or test doubles only at the unit boundary. Use integration tests to verify real serialization, persistence, database or job behavior. Use browser E2E for visible workflows and cross-role interactions. A browser check is not a unit test.
4. Use a separately derived expected outcome. Turn README examples into executable cases when their expected results are explicit. For a Python function, use `pytest.mark.parametrize` for equivalent value classes and use a small fixture for isolated dependencies. For frontend logic, use the repo's existing JavaScript runner and dependencies if available. Do not add an npm install dependency to the Windows/uv deliverable. Without supported runtime or source, mark unit coverage blocked and continue with accessible functional checks.
5. Run a minimal product smoke check first. Run the existing and new focused unit cases, then integration and GUI cases. Independent logic checks can still run if the browser's smoke check is blocked. Reuse existing meaningful coverage with a test reference and executed result instead of duplicating it.

## Prioritize failure diagnosis

- **Logic defect.** Reproduce with the smallest meaningful input. State the violated rule, confirmed behavior and test evidence. Suggest a targeted code area and the regression assertion to rerun.
- **Documented feature incomplete.** Record the claim and implementation or UI evidence. A confirmed missing behavior is a product failure. Missing access, uncertainty about feature flags, or undocumented behavior is a coverage gap until verified.
- **Test defect.** Verify the locator, fixture, expected result and wait signal. Repair test implementation with evidence while preserving the business assertion.
- **Unknown expected behavior.** Record what was exercised and the exact question or fixture needed. Leave the business result unverified.

Example requirement map:

| Requirement | README evidence | Unit checks | Integration or GUI checks |
|---|---|---|---|
| DB-REQ-01 Query results follow the requested sort | Querying / Sort examples | Build ordered query, invalid sort key, null handling where specified | Fixed DB fixture, exact row ordering, corresponding export |
| DB-REQ-02 Pivot uses SUM on numeric cells | Pivot example / supported aggregation | Grouping, negative/zero/null inputs, totals and precision | Select fields in UI, compare exact cells and grand total to fixture |
| ADJ-REQ-01 Rejection requires a reason | Approval workflow / Reject | Empty/whitespace/valid reason, state transition and validation feedback | Upload owned QA record, reject as approver, verify after refresh |

List every in-scope README claim and the cases connected to it. Report only the known contract and inspected code. Unspecified behavior, unavailable code, feature flags and unreachable branches can leave coverage incomplete. Include that evidence in the run report.
