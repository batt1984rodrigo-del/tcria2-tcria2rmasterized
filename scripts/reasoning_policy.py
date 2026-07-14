from __future__ import annotations

from typing import Any


POLICY_NAME = "generic_reasoning_policy"
UNKNOWN_STATUSES = {"inconclusive", "unknown", "not_evaluated", "not evaluated"}
HIGH_CONFIDENCE = {"high"}
DOCUMENT_REQUEST_HINTS = {
    "missing",
    "not present",
    "does not contain",
    "without",
    "pending",
    "attachment",
    "approval",
    "support",
    "record",
    "ratification",
}


def normalized_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def normalized_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def classify_claim_type(finding: dict[str, Any]) -> str:
    conformity_status = normalized_text(finding.get("conformity_status")).lower()
    if conformity_status in UNKNOWN_STATUSES:
        return "unknown"
    return "inference"


def evidence_is_sufficient(finding: dict[str, Any]) -> bool:
    what_identified = normalized_text(finding.get("what_identified"))
    why_matters = normalized_text(finding.get("why_matters"))
    supporting_evidence = normalized_list(finding.get("supporting_evidence"))
    return bool(what_identified and why_matters and supporting_evidence)


def must_request_more_documents(finding: dict[str, Any]) -> bool:
    haystack = " ".join(
        [
            normalized_text(finding.get("title")),
            normalized_text(finding.get("what_identified")),
            normalized_text(finding.get("why_matters")),
            " ".join(normalized_list(finding.get("supporting_evidence"))),
        ]
    ).lower()
    return any(hint in haystack for hint in DOCUMENT_REQUEST_HINTS)


def build_finding_reasoning(finding: dict[str, Any]) -> dict[str, Any]:
    claim_type = classify_claim_type(finding)
    evidence_sufficient = evidence_is_sufficient(finding)
    needs_more_documents = must_request_more_documents(finding)
    return {
        "claim_type": claim_type,
        "evidence_sufficient": evidence_sufficient,
        "evidence_sufficient_label": "sufficient" if evidence_sufficient else "insufficient",
        "needs_more_documents": needs_more_documents,
        "needs_more_documents_label": "yes" if needs_more_documents else "no",
        "preserve_unknown": claim_type == "unknown" or not evidence_sufficient,
    }


def validate_finding_reasoning(finding: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    finding_id = normalized_text(finding.get("finding_id"))
    title = normalized_text(finding.get("title"))
    follow_up = normalized_list(finding.get("follow_up"))
    confidence = normalized_text(finding.get("confidence")).lower()
    reasoning = build_finding_reasoning(finding)

    if not finding_id:
        issues.append("finding is missing finding_id")
    if not title:
        issues.append("finding is missing title")
    if not reasoning["evidence_sufficient"]:
        issues.append("finding is missing required reasoning support")
    if reasoning["claim_type"] == "unknown" and confidence in HIGH_CONFIDENCE:
        issues.append("inconclusive findings cannot use high confidence")
    if reasoning["needs_more_documents"] and not follow_up:
        issues.append("finding suggests missing material but has no follow-up request")

    return issues


def build_report_reasoning_summary(data: dict[str, Any]) -> dict[str, Any]:
    findings = data.get("findings")
    if not isinstance(findings, list):
        findings = []

    reasoning_records = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        reasoning = finding.get("reasoning")
        if not isinstance(reasoning, dict):
            reasoning = build_finding_reasoning(finding)
        reasoning_records.append(reasoning)

    findings_reviewed = len(reasoning_records)
    unknown_finding_count = sum(1 for item in reasoning_records if item["claim_type"] == "unknown")
    document_request_count = sum(1 for item in reasoning_records if item["needs_more_documents"])
    evidence_sufficient_count = sum(1 for item in reasoning_records if item["evidence_sufficient"])

    return {
        "policy_name": POLICY_NAME,
        "validation_status": "passed",
        "findings_reviewed": findings_reviewed,
        "unknown_finding_count": unknown_finding_count,
        "document_request_count": document_request_count,
        "evidence_sufficient_count": evidence_sufficient_count,
    }


def validate_report_reasoning(data: dict[str, Any]) -> None:
    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        raise ValueError("Report must contain at least one finding.")

    errors: list[str] = []
    unknown_finding_count = 0

    for finding in findings:
        if not isinstance(finding, dict):
            errors.append("finding entry must be an object")
            continue
        finding_id = normalized_text(finding.get("finding_id"), "unknown-finding")
        reasoning = build_finding_reasoning(finding)
        if reasoning["claim_type"] == "unknown":
            unknown_finding_count += 1
        for issue in validate_finding_reasoning(finding):
            errors.append(f"{finding_id}: {issue}")

    unresolved_points = normalized_list(data.get("unresolved_points"))
    if unknown_finding_count > 0 and not unresolved_points:
        errors.append("report contains inconclusive findings but no unresolved_points")

    if errors:
        joined = "\n".join(f"- {item}" for item in errors)
        raise ValueError(f"Reasoning policy validation failed:\n{joined}")


def apply_reasoning_policy(data: dict[str, Any]) -> dict[str, Any]:
    validate_report_reasoning(data)

    findings = []
    for finding in data.get("findings", []):
        if not isinstance(finding, dict):
            continue
        enriched_finding = dict(finding)
        enriched_finding["reasoning"] = build_finding_reasoning(finding)
        findings.append(enriched_finding)

    enriched_data = dict(data)
    enriched_data["findings"] = findings
    enriched_data["reasoning_policy_summary"] = build_report_reasoning_summary(enriched_data)
    return enriched_data


def build_legacy_reasoning_summary(report: dict[str, Any]) -> dict[str, Any]:
    coverage = report["coverage"]
    outcomes = report["document_outcomes"]
    gate_counts = report["gate_counts"]

    must_preserve_unknown = (
        coverage["insufficient_text_count"] > 0
        or coverage["unreadable_count"] > 0
        or outcomes["BLOCKED"] > 0
        or gate_counts["NOT_EVALUATED"] > 0
    )
    must_request_more_documents = (
        coverage["insufficient_text_count"] > 0
        or coverage["unreadable_count"] > 0
        or outcomes["BLOCKED"] > 0
    )

    if must_preserve_unknown:
        conclusion_posture = "bounded_only"
        conclusion_note = "Current material does not support a stronger conclusion."
    else:
        conclusion_posture = "bounded_supported"
        conclusion_note = "Current material supports a bounded technical summary."

    return {
        "policy_name": POLICY_NAME,
        "must_preserve_unknown": must_preserve_unknown,
        "must_request_more_documents": must_request_more_documents,
        "conclusion_posture": conclusion_posture,
        "conclusion_note": conclusion_note,
    }
