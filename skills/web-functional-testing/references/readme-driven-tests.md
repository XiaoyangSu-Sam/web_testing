# Derive tests from the repository README

Use the local checkout or the user-supplied GitHub repository. Read the primary README and relevant product docs. Record the actual revision and the section for each claim. Inspect app entry points, interfaces and product source. Scope `rg` or code searches to product paths and skip linked test code, fixtures, snapshots and reports.

## Build the requirement and test map

1. Extract distinct, testable promises. Include examples, supported formats, parameter defaults, error behavior, user roles, sorting rules, limits and state transitions when specified. Group duplicates under one stable requirement ID. Distinguish current features, roadmap items, prerequisites and marketing text by evidence. Record conflicting docs separately.
2. Map each current promise to a callable, component, API, or visible workflow. Record implementation evidence or the reason a mapping was unavailable. Use app code and observed controls to spot material boundaries, exceptions and state transitions. Keep facts about the implementation distinct from the expected behavior defined by the contract.
3. Select the appropriate layer. Author unit cases for isolated behavior and use test doubles at dependency boundaries if needed. Use integration tests for real serialization, persistence, database or job behavior and browser E2E for visible workflows and cross-role interactions. Derive additional cases from [independent test design](independent-test-design.md).
4. Establish expected results separately. Turn documented examples with explicit outcomes into new cases and vary their inputs using new fixtures. Use an applicable specification, a small independently calculated fixture, or a property implied by the requirement. If the available material only shows how the app currently behaves, record the observation and the missing business rule.
5. Execute a fresh minimal smoke case, then run the newly authored tests explicitly by file or recorded browser steps. Test logic that can run independently when the browser is blocked. If the language runtime or source is unavailable, report the unit gap and continue with accessible browser or documented interface checks.

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
