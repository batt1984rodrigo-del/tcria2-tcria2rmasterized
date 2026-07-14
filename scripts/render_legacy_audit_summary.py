#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from client_language import (
    client_label_for_classification,
    summarize_document_for_client,
    translate_client_text,
)
from reasoning_policy import build_legacy_reasoning_summary


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "examples" / "legacy" / "sanitized-strict-audit.json"
DEFAULT_OUTPUT = ROOT / "output" / "legacy" / "legacy-audit-summary.md"
PARTIAL_TEXT_QUALITIES = {"medium", "low"}
INSUFFICIENT_TEXT_QUALITIES = {"low", "very_low", "insufficient", "empty"}
PRIMARY_GATE_ORDER = ["complianceGate", "prescriptiveGate", "traceabilityCheck"]


def load_payload(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        items = [item for item in raw if isinstance(item, dict)]
        classification_counts = Counter(normalized_classification(item) for item in items)
        return {
            "generated_at": "unknown",
            "audit_basis": "legacy-list-normalized-for-coverage-summary",
            "input_path": str(path),
            "mode": "legacy-list-normalized",
            "compliance_gate_mode": "legacy-list-normalized",
            "total_files_scanned": len(items),
            "accusation_set_count": 0,
            "classification_counts": dict(classification_counts),
            "accusation_set": [],
            "non_accusation_set": items,
        }
    raise ValueError("Legacy payload must be a JSON object or list of legacy items.")


def legacy_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    accusation = payload.get("accusation_set") or []
    non_accusation = payload.get("non_accusation_set") or []
    items = [item for item in accusation + non_accusation if isinstance(item, dict)]
    if items:
        return items
    fallback = payload.get("items") or []
    return [item for item in fallback if isinstance(item, dict)]


def normalized_text(value: Any, default: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else default


def normalized_classification(item: dict[str, Any]) -> str:
    return normalized_text(item.get("classification"), "UNCLASSIFIED_LEGACY_ITEM").upper()


def normalized_extraction_status(item: dict[str, Any]) -> str:
    status = item.get("extraction_status")
    if status:
        return normalized_text(status).lower()
    if normalized_classification(item) == "UNREADABLE":
        return "unreadable_or_empty"
    return "unknown"


def normalized_text_quality(item: dict[str, Any]) -> str:
    quality = item.get("text_quality") or item.get("text_extraction_quality")
    return normalized_text(quality).lower()


def normalized_outcome(item: dict[str, Any]) -> str:
    return normalized_text(item.get("overall_outcome"), "NOT_REPORTED")


def normalized_reading_method(item: dict[str, Any]) -> str:
    method = normalized_text(item.get("reading_method"), "").lower()
    if method:
        return method
    ocr_status = normalized_ocr_status(item)
    status = normalized_extraction_status(item)
    if ocr_status == "attempted_success":
        return "ocr_text"
    if ocr_status == "attempted_failed":
        return "ocr_failed"
    if status == "ok":
        return "direct_text"
    return "unknown"


def normalized_ocr_status(item: dict[str, Any]) -> str:
    return normalized_text(item.get("ocr_status"), "unknown").lower()


def normalized_reading_confidence(item: dict[str, Any]) -> str:
    return normalized_text(item.get("reading_confidence"), normalized_text_quality(item)).lower()


def file_name(item: dict[str, Any]) -> str:
    name = item.get("file_name")
    if name:
        return str(name)
    path = item.get("file_path")
    if path:
        return Path(str(path)).name
    return "unknown-file"


def extractable_text_chars(item: dict[str, Any]) -> int:
    value = item.get("extractable_text_chars")
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def is_unreadable(item: dict[str, Any]) -> bool:
    status = normalized_extraction_status(item)
    classification = normalized_classification(item)
    return status in {"unreadable", "unreadable_or_empty", "error"} or classification == "UNREADABLE"


def is_partially_usable(item: dict[str, Any]) -> bool:
    if is_unreadable(item):
        return False
    outcome = normalized_outcome(item).upper()
    quality = normalized_text_quality(item)
    return "PARTIAL_PASS" in outcome or (normalized_extraction_status(item) == "ok" and quality in PARTIAL_TEXT_QUALITIES)


def has_insufficient_text(item: dict[str, Any]) -> bool:
    if normalized_extraction_status(item) == "unreadable_or_empty":
        return True
    if extractable_text_chars(item) == 0:
        return True
    return normalized_text_quality(item) in INSUFFICIENT_TEXT_QUALITIES


def classification_counts(payload: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, int]:
    raw_counts = payload.get("classification_counts")
    if isinstance(raw_counts, dict) and raw_counts:
        return {str(key): int(value) for key, value in raw_counts.items()}
    counts = Counter(normalized_classification(item) for item in items)
    return dict(counts)


def reading_method_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"direct_text": 0, "ocr_text": 0, "ocr_failed": 0}
    for item in items:
        method = normalized_reading_method(item)
        if method in counts:
            counts[method] += 1
    return counts


def document_outcome_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"PARTIAL_PASS": 0, "BLOCKED": 0, "PASS": 0}
    for item in items:
        outcome = normalized_outcome(item).upper()
        if "PARTIAL_PASS" in outcome:
            counts["PARTIAL_PASS"] += 1
        elif "BLOCKED" in outcome:
            counts["BLOCKED"] += 1
        elif outcome == "PASS" or outcome.startswith("PASS "):
            counts["PASS"] += 1
    return counts


def gate_status_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"WARN": 0, "NOT_EVALUATED": 0}
    for item in items:
        gates = item.get("gates")
        if not isinstance(gates, dict):
            continue
        for gate in gates.values():
            if not isinstance(gate, dict):
                continue
            status = normalized_text(gate.get("status")).upper()
            if status in counts:
                counts[status] += 1
    return counts


def summarize_gates(item: dict[str, Any]) -> str:
    gates = item.get("gates")
    if not isinstance(gates, dict) or not gates:
        return "not exposed in legacy item"
    ordered_names = [name for name in PRIMARY_GATE_ORDER if name in gates]
    ordered_names.extend(sorted(name for name in gates if name not in ordered_names))
    parts: list[str] = []
    for name in ordered_names:
        gate = gates.get(name)
        if not isinstance(gate, dict):
            continue
        status = normalized_text(gate.get("status")).upper()
        parts.append(f"{name}={status}")
    return "; ".join(parts) if parts else "not exposed in legacy item"


def aggregate_counter(value: Any, counter: Counter[str]) -> None:
    if isinstance(value, dict):
        for key, item_value in value.items():
            try:
                counter[str(key)] += int(item_value)
            except (TypeError, ValueError):
                counter[str(key)] += 1
        return
    if isinstance(value, list):
        for entry in value:
            text = str(entry).strip()
            if text:
                counter[text] += 1
        return
    text = str(value or "").strip()
    if text:
        counter[text] += 1


def flatten_scalar_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(entry).strip() for entry in value if str(entry).strip()]
    if isinstance(value, dict):
        return [str(key).strip() for key, item_value in value.items() if item_value]
    text = str(value or "").strip()
    return [text] if text else []


def pix_total(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return 1 if value.strip() else 0
    if isinstance(value, list):
        return sum(pix_total(entry) for entry in value) or len(value)
    if isinstance(value, dict):
        return sum(pix_total(entry) for entry in value.values()) or len(value)
    return 0


def aggregate_signals(items: list[dict[str, Any]]) -> dict[str, Any]:
    dates: list[str] = []
    currency_values: list[str] = []
    evidence_markers: Counter[str] = Counter()
    accusation_terms: Counter[str] = Counter()
    pix_mentions_total = 0
    pix_documents = 0

    for item in items:
        signals = item.get("key_signals")
        if not isinstance(signals, dict):
            continue
        dates.extend(flatten_scalar_list(signals.get("dates_found")))
        currency_values.extend(flatten_scalar_list(signals.get("currency_values_found")))
        aggregate_counter(signals.get("evidence_marker_hits") or {}, evidence_markers)
        aggregate_counter(signals.get("accusation_keyword_hits") or {}, accusation_terms)
        pix_value = signals.get("pix_mentions")
        total = pix_total(pix_value)
        if total > 0:
            pix_mentions_total += total
            pix_documents += 1

    unique_dates = sorted(dict.fromkeys(dates))
    unique_currency_values = list(dict.fromkeys(currency_values))
    return {
        "dates_found": unique_dates,
        "currency_values_found": unique_currency_values,
        "pix_mentions_total": pix_mentions_total,
        "pix_documents": pix_documents,
        "evidence_markers": evidence_markers,
        "accusation_terms": accusation_terms,
    }


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "nenhum marcador agregado"
    parts = [f"{key}={counter[key]}" for key in sorted(counter, key=lambda value: (-counter[value], value))]
    return ", ".join(parts)


def format_list(values: list[str], empty_text: str) -> str:
    return ", ".join(values) if values else empty_text


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    items = legacy_items(payload)
    gate_counts = gate_status_counts(items)
    outcomes = document_outcome_counts(items)
    counts = classification_counts(payload, items)
    reading_counts = reading_method_counts(items)
    signals = aggregate_signals(items)
    unreadable_count = sum(1 for item in items if is_unreadable(item))
    ok_count = sum(1 for item in items if normalized_extraction_status(item) == "ok")
    partial_count = sum(1 for item in items if is_partially_usable(item))
    insufficient_text_count = sum(1 for item in items if has_insufficient_text(item))
    non_accusation_count = len([item for item in payload.get("non_accusation_set") or [] if isinstance(item, dict)])
    report = {
        "generated_at": normalized_text(payload.get("generated_at")),
        "audit_basis": normalized_text(payload.get("audit_basis")),
        "mode": normalized_text(payload.get("mode") or payload.get("compliance_gate_mode")),
        "total_files_scanned": int(payload.get("total_files_scanned") or len(items)),
        "accusation_set_count": int(payload.get("accusation_set_count") or len(payload.get("accusation_set") or [])),
        "non_accusation_set_count": non_accusation_count,
        "classification_counts": counts,
        "document_outcomes": outcomes,
        "gate_counts": gate_counts,
        "reading_counts": reading_counts,
        "signals": signals,
        "coverage": {
            "ok_count": ok_count,
            "unreadable_count": unreadable_count,
            "partial_count": partial_count,
            "insufficient_text_count": insufficient_text_count,
        },
        "documents": [
            {
                "file_name": file_name(item),
                "classification": normalized_classification(item),
                "extraction_status": normalized_extraction_status(item),
                "text_quality": normalized_text_quality(item),
                "reading_method": normalized_reading_method(item),
                "ocr_status": normalized_ocr_status(item),
                "reading_confidence": normalized_reading_confidence(item),
                "overall_outcome": normalized_outcome(item),
                "gate_summary": summarize_gates(item),
            }
            for item in items
        ],
    }
    report["client_documents"] = [summarize_document_for_client(doc) for doc in report["documents"]]
    report["reasoning"] = build_legacy_reasoning_summary(report)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    docs = report["documents"]
    client_docs = report["client_documents"]
    counts = report["classification_counts"]
    outcomes = report["document_outcomes"]
    gate_counts = report["gate_counts"]
    reading_counts = report["reading_counts"]
    coverage = report["coverage"]
    signals = report["signals"]
    reasoning = report["reasoning"]

    lines: list[str] = []
    lines.append("# Resumo para primeira leitura do lote legado")
    lines.append("")
    lines.append("## 1. O que ja da para ver")
    lines.append(f"- Arquivos analisados: `{report['total_files_scanned']}`")
    lines.append(f"- Documentos que ja podem ser usados agora: `{outcomes['PASS']}`")
    lines.append(f"- Documentos que pedem cuidado ou complemento: `{outcomes['PARTIAL_PASS']}`")
    lines.append(f"- Documentos que ainda nao podem ser usados agora: `{outcomes['BLOCKED']}`")
    lines.append(f"- Documentos que ainda nao foi possivel avaliar: `{coverage['unreadable_count']}`")
    lines.append("")
    lines.append("## 2. Como os arquivos puderam ser lidos")
    lines.append(f"- Arquivos lidos sem dificuldade relevante: `{coverage['ok_count']}`")
    lines.append(f"- Arquivos lidos com aproveitamento parcial: `{coverage['partial_count']}`")
    lines.append(f"- Arquivos com texto insuficiente: `{coverage['insufficient_text_count']}`")
    lines.append(f"- Arquivos que dependeram de OCR: `{reading_counts['ocr_text']}`")
    lines.append(f"- Arquivos em que o OCR nao recuperou texto suficiente: `{reading_counts['ocr_failed']}`")
    lines.append("")
    lines.append("## 3. O que o lote mostra")
    lines.append("| Leitura para o cliente | Quantidade |")
    lines.append("| --- | ---: |")
    for classification, quantity in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {client_label_for_classification(classification)} | `{quantity}` |")
    lines.append(f"- Documentos que podem indicar problema: `{report['accusation_set_count']}`")
    if report["non_accusation_set_count"] > 0:
        lines.append(f"- Documentos de apoio ou contexto: `{report['non_accusation_set_count']}`")
    lines.append("")
    lines.append("## 4. Documento por documento")
    lines.append("| Documento | Esse documento ajuda o caso? | Pode ser usado agora? | Como foi a leitura? | Regras e origem |")
    lines.append("| --- | --- | --- | --- | --- |")
    for doc in client_docs:
        lines.append(
            "| `{file_name}` | {helps_case} | {can_use_now} | {reading_status} | {origin_and_rules} |".format(
                **doc
            )
        )
    lines.append("")
    lines.append("## 5. Sinais que apareceram com mais forca")
    lines.append(f"- Datas encontradas: {format_list(signals['dates_found'], 'nenhuma data agregada')}")
    lines.append(
        f"- Valores monetarios encontrados: {format_list(signals['currency_values_found'], 'nenhum valor monetario agregado')}"
    )
    lines.append(
        f"- Mencoes a Pix: `{signals['pix_mentions_total']}` ocorrencia(s) em `{signals['pix_documents']}` documento(s)"
    )
    lines.append(f"- Marcadores de prova: {translate_client_text(format_counter(signals['evidence_markers']))}")
    lines.append(f"- Termos que indicam problema: {translate_client_text(format_counter(signals['accusation_terms']))}")
    lines.append("")
    lines.append("## 6. Pendencias e cautelas")
    lines.append(f"- Preservar incerteza: `{'sim' if reasoning['must_preserve_unknown'] else 'nao'}`")
    lines.append(f"- Pedir mais documentos: `{'sim' if reasoning['must_request_more_documents'] else 'nao'}`")
    lines.append(f"- Nota de cautela: {translate_client_text(reasoning['conclusion_note'])}")
    lines.append("- Documento bloqueado nao e documento inutil. Ele apenas ainda nao sustenta um juizo mais forte.")
    lines.append("- Documento ainda nao avaliado nao significa falha final. Significa limite de leitura ou de estrutura.")
    lines.append("")
    lines.append("## 7. Apendice tecnico resumido")
    lines.append(f"- Modo tecnico registrado: `{report['mode']}`")
    lines.append(f"- Base tecnica registrada: `{report['audit_basis']}`")
    lines.append(f"- Gates com `WARN`: `{gate_counts['WARN']}`")
    lines.append(f"- Gates com `NOT_EVALUATED`: `{gate_counts['NOT_EVALUATED']}`")
    lines.append(f"- Policy de raciocinio: `{reasoning['policy_name']}`")
    lines.append("")
    lines.append("| Documento | Classificacao tecnica | Extraction status | Text quality | Metodo de leitura | OCR status | Confianca | Overall outcome | Gates principais |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for doc in docs:
        lines.append(
            "| `{file_name}` | `{classification}` | `{extraction_status}` | `{text_quality}` | `{reading_method}` | `{ocr_status}` | `{reading_confidence}` | `{overall_outcome}` | {gate_summary} |".format(
                **doc
            )
        )
    lines.append("")
    lines.append("## 8. Observacao final")
    lines.append(
        "Este resumo organiza o legado em linguagem de primeira leitura, mas preserva um apendice tecnico para rastreabilidade."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a sanitized legacy TCRIA audit payload into a human-readable Markdown coverage summary."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to the sanitized legacy JSON payload.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for the generated Markdown report.")
    args = parser.parse_args()

    payload = load_payload(args.input.expanduser().resolve())
    report = build_report(payload)

    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(report), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
