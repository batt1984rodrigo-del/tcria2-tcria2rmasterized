from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def normalized_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def load_json_object(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return raw


def render_investigation_section(
    lines: list[str],
    investigation: dict[str, Any],
    translate_fn: Callable[[Any], str],
) -> None:
    lines.append("### Hipoteses abertas pela investigacao")
    lines.append("")
    for item in investigation["hypotheses"]:
        statement = translate_fn(item.get("statement", "")).rstrip(".")
        status_reason = translate_fn(item.get("status_reason", ""))
        lines.append(f"- {item['hypothesis_id']}: {statement}. {status_reason}")
    lines.append("")
    lines.append("### O que sustenta essas hipoteses")
    lines.append("")
    for item in investigation["evidence"]["summary_lines"]:
        lines.append(f"- {translate_fn(item)}")
    for item in investigation["evidence"]["by_hypothesis"]:
        evidence = [translate_fn(v) for v in item.get("evidence_lines", [])]
        joined = "; ".join(evidence) if evidence else "sem prova destacada nesta rodada"
        lines.append(f"- {item['hypothesis_id']}: {joined}")
    lines.append("")
    lines.append("### O que nao bate")
    lines.append("")
    for item in investigation["contradictions"]["items"]:
        lines.append(f"- {translate_fn(item)}")
    lines.append("")
    lines.append("### O que esta faltando")
    lines.append("")
    for item in investigation["gaps"]["items"]:
        lines.append(f"- {translate_fn(item)}")
    lines.append("")
    lines.append("### O que podemos afirmar agora")
    lines.append("")
    lines.append(translate_fn(investigation["conclusions"]["summary_statement"]))
    lines.append("")
    for item in investigation["conclusions"]["can_affirm"]:
        lines.append(f"- {translate_fn(item)}")
    lines.append("")
    lines.append("### O que ainda nao podemos afirmar")
    lines.append("")
    for item in investigation["conclusions"]["cannot_affirm_yet"]:
        lines.append(f"- {translate_fn(item)}")
    lines.append("")
    lines.append("### Proximos movimentos da investigacao")
    lines.append("")
    for item in investigation["recommendations"]["items"]:
        lines.append(f"- {translate_fn(item)}")
    lines.append("")
