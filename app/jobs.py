from __future__ import annotations

import json
import os
import shutil
import stat
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile

from app.analysis import run_document_pipeline, synthesize, write_artifacts
from app.models import AnalysisStatus


MAX_FILES = int(os.getenv("TCRIA_MAX_FILES", "20"))
MAX_BATCH_BYTES = int(os.getenv("TCRIA_MAX_BATCH_BYTES", str(100 * 1024 * 1024)))
RETENTION_SECONDS = int(os.getenv("TCRIA_RETENTION_SECONDS", str(24 * 60 * 60)))
ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt", ".md", ".zip"}
ARCHIVE_SUFFIXES = ALLOWED_SUFFIXES - {".zip"}
CHUNK_SIZE = 1024 * 1024


class JobStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, question: str) -> tuple[str, Path]:
        analysis_id = str(uuid4())
        job_dir = self.root / analysis_id
        (job_dir / "input").mkdir(parents=True)
        (job_dir / "output").mkdir()
        self.write_status(
            job_dir,
            AnalysisStatus(
                analysis_id=analysis_id,
                state="queued",
                stage="Lote recebido",
                progress=5,
                question=question,
                accepted_files=[],
            ),
        )
        return analysis_id, job_dir

    def get(self, analysis_id: str) -> Path:
        try:
            canonical = str(UUID(analysis_id))
        except ValueError as error:
            raise HTTPException(status_code=404, detail="Análise não encontrada.") from error
        job_dir = self.root / canonical
        if not job_dir.is_dir():
            raise HTTPException(status_code=404, detail="Análise não encontrada.")
        return job_dir

    def read_status(self, job_dir: Path) -> AnalysisStatus:
        return AnalysisStatus.model_validate_json((job_dir / "status.json").read_text(encoding="utf-8"))

    def write_status(self, job_dir: Path, status: AnalysisStatus) -> None:
        temporary = job_dir / "status.json.tmp"
        temporary.write_text(status.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(job_dir / "status.json")

    def update(self, job_dir: Path, **changes: object) -> AnalysisStatus:
        status = self.read_status(job_dir).model_copy(update=changes)
        self.write_status(job_dir, status)
        return status

    def cleanup_expired(self) -> int:
        cutoff = time.time() - RETENTION_SECONDS
        removed = 0
        for candidate in self.root.iterdir():
            if candidate.is_dir() and candidate.stat().st_mtime < cutoff:
                shutil.rmtree(candidate)
                removed += 1
        return removed


def safe_name(raw_name: str | None, index: int) -> str:
    name = Path(raw_name or f"arquivo-{index}").name
    cleaned = "".join(char if char.isalnum() or char in "._- " else "_" for char in name).strip(" .")
    return cleaned or f"arquivo-{index}"


async def save_uploads(files: list[UploadFile], input_dir: Path) -> list[str]:
    if not files or len(files) > MAX_FILES:
        raise HTTPException(status_code=422, detail=f"Envie entre 1 e {MAX_FILES} arquivos.")
    accepted: list[str] = []
    total = 0
    for index, upload in enumerate(files, start=1):
        filename = safe_name(upload.filename, index)
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(status_code=415, detail=f"Formato não permitido: {filename}")
        destination = unique_destination(input_dir, filename)
        with destination.open("wb") as target:
            while chunk := await upload.read(CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_BATCH_BYTES:
                    raise HTTPException(status_code=413, detail="O lote excede 100 MB.")
                target.write(chunk)
        validate_file_signature(destination)
        accepted.append(destination.name)
    expand_archives(input_dir)
    document_count = len([path for path in input_dir.rglob("*") if path.is_file() and path.suffix.lower() != ".zip"])
    if document_count > MAX_FILES:
        raise HTTPException(status_code=422, detail=f"O lote expandido excede {MAX_FILES} documentos.")
    return accepted


def unique_destination(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    counter = 2
    while candidate.exists():
        candidate = directory / f"{Path(filename).stem}-{counter}{Path(filename).suffix}"
        counter += 1
    return candidate


def validate_file_signature(path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        with path.open("rb") as source:
            if source.read(5) != b"%PDF-":
                raise HTTPException(status_code=415, detail=f"O arquivo {path.name} não é um PDF válido.")
    elif suffix == ".zip" and not zipfile.is_zipfile(path):
        raise HTTPException(status_code=415, detail=f"O arquivo {path.name} não é um ZIP válido.")
    elif suffix == ".docx":
        if not zipfile.is_zipfile(path):
            raise HTTPException(status_code=415, detail=f"O arquivo {path.name} não é um DOCX válido.")
        with zipfile.ZipFile(path) as document:
            names = set(document.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise HTTPException(status_code=415, detail=f"O arquivo {path.name} não é um DOCX válido.")


def expand_archives(input_dir: Path) -> None:
    for archive_path in list(input_dir.glob("*.zip")):
        target_dir = input_dir / f"{archive_path.stem}-extraido"
        target_dir.mkdir()
        try:
            with zipfile.ZipFile(archive_path) as archive:
                expanded_size = sum(info.file_size for info in archive.infolist() if not info.is_dir())
                if expanded_size > MAX_BATCH_BYTES:
                    raise ValueError("expanded archive exceeds batch limit")
                for info in archive.infolist():
                    validate_archive_member(info)
                    if info.is_dir():
                        continue
                    destination = target_dir.joinpath(*PurePosixPath(info.filename).parts)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, destination.open("wb") as target:
                        copy_limited(source, target)
        except (zipfile.BadZipFile, RuntimeError, ValueError) as error:
            raise HTTPException(status_code=422, detail=f"ZIP inválido ou inseguro: {archive_path.name}") from error
        archive_path.unlink()


def validate_archive_member(info: zipfile.ZipInfo) -> None:
    path = PurePosixPath(info.filename)
    mode = info.external_attr >> 16
    if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
        raise ValueError("unsafe archive path")
    if stat.S_ISLNK(mode):
        raise ValueError("symbolic links are not allowed")
    if not info.is_dir() and path.suffix.lower() not in ARCHIVE_SUFFIXES:
        raise ValueError("unsupported archive member")
    if info.file_size > MAX_BATCH_BYTES:
        raise ValueError("archive member too large")


def copy_limited(source: BinaryIO, target: BinaryIO) -> None:
    written = 0
    while chunk := source.read(CHUNK_SIZE):
        written += len(chunk)
        if written > MAX_BATCH_BYTES:
            raise ValueError("expanded archive exceeds limit")
        target.write(chunk)


def process_job(store: JobStore, job_dir: Path) -> None:
    try:
        store.update(job_dir, state="processing", stage="Leitura direta e OCR", progress=20)
        _, report = run_document_pipeline(job_dir / "input", job_dir / "output")
        store.update(job_dir, stage="Análise de conformidade", progress=65)
        status = store.read_status(job_dir)
        analysis, source = synthesize(status.question, report)
        store.update(job_dir, stage="Geração do relatório", progress=85)
        artifacts = write_artifacts(job_dir / "output", status.question, analysis, report, source)
        (job_dir / "artifacts.json").write_text(json.dumps(artifacts), encoding="utf-8")
        store.update(job_dir, state="completed", stage="Concluído", progress=100)
    except Exception as error:  # boundary: safe status, detailed server log belongs to runtime
        store.update(job_dir, state="failed", stage="Falha no processamento", error=str(error)[:500])
