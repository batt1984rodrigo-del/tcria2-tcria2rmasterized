from __future__ import annotations

from typing import Any

from client_language import translate_client_text

from ._helpers import dedupe_keep_order


def build_report_conclusions(
    data: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    gaps: dict[str, Any],
) -> dict[str, Any]:
    can_affirm = [
        item["statement"]
        for item in hypotheses
        if item.get("status") in {"sustentada", "sustentada com ressalvas"}
    ]
    cannot_affirm_yet = [
        item["statement"]
        for item in hypotheses
        if item.get("status") == "em aberto"
    ]
    cannot_affirm_yet.extend(gaps.get("unresolved_points") or [])
    return {
        "summary_statement": translate_client_text(data.get("overall_conclusion") or ""),
        "can_affirm": dedupe_keep_order(can_affirm),
        "cannot_affirm_yet": dedupe_keep_order(cannot_affirm_yet),
    }


def build_legacy_conclusions(
    report: dict[str, Any],
    hypotheses: list[dict[str, Any]],
    gaps: dict[str, Any],
) -> dict[str, Any]:
    can_affirm = [
        item["statement"]
        for item in hypotheses
        if item.get("status") in {"sustentada", "sustentada com ressalvas"}
    ]
    cannot_affirm_yet = [
        item["statement"]
        for item in hypotheses
        if item.get("status") == "em aberto"
    ]
    cannot_affirm_yet.extend(gaps.get("items") or [])

    summary_statement = "O lote legado permite uma leitura util, mas ainda nao autoriza conclusao mais forte sem preservar incerteza."
    if not cannot_affirm_yet:
        summary_statement = "O lote legado permite uma leitura delimitada com baixo nivel de pendencia remanescente."

    return {
        "summary_statement": summary_statement,
        "can_affirm": dedupe_keep_order(can_affirm),
        "cannot_affirm_yet": dedupe_keep_order(cannot_affirm_yet),
    }
