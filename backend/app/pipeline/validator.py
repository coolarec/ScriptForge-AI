from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from app.models import ValidationIssue, ValidationResult

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "screenplay.schema.json"


def validate_yaml(yaml_text: str) -> ValidationResult:
    data = yaml.safe_load(yaml_text)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    issues = [
        ValidationIssue(path=_format_path(error.path), message=error.message)
        for error in sorted(validator.iter_errors(data), key=lambda err: list(err.path))
    ]
    return ValidationResult(valid=not issues, issues=issues)


def _format_path(path: jsonschema.protocols.Validator) -> str:
    parts = [str(part) for part in path]
    return ".".join(parts) if parts else "$"
