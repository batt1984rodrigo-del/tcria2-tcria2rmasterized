from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models import TcriaAnalysis


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from audit_accusation_bundle_with_tcr_gateway import (  # noqa: E402
    AuditMode,
    PipelineOptions,
    resolve_input_paths,
    run_pipeline,
)
from render_legacy_audit_summary import build_report, render_markdown  # noqa: E402


SYSTEM_PROMPT = """Role: compliance-review synthesis layer for TCRIA.

Goal: answer the user's review question using only the supplied deterministic pipeline result.

Success criteria:
- link material conclusions to named documents or mark them unresolved
- distinguish confirmed facts, gaps, and signals that require verification
- recommend one allowed decision and explain its conditions
- preserve reading and OCR limitations and required human validation

Constraints:
- never claim fraud, guilt, illegality, intent, or truth from isolated keywords or heuristic classifications
- never invent document content, dates, values, identities, or evidence
- absence in this bounded batch is not proof that something does not exist
- if evidence is too weak, choose HOLD_FOR_REVIEW or DO_NOT_PROCEED_YET
- the final institutional, legal, audit, or management decision remains human

Output: return only the structured schema requested by the application.
"""


def run_document_pipeline(input_dir: Path, output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    files, roots = resolve_input_paths([str(input_dir)])
    payload, _, _ = run_pipeline(
        PipelineOptions(
            input_files=files,
            input_roots=roots,
            output_dir=output_dir,
            output_stem="tcria-analysis",
            mode=AuditMode(strict_explicit_decision_record=True),
        )
    )
    return payload, build_report(payload)


def synthesize(question: str, report: dict[str, Any]) -> tuple[TcriaAnalysis, str]:
    if not os.getenv("OPENAI_API_KEY"):
        return deterministic_fallback(report), "deterministic_fallback"

    client = OpenAI()
    try:
        response = client.responses.parse(
            model=os.getenv("TCRIA_OPENAI_MODEL", "gpt-5.6-sol"),
            reasoning={"effort": os.getenv("TCRIA_REASONING_EFFORT", "medium")},
            input=[
                {"role": "developer", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"review_question": question, "pipeline_report": report},
                        ensure_ascii=False,
                    ),
                },
            ],
            text_format=TcriaAnalysis,
        )
    except OpenAIError:
        fallback = deterministic_fallback(report)
        fallback.limitations.append("A síntese por modelo não ficou disponível nesta execução; verifique cota e configuração da OpenAI.")
        return fallback, "deterministic_fallback_openai_unavailable"
    if response.output_parsed is None:
        raise RuntimeError("A OpenAI recusou ou não produziu uma análise estruturada utilizável.")
    return response.output_parsed, "openai"


def deterministic_fallback(report: dict[str, Any]) -> TcriaAnalysis:
    coverage = report.get("coverage") or {}
    outcomes = report.get("document_outcomes") or {}
    blocked = int(outcomes.get("BLOCKED") or 0)
    unreadable = int(coverage.get("unreadable_count") or 0)
    decision = "DO_NOT_PROCEED_YET" if blocked else "HOLD_FOR_REVIEW"
    gaps: list[str] = []
    if unreadable:
        gaps.append(f"{unreadable} documento(s) não puderam ser avaliados com leitura suficiente.")
    if blocked:
        gaps.append(f"{blocked} documento(s) permanecem bloqueados pelas regras do pipeline.")
    documents = report.get("documents") or []
    return TcriaAnalysis(
        recommended_decision=decision,
        rationale="O resultado determinístico organiza sinais e cobertura, mas não sustenta uma decisão institucional autônoma.",
        confirmed_facts=[f"{int(report.get('total_files_scanned') or 0)} arquivo(s) foram processados no lote delimitado."],
        gaps=gaps,
        verification_signals=["Revisar os sinais heurísticos no contexto dos documentos de origem."],
        evidence=[
            {"document": item["file_name"], "observation": f"Leitura {item['reading_method']}; situação {item['overall_outcome']}."}
            for item in documents
        ],
        limitations=["A síntese por modelo não estava configurada nesta execução."],
        human_validation_required=["Validar os documentos e a recomendação com o responsável competente."],
    )


def write_artifacts(
    output_dir: Path,
    question: str,
    analysis: TcriaAnalysis,
    report: dict[str, Any],
    synthesis_source: str,
) -> dict[str, str]:
    result = {
        "review_question": question,
        "synthesis_source": synthesis_source,
        "analysis": analysis.model_dump(),
        "pipeline_report": report,
    }
    json_path = output_dir / "result.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown_path = output_dir / "report.md"
    markdown_path.write_text(render_result_markdown(result), encoding="utf-8")

    html_path = output_dir / "report.html"
    html_path.write_text(render_result_html(result), encoding="utf-8")

    pdf_path = output_dir / "report.pdf"
    render_result_pdf(result, pdf_path)
    return {"json": json_path.name, "html": html_path.name, "pdf": pdf_path.name, "markdown": markdown_path.name}


def render_result_markdown(result: dict[str, Any]) -> str:
    analysis = result["analysis"]
    lines = [
        "# Relatório de revisão de conformidade TCRIA",
        "",
        "## Pergunta de revisão",
        "",
        result["review_question"],
        "",
        "## Recomendação",
        "",
        f"**{analysis['recommended_decision']}**",
        "",
        analysis["rationale"],
    ]
    sections = (
        ("Fatos confirmados", analysis["confirmed_facts"]),
        ("Lacunas", analysis["gaps"]),
        ("Sinais para verificação", analysis["verification_signals"]),
        ("Limitações", analysis["limitations"]),
        ("Validação humana necessária", analysis["human_validation_required"]),
    )
    for title, items in sections:
        lines.extend(["", f"## {title}", ""])
        lines.extend(f"- {item}" for item in items)
    lines.extend(["", "## Evidências referenciadas", ""])
    lines.extend(f"- `{item['document']}` — {item['observation']}" for item in analysis["evidence"])
    lines.extend(["", f"_Fonte da síntese: {result['synthesis_source']}._", ""])
    return "\n".join(lines)


def render_result_html(result: dict[str, Any]) -> str:
    markdown = render_result_markdown(result)
    blocks: list[str] = []
    for line in markdown.splitlines():
        escaped = html.escape(line)
        if line.startswith("# "):
            blocks.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            blocks.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            blocks.append(f"<p class='item'>• {html.escape(line[2:])}</p>")
        elif line:
            blocks.append(f"<p>{escaped}</p>")
    return "<!doctype html><html lang='pt-BR'><meta charset='utf-8'><title>Relatório TCRIA</title><style>body{font:16px/1.55 system-ui;max-width:900px;margin:48px auto;padding:0 24px;color:#17221d}h1,h2{color:#123f2c}.item{margin:.35rem 0}code{background:#eef4f0;padding:.1rem .3rem}</style><body>" + "".join(blocks) + "</body></html>"


def render_result_pdf(result: dict[str, Any], path: Path) -> None:
    styles = getSampleStyleSheet()
    story = []
    for line in render_result_markdown(result).splitlines():
        if line.startswith("# "):
            story.append(Paragraph(html.escape(line[2:]), styles["Title"]))
        elif line.startswith("## "):
            story.extend([Spacer(1, 10), Paragraph(html.escape(line[3:]), styles["Heading2"])])
        elif line.startswith("- "):
            story.append(Paragraph("• " + html.escape(line[2:]), styles["BodyText"]))
        elif line:
            story.append(Paragraph(html.escape(line.replace("**", "").replace("`", "")), styles["BodyText"]))
    SimpleDocTemplate(str(path), pagesize=A4, title="Relatório TCRIA").build(story)
