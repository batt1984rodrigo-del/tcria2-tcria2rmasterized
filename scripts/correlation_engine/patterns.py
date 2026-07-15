from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .normalize import canonical_value, display_value, slug


def pattern_key(document: dict[str, Any]) -> str:
    explicit = slug(document.get("pattern_group"))
    if explicit:
        return f"padrao:{explicit}"
    return ""


def grouped_for_patterns(documents: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for document in documents:
        key = pattern_key(document)
        if key:
            groups[key].append(document)
    return {key: items for key, items in groups.items() if len(items) >= 3}


def majority_value(observations: list[tuple[dict[str, Any], Any]]) -> tuple[str, int] | None:
    counts = Counter(canonical_value(value) for _, value in observations if canonical_value(value))
    if not counts:
        return None
    value, count = counts.most_common(1)[0]
    if count < 2 or count / len(observations) < 0.6:
        return None
    return value, count


def feature_candidates(group_id: str, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted({key for document in documents for key in (document.get("features") or {})})
    candidates: list[dict[str, Any]] = []
    for key in keys:
        observations = [
            (document, document["features"][key])
            for document in documents
            if key in (document.get("features") or {})
        ]
        if len(observations) < 3:
            continue
        majority = majority_value(observations)
        if majority is None:
            continue
        majority_key, majority_count = majority
        outliers = [(document, value) for document, value in observations if canonical_value(value) != majority_key]
        if not outliers:
            continue

        majority_display = next(
            display_value(value) for _, value in observations if canonical_value(value) == majority_key
        )
        signal_observations = [
            {
                "document_id": document["document_id"],
                "document_name": document["document_name"],
                "value": display_value(value),
            }
            for document, value in outliers
        ]
        signal_observations.insert(
            0,
            {
                "document_id": "padrao-do-grupo",
                "document_name": f"Padrao observado em {majority_count} documentos",
                "value": majority_display,
            },
        )
        candidates.append(
            {
                "signal_type": "quebra_de_padrao",
                "title": f"Quebra de padrao em {key.replace('_', ' ')}",
                "comparison_key": key,
                "relationship": "documentos do mesmo grupo de procedimento",
                "group_id": group_id,
                "observations": signal_observations,
                "impact": "Um item equivalente segue comportamento diferente do padrao predominante.",
                "confidence": "alta",
            }
        )
    return candidates


def process_candidate(group_id: str, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations = [(document, document.get("process_steps") or []) for document in documents]
    observations = [(document, steps) for document, steps in observations if steps]
    if len(observations) < 3:
        return []
    sequence_counts = Counter(tuple(slug(step) for step in steps) for _, steps in observations)
    majority_sequence, majority_count = sequence_counts.most_common(1)[0]
    if majority_count < 2 or majority_count / len(observations) < 0.6:
        return []
    outliers = [
        (document, steps)
        for document, steps in observations
        if tuple(slug(step) for step in steps) != majority_sequence
    ]
    if not outliers:
        return []

    majority_steps = next(
        steps for _, steps in observations if tuple(slug(step) for step in steps) == majority_sequence
    )
    signal_observations = [
        {
            "document_id": "padrao-do-grupo",
            "document_name": f"Padrao observado em {majority_count} documentos",
            "value": " -> ".join(majority_steps),
        }
    ]
    signal_observations.extend(
        {
            "document_id": document["document_id"],
            "document_name": document["document_name"],
            "value": " -> ".join(steps),
        }
        for document, steps in outliers
    )
    return [
        {
            "signal_type": "procedimento_diferente",
            "title": "Procedimento diferente do padrao",
            "comparison_key": "sequencia_do_procedimento",
            "relationship": "documentos do mesmo grupo de procedimento",
            "group_id": group_id,
            "observations": signal_observations,
            "impact": "A empresa pode nao estar executando o mesmo processo de forma uniforme.",
            "confidence": "alta",
        }
    ]


def detect_patterns(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for group_id, group_documents in grouped_for_patterns(documents).items():
        candidates.extend(feature_candidates(group_id, group_documents))
        candidates.extend(process_candidate(group_id, group_documents))
    return candidates
