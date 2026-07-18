from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.local")

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.jobs import JobStore, process_job, save_uploads
from app.models import AnalysisStatus


JOB_ROOT = Path(os.getenv("TCRIA_JOB_ROOT", str(ROOT / "tcria_jobs")))
store = JobStore(JOB_ROOT)
app = FastAPI(title="TCRIA", version="0.1.0")
cleanup_stop = threading.Event()


def cleanup_loop() -> None:
    while not cleanup_stop.wait(3600):
        store.cleanup_expired()


@app.on_event("startup")
def validate_production_configuration() -> None:
    if os.getenv("TCRIA_ENV", "development").lower() == "production" and not os.getenv("TCRIA_PILOT_TOKEN"):
        raise RuntimeError("TCRIA_PILOT_TOKEN must be configured in production.")
    store.cleanup_expired()
    cleanup_stop.clear()
    threading.Thread(target=cleanup_loop, name="tcria-retention-cleanup", daemon=True).start()


@app.on_event("shutdown")
def stop_cleanup() -> None:
    cleanup_stop.set()


def authorize(x_tcria_token: str | None = Header(default=None)) -> None:
    expected = os.getenv("TCRIA_PILOT_TOKEN")
    if expected and x_tcria_token != expected:
        raise HTTPException(status_code=401, detail="Credencial do piloto inválida.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyses", response_model=AnalysisStatus, status_code=202, dependencies=[Depends(authorize)])
async def create_analysis(
    background_tasks: BackgroundTasks,
    question: str = Form(min_length=10, max_length=2000),
    files: list[UploadFile] = File(),
) -> AnalysisStatus:
    store.cleanup_expired()
    analysis_id, job_dir = store.create(question.strip())
    try:
        accepted = await save_uploads(files, job_dir / "input")
    except Exception:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise
    status = store.update(job_dir, accepted_files=accepted)
    background_tasks.add_task(process_job, store, job_dir)
    return status


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisStatus, dependencies=[Depends(authorize)])
def get_analysis_status(analysis_id: str) -> AnalysisStatus:
    return store.read_status(store.get(analysis_id))


@app.get("/api/analyses/{analysis_id}/result", dependencies=[Depends(authorize)])
def get_analysis_result(analysis_id: str) -> dict:
    job_dir = store.get(analysis_id)
    status = store.read_status(job_dir)
    if status.state != "completed":
        raise HTTPException(status_code=409, detail="A análise ainda não foi concluída.")
    return json.loads((job_dir / "output" / "result.json").read_text(encoding="utf-8"))


@app.get("/api/analyses/{analysis_id}/artifacts/{artifact_format}", dependencies=[Depends(authorize)])
def download_analysis_artifact(analysis_id: str, artifact_format: str) -> FileResponse:
    if artifact_format not in {"pdf", "html", "json"}:
        raise HTTPException(status_code=404, detail="Artefato não encontrado.")
    job_dir = store.get(analysis_id)
    status = store.read_status(job_dir)
    if status.state != "completed":
        raise HTTPException(status_code=409, detail="A análise ainda não foi concluída.")
    artifacts = json.loads((job_dir / "artifacts.json").read_text(encoding="utf-8"))
    path = job_dir / "output" / artifacts[artifact_format]
    media_types = {"pdf": "application/pdf", "html": "text/html", "json": "application/json"}
    return FileResponse(path, media_type=media_types[artifact_format], filename=f"tcria-{analysis_id}.{artifact_format}")


app.mount("/", StaticFiles(directory=ROOT / "app" / "static", html=True), name="static")
