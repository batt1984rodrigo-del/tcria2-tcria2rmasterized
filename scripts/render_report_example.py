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


ROOT = Path(__file__).resolve().parents[1]
INPUT_JSON = ROOT / "docs" / "report-example.json"
OUTPUT_MD = ROOT / "docs" / "report-example.md"
OUTPUT_PDF = ROOT / "output" / "pdf" / "tcria-compliance-report-example.pdf"


def load_data() -> dict[str, Any]:
    return json.loads(INPUT_JSON.read_text(encoding="utf-8"))


def safe(value: Any) -> str:
    text = str(value)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def reading_summary(data: dict[str, Any]) -> dict[str, Any]:
    return data["reading_coverage_summary"]


def render_markdown(data: dict[str, Any]) -> str:
    reading = reading_summary(data)
    lines: list[str] = []
    lines.append(f"# {data['report_title']}")
    lines.append("")
    lines.append("## 1. Report Identification")
    lines.append("")
    lines.append(f"- Company: `{data['company_name']}`")
    lines.append(f"- Review batch: `{data['batch_name']}`")
    lines.append(f"- Report id: `{data['report_id']}`")
    lines.append(f"- Generated at: `{data['generated_at']}`")
    lines.append(f"- Review rules: `{data['rule_set_name']}`")
    lines.append("")
    lines.append("## 2. Executive Summary")
    lines.append("")
    lines.append(data["overall_conclusion"])
    lines.append("")
    lines.append("### Immediate Priorities")
    lines.append("")
    for idx, item in enumerate(data["immediate_priorities"], start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("### Snapshot")
    lines.append("")
    lines.append(f"- Documents reviewed: `{data['documents_reviewed']}`")
    lines.append(f"- Critical findings: `{data['critical_count']}`")
    lines.append(f"- Relevant findings: `{data['relevant_count']}`")
    lines.append(f"- Informational findings: `{data['informational_count']}`")
    lines.append(f"- Overall compliance status: `{data['overall_status']}`")
    lines.append("")
    lines.append("## 3. Analysis Scope")
    lines.append("")
    lines.append(data["scope_description"])
    lines.append("")
    lines.append(f"- Source: `{data['source_description']}`")
    lines.append(f"- Document types: `{data['document_types']}`")
    lines.append(f"- Business area: `{data['business_area']}`")
    lines.append(f"- Period covered: `{data['period_covered']}`")
    lines.append("")
    lines.append("### What Was Checked")
    lines.append("")
    lines.append(bullet_lines(data["checks"]))
    lines.append("")
    lines.append("## 4. Reading Coverage And Extraction Provenance")
    lines.append("")
    lines.append("### Reading Snapshot")
    lines.append("")
    lines.append(f"- Documents with direct text extraction: `{reading['direct_text_documents']}`")
    lines.append(f"- Documents read through OCR fallback: `{reading['ocr_text_documents']}`")
    lines.append(f"- Documents where OCR failed: `{reading['ocr_failed_documents']}`")
    lines.append(f"- Reading confidence rule: `{reading['reading_confidence_rule']}`")
    lines.append("")
    lines.append("### Reading Register")
    lines.append("")
    lines.append("| Document | Read method | OCR status | Reading confidence | Notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in data["reading_register"]:
        lines.append(
            f"| {item['document']} | {item['read_method']} | {item['ocr_status']} | {item['reading_confidence']} | {item['notes']} |"
        )
    lines.append("")
    lines.append("The report does not hide which reading method was used for the reviewed material.")
    lines.append("")
    lines.append("## 5. Applied Review Rules")
    lines.append("")
    lines.append(data["rules_summary"])
    lines.append("")
    lines.append("## 6. Main Findings")
    lines.append("")
    for item in data["findings"]:
        lines.append(f"### {item['finding_id']} - {item['title']}")
        lines.append("")
        lines.append(f"- Compliance area: `{item['compliance_area']}`")
        lines.append(f"- Severity: `{item['severity']}`")
        lines.append(f"- Conformity status: `{item['conformity_status']}`")
        lines.append(f"- Confidence: `{item['confidence']}`")
        lines.append("")
        lines.append("#### What Was Identified")
        lines.append("")
        lines.append(item["what_identified"])
        lines.append("")
        lines.append("#### Why It Matters")
        lines.append("")
        lines.append(item["why_matters"])
        lines.append("")
        lines.append("#### Supporting Evidence")
        lines.append("")
        for evidence in item["supporting_evidence"]:
            lines.append(f"- {evidence}")
        lines.append("")
        lines.append("#### Recommended Follow-Up")
        lines.append("")
        for follow_up in item["follow_up"]:
            lines.append(f"- {follow_up}")
        lines.append("")
    lines.append("## 7. Evidence Reference Register")
    lines.append("")
    lines.append("| Evidence id | Document | Reference | Why it matters |")
    lines.append("| --- | --- | --- | --- |")
    for item in data["evidence_register"]:
        lines.append(
            f"| {item['evidence_id']} | {item['document']} | {item['reference']} | {item['why_it_matters']} |"
        )
    lines.append("")
    lines.append("## 8. Unresolved Points And Limitations")
    lines.append("")
    lines.append("### Unresolved Points")
    lines.append("")
    lines.append(bullet_lines(data["unresolved_points"]))
    lines.append("")
    lines.append("### Analysis Limits")
    lines.append("")
    lines.append(bullet_lines(data["limits"]))
    lines.append("")
    lines.append("## 9. Next Review Priorities")
    lines.append("")
    for idx, item in enumerate(data["next_priorities"], start=1):
        lines.append(f"{idx}. {item}")
    lines.append("")
    lines.append("## 10. Annexes")
    lines.append("")
    lines.append(bullet_lines(data["annexes"]))
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
    table = Table(rows, colWidths=col_widths)
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
        ["Metric", "Value"],
        ["Documents reviewed", str(data["documents_reviewed"])],
        ["Critical findings", str(data["critical_count"])],
        ["Relevant findings", str(data["relevant_count"])],
        ["Informational findings", str(data["informational_count"])],
        ["Overall status", data["overall_status"]],
    ]
    table = Table(rows, colWidths=[58 * mm, 42 * mm], repeatRows=1)
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
        ["Reading metric", "Value"],
        ["Direct text extraction", str(reading["direct_text_documents"])],
        ["OCR fallback success", str(reading["ocr_text_documents"])],
        ["OCR failed", str(reading["ocr_failed_documents"])],
        ["Confidence rule", reading["reading_confidence_rule"]],
    ]
    table = Table(rows, colWidths=[54 * mm, 112 * mm], repeatRows=1)
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
    rows = [["Document", "Read method", "OCR status", "Confidence", "Notes"]]
    for item in data["reading_register"]:
        rows.append(
            [
                item["document"],
                item["read_method"],
                item["ocr_status"],
                item["reading_confidence"],
                item["notes"],
            ]
        )
    table = Table(rows, colWidths=[46 * mm, 24 * mm, 30 * mm, 22 * mm, 44 * mm], repeatRows=1)
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


def bullet_paragraphs(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"- {safe(item)}", style) for item in items]


def finding_block(item: dict[str, Any], styles) -> KeepTogether:
    badge = Table(
        [[item["severity"], item["conformity_status"], item["confidence"]]],
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
            ["Compliance area", item["compliance_area"]],
            ["Severity", item["severity"]],
            ["Conformity status", item["conformity_status"]],
            ["Confidence", item["confidence"]],
        ],
        [36 * mm, 124 * mm],
    )

    block = [
        Spacer(1, 6),
        Paragraph(f"{safe(item['finding_id'])} - {safe(item['title'])}", styles["FindingTitle"]),
        badge,
        Spacer(1, 4),
        meta,
        Spacer(1, 5),
        Paragraph("<b>What was identified</b>", styles["SubHeading"]),
        Paragraph(safe(item["what_identified"]), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Why it matters</b>", styles["SubHeading"]),
        Paragraph(safe(item["why_matters"]), styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Supporting evidence</b>", styles["SubHeading"]),
        *bullet_paragraphs(item["supporting_evidence"], styles["Body"]),
        Spacer(1, 3),
        Paragraph("<b>Recommended follow-up</b>", styles["SubHeading"]),
        *bullet_paragraphs(item["follow_up"], styles["Body"]),
    ]
    return KeepTogether(block)


def evidence_table(data: dict[str, Any]) -> Table:
    rows = [["Evidence id", "Document", "Reference", "Why it matters"]]
    for item in data["evidence_register"]:
        rows.append(
            [
                item["evidence_id"],
                item["document"],
                item["reference"],
                item["why_it_matters"],
            ]
        )
    table = Table(rows, colWidths=[22 * mm, 52 * mm, 28 * mm, 76 * mm], repeatRows=1)
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
    canvas_obj.drawString(doc.leftMargin, doc.pagesize[1] - 14 * mm, "TCRIA Compliance Review Report")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#475569"))
    canvas_obj.drawString(doc.leftMargin, 8 * mm, "Client-facing output template")
    canvas_obj.drawRightString(doc.pagesize[0] - doc.rightMargin, 8 * mm, f"Page {canvas_obj.getPageNumber()}")
    canvas_obj.restoreState()


def render_pdf(data: dict[str, Any]) -> None:
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title=data["report_title"],
        author="OpenAI Codex",
    )

    story = [
        Paragraph(safe(data["report_title"]), styles["ReportTitle"]),
        Paragraph(safe(data["overall_conclusion"]), styles["Body"]),
        Spacer(1, 8),
        label_value_table(
            [
                ["Company", data["company_name"]],
                ["Review batch", data["batch_name"]],
                ["Report id", data["report_id"]],
                ["Generated at", data["generated_at"]],
                ["Review rules", data["rule_set_name"]],
                ["Business area", data["business_area"]],
            ],
            [36 * mm, 132 * mm],
        ),
        Spacer(1, 8),
        Paragraph("Executive summary", styles["SectionHeading"]),
        issue_summary_table(data),
        Spacer(1, 8),
        Paragraph("Immediate priorities", styles["SubHeading"]),
        *bullet_paragraphs(data["immediate_priorities"], styles["Body"]),
        Spacer(1, 8),
        Paragraph("Analysis scope", styles["SectionHeading"]),
        Paragraph(safe(data["scope_description"]), styles["Body"]),
        Spacer(1, 4),
        label_value_table(
            [
                ["Source", data["source_description"]],
                ["Document types", data["document_types"]],
                ["Business area", data["business_area"]],
                ["Period covered", data["period_covered"]],
            ],
            [36 * mm, 132 * mm],
        ),
        Spacer(1, 6),
        Paragraph("What was checked", styles["SubHeading"]),
        *bullet_paragraphs(data["checks"], styles["Body"]),
        Spacer(1, 8),
        Paragraph("Reading coverage and extraction provenance", styles["SectionHeading"]),
        reading_summary_table(data),
        Spacer(1, 6),
        Paragraph("Reading register", styles["SubHeading"]),
        reading_register_table(data),
        Spacer(1, 6),
        Paragraph(
            "The report does not hide which reading method was used for the reviewed material.",
            styles["Small"],
        ),
        Spacer(1, 8),
        Paragraph("Applied review rules", styles["SectionHeading"]),
        Paragraph(safe(data["rules_summary"]), styles["Body"]),
        Spacer(1, 6),
        Paragraph("Severity scale", styles["SubHeading"]),
        label_value_table(
            [
                ["Critical", data["severity_scale"]["critical"]],
                ["Relevant", data["severity_scale"]["relevant"]],
                ["Attention", data["severity_scale"]["attention"]],
                ["Informational", data["severity_scale"]["informational"]],
            ],
            [28 * mm, 140 * mm],
        ),
        PageBreak(),
        Paragraph("Main findings", styles["SectionHeading"]),
    ]

    for item in data["findings"]:
        story.append(finding_block(item, styles))

    story.extend(
        [
            PageBreak(),
            Paragraph("Evidence reference register", styles["SectionHeading"]),
            evidence_table(data),
            Spacer(1, 8),
            Paragraph("Unresolved points", styles["SectionHeading"]),
            *bullet_paragraphs(data["unresolved_points"], styles["Body"]),
            Spacer(1, 8),
            Paragraph("Analysis limits", styles["SectionHeading"]),
            *bullet_paragraphs(data["limits"], styles["Body"]),
            Spacer(1, 8),
            Paragraph("Next review priorities", styles["SectionHeading"]),
            *bullet_paragraphs(data["next_priorities"], styles["Body"]),
            Spacer(1, 8),
            Paragraph("Annexes", styles["SectionHeading"]),
            *bullet_paragraphs(data["annexes"], styles["Body"]),
        ]
    )

    doc.build(story, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)


def main() -> None:
    data = load_data()
    OUTPUT_MD.write_text(render_markdown(data), encoding="utf-8")
    render_pdf(data)
    print(OUTPUT_MD)
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
