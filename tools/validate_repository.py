#!/usr/bin/env python3
"""Validate comparison metadata without building the implementation apps."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_SCHEMA_PATH = ROOT / "schemas" / "scenario.schema.json"
RESULT_SCHEMA_PATH = ROOT / "schemas" / "benchmark-result.schema.json"
FIXTURE_SCHEMA_PATH = ROOT / "schemas" / "fixture-manifest.schema.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_REPOSITORIES = {
    "slint": "slint-ui-comparison",
    "qml": "qml-ui-comparison",
    "bevy-egui": "bevy-egui-ui-comparison",
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_errors(validator: Draft202012Validator, document: object, path: Path) -> list[str]:
    return [
        f"{path.relative_to(ROOT)}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    ]


def main() -> int:
    errors: list[str] = []

    try:
        scenario_schema = load_json(SCENARIO_SCHEMA_PATH)
        result_schema = load_json(RESULT_SCHEMA_PATH)
        fixture_schema = load_json(FIXTURE_SCHEMA_PATH)
        Draft202012Validator.check_schema(scenario_schema)
        Draft202012Validator.check_schema(result_schema)
        Draft202012Validator.check_schema(fixture_schema)
    except (OSError, json.JSONDecodeError, SchemaError) as error:
        # Schema failures are fatal; there is no useful partial validation.
        print(f"Schema validation setup failed: {error}", file=sys.stderr)
        return 1

    scenario_validator = Draft202012Validator(scenario_schema)
    result_validator = Draft202012Validator(result_schema)
    fixture_validator = Draft202012Validator(fixture_schema)
    scenarios: dict[str, tuple[int, Path]] = {}

    for path in sorted((ROOT / "scenarios").rglob("*.json")):
        try:
            document = load_json(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue

        errors.extend(schema_errors(scenario_validator, document, path))
        if not isinstance(document, dict):
            continue

        scenario_id = document.get("id")
        if scenario_id != path.stem:
            errors.append(f"{path.relative_to(ROOT)}: scenario id must match its filename")

        tier = document.get("tier")
        if tier != path.parent.name:
            errors.append(f"{path.relative_to(ROOT)}: scenario tier must match its directory")

        if isinstance(scenario_id, str):
            revision = document.get("revision")
            previous = scenarios.get(scenario_id)
            if previous is not None:
                errors.append(
                    f"{path.relative_to(ROOT)}: duplicate scenario id also used by "
                    f"{previous[1].relative_to(ROOT)}"
                )
            elif isinstance(revision, int):
                scenarios[scenario_id] = (revision, path)

        implementations = document.get("implementations", {})
        if isinstance(implementations, dict):
            for implementation, mapping in implementations.items():
                if not isinstance(mapping, dict):
                    continue
                expected = EXPECTED_REPOSITORIES.get(implementation)
                if expected is not None and mapping.get("repository") != expected:
                    errors.append(
                        f"{path.relative_to(ROOT)}: {implementation} must use repository {expected}"
                    )

    fixture_families: dict[str, Path] = {}
    fixture_variants: dict[str, Path] = {}
    fixture_artifacts: dict[str, Path] = {}
    fixture_references: list[tuple[Path, str, str]] = []
    manifest_paths = sorted((ROOT / "fixtures" / "manifests").glob("*.json"))
    for path in manifest_paths:
        try:
            document = load_json(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue

        errors.extend(schema_errors(fixture_validator, document, path))
        if not isinstance(document, dict):
            continue

        family_id = document.get("id")
        if family_id != path.stem:
            errors.append(f"{path.relative_to(ROOT)}: family id must match its filename")
        if isinstance(family_id, str):
            if family_id in fixture_families:
                errors.append(f"{path.relative_to(ROOT)}: duplicate family id {family_id}")
            else:
                fixture_families[family_id] = path

        variants = document.get("variants", [])
        if not isinstance(variants, list):
            continue
        for variant in variants:
            if not isinstance(variant, dict):
                continue
            variant_id = variant.get("id")
            if isinstance(variant_id, str):
                if variant_id in fixture_variants:
                    errors.append(f"{path.relative_to(ROOT)}: duplicate variant id {variant_id}")
                else:
                    fixture_variants[variant_id] = path
            artifacts = variant.get("artifacts", [])
            if not isinstance(artifacts, list):
                continue
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue
                artifact_id = artifact.get("id")
                if isinstance(artifact_id, str):
                    if artifact_id in fixture_artifacts:
                        errors.append(f"{path.relative_to(ROOT)}: duplicate artifact id {artifact_id}")
                    else:
                        fixture_artifacts[artifact_id] = path
                digest = artifact.get("sha256")
                if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
                    errors.append(f"{path.relative_to(ROOT)}: invalid SHA-256 for artifact {artifact_id}")
                columns = artifact.get("columns", [])
                samples = artifact.get("golden_samples", [])
                if isinstance(columns, list) and isinstance(samples, list):
                    for sample in samples:
                        if isinstance(sample, dict) and isinstance(sample.get("row"), list):
                            if len(sample["row"]) != len(columns):
                                errors.append(
                                    f"{path.relative_to(ROOT)}: golden row width mismatch for {artifact_id}"
                                )

        references = document.get("references", [])
        if isinstance(references, list):
            for reference in references:
                if not isinstance(reference, dict):
                    continue
                referenced_family = reference.get("family")
                artifact_ids = reference.get("artifact_ids", [])
                if isinstance(referenced_family, str) and isinstance(artifact_ids, list):
                    for artifact_id in artifact_ids:
                        if isinstance(artifact_id, str):
                            fixture_references.append((path, referenced_family, artifact_id))

    for path, referenced_family, artifact_id in fixture_references:
        if referenced_family not in fixture_families:
            errors.append(f"{path.relative_to(ROOT)}: unknown referenced family {referenced_family}")
        if artifact_id not in fixture_artifacts:
            errors.append(f"{path.relative_to(ROOT)}: unknown referenced artifact {artifact_id}")

    for path in sorted((ROOT / "results" / "raw").rglob("*.json")):
        try:
            document = load_json(path)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue

        errors.extend(schema_errors(result_validator, document, path))
        if not isinstance(document, dict):
            continue

        scenario_id = document.get("scenario_id")
        scenario = scenarios.get(scenario_id) if isinstance(scenario_id, str) else None
        if scenario is None:
            errors.append(f"{path.relative_to(ROOT)}: result references an unknown scenario")
        elif (
            isinstance(document.get("scenario_revision"), int)
            and document["scenario_revision"] > scenario[0]
        ):
            errors.append(
                f"{path.relative_to(ROOT)}: result references a future revision of {scenario_id}"
            )

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    result_count = len(list((ROOT / "results" / "raw").rglob("*.json")))
    print(
        f"Validated 3 schemas, {len(manifest_paths)} fixture manifests, "
        f"{len(fixture_variants)} variants, {len(fixture_artifacts)} artifacts, "
        f"{len(scenarios)} scenarios, and {result_count} result documents."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
