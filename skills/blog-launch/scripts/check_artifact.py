#!/usr/bin/env python3
"""Optional structural checks; no external packages, network or mutation."""
import argparse
import json
import re
import sys
from pathlib import Path


def check_state(data):
    errors = []
    if not isinstance(data, dict):
        return ["State must be an object"]
    statuses = {"intake", "in_progress", "awaiting_decision", "awaiting_topic_approval",
                "awaiting_week_approval", "week_approved", "complete", "paused"}
    if not isinstance(data.get("status"), str) or data["status"] not in statuses:
        errors.append("Unknown status")
    for key in ("stage", "week", "revision"):
        value = data.get(key)
        if type(value) is not int or value < 1:
            errors.append(f"{key} must be a positive integer")
    if type(data.get("stage")) is int and data["stage"] > 15:
        errors.append("stage exceeds 15")
    if data.get("mode") is not None and (not isinstance(data["mode"], str) or data["mode"] not in {"zero", "growth", "noncommercial"}):
        errors.append("mode must be zero, growth, noncommercial or null")
    mix = data.get("content_mix")
    if mix is not None:
        expected = {"expert", "personal", "reach", "sales"}
        if not isinstance(mix, dict) or set(mix) != expected:
            errors.append("content_mix must contain expert, personal, reach, sales")
        elif any(type(v) not in (int, float) or not 0 <= v <= 100 for v in mix.values()):
            errors.append("content_mix values must be numbers from 0 to 100")
        elif abs(sum(mix.values()) - 100) > 0.001:
            errors.append("content_mix must sum to 100")
    if data.get("status") == "week_approved":
        approvals = data.get("approvals", [])
        if not isinstance(approvals, list) or not any(
            isinstance(a, dict) and a.get("kind") == "week" and
            a.get("target") == data.get("week") and a.get("revision") == data.get("revision") and
            isinstance(a.get("user_text"), str) and a["user_text"].strip()
            for a in approvals
        ):
            errors.append("Current week and revision have no recorded user approval")
    # A record is evidence only when the conversation really contains approval.
    # Natural-language intent is deliberately not inferred by this script.
    scripts = data.get("scripts", [])
    if not isinstance(scripts, list):
        errors.append("scripts must be an array")
    else:
        seen = set()
        for script in scripts:
            if not isinstance(script, dict) or not isinstance(script.get("id"), str) or not script["id"].strip():
                errors.append("Each script needs an id")
                continue
            if script["id"] in seen:
                errors.append(f"Duplicate script id: {script['id']}")
            seen.add(script["id"])
            scenes = script.get("scenes", [])
            if not scenes or not all(isinstance(s, dict) and
                    all(s.get(k) for k in ("number", "visual", "voice")) for s in scenes):
                errors.append(f"Script {script['id']} has no complete scenes")
    return errors


def check_mermaid(source):
    """Checks the template's simple flowchart subset, not the full Mermaid grammar."""
    errors = []
    if not re.match(r"\s*flowchart\s+TD\b", source):
        errors.append("Expected flowchart TD")
    declarations = re.findall(r'\b([A-Z][A-Z0-9_]*)\s*(?:\["[^"\n]*"\]|\{"[^"\n]*"\})', source)
    nodes = set(declarations)
    if len(nodes) != len(declarations):
        errors.append("Duplicate node declarations")
    edges = []
    for line in source.splitlines():
        if "-->" not in line:
            continue
        left, right = line.split("-->", 1)
        src = re.match(r"\s*([A-Z][A-Z0-9_]*)", left)
        dst = re.match(r'\s*(?:\|[^|]*\|\s*)?([A-Z][A-Z0-9_]*)', right)
        if not src or not dst:
            errors.append(f"Unsupported edge: {line.strip()}")
            continue
        edges.append((src[1], dst[1]))
    unknown = {n for edge in edges for n in edge} - nodes
    if unknown:
        errors.append("Undefined nodes: " + ", ".join(sorted(unknown)))
    incoming = {b for _, b in edges}
    roots = nodes - incoming
    if not roots:
        errors.append("No entry nodes")
    reachable = set(roots)
    while True:
        expanded = reachable | {b for a, b in edges if a in reachable}
        if expanded == reachable:
            break
        reachable = expanded
    if nodes - reachable:
        errors.append("Unreachable nodes: " + ", ".join(sorted(nodes - reachable)))
    used = {n for edge in edges for n in edge}
    if nodes - used:
        errors.append("Isolated nodes: " + ", ".join(sorted(nodes - used)))
    # Non-entry dangling ends may be intentional; report for editorial review.
    terminals = nodes - {a for a, _ in edges}
    return errors, {"nodes": len(nodes), "edges": len(edges),
                    "entries": sorted(roots), "terminals": sorted(terminals),
                    "scope": "structural subset only; consent/payment semantics and rendering require review"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["state", "mermaid", "bio"])
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    source = args.file.read_text(encoding="utf-8")
    details = {}
    if args.kind == "state":
        try:
            errors = check_state(json.loads(source))
        except json.JSONDecodeError as exc:
            errors = [f"Invalid JSON: {exc}"]
    elif args.kind == "mermaid":
        errors, details = check_mermaid(source)
    else:
        # Only ignore a conventional trailing file newline; preserve Bio line breaks.
        text = source[:-1] if source.endswith("\n") else source
        details = {"unicode_codepoints": len(text), "limit": 150}
        errors = [] if len(text) <= 150 else ["Bio exceeds 150 code points"]
    print(json.dumps({"ok": not errors, "errors": errors, **details}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
