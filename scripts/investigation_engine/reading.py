from __future__ import annotations

from typing import Any

from client_language import translate_client_text


def build_report_reading(data: dict[str, Any]) -> dict[str, Any]:
    reading = data.get("reading_coverage_summary") or {}
    direct = int(reading.get("direct_text_documents") or 0)
    ocr = int(reading.get("ocr_text_documents") or 0)
    failed = int(reading.get("ocr_failed_documents") or 0)
    items = [
        f"{direct} documentos foram lidos com texto direto.",
        f"{ocr} documentos dependeram de OCR para recuperar leitura util.",
        f"{failed} documentos continuaram com leitura limitada mesmo apos OCR.",
        translate_client_text(reading.get("reading_confidence_rule") or ""),
    ]
    return {
        "items": [item for item in items if item],
        "direct_text_documents": direct,
        "ocr_text_documents": ocr,
        "ocr_failed_documents": failed,
    }


def build_legacy_reading(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report.get("coverage") or {}
    reading_counts = report.get("reading_counts") or {}
    items = [
        f"{int(coverage.get('ok_count') or 0)} arquivo(s) tiveram leitura aproveitavel sem grande restricao.",
        f"{int(coverage.get('partial_count') or 0)} arquivo(s) tiveram aproveitamento parcial.",
        f"{int(coverage.get('insufficient_text_count') or 0)} arquivo(s) ficaram com texto insuficiente.",
        f"{int(reading_counts.get('ocr_text') or 0)} arquivo(s) dependeram de OCR.",
        f"{int(reading_counts.get('ocr_failed') or 0)} arquivo(s) continuaram limitados depois do OCR.",
    ]
    return {
        "items": items,
        "direct_text_documents": int(reading_counts.get("direct_text") or 0),
        "ocr_text_documents": int(reading_counts.get("ocr_text") or 0),
        "ocr_failed_documents": int(reading_counts.get("ocr_failed") or 0),
    }
