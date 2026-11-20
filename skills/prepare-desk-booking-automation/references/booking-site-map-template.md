# Booking site map template

Use this structure for the minimum context needed to maintain the booking flow. Reuse the target repository's equivalent location if it already has a site map. Record the observation date and the code revision. Use route names or relative paths and refer to configuration for the base URL. Keep exact selectors in the existing shared selector definition when one exists and link to them from the map.

For each stage, write the page or form, the observed control and stable locator, the active context, the readiness or error signal, the next transition, and evidence provenance. Mark evidence as live read-only, existing capture, local fixture, or unverified. Give an evidence-backed extraction rule when the site's visible label differs from its normalized value.

| Stage | What to capture |
| --- | --- |
| Session | Entry route, signed-in state, identity signal, signed-out or expired-session state, and available SSO recovery |
| My Events | List readiness, explicit empty state, filters, pagination, reservation ID and details, account, dates and times, and the site's pending/confirmed/cancelled meanings |
| Booking form | Location and floor controls, calendar date, time fields and timezone, valid selection constraints, submit-ready search control |
| Search | Evidence that the current search finished for the exact scope and interval, stale grid behavior, valid unchanged results, loaded empty results, and explicit errors |
| Desk row | Full desk ID, scope, a unique booking control, and any explicit occupancy or overlap evidence for the requested interval |
| Fallback | Same-scope alternatives and how the configured preference and radius apply to the observed desk listing |
| Cart and submission | Evidence from an approved fixture or capture for intended desk/date/slot/account, the submit control, definitive rejection, pending signal, and uncertain timing |
| Read-back | How to reach fresh My Events, locate the new matching record, and confirm its actual state and reservation details |

Treat a loading grid, absent control, or incomplete result as unresolved unless the site supplies a stronger signal. Capture a known available slot and a known conflicting slot when available. For partial-day occupancy, compare both overlapping and non-overlapping intervals for the same desk. Use site evidence to decide which cases support an occupied message.

Record the observed checks needed to detect a changed layout, such as ambiguous role/label matches or a scope value the script cannot confirm. Keep sample records synthetic or redacted. Use this map and the existing implementation as starting context when the site changes.
