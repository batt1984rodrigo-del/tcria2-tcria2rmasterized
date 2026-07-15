from __future__ import annotations

from typing import Any

from ._helpers import (
    EXCEPTION_TERMS,
    FRAUD_TERMS,
    INCONSISTENCY_TERMS,
    NO_ACCOUNTABILITY_TERMS,
    TAMPERING_TERMS,
    VAGUE_TERMS,
    dedupe_keep_order,
    finding_haystack,
    normalized_list,
    normalized_text,
)


def contains_any_term(haystack: str, terms: set[str]) -> bool:
    return any(term in haystack for term in terms)


def legacy_document_haystack(document: dict[str, Any]) -> str:
    parts = [
        normalized_text(document.get("file_name")),
        normalized_text(document.get("summary")),
        normalized_text(document.get("gate_summary")),
        normalized_text(document.get("notes")),
        " ".join(normalized_list(document.get("classification_reasons"))),
        " ".join(normalized_list(document.get("supporting_evidence"))),
    ]
    return " ".join(part for part in parts if part).lower()


def legacy_signal_haystack(report: dict[str, Any]) -> str:
    signals = report.get("signals") or {}
    accusation_terms = signals.get("accusation_terms") or {}
    evidence_markers = signals.get("evidence_markers") or {}
    parts = [str(key) for key in accusation_terms]
    parts.extend(str(key) for key in evidence_markers)
    return " ".join(part for part in parts if part).lower()


def build_report_contradictions(data: dict[str, Any], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    findings = [item for item in data.get("findings") or [] if isinstance(item, dict)]
    items: list[str] = []

    for finding in findings:
        haystack = finding_haystack(finding)
        if "pending" in haystack:
            items.append("Existe registro marcado como pendente onde deveria haver fechamento documental.")
        if "urgency" in haystack and "authorization" in haystack:
            items.append("A urgencia aparece no material, mas a autorizacao final nao aparece nas provas reunidas.")
        if "approved" in haystack and any(term in haystack for term in ("missing", "incomplete", "without source documents")):
            items.append("Algo aparece como aprovado, mas a prova que sustentaria essa aprovacao segue incompleta.")
        if "only by email" in haystack or "only by email language" in haystack:
            items.append("Parte do que deveria estar formalizado aparece apenas em e-mail.")
        if contains_any_term(haystack, INCONSISTENCY_TERMS):
            items.append("O documento apresenta trechos internamente divergentes ou incompatíveis.")
        if contains_any_term(haystack, EXCEPTION_TERMS):
            items.append("Foi identificada dispensa ou exceção de processo sem fundamentação formal clara.")
        if contains_any_term(haystack, VAGUE_TERMS):
            items.append("Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.")
        if contains_any_term(haystack, FRAUD_TERMS):
            items.append("Há sinais de direcionamento ou irregularidade na seleção ou pagamento ao fornecedor.")
        if contains_any_term(haystack, NO_ACCOUNTABILITY_TERMS):
            items.append("O documento diluiu ou omitiu responsabilidades que deveriam estar claramente atribuídas.")
        if contains_any_term(haystack, TAMPERING_TERMS):
            items.append("Foram identificados sinais de possível adulteração ou irregularidade formal no documento.")

    if not items and any(item.get("status") == "em aberto" for item in hypotheses):
        items.append("Ainda nao existe uma leitura uniforme o bastante para fechar todas as hipoteses do lote.")

    return {"items": dedupe_keep_order(items)}


def build_legacy_contradictions(report: dict[str, Any], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = report.get("coverage") or {}
    outcomes = report.get("document_outcomes") or {}
    documents = [item for item in report.get("documents") or [] if isinstance(item, dict)]
    document_haystacks = [legacy_document_haystack(document) for document in documents]
    signals_haystack = legacy_signal_haystack(report)
    items: list[str] = []

    if int(outcomes.get("PASS") or 0) > 0 and int(outcomes.get("BLOCKED") or 0) > 0:
        items.append("Parte do lote ajuda a leitura, mas outra parte ainda nao pode ser usada.")
    if int(coverage.get("ok_count") or 0) > 0 and int(coverage.get("insufficient_text_count") or 0) > 0:
        items.append("Alguns arquivos sustentam a leitura, mas outros continuam limitados pela qualidade do texto.")
    if int((report.get("gate_counts") or {}).get("NOT_EVALUATED") or 0) > 0:
        items.append("Ha trechos do lote em que a leitura avancou mais do que a validacao tecnica conseguiu fechar.")
    if any(contains_any_term(haystack, INCONSISTENCY_TERMS) for haystack in document_haystacks):
        items.append("O documento apresenta trechos internamente divergentes ou incompatíveis.")
    if contains_any_term(signals_haystack, EXCEPTION_TERMS) or any(
        contains_any_term(haystack, EXCEPTION_TERMS) for haystack in document_haystacks
    ):
        items.append("Foi identificada dispensa ou exceção de processo sem fundamentação formal clara.")
    if any(contains_any_term(haystack, VAGUE_TERMS) for haystack in document_haystacks):
        items.append("Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.")

    if not items and any(item.get("status") == "em aberto" for item in hypotheses):
        items.append("A leitura atual ainda mistura material util com limites que impedem fechamento completo.")

    return {"items": dedupe_keep_order(items)}
