from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any

from .normalize import canonical_value, display_value, slug


FIELD_RULES = {
    "dates": {
        "signal_type": "data_divergente",
        "title": "Data divergente",
        "impact": "A sequencia ou o enquadramento temporal pode mudar conforme a data adotada.",
    },
    "values": {
        "signal_type": "valor_divergente",
        "title": "Valor divergente",
        "impact": "A obrigacao financeira pode estar sendo interpretada com bases diferentes.",
    },
    "deadlines": {
        "signal_type": "prazo_divergente",
        "title": "Prazo divergente",
        "impact": "A execucao pode estar seguindo uma condicao diferente da que foi formalizada.",
    },
    "statuses": {
        "signal_type": "status_divergente",
        "title": "Situacao divergente",
        "impact": "O conjunto nao apresenta uma situacao unica para o mesmo assunto.",
    },
    "responsible_parties": {
        "signal_type": "responsavel_divergente",
        "title": "Responsavel divergente",
        "impact": "A atribuicao de responsabilidade pode nao estar clara ou uniforme.",
    },
    "approvals": {
        "signal_type": "aprovacao_divergente",
        "title": "Aprovacao divergente",
        "impact": "A autorizacao do ato pode depender de uma comprovacao ainda nao conciliada.",
    },
    "identifiers": {
        "signal_type": "identificador_divergente",
        "title": "Identificador divergente",
        "impact": "Os documentos podem estar apontando para pessoas, empresas ou operacoes diferentes.",
    },
}

STATUS_EQUIVALENTS = {
    "approved": "aprovado",
    "aprovada": "aprovado",
    "aprovado": "aprovado",
    "pending": "pendente",
    "pendente": "pendente",
    "rejected": "rejeitado",
    "rejeitada": "rejeitado",
    "rejeitado": "rejeitado",
    "completed": "concluido",
    "complete": "concluido",
    "concluida": "concluido",
    "concluido": "concluido",
}


def decimal_value(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    text = re.sub(r"[^0-9,.-]", "", str(value or ""))
    if not text:
        return None
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        decimal_digits = len(text.rsplit(",", 1)[1])
        text = text.replace(",", ".") if decimal_digits <= 2 else text.replace(",", "")
    elif "." in text:
        decimal_digits = len(text.rsplit(".", 1)[1])
        if decimal_digits > 2:
            text = text.replace(".", "")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def canonical_for_field(field: str, value: Any) -> str:
    if field == "dates":
        parsed = parse_date(value)
        return parsed.isoformat() if parsed else canonical_value(value)
    if field in {"values", "deadlines"}:
        number = decimal_value(value)
        return format(number.normalize(), "f") if number is not None else canonical_value(value)
    if field in {"statuses", "approvals"}:
        canonical = canonical_value(value)
        return STATUS_EQUIVALENTS.get(canonical, canonical)
    return canonical_value(value)


def field_candidates(group: dict[str, Any], field: str) -> list[dict[str, Any]]:
    documents = group["documents"]
    keys = sorted({key for document in documents for key in (document.get(field) or {})})
    candidates: list[dict[str, Any]] = []

    for key in keys:
        observations = []
        distinct_values: set[str] = set()
        for document in documents:
            mapping = document.get(field) or {}
            if key not in mapping:
                continue
            value = mapping[key]
            canonical = canonical_for_field(field, value)
            if not canonical:
                continue
            distinct_values.add(canonical)
            observations.append(
                {
                    "document_id": document["document_id"],
                    "document_name": document["document_name"],
                    "value": display_value(value),
                }
            )
        if len(observations) < 2 or len(distinct_values) < 2:
            continue

        rule = FIELD_RULES[field]
        candidates.append(
            {
                "signal_type": rule["signal_type"],
                "title": rule["title"],
                "comparison_key": key,
                "relationship": group["relationship"],
                "group_id": group["group_id"],
                "observations": observations,
                "impact": rule["impact"],
                "confidence": "alta" if group["group_id"].startswith("grupo:") else "media",
            }
        )
    return candidates


def parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    return None


def dated_observations(documents: list[dict[str, Any]], key_terms: tuple[str, ...]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for document in documents:
        for key, value in (document.get("dates") or {}).items():
            if not any(term in key for term in key_terms):
                continue
            parsed = parse_date(value)
            if parsed is None:
                continue
            observations.append(
                {
                    "document_id": document["document_id"],
                    "document_name": document["document_name"],
                    "value": display_value(value),
                    "parsed": parsed,
                    "date_key": key,
                }
            )
    return observations


def temporal_candidates(group: dict[str, Any]) -> list[dict[str, Any]]:
    documents = group["documents"]
    approvals = dated_observations(documents, ("aprovacao", "approval"))
    executions = dated_observations(documents, ("execucao", "execution", "assinatura", "signature", "inicio"))
    if not approvals or not executions:
        return []

    first_approval = min(approvals, key=lambda item: item["parsed"])
    first_execution = min(executions, key=lambda item: item["parsed"])
    if first_execution["parsed"] >= first_approval["parsed"]:
        return []

    observations = []
    for item in (first_execution, first_approval):
        observations.append(
            {
                "document_id": item["document_id"],
                "document_name": item["document_name"],
                "value": f"{item['date_key']}: {item['value']}",
            }
        )
    return [
        {
            "signal_type": "sequencia_temporal",
            "title": "Execucao anterior a aprovacao",
            "comparison_key": "ordem_aprovacao_execucao",
            "relationship": group["relationship"],
            "group_id": group["group_id"],
            "observations": observations,
            "impact": "O ato pode ter comecado antes do fechamento formal da aprovacao.",
            "confidence": "alta" if group["group_id"].startswith("grupo:") else "media",
        }
    ]


def available_reference_keys(documents: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for document in documents:
        keys.add(slug(document.get("document_id")))
        document_name = str(document.get("document_name") or "")
        keys.add(slug(document_name))
        keys.add(slug(document_name.rsplit(".", 1)[0]))
        for value in (document.get("identifiers") or {}).values():
            if isinstance(value, list):
                keys.update(slug(item) for item in value)
            else:
                keys.add(slug(value))
    return {key for key in keys if key}


def missing_reference_candidates(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    available = available_reference_keys(documents)
    candidates: list[dict[str, Any]] = []
    for document in documents:
        for reference in document.get("required_references") or []:
            if slug(reference) in available:
                continue
            candidates.append(
                {
                    "signal_type": "referencia_ausente",
                    "title": "Documento mencionado nao encontrado",
                    "comparison_key": "referencia_obrigatoria",
                    "relationship": document.get("relation_label") or "documento e referencia mencionada",
                    "group_id": f"referencia:{slug(reference)}",
                    "observations": [
                        {
                            "document_id": document["document_id"],
                            "document_name": document["document_name"],
                            "value": f"menciona {reference}",
                        }
                    ],
                    "impact": "Uma afirmacao relevante pode permanecer sem a comprovacao documental mencionada.",
                    "confidence": "alta",
                }
            )
    return candidates


def compare_groups(groups: list[dict[str, Any]], documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for group in groups:
        if len(group["documents"]) < 2:
            continue
        for field in FIELD_RULES:
            candidates.extend(field_candidates(group, field))
        candidates.extend(temporal_candidates(group))
    candidates.extend(missing_reference_candidates(documents))
    return candidates
