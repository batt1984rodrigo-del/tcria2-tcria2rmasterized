#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from client_language import (
    blocked_review_helpfulness,
    client_boolean,
    client_impact_label,
    client_label_for_artifact_type,
    client_phrase_for_outcome,
    client_reasons_list,
    translate_client_text,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "output" / "legacy"


def load_payload(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Blocked artifacts review payload must be a JSON object.")
    return raw


def blocked_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("blocked_artifacts_review")
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def short_sha(value: Any) -> str:
    text = str(value or "").strip()
    return text[:16] + "..." if len(text) > 16 else text


def render_item(item: dict[str, Any]) -> list[str]:
    artifact_identity = item.get("artifact_identity")
    if not isinstance(artifact_identity, dict):
        artifact_identity = {}

    review = item.get("blockedArtifactReview")
    if not isinstance(review, dict):
        review = {}

    reasons = client_reasons_list(review.get("organizational_issue_reasons"))
    if not reasons:
        reasons = [translate_client_text(review.get("traceability_gap_reason") or item.get("blocked_reason"))]

    lines: list[str] = []
    lines.append(f"## {item.get('file_name', 'Documento sem nome')}")
    lines.append(f"- Que tipo de documento e este? {client_label_for_artifact_type(review.get('document_kind'))}")
    lines.append(f"- Pode ser usado agora? {client_phrase_for_outcome(item.get('official_outcome'))}.")
    lines.append(f"- O que impediu o uso? {translate_client_text(item.get('blocked_reason'))}")
    lines.append(
        f"- Esse documento ainda ajuda o caso? {blocked_review_helpfulness(review.get('theme_related'), review.get('potential_case_impact'))}"
    )
    lines.append(f"- O impacto potencial dele hoje e: {client_impact_label(review.get('potential_case_impact'))}")
    lines.append(f"- Ha problema de organizacao? {client_boolean(review.get('organizational_issue'))}")
    lines.append("- O que esta faltando:")
    for reason in reasons:
        lines.append(f"  - {reason}")
    content_summary = translate_client_text(review.get("content_summary"))
    if content_summary:
        lines.append(f"- Sinais encontrados: {content_summary}")
    recommendation = translate_client_text(review.get("recommended_action"))
    if recommendation:
        lines.append(f"- O que fazer agora? {recommendation}")
    file_sha = short_sha(artifact_identity.get("file_sha256"))
    if file_sha:
        lines.append(f"- Identificacao do documento: sha256={file_sha}")
    lines.append("")
    return lines


def render_markdown(payload: dict[str, Any]) -> str:
    items = blocked_items(payload)
    lines: list[str] = []
    lines.append("# Documentos com pendencias que ainda podem ajudar o caso")
    lines.append("")
    lines.append("## 1. O que este material mostra")
    lines.append(f"- Gerado em: `{payload.get('generated_at', 'unknown')}`")
    lines.append(f"- Documentos com pendencia analisados: `{payload.get('blocked_count', len(items))}`")
    lines.append(
        "- Este material nao altera o status oficial dos documentos. Ele explica, em linguagem de primeira leitura, por que eles ainda nao podem ser usados e o que falta para avancar."
    )
    note = translate_client_text(payload.get("note"))
    if note:
        lines.append(f"- Observacao: {note}")
    lines.append("")
    lines.append("## 2. Como ler este resumo")
    lines.append("- Documento bloqueado nao significa documento inutil.")
    lines.append("- O foco aqui e mostrar o que ainda ajuda, o que falta e qual deve ser o proximo ajuste.")
    lines.append("")
    lines.append("## 3. Documento por documento")
    lines.append("")
    for item in items:
        lines.extend(render_item(item))
    lines.append("## 4. Observacao final")
    lines.append(
        "Este resumo foi escrito para leitura humana. O JSON tecnico continua sendo a fonte detalhada de rastreabilidade e compatibilidade."
    )
    lines.append("")
    return "\n".join(lines)


def default_output_path(input_path: Path) -> Path:
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{input_path.stem}.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a blocked artifacts review JSON into a client-facing Markdown summary."
    )
    parser.add_argument("--input", type=Path, required=True, help="Path to the blocked artifacts review JSON payload.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Path for the generated Markdown report. Defaults to output/legacy/<input-stem>.md",
    )
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    payload = load_payload(input_path)
    output_path = (args.output.expanduser().resolve() if args.output else default_output_path(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(payload), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
