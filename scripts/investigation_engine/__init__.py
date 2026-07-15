from __future__ import annotations

from typing import Any

from correlation_engine import build_correlation

from .conclusions import build_legacy_conclusions, build_report_conclusions
from .contradictions import build_legacy_contradictions, build_report_contradictions
from .evidence import build_legacy_evidence, build_report_evidence
from .gaps import build_legacy_gaps, build_report_gaps
from .hypotheses import build_legacy_hypotheses, build_report_hypotheses
from .inventory import build_legacy_inventory, build_report_inventory
from .questioning import build_legacy_questioning, build_report_questioning
from .reading import build_legacy_reading, build_report_reading
from .recommendations import build_legacy_recommendations, build_report_recommendations


ENGINE_NAME = "motor_de_investigacao_documental"


def build_report_investigation(data: dict[str, Any]) -> dict[str, Any]:
    questioning = build_report_questioning(data)
    inventory = build_report_inventory(data)
    reading = build_report_reading(data)
    correlation = build_correlation(data.get("correlation_documents") or [])
    hypotheses = build_report_hypotheses(data)
    evidence = build_report_evidence(data, hypotheses)
    contradictions = build_report_contradictions(data, hypotheses)
    gaps = build_report_gaps(data)
    conclusions = build_report_conclusions(data, hypotheses, gaps)
    recommendations = build_report_recommendations(data, correlation)
    return {
        "engine_name": ENGINE_NAME,
        "questioning": questioning,
        "inventory": inventory,
        "reading": reading,
        "correlation": correlation,
        "hypotheses": hypotheses,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "conclusions": conclusions,
        "recommendations": recommendations,
    }


def build_legacy_investigation(report: dict[str, Any]) -> dict[str, Any]:
    questioning = build_legacy_questioning(report)
    inventory = build_legacy_inventory(report)
    reading = build_legacy_reading(report)
    correlation = build_correlation(report.get("correlation_documents") or [])
    hypotheses = build_legacy_hypotheses(report)
    evidence = build_legacy_evidence(report, hypotheses)
    contradictions = build_legacy_contradictions(report, hypotheses)
    gaps = build_legacy_gaps(report)
    conclusions = build_legacy_conclusions(report, hypotheses, gaps)
    recommendations = build_legacy_recommendations(report)
    return {
        "engine_name": ENGINE_NAME,
        "questioning": questioning,
        "inventory": inventory,
        "reading": reading,
        "correlation": correlation,
        "hypotheses": hypotheses,
        "evidence": evidence,
        "contradictions": contradictions,
        "gaps": gaps,
        "conclusions": conclusions,
        "recommendations": recommendations,
    }
