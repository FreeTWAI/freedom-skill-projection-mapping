"""Validate a public synthetic collaboration plan; never perform external actions."""
import json
import sys
from pathlib import Path


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
    return errors


def number(value):
    return type(value) is int or type(value) is float


def records(data, key, errors):
    value = data.get(key)
    if type(value) is not list or not value:
        errors.append(key + " must contain at least one object")
        return []
    for item in value:
        if type(item) is not dict:
            errors.append(key + " must contain at least one object")
            return []
    return value


def unique_ids(items, label, errors):
    identifiers = set()
    has_type_error = False
    has_dup_error = False
    for item in items:
        val = item.get("id")
        if type(val) is not str or not val.strip():
            if not has_type_error:
                errors.append(label + " ids must be nonempty strings")
                has_type_error = True
        else:
            if val in identifiers and not has_dup_error:
                errors.append(label + " ids must be unique")
                has_dup_error = True
            identifiers.add(val)
    if has_type_error:
        return set()
    return identifiers


def text(value):
    return type(value) is str and bool(value.strip())


def check(data, errors):
    surfaces = records(data, "surfaces", errors)
    surface_ids = unique_ids(surfaces, "surface", errors)
    for surface in surfaces:
        w = surface.get("width_mm")
        h = surface.get("height_mm")
        if not (type(w) is int or type(w) is float) or w <= 0 or not (type(h) is int or type(h) is float) or h <= 0:
            errors.append("surface dimensions must be positive millimetres")

    assets = records(data, "assets", errors)
    asset_ids = unique_ids(assets, "asset", errors)
    for asset in assets:
        if not text(asset.get("source")) or not text(asset.get("rights")):
            errors.append("each asset needs a source and rights note")
        duration = asset.get("duration_seconds")
        if not (type(duration) is int or type(duration) is float) or duration <= 0:
            errors.append("asset duration must be positive")

    cues = records(data, "cues", errors)
    unique_ids(cues, "cue", errors)
    for cue in cues:
        if cue.get("surface_id") not in surface_ids or cue.get("asset_id") not in asset_ids:
            errors.append("cue must reference a listed surface and asset")
        duration = cue.get("duration_seconds")
        if not (type(duration) is int or type(duration) is float) or duration <= 0:
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
