from __future__ import annotations

from collections import defaultdict
from typing import Any

from .normalize import slug


def inferred_group_key(document: dict[str, Any]) -> tuple[str, str]:
    explicit_group = document.get("explicit_group")
    if explicit_group:
        return f"grupo:{slug(explicit_group)}", document.get("relation_label") or "mesmo processo"

    subject = slug(document.get("subject"))
    entities = [slug(item) for item in document.get("entities") or [] if slug(item)]
    if subject and entities:
        return f"assunto:{subject}:entidade:{entities[0]}", "mesmo assunto e entidade"

    document_id = slug(document.get("document_id"))
    return f"isolado:{document_id}", "documento sem grupo comparavel confirmado"


def group_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    labels: dict[str, str] = {}
    for document in documents:
        key, label = inferred_group_key(document)
        grouped[key].append(document)
        labels[key] = label
    return [
        {
            "group_id": key,
            "relationship": labels[key],
            "documents": grouped[key],
        }
        for key in sorted(grouped)
    ]


def public_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for group in groups:
        if len(group["documents"]) < 2:
            continue
        output.append(
            {
                "group_id": group["group_id"],
                "relationship": group["relationship"],
                "documents": [
                    {
                        "document_id": document["document_id"],
                        "document_name": document["document_name"],
                        "document_type": document["document_type"],
                    }
                    for document in group["documents"]
                ],
            }
        )
    return output
