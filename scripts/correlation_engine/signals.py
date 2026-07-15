from __future__ import annotations

from collections import Counter
from typing import Any

from .questions import question_for


SIGNAL_ORDER = {
    "sequencia_temporal": 0,
    "aprovacao_divergente": 1,
    "status_divergente": 2,
    "valor_divergente": 3,
    "prazo_divergente": 4,
    "responsavel_divergente": 5,
    "data_divergente": 6,
    "identificador_divergente": 7,
    "referencia_ausente": 8,
    "procedimento_diferente": 9,
    "quebra_de_padrao": 10,
}


def candidate_signature(candidate: dict[str, Any]) -> tuple[Any, ...]:
    observations = tuple(
        sorted(
            (
                str(item.get("document_id") or ""),
                str(item.get("value") or ""),
            )
            for item in candidate.get("observations") or []
        )
    )
    return (
        candidate.get("signal_type"),
        candidate.get("group_id"),
        candidate.get("comparison_key"),
        observations,
    )


def observation_text(observations: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{item.get('document_name')}: {item.get('value')}"
        for item in observations
        if item.get("document_name") and item.get("value")
    )


def finalize_signals(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    ordered = sorted(
        candidates,
        key=lambda item: (
            SIGNAL_ORDER.get(str(item.get("signal_type")), 99),
            str(item.get("group_id") or ""),
            str(item.get("comparison_key") or ""),
        ),
    )
    for candidate in ordered:
        signature = candidate_signature(candidate)
        if signature in seen:
            continue
        seen.add(signature)
        unique.append(candidate)

    signals: list[dict[str, Any]] = []
    for index, candidate in enumerate(unique, start=1):
        observations = list(candidate.get("observations") or [])
        document_names = []
        for item in observations:
            name = str(item.get("document_name") or "").strip()
            if name and not name.startswith("Padrao observado") and name not in document_names:
                document_names.append(name)
        signals.append(
            {
                "signal_id": f"S-{index:02d}",
                "signal_type": candidate["signal_type"],
                "title": candidate["title"],
                "comparison_key": candidate.get("comparison_key") or "",
                "relationship": candidate.get("relationship") or "documentos relacionados",
                "documents": document_names,
                "observation": observation_text(observations),
                "observations": observations,
                "impact": candidate.get("impact") or "A diferenca merece verificacao antes de concluir.",
                "confidence": candidate.get("confidence") or "media",
                "what_to_verify": question_for(candidate),
            }
        )
    return signals


def signal_counts(signals: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(signal.get("signal_type") or "outro") for signal in signals))
