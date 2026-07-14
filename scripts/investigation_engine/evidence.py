from __future__ import annotations

from typing import Any

from client_language import translate_client_text

from ._helpers import translated_list


def build_report_evidence(data: dict[str, Any], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    findings = [item for item in data.get("findings") or [] if isinstance(item, dict)]
    linked_items: list[dict[str, Any]] = []
    total_support_lines = 0
    for index, hypothesis in enumerate(hypotheses):
        finding = findings[index] if index < len(findings) else {}
        evidence_lines = translated_list(finding.get("supporting_evidence"))
        total_support_lines += len(evidence_lines)
        linked_items.append(
            {
                "hypothesis_id": hypothesis["hypothesis_id"],
                "statement": hypothesis["statement"],
                "evidence_lines": evidence_lines,
            }
        )

    summary_lines = [
        f"As hipoteses atuais se apoiam em {total_support_lines} referencia(s) descritas nos achados.",
        f"O registro formal de provas separado traz {len(data.get('evidence_register') or [])} itens adicionais para ancoragem.",
    ]
    return {
        "summary_lines": summary_lines,
        "by_hypothesis": linked_items,
    }


def build_legacy_evidence(report: dict[str, Any], hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    signals = report.get("signals") or {}
    summary_lines = [
        f"O lote legado reuniu {len(report.get('documents') or [])} registro(s) tecnicos de documento.",
        f"Foram agregadas {len(signals.get('dates_found') or [])} data(s) distinta(s) e {len(signals.get('currency_values_found') or [])} valor(es) monetario(s) como sinais auxiliares.",
    ]
    linked_items = [
        {
            "hypothesis_id": item["hypothesis_id"],
            "statement": item["statement"],
            "evidence_lines": [translate_client_text(item["basis"])],
        }
        for item in hypotheses
    ]
    return {
        "summary_lines": summary_lines,
        "by_hypothesis": linked_items,
    }
