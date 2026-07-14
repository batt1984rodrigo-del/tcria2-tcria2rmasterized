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

COMPLIANCE_AREA_LABELS = {
    "Approval Governance": "Governanca de aprovacoes",
    "Third-Party Compliance": "Conformidade de terceiros",
    "Exception Management": "Gestao de excecoes",
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
    "passed": "aprovada",
    "Compliance Review Report - Procurement And Vendor Documentation": "Resumo da analise documental de compras e fornecedores",
    "Corporate Procurement Compliance v1": "Regras de revisao de compras v1",
    "The reviewed batch shows a documented procurement process, but the current evidence is not sufficient to support a clean compliance conclusion. The main gaps are missing approval trails, incomplete vendor due diligence support, and inconsistent contract exception records.": "O lote analisado mostra um processo de compras documentado, mas as provas atuais ainda nao sustentam uma conclusao limpa de conformidade. As principais pendencias sao aprovacoes sem comprovacao suficiente, diligencia incompleta de fornecedores e registros irregulares de excecao contratual.",
    "Recover approval evidence for contracts signed above the delegated threshold.": "Recuperar provas de aprovacao para contratos assinados acima do limite de delegacao.",
    "Complete vendor due diligence support for suppliers marked as strategic.": "Completar a diligencia documental dos fornecedores marcados como estrategicos.",
    "Regularize exception records linked to emergency procurement requests.": "Regularizar os registros de excecao ligados a compras emergenciais.",
    "Review of procurement and vendor management documents related to contract approvals, vendor onboarding, and exception handling for the second quarter of 2026.": "Revisao de documentos de compras e gestao de fornecedores ligados a aprovacoes contratuais, cadastro de terceiros e tratamento de excecoes no segundo trimestre de 2026.",
    "Uploaded batch from procurement shared drive": "Lote enviado a partir da pasta compartilhada da area de compras",
    "contracts, approval forms, vendor onboarding files, exception memos, email exports": "contratos, formularios de aprovacao, arquivos de cadastro de fornecedores, memorandos de excecao e exportacoes de e-mail",
    "Procurement and Vendor Management": "Compras e gestao de fornecedores",
    "approval trail completeness": "completude da trilha de aprovacao",
    "vendor due diligence support": "diligencia documental de fornecedores",
    "exception justification records": "registros de justificativa de excecao",
    "contract conformity against internal thresholds": "aderencia contratual aos limites internos",
    "Confidence reflects reading quality only and does not replace compliance certainty.": "A confianca de leitura mede apenas a qualidade da leitura do documento e nao substitui a certeza da analise.",
    "Embedded text was available on all reviewed pages.": "O texto do arquivo ja estava disponivel nas paginas revisadas.",
    "Direct extraction returned no usable text; OCR recovered most checklist content.": "A extracao direta nao trouxe texto util, mas o OCR recuperou a maior parte do checklist.",
    "Scan quality remained insufficient after OCR fallback.": "A qualidade da digitalizacao continuou insuficiente mesmo apos o OCR.",
    "Native tabular text was read directly.": "O conteudo tabular nativo foi lido diretamente.",
    "The review rules classify findings by evidence completeness, traceability, approval support, and conformity with documented procurement controls.": "As regras desta revisao observam completude das provas, origem das informacoes, suporte de aprovacao e aderencia aos controles documentados de compras.",
    "Evidence indicates a material compliance gap requiring immediate review.": "Indica uma falha material que pede revisao imediata.",
    "Evidence indicates a meaningful control weakness or unresolved conformity gap.": "Indica uma fragilidade relevante de controle ou uma lacuna de conformidade ainda aberta.",
    "Evidence suggests a moderate issue that should be clarified or regularized.": "Indica um ponto moderado que precisa ser esclarecido ou regularizado.",
    "Evidence indicates a point worth tracking without immediate escalation.": "Indica um ponto que merece acompanhamento sem escalacao imediata.",
    "Missing approval trail for high-value contract amendments": "Falta comprovacao de aprovacao em aditivos contratuais de alto valor",
    "Incomplete vendor due diligence support for strategic suppliers": "Diligencia documental incompleta para fornecedores estrategicos",
    "Incomplete diligencia documental de fornecedores for strategic suppliers": "Diligencia documental incompleta para fornecedores estrategicos",
    "Emergency procurement exceptions are documented inconsistently": "As excecoes de compras emergenciais estao documentadas de forma inconsistente",
    "Three contract amendments above the delegated threshold were located without signed approval support in the submitted batch.": "Tres aditivos contratuais acima do limite de delegacao foram encontrados sem comprovacao assinada de aprovacao no lote enviado.",
    "The absence of approval evidence weakens traceability and creates exposure to unauthorized commercial commitment.": "A falta de comprovacao de aprovacao enfraquece a rastreabilidade e aumenta o risco de compromisso comercial sem autorizacao clara.",
    "Contract amendment file AM-17 with no approval attachment.": "Arquivo do aditivo contratual AM-17 sem anexo de aprovacao.",
    "Approval index spreadsheet marks the record as pending.": "A planilha de controle de aprovacoes marca o registro como pendente.",
    "Email chain references urgency but not final authorization.": "A troca de e-mails menciona urgencia, mas nao mostra autorizacao final.",
    "Retrieve signed approval records or formal ratification evidence.": "Recuperar os registros assinados de aprovacao ou prova formal de ratificacao.",
    "Confirm whether the contracts entered execution before approval closure.": "Confirmar se os contratos entraram em execucao antes do fechamento da aprovacao.",
    "Five strategic supplier files include onboarding forms but do not contain the full due diligence support referenced by the checklist.": "Cinco pastas de fornecedores estrategicos contem formularios de cadastro, mas nao trazem toda a diligencia documental indicada no checklist.",
    "Incomplete due diligence weakens evidence of onboarding conformity and reduces defensibility of vendor approval decisions.": "A diligencia incompleta enfraquece a prova de conformidade no cadastro e reduz a defensabilidade das aprovacoes de fornecedores.",
    "Checklist marks tax and sanction review as required.": "O checklist indica revisao fiscal e de sancoes como obrigatoria.",
    "Three folders contain only summary forms without source documents.": "Tres pastas contem apenas formularios-resumo, sem os documentos de origem.",
    "Vendor master sheet lists suppliers as approved.": "A planilha mestre de fornecedores lista esses terceiros como aprovados.",
    "Request the missing due diligence attachments from procurement operations.": "Solicitar os anexos faltantes de diligencia para a equipe de operacoes de compras.",
    "Confirm whether approval was granted with an exception process.": "Confirmar se a aprovacao foi concedida por processo de excecao.",
    "Exception memos exist for part of the emergency procurement set, but the rationale and approval pattern are not consistent across documents.": "Existem memorandos de excecao para parte das compras emergenciais, mas a justificativa e o padrao de aprovacao nao sao consistentes entre os documentos.",
    "Inconsistent exception records make it difficult to determine whether nonstandard procurement steps were justified and approved correctly.": "Registros inconsistentes de excecao dificultam saber se etapas fora do padrao foram justificadas e aprovadas corretamente.",
    "Two memos use the standard exception form.": "Dois memorandos usam o formulario padrao de excecao.",
    "One request is supported only by email language.": "Um pedido esta sustentado apenas por linguagem em e-mail.",
    "No single register consolidates all emergency exceptions.": "Nao existe um registro unico consolidando todas as excecoes emergenciais.",
    "Create a reconciled list of all emergency exceptions in the batch.": "Criar uma lista reconciliada de todas as excecoes emergenciais do lote.",
    "Verify whether each exception has a matching approval record.": "Verificar se cada excecao possui o respectivo registro de aprovacao.",
    "Contains amendment terms but no attached approval support.": "Traz os termos do aditivo, mas nao traz a comprovacao de aprovacao anexada.",
    "Flags approval record as pending.": "Indica que o registro de aprovacao esta pendente.",
    "Shows missing due diligence attachments for strategic suppliers.": "Mostra a ausencia de anexos de diligencia para fornecedores estrategicos.",
    "Pages 2-4": "Paginas 2-4",
    "Row 118": "Linha 118",
    "Supplier folders S-04 to S-08": "Pastas de fornecedores S-04 a S-08",
    "The batch does not confirm whether missing approval evidence exists outside the submitted scope.": "O lote nao confirma se a comprovacao de aprovacao faltante existe fora do material enviado.",
    "Two vendor files contain placeholders that suggest pending uploads.": "Dois arquivos de fornecedores trazem marcadores que sugerem upload pendente.",
    "The review is limited to the submitted document batch.": "A revisao esta limitada ao lote de documentos enviado.",
    "No direct system-of-record validation was performed.": "Nao houve validacao direta em sistema de registro oficial.",
    "Two PDF scans remained weak even after automatic OCR fallback.": "Duas digitalizacoes em PDF continuaram fracas mesmo apos o OCR automatico.",
    "Recover approval support for high-value amendments.": "Recuperar a comprovacao de aprovacao para aditivos de alto valor.",
    "Close due diligence evidence gaps for strategic suppliers.": "Fechar as lacunas de diligencia documental para fornecedores estrategicos.",
    "Normalize exception records and reconcile them against approvals.": "Padronizar os registros de excecao e reconciliar com as aprovacoes.",
    "Detailed evidence register": "Registro detalhado de provas",
    "Full document inventory": "Inventario completo de documentos",
    "Rule set reference": "Referencia do conjunto de regras",
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


def client_label_for_compliance_area(value: Any) -> str:
    text = normalized_text(value)
    return COMPLIANCE_AREA_LABELS.get(text, translate_client_text(text))


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
