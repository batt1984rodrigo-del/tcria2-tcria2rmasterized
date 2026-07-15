from __future__ import annotations

from typing import Any

from client_language import translate_client_text

from ._helpers import normalized_text


def build_report_inventory(data: dict[str, Any]) -> dict[str, Any]:
    items = [
        f"Lote analisado: {normalized_text(data.get('batch_name'), 'lote nao informado')}.",
        f"Documentos revisados nesta rodada: {int(data.get('documents_reviewed') or 0)}.",
        f"Origem declarada do material: {translate_client_text(normalized_text(data.get('source_description'), 'origem nao informada'))}.",
        f"Tipos de documento recebidos: {translate_client_text(normalized_text(data.get('document_types'), 'tipos nao informados'))}.",
        f"Registros de prova formal separados: {len(data.get('evidence_register') or [])}.",
        f"Fichas estruturadas para comparacao: {len(data.get('correlation_documents') or [])}.",
        f"Pontos principais abertos pela analise: {len(data.get('findings') or [])}.",
    ]
    return {
        "items": items,
        "document_count": int(data.get("documents_reviewed") or 0),
        "finding_count": len(data.get("findings") or []),
        "evidence_count": len(data.get("evidence_register") or []),
        "correlation_document_count": len(data.get("correlation_documents") or []),
    }


def build_legacy_inventory(report: dict[str, Any]) -> dict[str, Any]:
    items = [
        f"Arquivos totais considerados: {int(report.get('total_files_scanned') or 0)}.",
        f"Documentos que podem indicar problema: {int(report.get('accusation_set_count') or 0)}.",
        f"Documentos de apoio ou contexto: {int(report.get('non_accusation_set_count') or 0)}.",
        f"Classificacoes tecnicas distintas no lote: {len(report.get('classification_counts') or {})}.",
    ]
    return {
        "items": items,
        "document_count": int(report.get("total_files_scanned") or 0),
        "finding_count": len(report.get("classification_counts") or {}),
        "evidence_count": len(report.get("documents") or []),
    }
