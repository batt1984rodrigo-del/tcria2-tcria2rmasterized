#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "examples" / "legacy" / "sanitized-strict-audit.json"
DEFAULT_MD = ROOT / "output" / "legacy" / "legacy-audit-summary.md"
DEFAULT_PDF = ROOT / "output" / "pdf" / "legacy-audit-summary.pdf"


def load_payload(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Legacy payload must be a JSON object.")
    return data


def safe(value: Any) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
    )


def all_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    accusation = payload.get("accusation_set") or []
    non_accusation = payload.get("non_accusation_set") or []
    return [item for item in accusation + non_accusation if isinstance(item, dict)]


def relative_name(item: dict[str, Any]) -> str:
    path = item.get("file_path") or item.get("file_name") or "unknown-file"
    return str(path).split("/sanitized/")[-1].split("/")[-1]


def count_stats(items: list[dict[str, Any]], payload: dict[str, Any]) -> dict[str, int]:
    read_count = 0
    unread_count = 0
    blocked_count = 0
    partial_count = 0
    for item in items:
        extraction_status = str(item.get("extraction_status") or "").lower()
        text_quality = str(item.get("text_quality") or "").lower()
        outcome = str(item.get("overall_outcome") or "")
        classification = str(item.get("classification") or "").upper()
        if extraction_status == "ok":
            read_count += 1
        if extraction_status != "ok" or "UNREADABLE" in classification:
            unread_count += 1
        if "BLOCKED" in outcome.upper():
            blocked_count += 1
        if extraction_status == "ok" and text_quality in {"low", "medium"}:
            partial_count += 1

    return {
        "total_files": int(payload.get("total_files_scanned") or len(items)),
        "files_read": read_count,
        "files_unread": unread_count,
        "files_blocked": blocked_count,
        "files_partially_read": partial_count,
    }


def severity_rank(item: dict[str, Any]) -> tuple[int, str]:
    outcome = str(item.get("overall_outcome") or "").upper()
    classification = str(item.get("classification") or "").upper()
    if "BLOCKED" in outcome:
        return (0, relative_name(item))
    if "PARTIAL" in outcome:
        return (1, relative_name(item))
    if "UNREADABLE" in classification:
        return (2, relative_name(item))
    return (3, relative_name(item))


def collect_findings(items: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in sorted(items, key=severity_rank):
        outcome = str(item.get("overall_outcome") or "")
        classification = str(item.get("classification") or "")
        reasons = item.get("classification_reasons") or []
        if outcome or classification:
            findings.append(
                {
                    "title": relative_name(item),
                    "status": outcome or classification,
                    "summary": str(item.get("summary") or "No summary provided in the legacy payload."),
                    "reasons": [str(reason) for reason in reasons[:3]],
                }
            )
        if len(findings) >= limit:
            break
    return findings


def collect_evidence(items: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for item in items:
        classification = str(item.get("classification") or "").upper()
        signal_hits = (item.get("key_signals") or {}).get("evidence_marker_hits") or {}
        if "SUPPORTING_EVIDENCE" in classification or signal_hits:
            detail = ", ".join(f"{k}={v}" for k, v in list(signal_hits.items())[:3]) or "supporting evidence markers present"
            evidence.append(
                {
                    "title": relative_name(item),
                    "classification": classification or "UNKNOWN",
                    "detail": detail,
                    "summary": str(item.get("summary") or "No summary provided in the legacy payload."),
                }
            )
        if len(evidence) >= limit:
            break
    return evidence


def collect_limits(items: list[dict[str, Any]], stats: dict[str, int]) -> list[str]:
    limits: list[str] = []
    if stats["files_unread"] > 0:
        limits.append(f"{stats['files_unread']} file(s) could not be read reliably from the legacy batch.")
    if stats["files_partially_read"] > 0:
        limits.append(f"{stats['files_partially_read']} file(s) were read with only low or medium extraction quality.")
    if any(item.get("gates") is None for item in items):
        limits.append("Some legacy items do not expose gate details in a consistent way.")
    limits.append("This adapted report summarizes a legacy payload and does not re-run the original engine.")
    return limits


def build_summary(payload: dict[str, Any]) -> dict[str, Any]:
    items = all_items(payload)
    stats = count_stats(items, payload)
    findings = collect_findings(items)
    evidence = collect_evidence(items)
    limits = collect_limits(items, stats)
    top_issue = findings[0]["summary"] if findings else "No major finding could be extracted from the legacy payload."
    return {
        "generated_at": payload.get("generated_at") or "unknown",
        "input_path": payload.get("input_path") or "unknown",
        "mode": payload.get("mode") or "unknown",
        "audit_basis": payload.get("audit_basis") or "unknown",
        "classification_counts": payload.get("classification_counts") or {},
        "route_counts": payload.get("route_counts") or {},
        "stats": stats,
        "findings": findings,
        "evidence": evidence,
        "limits": limits,
        "executive_summary": (
            "This report translates a legacy TCRIA audit payload into a reader-oriented summary. "
            f"The most visible issue in the reviewed batch is: {top_issue}"
        ),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    stats = summary["stats"]
    lines: list[str] = []
    lines.append("# Legacy Audit Summary")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(summary["executive_summary"])
    lines.append("")
    lines.append("## Batch Snapshot")
    lines.append("")
    lines.append(f"- Generated at: `{summary['generated_at']}`")
    lines.append(f"- Legacy mode: `{summary['mode']}`")
    lines.append(f"- Total files scanned: `{stats['total_files']}`")
    lines.append(f"- Files read: `{stats['files_read']}`")
    lines.append(f"- Files not read: `{stats['files_unread']}`")
    lines.append(f"- Files blocked: `{stats['files_blocked']}`")
    lines.append(f"- Files partially read: `{stats['files_partially_read']}`")
    lines.append("")
    lines.append("## Main Findings")
    lines.append("")
    for idx, finding in enumerate(summary["findings"], start=1):
        lines.append(f"### Finding {idx}: {finding['title']}")
        lines.append("")
        lines.append(f"- Legacy status: `{finding['status']}`")
        lines.append("")
        lines.append(finding["summary"])
        lines.append("")
        if finding["reasons"]:
            lines.append("Reasons carried from the legacy payload:")
            lines.append("")
            for reason in finding["reasons"]:
                lines.append(f"- {reason}")
            lines.append("")
    lines.append("## Evidence Highlights")
    lines.append("")
    for idx, item in enumerate(summary["evidence"], start=1):
        lines.append(f"### Evidence {idx}: {item['title']}")
        lines.append("")
        lines.append(f"- Classification: `{item['classification']}`")
        lines.append(f"- Signal summary: `{item['detail']}`")
        lines.append("")
        lines.append(item["summary"])
        lines.append("")
    lines.append("## Limits And Translation Notes")
    lines.append("")
    for item in summary["limits"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Legacy Counters")
    lines.append("")
    lines.append(f"- Classification counts: `{summary['classification_counts']}`")
    lines.append(f"- Route counts: `{summary['route_counts']}`")
    lines.append("")
    return "\n".join(lines)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
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
            spaceAfter=3,
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
    return styles


def label_table(rows: list[list[str]], col_widths: list[float]) -> Table:
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


def metric_table(summary: dict[str, Any]) -> Table:
    stats = summary["stats"]
    rows = [
        ["Metric", "Value"],
        ["Total files scanned", str(stats["total_files"])],
        ["Files read", str(stats["files_read"])],
        ["Files not read", str(stats["files_unread"])],
        ["Files blocked", str(stats["files_blocked"])],
        ["Files partially read", str(stats["files_partially_read"])],
    ]
    table = Table(rows, colWidths=[58 * mm, 42 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
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
    )
    return table


def bullet_paragraphs(items: list[str], style: ParagraphStyle) -> list[Paragraph]:
    return [Paragraph(f"- {safe(item)}", style) for item in items]


def add_page_chrome(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas_obj.setLineWidth(0.4)
    canvas_obj.line(doc.leftMargin, doc.pagesize[1] - 20 * mm, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 20 * mm)
    canvas_obj.line(doc.leftMargin, 14 * mm, doc.pagesize[0] - doc.rightMargin, 14 * mm)
    canvas_obj.setFont("Helvetica-Bold", 8)
    canvas_obj.setFillColor(colors.HexColor("#0f172a"))
    canvas_obj.drawString(doc.leftMargin, doc.pagesize[1] - 14 * mm, "TCRIA Legacy Audit Adapter")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#475569"))
    canvas_obj.drawString(doc.leftMargin, 8 * mm, "Adapted legacy output")
    canvas_obj.drawRightString(doc.pagesize[0] - doc.rightMargin, 8 * mm, f"Page {canvas_obj.getPageNumber()}")
    canvas_obj.restoreState()


def render_pdf(summary: dict[str, Any], pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title="Legacy Audit Summary",
        author="OpenAI Codex",
    )

    story = [
        Paragraph("Legacy Audit Summary", styles["ReportTitle"]),
        Paragraph(safe(summary["executive_summary"]), styles["Body"]),
        Spacer(1, 8),
        label_table(
            [
                ["Generated at", str(summary["generated_at"])],
                ["Legacy mode", str(summary["mode"])],
                ["Legacy basis", str(summary["audit_basis"])],
                ["Input path", str(summary["input_path"])],
            ],
            [36 * mm, 132 * mm],
        ),
        Spacer(1, 8),
        Paragraph("Batch snapshot", styles["SectionHeading"]),
        metric_table(summary),
        Spacer(1, 8),
        Paragraph("Main findings", styles["SectionHeading"]),
    ]

    for finding in summary["findings"]:
        story.append(
            KeepTogether(
                [
                    Paragraph(safe(finding["title"]), styles["SubHeading"]),
                    Paragraph(f"<b>Legacy status:</b> {safe(finding['status'])}", styles["Body"]),
                    Paragraph(safe(finding["summary"]), styles["Body"]),
                    *bullet_paragraphs(finding["reasons"], styles["Body"]),
                    Spacer(1, 4),
                ]
            )
        )

    story.extend([Paragraph("Evidence highlights", styles["SectionHeading"])])
    for item in summary["evidence"]:
        story.append(
            KeepTogether(
                [
                    Paragraph(safe(item["title"]), styles["SubHeading"]),
                    Paragraph(f"<b>Classification:</b> {safe(item['classification'])}", styles["Body"]),
                    Paragraph(f"<b>Signal summary:</b> {safe(item['detail'])}", styles["Body"]),
                    Paragraph(safe(item["summary"]), styles["Body"]),
                    Spacer(1, 4),
                ]
            )
        )

    story.extend(
        [
            Paragraph("Limits and translation notes", styles["SectionHeading"]),
            *bullet_paragraphs(summary["limits"], styles["Body"]),
            Spacer(1, 6),
            Paragraph("Legacy counters", styles["SectionHeading"]),
            Paragraph(f"<b>Classification counts:</b> {safe(summary['classification_counts'])}", styles["Body"]),
            Paragraph(f"<b>Route counts:</b> {safe(summary['route_counts'])}", styles["Body"]),
        ]
    )

    doc.build(story, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a legacy TCRIA audit payload into Markdown and PDF.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to the legacy JSON payload.")
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD, help="Path for the generated Markdown report.")
    parser.add_argument("--pdf-output", type=Path, default=DEFAULT_PDF, help="Path for the generated PDF report.")
    args = parser.parse_args()

    payload = load_payload(args.input.expanduser().resolve())
    summary = build_summary(payload)

    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.write_text(render_markdown(summary), encoding="utf-8")
    render_pdf(summary, args.pdf_output.expanduser().resolve())

    print(args.md_output.expanduser().resolve())
    print(args.pdf_output.expanduser().resolve())


if __name__ == "__main__":
    main()
