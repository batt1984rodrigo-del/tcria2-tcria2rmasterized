from __future__ import annotations

import re
import unicodedata
from typing import Any


COMPARABLE_FIELDS = (
    "dates",
    "values",
    "deadlines",
    "statuses",
    "responsible_parties",
    "approvals",
    "identifiers",
)

FIELD_ALIASES = {
    "dates": ("dates", "datas"),
    "values": ("values", "valores"),
    "deadlines": ("deadlines", "prazos"),
    "statuses": ("statuses", "status", "situacoes"),
    "responsible_parties": ("responsible_parties", "responsaveis"),
    "approvals": ("approvals", "aprovacoes"),
    "identifiers": ("identifiers", "identificadores"),
}


def normalized_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def slug(value: Any) -> str:
    text = unicodedata.normalize("NFKD", normalized_text(value))
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return text


def normalized_list(value: Any) -> list[str]:
    if value is None:
        return []
    source = value if isinstance(value, list) else [value]
    output: list[str] = []
    seen: set[str] = set()
    for item in source:
        text = normalized_text(item)
        key = slug(text)
        if not text or not key or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def normalized_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, Any] = {}
    for raw_key, raw_value in value.items():
        key = slug(raw_key)
        if not key or raw_value is None or raw_value == "":
            continue
        if isinstance(raw_value, list):
            values = normalized_list(raw_value)
            if values:
                output[key] = values
            continue
        if isinstance(raw_value, (str, int, float, bool)):
            output[key] = raw_value.strip() if isinstance(raw_value, str) else raw_value
    return output


def first_value(source: dict[str, Any], keys: tuple[str, ...], default: Any = "") -> Any:
    for key in keys:
        value = source.get(key)
        if value is not None and value != "":
            return value
    return default


def collect_mapping(source: dict[str, Any], field: str) -> dict[str, Any]:
    for alias in FIELD_ALIASES[field]:
        value = source.get(alias)
        if isinstance(value, dict):
            return normalized_mapping(value)
    facts = source.get("facts") or source.get("fatos")
    if isinstance(facts, dict):
        for alias in FIELD_ALIASES[field]:
            value = facts.get(alias)
            if isinstance(value, dict):
                return normalized_mapping(value)
    return {}


def normalize_document(raw_document: dict[str, Any], index: int) -> dict[str, Any]:
    name = normalized_text(
        first_value(raw_document, ("document_name", "document", "file_name", "name", "nome")),
        f"documento-{index}",
    )
    document_id = normalized_text(
        first_value(raw_document, ("document_id", "id", "evidence_id", "identificacao")),
        slug(name) or f"documento-{index}",
    )
    explicit_group = normalized_text(
        first_value(
            raw_document,
            ("group_id", "contract_id", "process_id", "operation_id", "event_id", "grupo_id"),
        )
    )

    normalized = {
        "document_id": document_id,
        "document_name": name,
        "document_type": normalized_text(
            first_value(raw_document, ("document_type", "type", "tipo_documento", "tipo")),
            "documento",
        ),
        "subject": normalized_text(first_value(raw_document, ("subject", "assunto"))),
        "entities": normalized_list(first_value(raw_document, ("entities", "entidades"), [])),
        "explicit_group": explicit_group,
        "pattern_group": normalized_text(
            first_value(raw_document, ("pattern_group", "grupo_de_padrao", "procedure_group"))
        ),
        "relation_label": normalized_text(
            first_value(raw_document, ("relation_label", "relacao", "relationship")),
            "mesmo assunto ou processo",
        ),
        "required_references": normalized_list(
            first_value(raw_document, ("required_references", "referencias_obrigatorias"), [])
        ),
        "process_steps": normalized_list(
            first_value(raw_document, ("process_steps", "etapas_do_processo", "procedimento"), [])
        ),
        "features": normalized_mapping(first_value(raw_document, ("features", "caracteristicas"), {})),
    }
    for field in COMPARABLE_FIELDS:
        normalized[field] = collect_mapping(raw_document, field)
    return normalized


def normalize_documents(raw_documents: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_documents, list):
        return []
    return [
        normalize_document(item, index)
        for index, item in enumerate(raw_documents, start=1)
        if isinstance(item, dict)
    ]


def canonical_value(value: Any) -> str:
    if isinstance(value, list):
        return "|".join(sorted(slug(item) for item in value if slug(item)))
    if isinstance(value, bool):
        return "sim" if value else "nao"
    if isinstance(value, (int, float)):
        return str(value)
    return slug(value)


def display_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, bool):
        return "sim" if value else "nao"
    return str(value)
