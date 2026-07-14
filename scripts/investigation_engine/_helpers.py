from __future__ import annotations

from typing import Any

from client_language import (
    client_label_for_confidence,
    client_label_for_conformity,
    translate_client_text,
)


def normalized_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def normalized_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def translated_list(value: Any) -> list[str]:
    return [translate_client_text(item) for item in normalized_list(value)]


def dedupe_keep_order(items: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = normalized_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output


def lower_first(text: str) -> str:
    clean = normalized_text(text)
    if not clean:
        return clean
    return clean[0].lower() + clean[1:]


def hypothesis_status(conformity_status: Any, confidence: Any) -> str:
    conformity = normalized_text(conformity_status).lower()
    confidence_text = normalized_text(confidence).lower()
    if conformity == "noncompliant" and confidence_text == "high":
        return "sustentada"
    if conformity in {"noncompliant", "partially compliant"}:
        return "sustentada com ressalvas"
    if conformity in {"inconclusive", "unknown", "not evaluated", "not_evaluated"}:
        return "em aberto"
    if conformity == "compliant":
        return "nao abriu problema relevante"
    return "em avaliacao"


def hypothesis_status_reason(finding: dict[str, Any]) -> str:
    conformity = client_label_for_conformity(finding.get("conformity_status")).lower()
    confidence = client_label_for_confidence(finding.get("confidence")).lower()
    return f"Situacao {conformity} com confianca {confidence}."


def finding_haystack(finding: dict[str, Any]) -> str:
    parts = [
        normalized_text(finding.get("title")),
        normalized_text(finding.get("what_identified")),
        normalized_text(finding.get("why_matters")),
        " ".join(normalized_list(finding.get("supporting_evidence"))),
    ]
    return " ".join(part for part in parts if part).lower()
