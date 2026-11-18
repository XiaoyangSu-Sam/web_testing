"""Validate a functional test run and render its coverage.json as Markdown."""

import argparse
from collections import Counter
import json
from math import isfinite
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote

STATUSES = {
    "passed": "Passed", "failed": "Failed", "timed_out": "Timed out",
    "exercised_unverified": "Exercised, result unverified", "blocked": "Blocked", "not_run": "Not run",
}
EXECUTED = {"passed", "failed", "timed_out", "exercised_unverified"}
CAUSES = {"product", "test", "environment", "unknown"}
LAYERS = {"smoke", "unit", "integration", "gui", "capacity"}


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def strings(value, label, required=True):
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{label} must be a {'nonempty ' if required else ''}list")
    return [string(item, label) for item in value]


def safe_artifact(value, root):
    name = string(value, "artifact path")
    parts = name.split("/")
    path = PurePosixPath(name)
    if path.is_absolute() or "\\" in name or ":" in name or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Artifact must be a relative file inside the run folder: {name}")
    destination = root.joinpath(*parts).resolve()
    if not destination.is_relative_to(root) or not destination.is_file():
        raise ValueError(f"Artifact is missing or outside the run folder: {name}")
    return name


def cell(value):
    return re.sub(r"([\\`*_{}\[\]()#+!|])", r"\\\1", " ".join(value.splitlines())).replace("<", "&lt;").replace(">", "&gt;")


def job_evidence(case, root):
    wait = string(case["wait_evidence"], "wait evidence path")
    if wait not in case.get("artifacts", []):
        raise ValueError(f"List {case['id']} wait_evidence in its artifacts")
    evidence = json.loads((root / safe_artifact(wait, root)).read_text(encoding="utf-8"))
    if not isinstance(evidence, dict) or evidence.get("outcome") not in ("completed", "failed", "timed_out", "observation_error"):
        raise ValueError("Invalid job evidence outcome")
    elapsed = evidence.get("elapsed_seconds")
    attempts = evidence.get("attempts")
    if type(elapsed) not in (float, int) or not isfinite(elapsed) or elapsed < 0 or type(attempts) is not int or attempts < 0:
        raise ValueError("Invalid job evidence timing")
    if evidence.get("last_observed_state") is not None:
        string(evidence["last_observed_state"], "last observed job state")
    return evidence


def render(data, root):
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Expected coverage schema version 1")
    for key in ("run_id", "target", "environment", "scope", "cleanup"):
        string(data.get(key), key)
    commands = strings(data.get("commands"), "commands", required=False)
    next_steps = strings(data.get("next_steps"), "next_steps", required=False)
    requirements = data.get("requirements", [])
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
    requirement_ids = set()
    for requirement in requirements:
        for key in ("id", "claim", "source", "implementation"):
            string(requirement.get(key), f"requirement {key}")
        if requirement["id"] in requirement_ids:
            raise ValueError(f"Duplicate requirement ID: {requirement['id']}")
        requirement_ids.add(requirement["id"])
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases must be a list")
    if not cases and not next_steps:
        raise ValueError("A zero-discovery run must explain its blocker or next step")

    seen = set()
    count = Counter()
    waits = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each case must be an object")
        for key in ("id", "feature", "role", "scenario", "expected", "observed"):
            string(case.get(key), key)
        case_id = case["id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", case_id) or case_id in seen:
            raise ValueError(f"Invalid or duplicate case ID: {case_id}")
        seen.add(case_id)
        status = case.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError(f"Unknown case status for {case_id}")
        count[status] += 1
        if case.get("layer") not in LAYERS:
            raise ValueError(f"Invalid test layer for {case_id}")
        for requirement_id in strings(case.get("requirement_ids", []), "requirement_ids", required=False):
            if requirement_id not in requirement_ids:
                raise ValueError(f"Unknown requirement ID {requirement_id} for {case_id}")
        artifacts = strings(case.get("artifacts", []), "artifacts", required=False)
        for artifact in artifacts:
            safe_artifact(artifact, root)
        if status in EXECUTED:
            strings(case.get("steps"), f"{case_id} executed steps")
        if status == "passed":
            string(case.get("oracle"), f"{case_id} independent expected-result source")
        if status in {"failed", "timed_out"}:
            if case.get("cause") not in CAUSES:
                raise ValueError(f"Provide a cause classification for {case_id}")
            if not artifacts:
                raise ValueError(f"Provide at least one evidence file for {case_id}")
            string(case.get("cause_detail"), f"{case_id} reason or supported hypothesis")
            string(case.get("recommendation"), f"{case_id} recommended fix or next diagnostic")
            string(case.get("verification"), f"{case_id} verification after the recommendation")
        if status in {"blocked", "not_run", "exercised_unverified"}:
            string(case.get("next_step"), f"{case_id} follow-up")
        if "wait_evidence" in case:
            evidence = waits[case_id] = job_evidence(case, root)
            expected_wait = case.get("expected_wait_outcome", "completed")
            if expected_wait not in ("completed", "failed"):
                raise ValueError(f"Invalid expected wait outcome for {case_id}")
            if status == "passed" and evidence["outcome"] != expected_wait:
                raise ValueError(f"{case_id} cannot pass with contradictory job evidence")
            if status == "timed_out" and evidence["outcome"] != "timed_out":
                raise ValueError(f"{case_id} timeout disagrees with its attached job evidence")

    trials = data.get("capacity", [])
    if not isinstance(trials, list):
        raise ValueError("capacity must be a list")
    cases_by_id = {case["id"]: case for case in cases}
    for trial in trials:
        case_id = string(trial.get("case_id"), "capacity case ID")
        if case_id not in cases_by_id or cases_by_id[case_id]["layer"] != "capacity":
            raise ValueError(f"Capacity trial refers to a missing or non-capacity case: {case_id}")
        for key in ("input", "criterion", "output_check"):
            string(trial.get(key), f"capacity {key}")
        seconds = trial.get("seconds")
        if type(seconds) not in (int, float) or not isfinite(seconds) or seconds < 0:
            raise ValueError("Capacity seconds must be finite and nonnegative")
    ran = sum(count[status] for status in EXECUTED)
    lines = ["# Web functional test report", "", f"Run **{cell(data['run_id'])}** against **{cell(data['target'])}**.", "",
             f"Environment — {cell(data['environment'])}", "", f"Scope — {cell(data['scope'])}", "",
             "## Coverage summary", "", f"**{ran} of {len(cases)} discovered cases exercised.**", "",
             "| Outcome | Cases |", "|---|---:|"]
    lines.extend(f"| {label} | {count[status]} |" for status, label in STATUSES.items())
    if requirements:
        lines.extend(["", "## Requirements traced to tests", "", "| Requirement | Documented behavior | Source | Implementation | Cases |", "|---|---|---|---|---|"])
        for requirement in requirements:
            matching = [case for case in cases if requirement["id"] in case.get("requirement_ids", [])]
            mapped = ", ".join(f"{case['id']} ({STATUSES[case['status']]})" for case in matching) or "Uncovered"
            columns = [requirement[key] for key in ("id", "claim", "source", "implementation")] + [mapped]
            lines.append("| " + " | ".join(map(cell, columns)) + " |")
    lines.extend(["", "## Case matrix", "", "| Case | Layer | Feature | Role | Scenario | Result |", "|---|---|---|---|---|---|"])
    lines.extend(
        f"| {case['id']} | {case['layer']} | {cell(case['feature'])} | {cell(case['role'])} | {cell(case['scenario'])} | {STATUSES[case['status']]} |"
        for case in cases
    )
    if trials:
        lines.extend(["", "## Capacity observations", "", "| Case | Input | Seconds | Acceptance criterion | Output check | Result |", "|---|---|---:|---|---|---|"])
        for trial in trials:
            case = cases_by_id[trial["case_id"]]
            lines.append(f"| {case['id']} | {cell(trial['input'])} | {trial['seconds']:.4g} | {cell(trial['criterion'])} | {cell(trial['output_check'])} | {STATUSES[case['status']]} |")

    for heading, selection in (
        ("Failures and timeouts", {"failed", "timed_out"}),
        ("Coverage gaps", {"blocked", "not_run", "exercised_unverified"}),
        ("Verified outcomes", {"passed"}),
    ):
        lines.extend(["", f"## {heading}", ""])
        matched = [case for case in cases if case["status"] in selection]
        if not matched:
            lines.append("None recorded for this run.")
        for case in matched:
            lines.extend([f"### {case['id']} — {cell(case['scenario'])}", "", f"- Expected — {cell(case['expected'])}",
                          f"- Observed — {cell(case['observed'])}"])
            if case.get("oracle"):
                lines.append(f"- Basis — {cell(string(case['oracle'], 'oracle'))}")
            if case.get("cause"):
                lines.append(f"- Cause classification — {cell(string(case['cause'], 'cause'))}")
            if case.get("test_ref"):
                lines.append(f"- Test implementation — {cell(string(case['test_ref'], 'test_ref'))}")
            for key, label in (("cause_detail", "Why it failed"), ("recommendation", "Suggested fix or diagnostic"), ("verification", "Verify the fix")):
                if case.get(key):
                    lines.append(f"- {label} — {cell(string(case[key], key))}")
            if case.get("next_step"):
                lines.append(f"- Follow-up — {cell(string(case['next_step'], 'next_step'))}")
            if evidence := waits.get(case["id"]):
                observed = evidence.get("last_observed_state") or "none"
                lines.append(f"- Job wait — {cell(evidence['outcome'])}, {evidence['elapsed_seconds']}s elapsed, {evidence['attempts']} reads, last state {cell(observed)}")
            if artifacts := case.get("artifacts"):
                links = ", ".join(f"[{cell(path)}]({quote(path, safe='/')})" for path in artifacts)
                lines.append(f"- Evidence — {links}")
            if steps := case.get("steps"):
                lines.extend(["", "Reproduction steps", ""])
                lines.extend(f"{index}. {cell(step)}" for index, step in enumerate(strings(steps, "steps"), 1))
            lines.append("")

    lines.extend(["## Rerun and cleanup", "", f"- Test data — {cell(data['cleanup'])}"])
    for command in commands:
        lines.append(f"- Command — {cell(command)}")
    lines.extend(f"- Next — {cell(step)}" for step in next_steps)
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coverage", type=Path)
    args = parser.parse_args()
    root = args.coverage.resolve().parent
    try:
        report = render(json.loads(args.coverage.read_text(encoding="utf-8")), root)
        target = root / "report.md"
        target.write_text(report, encoding="utf-8")
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as error:
        parser.exit(2, f"Report validation failed: {error}\n")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
