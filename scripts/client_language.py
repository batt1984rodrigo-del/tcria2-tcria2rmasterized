from __future__ import annotations

from typing import Any


CLASSIFICATION_LABELS = {
    "ACCUSATORY_CANDIDATE": "Pode indicar problema",
    "SUPPORTING_EVIDENCE_RELEVANT": "Prova importante",
    "SUPPORTING_EVIDENCE": "Prova",
    "SUPPORTING_PROOF": "Comprovacao",
    "EVIDENTIARY_SUPPORT_GENERAL": "Outras provas",
    "NEUTRAL_OR_CONTEXT": "Ajuda como contexto",
    "UNREADABLE": "Nao foi possivel ler",
    "UNREADABLE_OR_EMPTY": "Nao foi possivel ler",
    "UNDETERMINED": "Ainda nao foi possivel classificar",
}

ARTIFACT_TYPE_LABELS = {
    "DECISION_ARTIFACT": "Documento de posicao",
    "ANALYTICAL_ARTIFACT": "Documento de analise",
    "DOSSIER": "Dossie",
    "FINANCIAL_EVIDENCE_BUNDLE": "Conjunto de provas financeiras",
    "DECISION_ARTIFACT".lower(): "Documento de posicao",
    "ANALYTICAL_ARTIFACT".lower(): "Documento de analise",
    "dossier": "Dossie",
    "decision_artifact": "Documento de posicao",
    "analytical_artifact": "Documento de analise",
    "financial_evidence_bundle": "Conjunto de provas financeiras",
}

READING_METHOD_LABELS = {
    "direct_text": "Leitura direta do texto",
    "ocr_text": "Leitura por OCR",
    "ocr_failed": "OCR nao recuperou texto suficiente",
    "unknown": "Metodo de leitura nao informado",
}

OCR_STATUS_LABELS = {
    "not_needed": "OCR nao foi necessario",
    "not_applicable": "OCR nao se aplica",
    "attempted_success": "OCR ajudou a recuperar o texto",
    "attempted_failed": "OCR nao conseguiu recuperar o texto",
    "unknown": "Status de OCR nao informado",
}

STATUS_ANSWERS = {
    "PASS": "Sim",
    "WARN": "Ha ressalvas",
    "BLOCKED": "Ainda nao",
    "NOT_EVALUATED": "Ainda nao foi possivel avaliar",
    "NOT_APPLICABLE": "Nao se aplica",
    "UNKNOWN": "Ainda nao foi possivel concluir",
}

CONFIDENCE_LABELS = {
    "high": "Alta",
    "medium": "Media",
    "low": "Baixa",
    "very_low": "Muito baixa",
    "unknown": "Nao informada",
}

SEVERITY_LABELS = {
    "Critical": "Critico",
    "Relevant": "Relevante",
    "Attention": "Atencao",
    "Informational": "Informativo",
}

CONFORMITY_LABELS = {
    "Noncompliant": "Nao conforme",
    "Partially Compliant": "Parcialmente conforme",
    "Compliant": "Conforme",
    "Inconclusive": "Inconclusivo",
}

OVERALL_STATUS_LABELS = {
    "Attention Required": "Exige atencao",
}

GATE_LABELS = {
    "complianceGate": "Verificacao de regras",
    "prescriptiveGate": "Linguagem do documento",
    "traceabilityCheck": "Verificacao da origem",
    "maturityGate": "Maturidade do material",
    "ledgerRuntimeCheck": "Verificacao de execucao",
}

ORGANIZATIONAL_REASON_LABELS = {
    "falta_metadado_governanca": "Faltam informacoes claras de responsabilidade e aprovacao",
    "sem_objetivo_explicito": "O documento nao deixa claro seu objetivo",
    "rastreabilidade_limitada": "Faltam elementos para rastrear melhor a origem do conteudo",
    "sem_autor_responsavel_explicito": "Nao esta claro quem assume a autoria ou responsabilidade",
}

TEXT_REPLACEMENTS = {
    "DecisionRecord header not found in strict mode.": "Falta registro claro de responsabilidade, objetivo e aprovacao do documento.",
    "Prescriptive/condemnatory language detected.": "O texto usa linguagem acusatoria ou conclusiva sem formulacao factual suficiente.",
    "Add explicit DecisionRecord metadata: responsibleHuman, declaredPurpose, approved.": "Informar quem assumiu o documento, qual e o objetivo dele e registrar sua aprovacao.",
    "Attach traceable anchors (dates, values, and linkable supporting files).": "Anexar datas, valores e arquivos de suporte que permitam rastrear a informacao.",
    "Rewrite prescriptive language into factual and attributable statements.": "Reescrever trechos acusatorios em linguagem factual, descritiva e atribuivel.",
    "Current material does not support a stronger conclusion.": "O material atual ainda nao sustenta uma conclusao mais forte.",
    "Current material supports a bounded technical summary.": "O material atual permite apenas um resumo tecnico delimitado.",
    "Complementary analysis only. Official gate outcomes are preserved.": "Analise complementar apenas. Os resultados oficiais permanecem inalterados.",
}

CONTENT_LABEL_REPLACEMENTS = {
    "Accusatory terms": "Termos que indicam problema",
    "Evidence markers": "Marcadores de prova",
    "Theme entities": "Entidades centrais",
    "Traceability markers": "Sinais de origem",
    "dates=": "datas=",
    "currency=": "valores=",
}


def normalized_text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def client_boolean(value: Any) -> str:
    return "Sim" if bool(value) else "Nao"


def client_label_for_classification(value: Any) -> str:
    text = normalized_text(value, "UNDETERMINED")
    return CLASSIFICATION_LABELS.get(text, text.replace("_", " ").title())


def client_helpfulness_answer(value: Any) -> str:
    text = normalized_text(value, "UNDETERMINED")
    if text == "ACCUSATORY_CANDIDATE":
        return "Pode indicar problema"
    if text == "SUPPORTING_EVIDENCE_RELEVANT":
        return "Sim, traz prova importante"
    if text == "SUPPORTING_EVIDENCE":
        return "Sim, traz prova"
    if text == "SUPPORTING_PROOF":
        return "Sim, ajuda a comprovar"
    if text == "NEUTRAL_OR_CONTEXT":
        return "Ajuda como contexto"
    if text in {"UNREADABLE", "UNREADABLE_OR_EMPTY"}:
        return "Ainda nao foi possivel saber"
    return client_label_for_classification(text)


def client_label_for_artifact_type(value: Any) -> str:
    text = normalized_text(value, "unknown")
    return ARTIFACT_TYPE_LABELS.get(text, text.replace("_", " ").title())


def client_label_for_confidence(value: Any) -> str:
    text = normalized_text(value, "unknown").lower()
    return CONFIDENCE_LABELS.get(text, text.title())


def client_label_for_severity(value: Any) -> str:
    text = normalized_text(value)
    return SEVERITY_LABELS.get(text, text)


def client_label_for_conformity(value: Any) -> str:
    text = normalized_text(value)
    return CONFORMITY_LABELS.get(text, text)


def client_label_for_overall_status(value: Any) -> str:
    text = normalized_text(value)
    return OVERALL_STATUS_LABELS.get(text, text)


def client_label_for_reading_method(value: Any) -> str:
    text = normalized_text(value, "unknown").lower()
    return READING_METHOD_LABELS.get(text, text)


def client_label_for_ocr_status(value: Any) -> str:
    text = normalized_text(value, "unknown").lower()
    return OCR_STATUS_LABELS.get(text, text)


def client_answer_for_status(value: Any) -> str:
    text = normalized_text(value, "UNKNOWN").upper()
    return STATUS_ANSWERS.get(text, text)


def client_answer_for_outcome(value: Any) -> str:
    text = normalized_text(value, "UNKNOWN").upper()
    if "BLOCKED" in text:
        return "Ainda nao"
    if "PARTIAL_PASS" in text:
        return "Parcialmente"
    if text == "PASS" or text.startswith("PASS "):
        return "Sim"
    if "NOT_EVALUATED" in text:
        return "Ainda nao foi possivel avaliar"
    if "NOT_APPLICABLE" in text:
        return "Nao se aplica"
    return "Ainda nao foi possivel concluir"


def client_phrase_for_outcome(value: Any) -> str:
    text = normalized_text(value, "UNKNOWN").upper()
    if "BLOCKED" in text:
        return "Nao pode ser usado agora"
    if "PARTIAL_PASS" in text:
        return "Pode ser usado com ressalvas"
    if text == "PASS" or text.startswith("PASS "):
        return "Pode ser usado agora"
    if "NOT_EVALUATED" in text:
        return "Ainda nao foi possivel avaliar"
    return "A situacao ainda nao foi fechada"


def client_label_for_gate(name: Any) -> str:
    text = normalized_text(name)
    return GATE_LABELS.get(text, text)


def humanize_gate_summary(value: Any) -> str:
    text = normalized_text(value)
    if not text or text == "not exposed in legacy item":
        return "Nao ha detalhe tecnico suficiente sobre regras e origem."

    parts: list[str] = []
    for entry in text.split(";"):
        raw = entry.strip()
        if not raw or "=" not in raw:
            continue
        gate_name, gate_status = raw.split("=", 1)
        parts.append(f"{client_label_for_gate(gate_name)}: {client_answer_for_status(gate_status)}")
    return "; ".join(parts) if parts else "Nao ha detalhe tecnico suficiente sobre regras e origem."


def reading_reliability_text(read_method: Any, confidence: Any, ocr_status: Any) -> str:
    method = client_label_for_reading_method(read_method)
    confidence_label = client_label_for_confidence(confidence)
    ocr_label = client_label_for_ocr_status(ocr_status)
    return f"{method}. Confianca de leitura: {confidence_label}. {ocr_label}."


def translate_client_text(value: Any) -> str:
    text = normalized_text(value)
    if not text:
        return text

    translated = text
    for source, target in TEXT_REPLACEMENTS.items():
        translated = translated.replace(source, target)
    for source, target in CONTENT_LABEL_REPLACEMENTS.items():
        translated = translated.replace(source, target)
    return translated


def client_impact_label(value: Any) -> str:
    text = normalized_text(value).lower()
    if text == "mixed":
        return "Ajuda em parte, mas exige cuidado"
    if text == "high":
        return "Pode ter impacto forte"
    if text == "medium":
        return "Pode ter impacto relevante"
    if text == "low":
        return "Pode ter impacto limitado"
    if not text:
        return "Impacto ainda nao informado"
    return text


def client_reasons_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    output: list[str] = []
    for item in values:
        text = normalized_text(item)
        if not text:
            continue
        output.append(ORGANIZATIONAL_REASON_LABELS.get(text, translate_client_text(text)))
    return output


def blocked_review_helpfulness(theme_related: Any, potential_impact: Any) -> str:
    if not theme_related:
        return "Nao diretamente"
    impact = normalized_text(potential_impact).lower()
    if impact == "mixed":
        return "Sim, mas com cautela"
    return "Sim"


def summarize_document_for_client(doc: dict[str, Any]) -> dict[str, str]:
    return {
        "file_name": normalized_text(doc.get("file_name"), "documento-sem-nome"),
        "helps_case": client_helpfulness_answer(doc.get("classification")),
        "can_use_now": client_answer_for_outcome(doc.get("overall_outcome")),
        "reading_status": reading_reliability_text(
            doc.get("reading_method"),
            doc.get("reading_confidence"),
            doc.get("ocr_status"),
        ),
        "origin_and_rules": humanize_gate_summary(doc.get("gate_summary")),
    }
