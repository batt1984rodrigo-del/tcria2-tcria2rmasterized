from __future__ import annotations

from typing import Any

from ._helpers import dedupe_keep_order, finding_haystack


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
        if "inconsistent" in haystack:
            items.append("Documentos semelhantes nao seguem o mesmo padrao de justificativa e aprovacao.")

    if not items and any(item.get("status") == "em aberto" for item in hypotheses):
        items.append("Ainda nao existe uma leitura uniforme o bastante para fechar todas as hipoteses do lote.")

    return {"items": dedupe_keep_order(items)}


def build_legacy_contradictions(report: dict[str, Any], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = report.get("coverage") or {}
    outcomes = report.get("document_outcomes") or {}
    items: list[str] = []

    if int(outcomes.get("PASS") or 0) > 0 and int(outcomes.get("BLOCKED") or 0) > 0:
        items.append("Parte do lote ajuda a leitura, mas outra parte ainda nao pode ser usada.")
    if int(coverage.get("ok_count") or 0) > 0 and int(coverage.get("insufficient_text_count") or 0) > 0:
        items.append("Alguns arquivos sustentam a leitura, mas outros continuam limitados pela qualidade do texto.")
    if int((report.get("gate_counts") or {}).get("NOT_EVALUATED") or 0) > 0:
        items.append("Ha trechos do lote em que a leitura avancou mais do que a validacao tecnica conseguiu fechar.")

    if not items and any(item.get("status") == "em aberto" for item in hypotheses):
        items.append("A leitura atual ainda mistura material util com limites que impedem fechamento completo.")

    return {"items": dedupe_keep_order(items)}
