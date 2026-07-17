#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "output" / "pipeline"
DEFAULT_OUTPUT_STEM = "legacy_document_audit"

SUPPORTED_SUFFIXES = {
    ".csv",
    ".docx",
    ".heic",
    ".jpeg",
    ".jpg",
    ".md",
    ".pdf",
    ".png",
    ".rtf",
    ".txt",
    ".webarchive",
}

DEFAULT_SENSITIVE_NAME_PATTERNS = (
    r"(^|[._-])senhas?([._-]|$)",
    r"(^|[._-])passwords?([._-]|$)",
    r"(^|[._-])credentials?([._-]|$)",
    r"(^|[._-])secrets?([._-]|$)",
    r"^\.env($|\.)",
)

PRESCRIPTIVE_PATTERNS = (
    "voce deve",
    "deve-se",
    "e obrigatorio",
    "e necessario",
    "a unica solucao e",
)

ACCUSATION_PATTERNS = (
    r"\bfraude\b",
    r"\bgolpe\b",
    r"\bestelionat",
    r"\bden[uú]ncia\b",
    r"\bacusa[cç][aã]o\b",
    r"n[aã]o\s+reconhe[cç]o",
    r"n[aã]o\s+autorizei",
    r"\bindevid",
    r"\bclonad",
    r"\bphishing\b",
    r"engenharia\s+social",
    r"acesso\s+indevido",
    r"movimenta[cç][aã]o\s+at[ií]pica",
    r"(?:pix|transfer[eê]ncia)\s+n[aã]o\s+autorizad",
    r"\bpreju[ií]zo\b",
)

LEGAL_PATTERNS = (
    r"\bart\.?\s*\d+[a-zA-Z]?\b",
    r"§\s*\d+º?",
    r"\blei\s*(?:n[ºo]\.?\s*)?\d{1,5}(?:[./]\d{2,4})?\b",
    r"\bs[uú]mula\s*\d+\b",
    r"\bresolu[cç][aã]o\s*\d+\b",
    r"\binstru[cç][aã]o\s+normativa\s*\d+\b",
    r"\b(?:cdc|cpc|lgpd)\b",
    r"responsabilidade\s+objetiva",
    r"[oô]nus\s+da\s+prova",
    r"tutela\s+de\s+urg[eê]ncia",
)

EVIDENCE_MARKERS = (
    "anexo",
    "comprovante",
    "documento",
    "email",
    "e-mail",
    "extrato",
    "fatura",
    "linha do tempo",
    "log",
    "pix",
    "prova",
    "transferencia",
)

ANALYTICAL_NAME_MARKERS = (
    "analise",
    "comparativo",
    "dossie",
    "linha do tempo",
    "manual",
    "narrativa",
    "painel",
    "relatorio",
    "sumario",
    "timeline",
)

DECISION_NAME_MARKERS = (
    "contestacao",
    "diligencia",
    "encaminhamento",
    "manifestacao",
    "oficio",
    "pedido",
    "peticao",
    "reclamacao",
    "recurso",
    "requerimento",
)


@dataclass
class GateResult:
    status: str
    reason: str
    evidence: str | None = None


@dataclass
class ExtractionResult:
    text: str
    status: str
    method: str
    reading_method: str
    ocr_status: str


@dataclass
class AuditMode:
    strict_explicit_decision_record: bool = False

    @property
    def slug(self) -> str:
        return "strict" if self.strict_explicit_decision_record else "default"

    @property
    def label(self) -> str:
        if self.strict_explicit_decision_record:
            return "strict-explicit-decision-record"
        return "default-heuristic"


@dataclass
class PipelineOptions:
    input_files: list[Path]
    input_roots: list[Path]
    output_dir: Path
    output_stem: str = DEFAULT_OUTPUT_STEM
    mode: AuditMode = field(default_factory=AuditMode)
    target_terms: tuple[str, ...] = ()
    sensitive_names: tuple[str, ...] = ()
    include_source_paths: bool = False
    enable_ocr: bool = True


@dataclass
class FileRecord:
    file_name: str
    file_path: str
    suffix: str
    size_bytes: int
    sha256: str
    extraction_status: str
    extraction_method: str
    extractable_text_chars: int
    text_chars: int
    text_quality: str
    reading_method: str
    ocr_status: str
    reading_confidence: str
    sensitive_handling: str
    classification: str
    artifact_type: str
    artifact_type_reason: str
    raises_accusation: bool
    classification_reasons: list[str]
    key_signals: dict[str, Any]
    gates: dict[str, dict[str, Any]] | None
    overall_outcome: str | None


def normalize(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def fold_text(text: Any) -> str:
    value = normalize(text).lower()
    replacements = str.maketrans(
        {
            "á": "a",
            "à": "a",
            "â": "a",
            "ã": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ü": "u",
            "ç": "c",
        }
    )
    return value.translate(replacements)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_output_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._-")
    if not stem:
        raise ValueError("Output stem must contain at least one letter or number.")
    return stem


def resolve_input_paths(raw_inputs: list[str]) -> tuple[list[Path], list[Path]]:
    if not raw_inputs:
        raise ValueError("At least one --path input is required.")

    roots: list[Path] = []
    files: list[Path] = []
    seen: set[Path] = set()
    missing: list[str] = []
    for raw_input in raw_inputs:
        root = Path(raw_input).expanduser().resolve()
        if not root.exists():
            missing.append(raw_input)
            continue
        roots.append(root)
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for candidate in candidates:
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(resolved)

    if missing:
        raise FileNotFoundError(f"Input path not found: {', '.join(missing)}")
    if not files:
        raise ValueError("No supported files were found in the provided inputs.")
    return sorted(files, key=lambda path: (path.name.lower(), str(path).lower())), roots


def source_label(path: Path, roots: list[Path], include_absolute: bool) -> str:
    if include_absolute:
        return str(path)
    for root in roots:
        if root.is_file() and path == root:
            return path.name
        if root.is_dir():
            try:
                return str(Path(root.name) / path.relative_to(root))
            except ValueError:
                continue
    return path.name


def is_sensitive_name(path: Path, explicit_names: tuple[str, ...]) -> bool:
    name = fold_text(path.name)
    explicit = {fold_text(value) for value in explicit_names}
    if name in explicit:
        return True
    return any(re.search(pattern, name, flags=re.IGNORECASE) for pattern in DEFAULT_SENSITIVE_NAME_PATTERNS)


def decode_bytes(raw: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", errors="replace"), "latin1-replace"


def run_command(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def direct_result(text: str, method: str) -> ExtractionResult:
    if text.strip():
        return ExtractionResult(text, "ok", method, "direct_text", "not_needed")
    return ExtractionResult("", "unreadable_or_empty", method, "direct_text", "not_needed")


def extract_plain_text(path: Path) -> ExtractionResult:
    text, encoding = decode_bytes(path.read_bytes())
    return direct_result(text, encoding)


def extract_docx(path: Path) -> ExtractionResult:
    try:
        with zipfile.ZipFile(path) as archive:
            document_xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(document_xml)
        fragments = [node.text or "" for node in root.iter() if node.tag.endswith("}t")]
        return direct_result("\n".join(fragment for fragment in fragments if fragment), "docx_xml")
    except (KeyError, OSError, zipfile.BadZipFile, ElementTree.ParseError):
        return ExtractionResult("", "error", "docx_xml", "direct_text", "not_needed")


def extract_with_textutil(path: Path) -> ExtractionResult:
    if not shutil.which("textutil"):
        return ExtractionResult("", "unsupported", "textutil_missing", "direct_text", "not_needed")
    completed = run_command(["textutil", "-convert", "txt", "-stdout", str(path)])
    if completed is None or completed.returncode != 0:
        return ExtractionResult("", "error", "textutil", "direct_text", "not_needed")
    return direct_result(completed.stdout or "", "textutil")


def extract_pdf_direct(path: Path) -> ExtractionResult:
    if shutil.which("pdftotext"):
        completed = run_command(["pdftotext", "-layout", str(path), "-"])
        if completed is not None and completed.returncode == 0 and (completed.stdout or "").strip():
            return direct_result(completed.stdout, "pdftotext")
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return direct_result(text, "pypdf")
    except Exception:
        pass
    return ExtractionResult("", "unreadable_or_empty", "pdf_direct_failed", "direct_text", "not_needed")


def ocr_image(path: Path) -> ExtractionResult:
    if not shutil.which("tesseract"):
        return ExtractionResult("", "ocr_unavailable", "tesseract_missing", "ocr_failed", "not_available")

    target = path
    temporary_png: Path | None = None
    if path.suffix.lower() == ".heic":
        if not shutil.which("sips"):
            return ExtractionResult("", "ocr_unavailable", "heic_converter_missing", "ocr_failed", "not_available")
        temporary = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temporary.close()
        temporary_png = Path(temporary.name)
        converted = run_command(["sips", "-s", "format", "png", str(path), "--out", str(temporary_png)])
        if converted is None or converted.returncode != 0:
            temporary_png.unlink(missing_ok=True)
            return ExtractionResult("", "error", "sips", "ocr_failed", "attempted_failed")
        target = temporary_png

    completed = run_command(["tesseract", str(target), "stdout", "-l", "por+eng"])
    if completed is None or completed.returncode != 0:
        completed = run_command(["tesseract", str(target), "stdout"])
    if temporary_png is not None:
        temporary_png.unlink(missing_ok=True)
    if completed is None or completed.returncode != 0 or not (completed.stdout or "").strip():
        return ExtractionResult("", "unreadable_or_empty", "tesseract", "ocr_failed", "attempted_failed")
    return ExtractionResult(completed.stdout, "ok", "tesseract", "ocr_text", "attempted_success")


def ocr_pdf(path: Path) -> ExtractionResult:
    if not shutil.which("pdftoppm") or not shutil.which("tesseract"):
        return ExtractionResult("", "ocr_unavailable", "pdf_ocr_tools_missing", "ocr_failed", "not_available")
    with tempfile.TemporaryDirectory(prefix="tcria-pdf-ocr-") as temporary_dir:
        prefix = Path(temporary_dir) / "page"
        rendered = run_command(["pdftoppm", "-png", "-r", "200", str(path), str(prefix)])
        if rendered is None or rendered.returncode != 0:
            return ExtractionResult("", "error", "pdftoppm", "ocr_failed", "attempted_failed")
        pages = sorted(Path(temporary_dir).glob("page-*.png"))
        texts: list[str] = []
        for page in pages:
            extracted = ocr_image(page)
            if extracted.text.strip():
                texts.append(extracted.text)
        text = "\n".join(texts)
        if text.strip():
            return ExtractionResult(text, "ok", "pdftoppm+tesseract", "ocr_text", "attempted_success")
    return ExtractionResult("", "unreadable_or_empty", "pdftoppm+tesseract", "ocr_failed", "attempted_failed")


def extract_text(path: Path, enable_ocr: bool = True) -> ExtractionResult:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".csv", ".md"}:
        return extract_plain_text(path)
    if suffix == ".docx":
        return extract_docx(path)
    if suffix in {".rtf", ".webarchive"}:
        return extract_with_textutil(path)
    if suffix == ".pdf":
        direct = extract_pdf_direct(path)
        if direct.text.strip() or not enable_ocr:
            return direct
        return ocr_pdf(path)
    if suffix in {".png", ".jpg", ".jpeg", ".heic"}:
        if not enable_ocr:
            return ExtractionResult("", "ocr_disabled", "none", "ocr_failed", "not_attempted")
        return ocr_image(path)
    return ExtractionResult("", "unsupported", "none", "unknown", "not_applicable")


def classify_text_quality(characters: int, suffix: str) -> str:
    if characters <= 0:
        return "none"
    high_threshold, medium_threshold = {
        ".csv": (600, 150),
        ".docx": (1200, 300),
        ".md": (1200, 250),
        ".txt": (1200, 250),
    }.get(suffix, (1000, 250))
    if characters >= high_threshold:
        return "high"
    if characters >= medium_threshold:
        return "medium"
    return "low"


def reading_confidence(extraction: ExtractionResult, quality: str) -> str:
    if extraction.status != "ok":
        return "low"
    if extraction.reading_method == "ocr_text" and quality == "high":
        return "medium"
    return quality if quality in {"high", "medium", "low"} else "low"


def count_patterns(text: str, patterns: tuple[str, ...]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def count_markers(folded_text: str, markers: tuple[str, ...]) -> dict[str, int]:
    hits: dict[str, int] = {}
    for marker in markers:
        count = folded_text.count(fold_text(marker))
        if count:
            hits[marker] = count
    return hits


def infer_dataset_shape(text: str, suffix: str) -> dict[str, Any]:
    if suffix != ".csv":
        return {}
    lines = text.splitlines()
    try:
        rows = list(csv.reader(lines[:3]))
        column_count = max((len(row) for row in rows), default=0)
        header = ",".join(rows[0][:8]) if rows else ""
    except csv.Error:
        column_count = 0
        header = lines[0] if lines else ""
    return {
        "csv_rows_est": len(lines),
        "csv_cols_est": column_count,
        "csv_header_preview": header[:200],
    }


def collect_signals(path: Path, text: str, target_terms: tuple[str, ...]) -> dict[str, Any]:
    folded = fold_text(text)
    accusation_count = count_patterns(text, ACCUSATION_PATTERNS)
    legal_count = count_patterns(text, LEGAL_PATTERNS)
    evidence_hits = count_markers(folded, EVIDENCE_MARKERS)
    target_hits = {
        term: folded.count(fold_text(term))
        for term in target_terms
        if fold_text(term) and folded.count(fold_text(term))
    }
    text_kb = max(1.0, len(text) / 1000.0)
    signals: dict[str, Any] = {
        "dates_found": len(re.findall(r"\b\d{2}/\d{2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b", text)),
        "currency_values_found": len(re.findall(r"(?:R\$|US\$|USD)\s*[\d.,]+", text, flags=re.IGNORECASE)),
        "pix_mentions": folded.count("pix"),
        "email_mentions": len(re.findall(r"[\w.+-]+@[\w.-]+\.\w+", text)),
        "transaction_terms": sum(folded.count(term) for term in ("extrato", "fatura", "lancamento", "transacao")),
        "accusation_keyword_hits": {"pattern_matches": accusation_count} if accusation_count else {},
        "evidence_marker_hits": evidence_hits,
        "target_term_hits": target_hits,
        "contains_objetivo_label": bool(re.search(r"\bobjetivo\s*:", text, flags=re.IGNORECASE)),
        "contains_responsavel_label": bool(re.search(r"\brespons[áa]vel\s*:", text, flags=re.IGNORECASE)),
        "contains_summary_label": bool(re.search(r"\bresumo\b|\bsum[áa]rio\b", text, flags=re.IGNORECASE)),
        "legal_pattern_counts": {"legal": legal_count, "accusation": accusation_count},
        "legal_refs_density": round(min(1.0, legal_count / text_kb * 0.10), 6),
        "accusation_density": round(min(1.0, accusation_count / text_kb * 0.08), 6),
    }
    signals.update(infer_dataset_shape(text, path.suffix.lower()))
    return signals


def empty_signals(suffix: str) -> dict[str, Any]:
    signals: dict[str, Any] = {
        "dates_found": 0,
        "currency_values_found": 0,
        "pix_mentions": 0,
        "email_mentions": 0,
        "transaction_terms": 0,
        "accusation_keyword_hits": {},
        "evidence_marker_hits": {},
        "target_term_hits": {},
        "contains_objetivo_label": False,
        "contains_responsavel_label": False,
        "contains_summary_label": False,
        "legal_pattern_counts": {"legal": 0, "accusation": 0},
        "legal_refs_density": 0.0,
        "accusation_density": 0.0,
    }
    signals.update(infer_dataset_shape("", suffix))
    return signals


def detect_declared_purpose(text: str, strict: bool) -> tuple[bool, str | None]:
    patterns = [
        r"\bobjetivo\s*:\s*([^\n]{1,200})",
        r"\bfinalidade\s*:\s*([^\n]{1,200})",
    ]
    if not strict:
        patterns.extend(
            [
                r"\b(?:este|o presente)\s+(?:documento|relat[óo]rio|sum[áa]rio)\s+visa\s+([^\n]{1,200})",
                r"\bencaminhamento\s+para\b",
            ]
        )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return True, normalize(match.group(0))[:220]
    return False, None


def detect_responsible_actor(text: str, strict: bool) -> tuple[bool, str | None]:
    patterns = [r"\brespons[áa]vel(?:\s+humano)?\s*:\s*([^\n]{1,160})"]
    if not strict:
        patterns.extend(
            [
                r"\bautor\s*:\s*([^\n]{1,160})",
                r"\bassinado\s+por\s*:\s*([^\n]{1,160})",
            ]
        )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return True, normalize(match.group(0))[:220]
    return False, None


def detect_approval(text: str, strict: bool) -> tuple[bool, str | None]:
    patterns = [
        r"\baprovad[oa]\s*:\s*([^\n]{0,120})",
        r"\baprova[cç][aã]o\s*:\s*([^\n]{0,120})",
    ]
    if not strict:
        patterns.extend((r"\baprovad[oa]\b", r"\bassinado\b", r"\bvalidado\b"))
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return True, normalize(match.group(0))[:180]
    return False, None


def infer_artifact_type(path: Path, text: str) -> tuple[str, str]:
    name = fold_text(path.name)
    folded = fold_text(text)
    if any(marker in name for marker in ANALYTICAL_NAME_MARKERS):
        return "ANALYTICAL_ARTIFACT", "Filename matches analytical or reporting markers."
    if any(marker in name for marker in DECISION_NAME_MARKERS):
        return "DECISION_ARTIFACT", "Filename matches procedural or filing markers."
    if any(marker in folded for marker in ("processo n", "requeiro", "solicito", "protocolo", "vara de")):
        return "DECISION_ARTIFACT", "Content contains procedural or filing language."
    if path.suffix.lower() == ".md":
        return "ANALYTICAL_ARTIFACT", "Markdown defaults to analytical material."
    return "DECISION_ARTIFACT", "Fallback for material that can support a decision."


def detect_prescriptive(text: str) -> GateResult:
    folded = fold_text(text)
    hits = [pattern for pattern in PRESCRIPTIVE_PATTERNS if pattern in folded]
    if hits:
        return GateResult("BLOCKED", "Prescriptive language was detected.", ", ".join(hits[:5]))
    return GateResult("PASS", "No configured prescriptive pattern was detected.")


def compliance_gate(text: str, mode: AuditMode, artifact_type: str) -> GateResult:
    strict = mode.strict_explicit_decision_record
    actor, actor_evidence = detect_responsible_actor(text, strict)
    if artifact_type == "ANALYTICAL_ARTIFACT":
        if not actor:
            return GateResult("WARN", "Analytical material does not identify a responsible person explicitly.")
        return GateResult("PASS", "A responsibility indicator was found.", actor_evidence)

    purpose, purpose_evidence = detect_declared_purpose(text, strict)
    approval, approval_evidence = detect_approval(text, strict)
    missing = []
    if not actor:
        missing.append("responsibleHuman")
    if not purpose:
        missing.append("declaredPurpose")
    if not approval:
        missing.append("approved")
    evidence = " | ".join(
        part
        for part in (
            f"actor={actor_evidence}" if actor_evidence else "",
            f"purpose={purpose_evidence}" if purpose_evidence else "",
            f"approval={approval_evidence}" if approval_evidence else "",
        )
        if part
    )
    if missing:
        return GateResult("BLOCKED", f"Decision record is incomplete: {', '.join(missing)}.", evidence or None)
    return GateResult("PASS", "Actor, purpose and approval indicators were found.", evidence or None)


def traceability_gate(signals: dict[str, Any]) -> GateResult:
    dates = int(signals.get("dates_found") or 0)
    values = int(signals.get("currency_values_found") or 0)
    markers = sum(int(value) for value in (signals.get("evidence_marker_hits") or {}).values())
    score = int(dates > 0) + int(values > 0) + int(markers > 0)
    evidence = f"dates={dates}, currency={values}, evidence_markers={markers}"
    if score >= 2:
        return GateResult("PASS", "Multiple traceability signals were found.", evidence)
    if score == 1:
        return GateResult("WARN", "Only one traceability signal was found.", evidence)
    return GateResult("WARN", "No clear traceability signal was found.")


def compute_gates(
    text: str,
    signals: dict[str, Any],
    mode: AuditMode,
    artifact_type: str,
) -> tuple[dict[str, dict[str, Any]], str]:
    prescriptive = detect_prescriptive(text)
    compliance = compliance_gate(text, mode, artifact_type)
    traceability = traceability_gate(signals)
    maturity = GateResult("NOT_EVALUATED", "Maturity scoring requires runtime context.")
    ledger = GateResult("NOT_APPLICABLE", "Static files do not expose ledger or hash-chain state.")

    if prescriptive.status == "BLOCKED":
        outcome = "BLOCKED (prescriptiveGate)"
    elif compliance.status == "BLOCKED":
        outcome = "BLOCKED (complianceGate)"
    elif traceability.status == "WARN":
        outcome = "PARTIAL_PASS (traceability warning; static audit)"
    else:
        outcome = "PARTIAL_PASS (static document audit; runtime checks pending)"

    return {
        "prescriptiveGate": asdict(prescriptive),
        "maturityGate": asdict(maturity),
        "complianceGate": asdict(compliance),
        "ledgerRuntimeCheck": asdict(ledger),
        "traceabilityCheck": asdict(traceability),
    }, outcome


def classify_file(
    path: Path,
    extraction: ExtractionResult,
    signals: dict[str, Any],
    sensitive: bool,
) -> tuple[str, bool, list[str]]:
    if sensitive:
        return "SENSITIVE_EXCLUDED", False, ["Sensitive filename matched; content was not read."]
    if extraction.status == "unsupported":
        return "UNSUPPORTED", False, ["Unsupported file type or missing platform extractor."]
    if extraction.status in {"error", "ocr_unavailable", "ocr_disabled"}:
        return "UNREADABLE", False, ["Text extraction did not produce usable content."]
    if extraction.status == "unreadable_or_empty":
        return "UNREADABLE_OR_EMPTY", False, ["The file yielded no usable text."]

    suffix = path.suffix.lower()
    name = fold_text(path.name)
    accusation_hits = int((signals.get("legal_pattern_counts") or {}).get("accusation") or 0)
    evidence_hits = sum(int(value) for value in (signals.get("evidence_marker_hits") or {}).values())
    target_hits = sum(int(value) for value in (signals.get("target_term_hits") or {}).values())
    legal_density = float(signals.get("legal_refs_density") or 0.0)
    filename_score = 2 * sum(
        marker in name
        for marker in ("acusacao", "denuncia", "dossie", "fraude", "golpe", "reclamacao")
    )
    content_score = min(accusation_hits, 8)
    content_score += 2 if target_hits and accusation_hits else 0
    content_score += 1 if signals.get("contains_objetivo_label") else 0
    content_score += 1 if signals.get("contains_responsavel_label") else 0
    content_score += 2 if legal_density >= 0.15 else int(legal_density >= 0.05)
    total_score = filename_score + content_score

    if suffix == ".csv":
        reasons = ["CSV was treated primarily as supporting evidence or a data source."]
        if accusation_hits >= 2 and (target_hits > 0 or evidence_hits > 0):
            reasons.append("The data contains accusation-related and contextual signals.")
            return "SUPPORTING_EVIDENCE_RELEVANT", False, reasons
        return "SUPPORTING_EVIDENCE", False, reasons

    if total_score >= 5 and accusation_hits > 0:
        reasons = [f"Investigation-signal score={total_score}."]
        if target_hits:
            reasons.append("Configured target terms were found.")
        if evidence_hits:
            reasons.append("Evidence or documentation markers were found.")
        return "ACCUSATORY_CANDIDATE", True, reasons

    if evidence_hits > 0 or int(signals.get("transaction_terms") or 0) > 0 or target_hits > 0:
        return "SUPPORTING_EVIDENCE_RELEVANT", False, ["Relevant contextual or supporting content was found."]
    return "NEUTRAL_OR_CONTEXT", False, [f"Low investigation-signal score={total_score}."]


def process_file(path: Path, options: PipelineOptions) -> FileRecord:
    sensitive = is_sensitive_name(path, options.sensitive_names)
    if sensitive:
        extraction = ExtractionResult("", "skipped_sensitive", "none", "unknown", "not_attempted")
        digest = "not_computed_sensitive"
    else:
        extraction = extract_text(path, enable_ocr=options.enable_ocr)
        digest = sha256_file(path)

    text_characters = len(extraction.text)
    quality = classify_text_quality(text_characters, path.suffix.lower())
    signals = (
        collect_signals(path, extraction.text, options.target_terms)
        if extraction.status == "ok" and extraction.text
        else empty_signals(path.suffix.lower())
    )
    classification, raises_accusation, reasons = classify_file(path, extraction, signals, sensitive)

    artifact_type = "N/A"
    artifact_type_reason = "Not evaluated for material outside the investigation-signal set."
    gates = None
    outcome = None
    if raises_accusation and extraction.status == "ok" and extraction.text:
        artifact_type, artifact_type_reason = infer_artifact_type(path, extraction.text)
        gates, outcome = compute_gates(extraction.text, signals, options.mode, artifact_type)

    return FileRecord(
        file_name=path.name,
        file_path=source_label(path, options.input_roots, options.include_source_paths),
        suffix=path.suffix.lower(),
        size_bytes=path.stat().st_size,
        sha256=digest,
        extraction_status=extraction.status,
        extraction_method=extraction.method,
        extractable_text_chars=text_characters,
        text_chars=text_characters,
        text_quality=quality,
        reading_method=extraction.reading_method,
        ocr_status=extraction.ocr_status,
        reading_confidence=reading_confidence(extraction, quality),
        sensitive_handling="skipped_content" if sensitive else "normal",
        classification=classification,
        artifact_type=artifact_type,
        artifact_type_reason=artifact_type_reason,
        raises_accusation=raises_accusation,
        classification_reasons=reasons,
        key_signals=signals,
        gates=gates,
        overall_outcome=outcome,
    )


def count_by(records: list[FileRecord], attribute: str) -> dict[str, int]:
    counts = Counter(str(getattr(record, attribute)) for record in records)
    return dict(sorted(counts.items()))


def input_scope(options: PipelineOptions) -> list[str]:
    if options.include_source_paths:
        return [str(root) for root in options.input_roots]
    return [root.name for root in options.input_roots]


def build_payload(records: list[FileRecord], options: PipelineOptions) -> dict[str, Any]:
    accusation_set = [asdict(record) for record in records if record.raises_accusation]
    non_accusation_set = [asdict(record) for record in records if not record.raises_accusation]
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "audit_basis": "Sanitized TCRIA static document audit with explicit reading provenance.",
        "mode": options.mode.slug,
        "compliance_gate_mode": options.mode.label,
        "input_path": input_scope(options),
        "input_scope": input_scope(options),
        "total_files_scanned": len(records),
        "accusation_set_count": len(accusation_set),
        "classification_counts": count_by(records, "classification"),
        "route_counts": {
            "investigation_signal_set": len(accusation_set),
            "support_or_context_set": len(non_accusation_set),
        },
        "document_role_counts": count_by(records, "artifact_type"),
        "accusation_set": accusation_set,
        "non_accusation_set": non_accusation_set,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Auditoria documental do lote",
        "",
        "Este arquivo e uma saida tecnica do pipeline. Ele organiza sinais e limites sem afirmar culpa ou veracidade juridica.",
        "",
        f"- Gerado em: `{payload['generated_at']}`",
        f"- Modo de verificacao: `{payload['compliance_gate_mode']}`",
        f"- Arquivos analisados: `{payload['total_files_scanned']}`",
        f"- Documentos que abriram sinais de investigacao: `{payload['accusation_set_count']}`",
        f"- Contagens tecnicas: `{payload['classification_counts']}`",
        "",
        "## Documentos que abriram sinais",
        "",
    ]

    accusation_set = payload.get("accusation_set") or []
    if not accusation_set:
        lines.append("Nenhum documento abriu sinal pelas regras configuradas nesta rodada.")
        lines.append("")
    for record in accusation_set:
        lines.extend(
            [
                f"### {record['file_name']}",
                f"- Caminho registrado: `{record['file_path']}`",
                f"- Como foi lido: `{record['reading_method']}`",
                f"- Situacao do OCR: `{record['ocr_status']}`",
                f"- Confianca da leitura: `{record['reading_confidence']}`",
                f"- Resultado tecnico: `{record['overall_outcome']}`",
                f"- Tipo interno: `{record['artifact_type']}`",
                f"- Motivos: {'; '.join(record['classification_reasons'])}",
            ]
        )
        for gate_name, gate in (record.get("gates") or {}).items():
            lines.append(f"- `{gate_name}`: `{gate['status']}` - {gate['reason']}")
        lines.append("")

    lines.extend(["## Demais documentos", ""])
    for record in payload.get("non_accusation_set") or []:
        reason = (record.get("classification_reasons") or ["sem motivo registrado"])[0]
        lines.append(
            f"- `{record['file_name']}` -> `{record['classification']}`; leitura `{record['reading_method']}`; {reason}"
        )

    lines.extend(
        [
            "",
            "## Limites",
            "",
            "- A auditoria avalia estrutura e sinais textuais; nao verifica a verdade material das alegacoes.",
            "- Documentos sensiveis identificados pelo nome nao tem o conteudo lido nem o hash calculado.",
            "- Controles de maturidade, ledger e hash-chain dependem de contexto de runtime.",
            "- A decisao final continua sob responsabilidade profissional humana.",
            "",
        ]
    )
    return "\n".join(lines)


def run_pipeline(options: PipelineOptions) -> tuple[dict[str, Any], Path, Path]:
    records = [process_file(path, options) for path in options.input_files]
    payload = build_payload(records, options)
    output_dir = options.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_output_stem(options.output_stem)
    if options.mode.strict_explicit_decision_record:
        stem = f"{stem}_strict"
    json_output = output_dir / f"{stem}.json"
    markdown_output = output_dir / f"{stem}.md"
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_output.write_text(build_markdown(payload), encoding="utf-8")
    return payload, json_output, markdown_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the sanitized legacy TCRIA static-document audit on an explicit input batch."
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        required=True,
        help="File or directory to process. Repeat for multiple inputs.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for JSON and Markdown outputs.",
    )
    parser.add_argument(
        "--output-stem",
        default=DEFAULT_OUTPUT_STEM,
        help="Output filename without extension.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require explicit labels for responsible person, purpose and approval.",
    )
    parser.add_argument(
        "--target-term",
        action="append",
        default=[],
        help="Case-specific person, entity or identifier to correlate. Repeatable; never stored in source code.",
    )
    parser.add_argument(
        "--sensitive-name",
        action="append",
        default=[],
        help="Additional exact filename whose content must not be read. Repeatable.",
    )
    parser.add_argument(
        "--include-source-paths",
        action="store_true",
        help="Expose absolute input paths in output. Disabled by default.",
    )
    parser.add_argument(
        "--disable-ocr",
        action="store_true",
        help="Do not use OCR fallback for scanned PDFs or images.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()
    try:
        files, roots = resolve_input_paths(arguments.paths)
        options = PipelineOptions(
            input_files=files,
            input_roots=roots,
            output_dir=Path(arguments.output_dir),
            output_stem=arguments.output_stem,
            mode=AuditMode(strict_explicit_decision_record=arguments.strict),
            target_terms=tuple(arguments.target_term),
            sensitive_names=tuple(arguments.sensitive_name),
            include_source_paths=arguments.include_source_paths,
            enable_ocr=not arguments.disable_ocr,
        )
        payload, json_output, markdown_output = run_pipeline(options)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Mode: {options.mode.label}")
    print(f"JSON report: {json_output}")
    print(f"Markdown report: {markdown_output}")
    print(f"Total scanned: {payload['total_files_scanned']}")
    print(f"Investigation signals: {payload['accusation_set_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
