---
name: prepare-desk-booking-automation
description: Prepare or repair an existing Desk Booking Skill. Discover the booking site's UI, save a reusable page map, update the Python workflow, and verify unattended booking with independent local acceptance tests. Use for setup, site changes, and reliability work.
---

# Prepare Desk Booking automation

Use this maintenance workflow when asked to set up, test, or repair Desk Booking. The existing `desk-booking` Skill owns ordinary requests to reserve or check a desk. Complete the discovery, implementation, and verification in the current session when the available repository and environment permit it.

## Identify the existing workflow

- Resolve the real Desk Booking `SKILL.md`, `book_desk.py`, selector configuration, and result reader. Inspect the worktree diff and read the repository's booking rules. Keep unrelated edits, account preferences, the configured booking scope, and fallback rules intact while making the scoped changes requested here.
- Use the installed `web-functional-testing` Skill for browser exploration, independent test design, and evidence when available. Reuse the workspace's approved browser tools and installed Python, Playwright, and Edge environment.
- Confirm the existing CLI modes from source or `--help`. Before a real-site discovery run, trace the chosen mode to verify it has zero cart adds, submits, edits, or cancellations. Production discovery uses sign-in, normal navigation, My Events, and availability searches. Exercise writes and failure injection against localhost fixtures or an authorized QA target. Use redacted existing captures for write-path evidence when only production read access is available.

## Discover the site and persist the context

- Walk the booking screens using the authorized session and browser tooling already available. If the integrated browser cannot open the company site or carry its sign-in, use the repository's existing Python Playwright and dedicated Edge profile through a verified read-only path. Let the user complete interactive SSO when required. Keep passwords, tokens, browser state, and employee details out of the page map and tracked files.
- Follow [the booking site map template](references/booking-site-map-template.md). Capture the accessible roles or stable locators, scope, readiness signals, and transitions needed for booking. Record which signals came from the live site and which rely on fixtures or existing captures. Keep unknown rules explicit and keep raw page dumps local under the company's evidence policy.
- Update the existing site reference or save `references/booking-site-map.md` next to the active Desk Booking `SKILL.md`. Reuse the central selector configuration where present and link the map from that Skill so a fresh session can inspect it. The Python path should use implemented locators and checks. The map gives later Copilot sessions evidence for diagnosis and maintenance.

## Make an ordinary booking automatic

Update the existing Desk Booking Skill and its Python entry point as needed. Route an explicit request to reserve a desk directly to the existing booking mode when the request and configured defaults give a valid date scope, time, location, and desk. An explicit single-date request uses `book-one`. Apply the existing default scope for an unspecified date when the configuration defines one. When an essential preference is missing, ask only for that value. Use the current fallback policy to decide when an alternative requires a choice, and keep availability questions in read-only mode.

For an authenticated, configured session, one ordinary request should run from search through verified result without user interaction. Launch the existing Python workflow from the normal Skill entry point. Reuse the dedicated booking session and follow the existing browser isolation and organization settings. Keep interactive SSO as the recovery path when the session expires. Test any headless mode against the supported session behavior before enabling it. If the site has drifted, stop at the first ambiguous state and report the responsible stage. Use this maintenance workflow to re-observe and test changes before the next booking attempt.

- Before adding a desk, verify fresh results for the exact location and requested interval and match the complete normalized desk ID. Require clear occupancy evidence for an occupied result. If a smaller booking overlaps the requested interval, describe it as a conflict with the requested interval. Keep unavailable, absent, and unknown outcomes distinct.
- Apply configured alternatives from the same fresh search where possible. Verify the cart and active account before submission. Keep the attempt journal and the existing run lock. Use the supplied fallback rules and one submission for the selected reservation. If a submit may have happened and the outcome is uncertain, reconcile read-only before considering another write for that date.
- Read fresh My Events or the supported reservation detail view. Correlate the new reservation to the current attempt and verify the desk, date, interval, location where needed, active account, and actual reservation status. Keep pending and confirmed outcomes distinct. Use the existing result reader and the `run_id` produced by this execution to report the outcome.
- Keep normal runs short through warm-session reuse, bounded readiness waits, and one search per unchanged scope. Record search, submit, and verification time separately from browser shutdown. Preserve the process lock until it is safe to reuse the profile. Keep speed improvements focused on measured waits and redundant actions.

## Verify the change

Author fresh tests from [the acceptance cases](references/acceptance.md), the booking rules, and the observed workflow. Run the real CLI and result reader against controlled scenarios and independently chosen synthetic inputs. Keep the test logic and evidence independent of existing test cases and reports. Repeat a small set serially if timing or state reuse is relevant.

Verify discovery of the normal Desk Booking entry in the target workspace and test a fresh-session natural-language booking prompt against the fixture. If direct Copilot invocation is inaccessible, report the CLI result and the remaining invocation check separately. Write a verification report with the context file path, changes, commands, per-case outcomes, timing, and unverified live behaviors. Report success at the level supported by observed evidence.
