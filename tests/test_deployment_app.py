from __future__ import annotations

import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import time

from fastapi import HTTPException

from app.jobs import JobStore, expand_archives, safe_name, validate_file_signature
from app.models import AnalysisStatus
from app.analysis import synthesize
from openai import RateLimitError
from httpx import Request, Response


class DeploymentAppTests(unittest.TestCase):
    def test_safe_name_removes_paths_and_unsafe_characters(self) -> None:
        self.assertEqual(safe_name("../../contrato<script>.pdf", 1), "contrato_script_.pdf")

    def test_zip_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "lote.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../fora.txt", "nao extrair")
            with self.assertRaises(HTTPException):
                expand_archives(root)
            self.assertFalse((root.parent / "fora.txt").exists())

    def test_zip_with_supported_document_is_expanded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "lote.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("pasta/evidencia.txt", "conteudo")
            expand_archives(root)
            self.assertEqual((root / "lote-extraido" / "pasta" / "evidencia.txt").read_text(), "conteudo")
            self.assertFalse(archive_path.exists())

    def test_fake_pdf_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "falso.pdf"
            path.write_text("isto nao e pdf")
            with self.assertRaises(HTTPException):
                validate_file_signature(path)

    def test_job_store_rejects_invalid_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary))
            with self.assertRaises(HTTPException):
                store.get("../../etc")

    def test_expired_jobs_are_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch("app.jobs.RETENTION_SECONDS", 10):
            store = JobStore(Path(temporary))
            _, job_dir = store.create("Esta pergunta possui tamanho suficiente?")
            old = time.time() - 20
            os.utime(job_dir, (old, old))
            self.assertEqual(store.cleanup_expired(), 1)
            self.assertFalse(job_dir.exists())

    def test_job_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            store = JobStore(Path(temporary))
            _, job_dir = store.create("Esta pergunta possui tamanho suficiente?")
            status = store.update(job_dir, accepted_files=["documento.pdf"], progress=20)
            self.assertIsInstance(status, AnalysisStatus)
            self.assertEqual(store.read_status(job_dir).accepted_files, ["documento.pdf"])

    def test_openai_quota_error_uses_auditable_fallback(self) -> None:
        report = {"total_files_scanned": 1, "coverage": {}, "document_outcomes": {}, "documents": []}
        response = Response(429, request=Request("POST", "https://api.openai.com/v1/responses"))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "configured-for-test"}), patch(
            "app.analysis.OpenAI"
        ) as client:
            client.return_value.responses.parse.side_effect = RateLimitError(
                "quota unavailable", response=response, body=None
            )
            analysis, source = synthesize("Esta pergunta possui tamanho suficiente?", report)
        self.assertEqual(source, "deterministic_fallback_openai_unavailable")
        self.assertIn("OpenAI", " ".join(analysis.limitations))


if __name__ == "__main__":
    unittest.main()
