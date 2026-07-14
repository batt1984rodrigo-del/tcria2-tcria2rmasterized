from __future__ import annotations

from typing import Any

from ._helpers import dedupe_keep_order, translated_list


def build_report_recommendations(data: dict[str, Any]) -> dict[str, Any]:
    items = translated_list(data.get("immediate_priorities")) + translated_list(data.get("next_priorities"))
    return {"items": dedupe_keep_order(items)}


def build_legacy_recommendations(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report.get("coverage") or {}
    items: list[str] = []

    if int(coverage.get("insufficient_text_count") or 0) > 0:
        items.append("Separar e revisar primeiro os arquivos com texto insuficiente.")
    if int((report.get("document_outcomes") or {}).get("BLOCKED") or 0) > 0:
        items.append("Tratar os documentos bloqueados como fila prioritaria de complemento e organizacao.")
    items.append("Usar primeiro os documentos com leitura mais forte para montar a narrativa base do caso.")

    return {"items": dedupe_keep_order(items)}
