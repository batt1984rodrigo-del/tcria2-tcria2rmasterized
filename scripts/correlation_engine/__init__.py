from __future__ import annotations

from typing import Any

from .compare import compare_groups
from .group import group_documents, public_groups
from .normalize import normalize_documents
from .patterns import detect_patterns, grouped_for_patterns
from .signals import finalize_signals, signal_counts


ENGINE_NAME = "motor_de_correlacao_documental"


def build_correlation(raw_documents: Any) -> dict[str, Any]:
    documents = normalize_documents(raw_documents)
    groups = group_documents(documents)
    pattern_groups = grouped_for_patterns(documents)
    candidates = compare_groups(groups, documents)
    candidates.extend(detect_patterns(documents))
    signals = finalize_signals(candidates)
    comparable_groups = [group for group in groups if len(group["documents"]) > 1]
    compared_group_count = len(comparable_groups) + len(pattern_groups)
    visible_groups = public_groups(groups)
    visible_groups.extend(
        {
            "group_id": group_id,
            "relationship": "mesmo grupo de procedimento",
            "documents": [
                {
                    "document_id": document["document_id"],
                    "document_name": document["document_name"],
                    "document_type": document["document_type"],
                }
                for document in group_documents
            ],
        }
        for group_id, group_documents in pattern_groups.items()
    )

    if not documents:
        summary = "Nenhuma ficha comparavel foi recebida nesta rodada."
    elif not signals:
        summary = (
            f"{len(documents)} fichas foram comparadas em {compared_group_count} grupos, "
            "sem divergencia relevante nas regras atuais."
        )
    else:
        summary = (
            f"{len(documents)} fichas foram comparadas em {compared_group_count} grupos "
            f"e abriram {len(signals)} sinais para verificacao."
        )

    return {
        "engine_name": ENGINE_NAME,
        "documents_compared": len(documents),
        "groups_compared": compared_group_count,
        "groups": visible_groups,
        "signals": signals,
        "signal_counts": signal_counts(signals),
        "summary": summary,
        "consistency_question": "O conjunto de documentos conta a mesma historia?",
    }


__all__ = ["ENGINE_NAME", "build_correlation"]
