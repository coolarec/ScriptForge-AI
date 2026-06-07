from __future__ import annotations

import yaml

from app.models import ScriptProject


def build_yaml(project: ScriptProject) -> str:
    data = project.model_dump(mode="json", exclude_none=True)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
