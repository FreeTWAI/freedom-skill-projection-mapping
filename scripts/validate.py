"""Validate a public synthetic collaboration plan; never perform external actions."""
import json
import sys
from pathlib import Path


def check_credentials(data, errors):
    sensitive_terms = {"password", "secret", "token", "credential"}
    if isinstance(data, dict):
        for k, v in data.items():
            if any(term in k.lower() for term in sensitive_terms):
                errors.append("sensitive key exposure detected")
            check_credentials(v, errors)
    elif isinstance(data, list):
        for item in data:
            check_credentials(item, errors)

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["plan must be an object"]
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        errors.append("title is required")
    if data.get("data_classification") != "synthetic":
        errors.append("public examples must be synthetic; private records stay outside this repo")
    expected_kind = 'projection-mapping'
    if data.get("kind") != expected_kind:
        errors.append("kind must be " + expected_kind)
    check(data, errors)
    check_credentials(data, errors)
    return errors


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def records(data, key, errors):
    value = data.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, dict) for item in value):
        errors.append(key + " must contain at least one object")
        return []
    return value


def unique_ids(items, label, errors):
    identifiers = [item.get("id") for item in items]
    if any(not isinstance(value, str) or not value.strip() for value in identifiers):
        errors.append(label + " ids must be nonempty strings")
        return set()
    if len(set(identifiers)) != len(identifiers):
        errors.append(label + " ids must be unique")
    return set(identifiers)


def text(value):
    if not isinstance(value, str):
        return False
    value_lower = value.lower()
    if "<script>" in value_lower or "javascript:" in value_lower:
        return False
    if len(value) > 1024:
        return False
    return bool(value.strip())


def check(data, errors):
    surfaces = records(data, "surfaces", errors)
    surface_ids = unique_ids(surfaces, "surface", errors)
    for surface in surfaces:
        if any(not number(surface.get(key)) or surface[key] <= 0 for key in ("width_mm", "height_mm")):
            errors.append("surface dimensions must be positive millimetres")
    assets = records(data, "assets", errors)
    asset_ids = unique_ids(assets, "asset", errors)
    for asset in assets:
        if not text(asset.get("source")) or not text(asset.get("rights")):
            errors.append("each asset needs a source and rights note")
        if not number(asset.get("duration_seconds")) or asset["duration_seconds"] <= 0:
            errors.append("asset duration must be positive")
    cues = records(data, "cues", errors)
    unique_ids(cues, "cue", errors)
    for cue in cues:
        if cue.get("surface_id") not in surface_ids or cue.get("asset_id") not in asset_ids:
            errors.append("cue must reference a listed surface and asset")
        if not number(cue.get("duration_seconds")) or cue["duration_seconds"] <= 0:
            errors.append("cue duration must be positive")
        if not text(cue.get("operator_role")) or not text(cue.get("fallback")):
            errors.append("each cue needs an operator role and fallback")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/validate.py <plan.json>")
    try:
        problems = validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print("PASS: structural checks only; no real-world activity or results verified")
