from __future__ import annotations

from typing import Any

from client_language import translate_client_text

from ._helpers import dedupe_keep_order, translated_list


def build_report_gaps(data: dict[str, Any]) -> dict[str, Any]:
    unresolved_points = translated_list(data.get("unresolved_points"))
    limits = translated_list(data.get("limits"))
    items = dedupe_keep_order(unresolved_points + limits)
    return {
        "items": items,
        "unresolved_points": unresolved_points,
        "limits": limits,
    }


def build_legacy_gaps(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report.get("coverage") or {}
    outcomes = report.get("document_outcomes") or {}
    items: list[str] = []

    if int(coverage.get("insufficient_text_count") or 0) > 0:
        items.append("Ainda faltam arquivos com texto suficiente para fechar parte da leitura.")
    if int(coverage.get("unreadable_count") or 0) > 0:
        items.append("Parte do lote segue sem leitura aproveitavel.")
    if int(outcomes.get("BLOCKED") or 0) > 0:
        items.append("Ainda ha documentos com pendencias estruturais ou de origem.")
    if int((report.get("gate_counts") or {}).get("NOT_EVALUATED") or 0) > 0:
        items.append("Ha verificacoes tecnicas que ainda nao puderam ser avaliadas.")

    return {
        "items": dedupe_keep_order(items),
        "unresolved_points": dedupe_keep_order(items),
        "limits": [],
    }
