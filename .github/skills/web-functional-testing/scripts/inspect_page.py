"""Observe one web page for an AI agent; no crawling, clicks or LLM calls."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4
from playwright.sync_api import sync_playwright, expect

def safe_url(value):
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if parsed.port:
        host += ":" + str(parsed.port)
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))

def inspect(args):
    parsed = urlsplit(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an HTTP(S) URL without embedded credentials")
    if bool(args.identity_selector) != bool(args.expected_identity):
        raise ValueError("Supply identity-selector and expected-identity together")
    folder = Path(args.out) if args.out else Path("reports/exploration") / ("inspection-" + uuid4().hex[:12])
    folder.mkdir(parents=True, exist_ok=False)
    result = {
        "requested_url": safe_url(args.url), "observed_at": datetime.now(timezone.utc).isoformat(),
        "identity_verified": False, "interaction_scope": "one-page observation only",
        "page_errors": [], "console_errors": [], "http_errors": [], "failed_requests": [],
        "inspection_errors": [], "artifact_errors": [],
    }
    def record(key, value):
        if len(result[key]) < 50:
            result[key].append(value)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=not args.headed)
        try:
            context = browser.new_context(storage_state=args.storage_state, viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            page.set_default_timeout(10_000)
            page.on("pageerror", lambda error: record("page_errors", str(error)))
            page.on("console", lambda message: record("console_errors", message.text) if message.type == "error" else None)
            page.on("response", lambda response: record("http_errors", {"status": response.status, "url": safe_url(response.url)}) if response.status >= 400 else None)
            page.on("requestfailed", lambda request: record("failed_requests", {"url": safe_url(request.url), "failure": request.failure}))
            try:
                response = page.goto(args.url, wait_until="domcontentloaded", timeout=30_000)
                result["navigation_status"] = response.status if response else None
                page.locator("body").wait_for()
                if args.ready_selector:
                    page.locator(args.ready_selector).wait_for(state="visible")
                if args.identity_selector:
                    expect(page.locator(args.identity_selector)).to_have_text(args.expected_identity, timeout=8_000)
                    result["identity_verified"] = True
                result["final_url"] = safe_url(page.url)
                result["title"] = page.title()
                controls = page.locator("a,button,input,select,textarea,[role=button],[role=tab]").evaluate_all("""elements => elements.filter(e => e.getClientRects().length > 0).slice(0,150).map(e => ({
                    tag: e.tagName.toLowerCase(), role: e.getAttribute('role'),
                    text: (e.innerText || '').trim().slice(0,150), label: e.getAttribute('aria-label'),
                    labels: Array.from(e.labels || []).map(x => x.innerText.trim()).join(' '),
                    test_id: e.getAttribute('data-testid'), type: e.getAttribute('type'),
                    href: e.tagName === 'A' ? e.href : null, disabled: !!e.disabled
                }))""")
                for control in controls:
                    if control["href"]:
                        control["href"] = safe_url(control["href"])
                result["visible_controls"] = controls
                result["control_limit"] = 150
                (folder / "accessibility.yml").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
            except Exception as error:
                result["inspection_errors"].append(str(error))
            try:
                page.screenshot(path=str(folder / "page.png"), full_page=True)
            except Exception as error:
                result["artifact_errors"].append(str(error))
            context.close()
        finally:
            browser.close()
    (folder / "observation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"directory": str(folder.resolve()), "inspection_ok": not result["inspection_errors"], "identity_verified": result["identity_verified"], "visible_controls": len(result.get("visible_controls", [])), "page_errors": len(result["page_errors"]), "http_errors": len(result["http_errors"]), "note": "Observation is not a test pass or a complete exploration."}))
    return 1 if result["inspection_errors"] or result["artifact_errors"] else 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--storage-state")
    parser.add_argument("--identity-selector")
    parser.add_argument("--expected-identity")
    parser.add_argument("--ready-selector")
    parser.add_argument("--out")
    parser.add_argument("--headed", action="store_true")
    raise SystemExit(inspect(parser.parse_args()))

if __name__ == "__main__":
    main()
