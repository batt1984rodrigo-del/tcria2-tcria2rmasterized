from __future__ import annotations

import re


FORBIDDEN_CLIENT_TERMS = [
    "ACCUSATORY_CANDIDATE",
    "SUPPORTING_EVIDENCE_RELEVANT",
    "SUPPORTING_EVIDENCE",
    "SUPPORTING_PROOF",
    "EVIDENTIARY_SUPPORT_GENERAL",
    "complianceGate",
    "traceabilityCheck",
    "blockedArtifactReview",
    "artifact_type",
    "artifact_identity",
    "classification_reasons",
    "official_outcome",
]

FORBIDDEN_TITLE_TERMS = [
    "Blocked Artifacts Review",
    "Strict Audit",
    "Audit Coverage",
    "Compliance Review Report",
    "ComplianceGate",
    "TraceabilityCheck",
]

FORBIDDEN_STATUS_PATTERNS = [
    r"\bPASS\b",
    r"\bWARN\b",
    r"\bBLOCKED\b",
    r"\bNOT_EVALUATED\b",
    r"\bNOT_APPLICABLE\b",
    r"\bTrue\b",
    r"\bFalse\b",
]

FIRST_TIME_CLIENT_SIGNALS = [
    "O que",
    "Pode",
    "Proximos passos",
    "Como ler",
    "Situacao",
    "Documento por documento",
]


def strip_technical_appendix(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("## ") and "Apendice tecnico" in line:
            return "\n".join(lines[:index])
    return markdown_text


def validate_title(title_line: str) -> list[str]:
    errors: list[str] = []
    for term in FORBIDDEN_TITLE_TERMS:
        if term in title_line:
            errors.append(f"title still sounds like engine output: {term}")
    return errors


def find_forbidden_terms(text: str) -> list[str]:
    errors: list[str] = []
    for term in FORBIDDEN_CLIENT_TERMS:
        if term in text:
            errors.append(f"client-visible engine term found: {term}")
    for pattern in FORBIDDEN_STATUS_PATTERNS:
        match = re.search(pattern, text)
        if match:
            errors.append(f"client-visible raw status found: {match.group(0)}")
    return errors


def validate_first_time_client_opening(markdown_text: str) -> list[str]:
    opening = "\n".join(markdown_text.splitlines()[:30])
    if any(signal in opening for signal in FIRST_TIME_CLIENT_SIGNALS):
        return []
    return ["opening section does not guide a first-time client reader"]


def validate_client_markdown(markdown_text: str) -> None:
    lines = markdown_text.splitlines()
    title_line = next((line for line in lines if line.startswith("# ")), "")
    client_visible_body = strip_technical_appendix(markdown_text)

    errors: list[str] = []
    errors.extend(validate_title(title_line))
    errors.extend(validate_first_time_client_opening(markdown_text))
    errors.extend(find_forbidden_terms(client_visible_body))

    if errors:
        unique_errors = []
        seen = set()
        for error in errors:
            if error in seen:
                continue
            seen.add(error)
            unique_errors.append(error)
        message = "\n".join(f"- {error}" for error in unique_errors)
        raise ValueError(f"Client-facing language validation failed:\n{message}")
