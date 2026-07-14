from __future__ import annotations

from typing import Any

from client_language import translate_client_text

from ._helpers import normalized_list, normalized_text, translated_list


def build_report_questioning(data: dict[str, Any]) -> dict[str, Any]:
    scope = translate_client_text(normalized_text(data.get("scope_description")))
    context = translate_client_text(normalized_text(data.get("source_description"), "Origem nao informada"))
    discovery_targets = translated_list(data.get("checks"))
    focus_statement = "Precisamos entender se o material enviado sustenta, com prova suficiente, uma leitura segura do lote."
    if scope:
        focus_statement = f"Precisamos entender se o material enviado sustenta, com prova suficiente, esta frente de investigacao: {scope}"
    return {
        "core_question": "O que precisamos descobrir neste lote?",
        "focus_statement": focus_statement,
        "received_context": context,
        "discovery_targets": discovery_targets,
        "source_signals": normalized_list(data.get("document_types")),
    }


def build_legacy_questioning(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "core_question": "O que este lote legado realmente permite afirmar?",
        "focus_statement": "Separar o que ajuda o caso, o que ainda nao pode ser usado e o que ficou limitado pela leitura ou pela origem.",
        "received_context": "Lote legado sanitizado para investigacao documental.",
        "discovery_targets": [
            "quais arquivos ajudam o caso",
            "quais arquivos ainda nao podem ser usados agora",
            "quais limites impedem uma conclusao mais forte",
        ],
        "source_signals": [],
    }
