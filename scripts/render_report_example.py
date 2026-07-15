#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from investigation_engine import build_report_investigation
from client_language import (
    client_label_for_compliance_area,
    client_label_for_confidence,
    client_label_for_conformity,
    client_label_for_ocr_status,
    client_label_for_overall_status,
    client_label_for_reading_method,
    client_label_for_severity,
    translate_client_text,
)
from client_output_validator import validate_client_markdown
from reasoning_policy import apply_reasoning_policy


ROOT = Path(__file__).resolve().parents[1]
INPUT_JSON = ROOT / "docs" / "report-example.json"
OUTPUT_MD = ROOT / "docs" / "report-example.md"
OUTPUT_PDF = ROOT / "output" / "pdf" / "tcria-compliance-report-example.pdf"


def load_data() -> dict[str, Any]:
    raw_data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    enriched_data = apply_reasoning_policy(raw_data)
    enriched_data["investigation_summary"] = build_report_investigation(enriched_data)
    return enriched_data


def safe(value: Any) -> str:
    text = str(value)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


TABLE_BODY_STYLE = ParagraphStyle(
    name="TableBodyCell",
    fontName="Helvetica",
    fontSize=7.6,
    leading=9.2,
    textColor=colors.HexColor("#111827"),
    splitLongWords=True,
)
TABLE_LABEL_STYLE = ParagraphStyle(
    name="TableLabelCell",
    parent=TABLE_BODY_STYLE,
    fontName="Helvetica-Bold",
)
TABLE_HEADER_STYLE = ParagraphStyle(
    name="TableHeaderCell",
    parent=TABLE_BODY_STYLE,
    fontName="Helvetica-Bold",
    textColor=colors.white,
)


def table_cell(value: Any, style: ParagraphStyle = TABLE_BODY_STYLE) -> Paragraph:
    return Paragraph(safe(value), style)


def wrapped_table_rows(rows: list[list[Any]], has_header: bool = False) -> list[list[Paragraph]]:
    wrapped: list[list[Paragraph]] = []
    for row_index, row in enumerate(rows):
        wrapped_row: list[Paragraph] = []
        for column_index, value in enumerate(row):
            if has_header and row_index == 0:
                style = TABLE_HEADER_STYLE
            elif column_index == 0:
                style = TABLE_LABEL_STYLE
            else:
                style = TABLE_BODY_STYLE
            wrapped_row.append(table_cell(value, style))
        wrapped.append(wrapped_row)
    return wrapped


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def reading_summary(data: dict[str, Any]) -> dict[str, Any]:
    return data["reading_coverage_summary"]


def reasoning_summary(data: dict[str, Any]) -> dict[str, Any]:
    return data["reasoning_policy_summary"]


def investigation_summary(data: dict[str, Any]) -> dict[str, Any]:
    return data["investigation_summary"]


def client_text(value: Any) -> str:
    return translate_client_text(value)


def client_list(values: list[str]) -> list[str]:
    return [client_text(value) for value in values]


def investigation_lines(items: list[dict[str, Any]], detail_label: str) -> list[str]:
    lines: list[str] = []
    for item in items:
        statement = client_text(item.get("statement"))
        detail = client_text(item.get(detail_label))
        if detail:
            lines.append(f"{item['hypothesis_id']}: {statement}. {detail}")
        else:
            lines.append(f"{item['hypothesis_id']}: {statement}")
    return lines


def evidence_lines(items: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for item in items:
        evidence_list = [client_text(value) for value in item.get("evidence_lines") or []]
        if evidence_list:
            lines.append(f"{item['hypothesis_id']}: {'; '.join(evidence_list)}")
        else:
            lines.append(f"{item['hypothesis_id']}: sem prova destacada nesta rodada")
    return lines


def correlation_group_lines(groups: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for group in groups:
        names = [item["document_name"] for item in group.get("documents") or []]
        lines.append(f"{group['relationship']}: {'; '.join(names)}")
    return lines


def correlation_signal_lines(signals: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for signal in signals:
        lines.extend(
            [
                f"#### {signal['signal_id']} - {signal['title']}",
                "",
                f"- Relacao analisada: {signal['relationship']}",
                f"- O que divergiu: {signal['observation']}",
                f"- Por que pode importar: {signal['impact']}",
                f"- Quanto confiamos neste sinal: {signal['confidence']}",
                f"- O que verificar: {signal['what_to_verify']}",
                "",
            ]
        )
    return lines


def render_markdown(data: dict[str, Any]) -> str:
    reading = reading_summary(data)
    reasoning = reasoning_summary(data)
    investigation = investigation_summary(data)
    lines: list[str] = []
    lines.append(f"# {client_text(data['report_title'])}")
    lines.append("")
    lines.append("## 1. Identificacao do relatorio")
    lines.append("")
    lines.append(f"- Empresa: `{data['company_name']}`")
    lines.append(f"- Lote analisado: `{data['batch_name']}`")
    lines.append(f"- Id do relatorio: `{data['report_id']}`")
    lines.append(f"- Gerado em: `{data['generated_at']}`")
    lines.append(f"- Regras aplicadas: `{client_text(data['rule_set_name'])}`")
    lines.append("")
    lines.append("## 2. O que precisa ser visto primeiro")
    lines.append("")
    lines.append(client_text(data["overall_conclusion"]))
    lines.append("")
    lines.append("### Proximos passos imediatos")
    lines.append("")
    for idx, item in enumerate(client_list(data["immediate_priorities"]), start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("### Resumo rapido")
    lines.append("")
    lines.append(f"- Documentos revisados: `{data['documents_reviewed']}`")
    lines.append(f"- Achados criticos: `{data['critical_count']}`")
    lines.append(f"- Achados relevantes: `{data['relevant_count']}`")
    lines.append(f"- Achados informativos: `{data['informational_count']}`")
    lines.append(f"- Situacao geral: `{client_label_for_overall_status(data['overall_status'])}`")
    lines.append("")
    lines.append("## 3. Escopo da analise")
    lines.append("")
    lines.append(client_text(data["scope_description"]))
    lines.append("")
    lines.append(f"- Origem: `{client_text(data['source_description'])}`")
    lines.append(f"- Tipos de documento: `{client_text(data['document_types'])}`")
    lines.append(f"- Area de negocio: `{client_text(data['business_area'])}`")
    lines.append(f"- Periodo coberto: `{data['period_covered']}`")
    lines.append("")
    lines.append("### O que foi verificado")
    lines.append("")
    lines.append(bullet_lines(client_list(data["checks"])))
    lines.append("")
    lines.append("## 4. Leitura dos documentos e confianca da leitura")
    lines.append("")
    lines.append("### Resumo da leitura")
    lines.append("")
    lines.append(f"- Documentos lidos com texto direto: `{reading['direct_text_documents']}`")
    lines.append(f"- Documentos que dependeram de OCR: `{reading['ocr_text_documents']}`")
    lines.append(f"- Documentos em que o OCR falhou: `{reading['ocr_failed_documents']}`")
    lines.append(f"- Regra de confianca da leitura: `{client_text(reading['reading_confidence_rule'])}`")
    lines.append("")
    lines.append("### Documento por documento")
    lines.append("")
    lines.append("| Documento | Metodo de leitura | Situacao do OCR | Confianca da leitura | Observacao |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in data["reading_register"]:
        lines.append(
            f"| {item['document']} | {client_label_for_reading_method(item['read_method'])} | {client_label_for_ocr_status(item['ocr_status'])} | {client_label_for_confidence(item['reading_confidence'])} | {client_text(item['notes'])} |"
        )
    lines.append("")
    lines.append("O relatorio nao esconde como cada documento foi lido.")
    lines.append("")
    lines.append("## 5. Como a investigacao foi conduzida")
    lines.append("")
    lines.append(f"- Pergunta central: {investigation['questioning']['core_question']}")
    lines.append(f"- Foco desta investigacao: {client_text(investigation['questioning']['focus_statement'])}")
    lines.append(f"- Contexto recebido: {client_text(investigation['questioning']['received_context'])}")
    lines.append("")
    lines.append("### O que chegou")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["inventory"]["items"])))
    lines.append("")
    lines.append("### O que conseguimos ler")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["reading"]["items"])))
    lines.append("")
    correlation = investigation["correlation"]
    lines.append("### Como os documentos foram relacionados")
    lines.append("")
    lines.append(correlation["summary"])
    lines.append("")
    lines.append(f"- Pergunta de consistencia: {correlation['consistency_question']}")
    lines.append(f"- Fichas comparadas: `{correlation['documents_compared']}`")
    lines.append(f"- Grupos realmente comparados: `{correlation['groups_compared']}`")
    lines.append(bullet_lines(correlation_group_lines(correlation["groups"])))
    lines.append("")
    lines.append("### Sinais encontrados na comparacao")
    lines.append("")
    if correlation["signals"]:
        lines.extend(correlation_signal_lines(correlation["signals"]))
    else:
        lines.append("Nenhum sinal comparativo foi aberto pelas regras atuais.")
        lines.append("")
    lines.append("### Hipoteses abertas pela investigacao")
    lines.append("")
    lines.append(bullet_lines(investigation_lines(investigation["hypotheses"], "status_reason")))
    lines.append("")
    lines.append("### O que sustenta essas hipoteses")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["evidence"]["summary_lines"])))
    lines.append("")
    lines.append(bullet_lines(evidence_lines(investigation["evidence"]["by_hypothesis"])))
    lines.append("")
    lines.append("### O que nao bate")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["contradictions"]["items"])))
    lines.append("")
    lines.append("### O que esta faltando")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["gaps"]["items"])))
    lines.append("")
    lines.append("### O que podemos afirmar agora")
    lines.append("")
    lines.append(client_text(investigation["conclusions"]["summary_statement"]))
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["conclusions"]["can_affirm"])))
    lines.append("")
    lines.append("### O que ainda nao podemos afirmar")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["conclusions"]["cannot_affirm_yet"])))
    lines.append("")
    lines.append("### Proximos movimentos da investigacao")
    lines.append("")
    lines.append(bullet_lines(client_list(investigation["recommendations"]["items"])))
    lines.append("")
    lines.append("### Disciplina interna da analise")
    lines.append("")
    lines.append(client_text(data["rules_summary"]))
    lines.append("")
    lines.append("- Postura da conclusao: o relatorio preserva incerteza quando a prova ainda nao fecha.")
    lines.append(f"- Validacao em runtime: `{client_text(reasoning['validation_status'])}`")
    lines.append(f"- Achados revisados: `{reasoning['findings_reviewed']}`")
    lines.append(f"- Pontos mantidos como inconclusivos: `{reasoning['unknown_finding_count']}`")
    lines.append(f"- Pontos que pedem mais documentos: `{reasoning['document_request_count']}`")
    lines.append("")
    lines.append("## 6. Principais pontos do lote")
    lines.append("")
    for item in data["findings"]:
        lines.append(f"### {item['finding_id']} - {client_text(item['title'])}")
        lines.append("")
        lines.append(f"- Area analisada: `{client_label_for_compliance_area(item['compliance_area'])}`")
        lines.append(f"- Gravidade: `{client_label_for_severity(item['severity'])}`")
        lines.append(f"- Situacao: `{client_label_for_conformity(item['conformity_status'])}`")
        lines.append(f"- Quanto confiamos nesta leitura: `{client_label_for_confidence(item['confidence'])}`")
        lines.append("")
        lines.append("#### O que foi encontrado")
        lines.append("")
        lines.append(client_text(item["what_identified"]))
        lines.append("")
        lines.append("#### Por que isso importa")
        lines.append("")
        lines.append(client_text(item["why_matters"]))
        lines.append("")
        lines.append("#### Quais provas sustentam esse ponto")
        lines.append("")
        for evidence in client_list(item["supporting_evidence"]):
            lines.append(f"- {evidence}")
        lines.append("")
        lines.append("#### O que fazer agora")
        lines.append("")
        for follow_up in client_list(item["follow_up"]):
            lines.append(f"- {follow_up}")
        lines.append("")
    lines.append("## 7. Registro de provas")
    lines.append("")
    lines.append("| Id da prova | Documento | Referencia | Por que isso importa |")
    lines.append("| --- | --- | --- | --- |")
    for item in data["evidence_register"]:
        lines.append(
            f"| {item['evidence_id']} | {item['document']} | {client_text(item['reference'])} | {client_text(item['why_it_matters'])} |"
        )
    lines.append("")
    lines.append("## 8. O que ainda nao foi fechado")
    lines.append("")
    lines.append("### Pontos ainda em aberto")
    lines.append("")
    lines.append(bullet_lines(client_list(data["unresolved_points"])))
    lines.append("")
    lines.append("### Limites desta analise")
    lines.append("")
    lines.append(bullet_lines(client_list(data["limits"])))
    lines.append("")
    lines.append("## 9. Prioridades da proxima revisao")
    lines.append("")
    for idx, item in enumerate(client_list(data["next_priorities"]), start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("## 10. Anexos")
    lines.append("")
    lines.append(bullet_lines(client_list(data["annexes"])))
    lines.append("")
    return "\n".join(lines)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=4,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#475569"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="FindingTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
        )
    )
    return styles


def severity_color(severity: str):
    mapping = {
        "Critical": colors.HexColor("#991b1b"),
        "Relevant": colors.HexColor("#b45309"),
        "Attention": colors.HexColor("#1d4ed8"),
        "Informational": colors.HexColor("#475569"),
    }
    return mapping.get(severity, colors.HexColor("#475569"))


def label_value_table(rows: list[list[str]], col_widths: list[float]) -> Table:
    table = Table(wrapped_table_rows(rows), colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dbeafe")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def issue_summary_table(data: dict[str, Any]) -> Table:
    rows = [
        ["Metrica", "Valor"],
        ["Documentos revisados", str(data["documents_reviewed"])],
        ["Achados criticos", str(data["critical_count"])],
        ["Achados relevantes", str(data["relevant_count"])],
        ["Achados informativos", str(data["informational_count"])],
        ["Situacao geral", client_label_for_overall_status(data["overall_status"])],
    ]
    table = Table(wrapped_table_rows(rows, has_header=True), colWidths=[58 * mm, 42 * mm], repeatRows=1)
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
    table.setStyle(style)
    return table


def reading_summary_table(data: dict[str, Any]) -> Table:
    reading = reading_summary(data)
    rows = [
        ["Metrica de leitura", "Valor"],
        ["Leitura direta do texto", str(reading["direct_text_documents"])],
        ["OCR com recuperacao util", str(reading["ocr_text_documents"])],
        ["OCR sem recuperacao suficiente", str(reading["ocr_failed_documents"])],
        ["Regra de confianca", client_text(reading["reading_confidence_rule"])],
    ]
    table = Table(wrapped_table_rows(rows, has_header=True), colWidths=[54 * mm, 112 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def reading_register_table(data: dict[str, Any]) -> Table:
    rows = [["Documento", "Metodo de leitura", "Situacao do OCR", "Confianca", "Observacao"]]
    for item in data["reading_register"]:
        rows.append(
            [
                item["document"],
                client_label_for_reading_method(item["read_method"]),
                client_label_for_ocr_status(item["ocr_status"]),
                client_label_for_confidence(item["reading_confidence"]),
                client_text(item["notes"]),
            ]
        )
    table = Table(
        wrapped_table_rows(rows, has_header=True),
        colWidths=[42 * mm, 25 * mm, 28 * mm, 20 * mm, 51 * mm],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def reasoning_summary_table(data: dict[str, Any]) -> Table:
    reasoning = reasoning_summary(data)
    rows = [
        ["Metrica de coerencia", "Valor"],
        ["Postura da conclusao", "Preserva incerteza quando a prova ainda nao fecha"],
        ["Validacao em runtime", client_text(reasoning["validation_status"])],
        ["Achados revisados", str(reasoning["findings_reviewed"])],
        ["Pontos inconclusivos", str(reasoning["unknown_finding_count"])],
        ["Pontos que pedem documentos", str(reasoning["document_request_count"])],
    ]
    table = Table(wrapped_table_rows(rows, has_header=True), colWidths=[54 * mm, 112 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def bullet_paragraphs(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"- {safe(item)}", style) for item in items]


def correlation_signal_flowables(signals: list[dict[str, Any]], styles) -> list[Any]:
    flowables: list[Any] = []
    for signal in signals:
        flowables.append(
            KeepTogether(
                [
                Paragraph(f"{safe(signal['signal_id'])} - {safe(signal['title'])}", styles["SubHeading"]),
                Paragraph(f"<b>Relacao analisada:</b> {safe(signal['relationship'])}", styles["Body"]),
                Paragraph(f"<b>O que divergiu:</b> {safe(signal['observation'])}", styles["Body"]),
                Paragraph(f"<b>Por que pode importar:</b> {safe(signal['impact'])}", styles["Body"]),
                Paragraph(f"<b>Quanto confiamos:</b> {safe(signal['confidence'])}", styles["Body"]),
                Paragraph(f"<b>O que verificar:</b> {safe(signal['what_to_verify'])}", styles["Body"]),
                Spacer(1, 5),
                ]
            )
        )
    return flowables


def finding_block(item: dict[str, Any], styles) -> KeepTogether:
    badge = Table(
        [[client_label_for_severity(item["severity"]), client_label_for_conformity(item["conformity_status"]), client_label_for_confidence(item["confidence"])]],
        colWidths=[30 * mm, 42 * mm, 28 * mm],
    )
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), severity_color(item["severity"])),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#e2e8f0")),
                ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#eff6ff")),
                ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
                ("TEXTCOLOR", (1, 0), (2, 0), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    meta = label_value_table(
        [
            ["Area analisada", client_label_for_compliance_area(item["compliance_area"])],
            ["Gravidade", client_label_for_severity(item["severity"])],
            ["Situacao", client_label_for_conformity(item["conformity_status"])],
            ["Confianca", client_label_for_confidence(item["confidence"])],
        ],
        [36 * mm, 124 * mm],
    )

    block = [
        Spacer(1, 6),
        Paragraph(f"{safe(item['finding_id'])} - {safe(client_text(item['title']))}", styles["FindingTitle"]),
        badge,
        Spacer(1, 4),
        meta,
        Spacer(1, 5),
        Paragraph("<b>O que foi encontrado</b>", styles["SubHeading"]),
        Paragraph(safe(client_text(item["what_identified"])), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Por que isso importa</b>", styles["SubHeading"]),
        Paragraph(safe(client_text(item["why_matters"])), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Quais provas sustentam esse ponto</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(item["supporting_evidence"]), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>O que fazer agora</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(item["follow_up"]), styles["Body"]),
    ]
    return KeepTogether(block)


def evidence_table(data: dict[str, Any]) -> Table:
    rows = [["Id da prova", "Documento", "Referencia", "Por que isso importa"]]
    for item in data["evidence_register"]:
        rows.append(
            [
                item["evidence_id"],
                item["document"],
                client_text(item["reference"]),
                client_text(item["why_it_matters"]),
            ]
        )
    table = Table(
        wrapped_table_rows(rows, has_header=True),
        colWidths=[20 * mm, 46 * mm, 27 * mm, 73 * mm],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def add_page_chrome(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas_obj.setLineWidth(0.4)
    canvas_obj.line(doc.leftMargin, doc.pagesize[1] - 20 * mm, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 20 * mm)
    canvas_obj.line(doc.leftMargin, 14 * mm, doc.pagesize[0] - doc.rightMargin, 14 * mm)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.setFillColor(colors.HexColor("#0f172a"))
    canvas_obj.drawString(doc.leftMargin, doc.pagesize[1] - 14 * mm, "TCRIA - resumo documental para primeira leitura")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#475569"))
    canvas_obj.drawString(doc.leftMargin, 8 * mm, "Saida orientada ao cliente")
    canvas_obj.drawRightString(doc.pagesize[0] - doc.rightMargin, 8 * mm, f"Page {canvas_obj.getPageNumber()}")
    canvas_obj.restoreState()


def render_pdf(data: dict[str, Any]) -> None:
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    investigation = investigation_summary(data)
    correlation = investigation["correlation"]
    reasoning = reasoning_summary(data)
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title=client_text(data["report_title"]),
        author="OpenAI Codex",
    )

    story = [
        Paragraph(safe(client_text(data["report_title"])), styles["ReportTitle"]),
        Paragraph(safe(client_text(data["overall_conclusion"])), styles["Body"]),
        Spacer(1, 8),
        label_value_table(
            [
                ["Empresa", data["company_name"]],
                ["Lote analisado", data["batch_name"]],
                ["Id do relatorio", data["report_id"]],
                ["Gerado em", data["generated_at"]],
                ["Regras aplicadas", client_text(data["rule_set_name"])],
                ["Area de negocio", client_text(data["business_area"])],
            ],
            [36 * mm, 132 * mm],
        ),
        Spacer(1, 8),
        Paragraph("O que precisa ser visto primeiro", styles["SectionHeading"]),
        issue_summary_table(data),
        Spacer(1, 8),
        Paragraph("Proximos passos imediatos", styles["SubHeading"]),
        *bullet_paragraphs(client_list(data["immediate_priorities"]), styles["Body"]),
        Spacer(1, 8),
        Paragraph("Escopo da analise", styles["SectionHeading"]),
        Paragraph(safe(client_text(data["scope_description"])), styles["Body"]),
        Spacer(1, 4),
        label_value_table(
            [
                ["Origem", client_text(data["source_description"])],
                ["Tipos de documento", client_text(data["document_types"])],
                ["Area de negocio", client_text(data["business_area"])],
                ["Periodo coberto", data["period_covered"]],
            ],
            [36 * mm, 132 * mm],
        ),
        Spacer(1, 6),
        Paragraph("O que foi verificado", styles["SubHeading"]),
        *bullet_paragraphs(client_list(data["checks"]), styles["Body"]),
        Spacer(1, 8),
        KeepTogether(
            [
                Paragraph("Leitura dos documentos e confianca da leitura", styles["SectionHeading"]),
                reading_summary_table(data),
            ]
        ),
        Spacer(1, 6),
        Paragraph("Documento por documento", styles["SubHeading"]),
        reading_register_table(data),
        Spacer(1, 6),
        Paragraph(
            "O relatorio nao esconde como cada documento foi lido.",
            styles["Small"],
        ),
        Spacer(1, 8),
        Paragraph("Como a investigacao foi conduzida", styles["SectionHeading"]),
        Paragraph("<b>Pergunta central</b>", styles["SubHeading"]),
        Paragraph(safe(investigation["questioning"]["core_question"]), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Foco desta investigacao</b>", styles["SubHeading"]),
        Paragraph(safe(client_text(investigation["questioning"]["focus_statement"])), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>O que chegou</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["inventory"]["items"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que conseguimos ler</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["reading"]["items"]), styles["Body"]),
        Spacer(1, 6),
        KeepTogether(
            [
                Paragraph("<b>Como os documentos foram relacionados</b>", styles["SubHeading"]),
                Paragraph(safe(correlation["summary"]), styles["Body"]),
                Paragraph(
                    f"<b>Pergunta de consistencia:</b> {safe(correlation['consistency_question'])}",
                    styles["Body"],
                ),
                *bullet_paragraphs(correlation_group_lines(correlation["groups"]), styles["Body"]),
            ]
        ),
        Spacer(1, 6),
        Paragraph("<b>Sinais encontrados na comparacao</b>", styles["SubHeading"]),
        *correlation_signal_flowables(correlation["signals"], styles),
        Spacer(1, 6),
        Paragraph("<b>Hipoteses abertas pela investigacao</b>", styles["SubHeading"]),
        *bullet_paragraphs(investigation_lines(investigation["hypotheses"], "status_reason"), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que sustenta essas hipoteses</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["evidence"]["summary_lines"]), styles["Body"]),
        *bullet_paragraphs(evidence_lines(investigation["evidence"]["by_hypothesis"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que nao bate</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["contradictions"]["items"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que esta faltando</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["gaps"]["items"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que podemos afirmar agora</b>", styles["SubHeading"]),
        Paragraph(safe(client_text(investigation["conclusions"]["summary_statement"])), styles["Body"]),
        *bullet_paragraphs(client_list(investigation["conclusions"]["can_affirm"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>O que ainda nao podemos afirmar</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["conclusions"]["cannot_affirm_yet"]), styles["Body"]),
        Spacer(1, 5),
        Paragraph("<b>Proximos movimentos da investigacao</b>", styles["SubHeading"]),
        *bullet_paragraphs(client_list(investigation["recommendations"]["items"]), styles["Body"]),
        Spacer(1, 6),
        Paragraph("Disciplina interna da analise", styles["SubHeading"]),
        Paragraph(safe(client_text(data["rules_summary"])), styles["Body"]),
        Spacer(1, 4),
        reasoning_summary_table(data),
        Spacer(1, 6),
        Paragraph("Como ler a gravidade dos pontos", styles["SubHeading"]),
        label_value_table(
            [
                ["Critico", client_text(data["severity_scale"]["critical"])],
                ["Relevante", client_text(data["severity_scale"]["relevant"])],
                ["Atencao", client_text(data["severity_scale"]["attention"])],
                ["Informativo", client_text(data["severity_scale"]["informational"])],
            ],
            [28 * mm, 140 * mm],
        ),
        PageBreak(),
        Paragraph("Principais pontos do lote", styles["SectionHeading"]),
    ]

    for item in data["findings"]:
        story.append(finding_block(item, styles))

    story.extend(
        [
            PageBreak(),
            Paragraph("Registro de provas", styles["SectionHeading"]),
            evidence_table(data),
            Spacer(1, 8),
            Paragraph("Pontos ainda em aberto", styles["SectionHeading"]),
            *bullet_paragraphs(client_list(data["unresolved_points"]), styles["Body"]),
            Spacer(1, 8),
            Paragraph("Limites desta analise", styles["SectionHeading"]),
            *bullet_paragraphs(client_list(data["limits"]), styles["Body"]),
            Spacer(1, 8),
            Paragraph("Prioridades da proxima revisao", styles["SectionHeading"]),
            *bullet_paragraphs(client_list(data["next_priorities"]), styles["Body"]),
            Spacer(1, 8),
            Paragraph("Anexos", styles["SectionHeading"]),
            *bullet_paragraphs(client_list(data["annexes"]), styles["Body"]),
        ]
    )

    doc.build(story, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)


def main() -> None:
    data = load_data()
    markdown = render_markdown(data)
    validate_client_markdown(markdown)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    render_pdf(data)
    print(OUTPUT_MD)
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
