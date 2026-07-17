from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_accusation_bundle_with_tcr_gateway as pipeline
from render_legacy_audit_summary import build_report


class LegacyAuditPipelineTests(unittest.TestCase):
    def test_sensitive_file_content_and_hash_are_never_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir) / "case"
            root.mkdir()
            sensitive = root / "senhas.csv"
            sensitive.write_text("password,never-expose-this-value", encoding="utf-8")
            files, roots = pipeline.resolve_input_paths([str(root)])
            options = pipeline.PipelineOptions(
                input_files=files,
                input_roots=roots,
                output_dir=Path(temporary_dir) / "output",
            )

            payload, json_output, _ = pipeline.run_pipeline(options)
            record = payload["non_accusation_set"][0]
            serialized = json_output.read_text(encoding="utf-8")

            self.assertEqual(record["classification"], "SENSITIVE_EXCLUDED")
            self.assertEqual(record["extraction_status"], "skipped_sensitive")
            self.assertEqual(record["sha256"], "not_computed_sensitive")
            self.assertNotIn("never-expose-this-value", serialized)

    def test_output_uses_relative_source_and_matches_legacy_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir) / "case-batch"
            root.mkdir()
            document = root / "relatorio_fraude.txt"
            document.write_text(
                "\n".join(
                    [
                        "Objetivo: revisar a denuncia de fraude.",
                        "Responsavel: Analista designado.",
                        "Aprovado: revisao preliminar.",
                        "Entidade Exemplo apresentou comprovante e extrato em 17/07/2026.",
                    ]
                ),
                encoding="utf-8",
            )
            files, roots = pipeline.resolve_input_paths([str(root)])
            options = pipeline.PipelineOptions(
                input_files=files,
                input_roots=roots,
                output_dir=Path(temporary_dir) / "output",
                target_terms=("Entidade Exemplo",),
            )

            payload, json_output, markdown_output = pipeline.run_pipeline(options)
            record = payload["accusation_set"][0]
            adapted = build_report(json.loads(json_output.read_text(encoding="utf-8")))

            self.assertFalse(Path(record["file_path"]).is_absolute())
            self.assertEqual(record["reading_method"], "direct_text")
            self.assertEqual(record["ocr_status"], "not_needed")
            self.assertEqual(adapted["total_files_scanned"], 1)
            self.assertEqual(len(adapted["documents"]), 1)
            self.assertTrue(markdown_output.exists())

    def test_pdf_ocr_runs_only_after_direct_extraction_fails(self) -> None:
        direct_success = pipeline.ExtractionResult(
            "texto incorporado",
            "ok",
            "pdftotext",
            "direct_text",
            "not_needed",
        )
        with patch.object(pipeline, "extract_pdf_direct", return_value=direct_success), patch.object(
            pipeline,
            "ocr_pdf",
            side_effect=AssertionError("OCR should not run"),
        ):
            result = pipeline.extract_text(Path("document.pdf"), enable_ocr=True)
            self.assertEqual(result.reading_method, "direct_text")

        direct_failure = pipeline.ExtractionResult(
            "",
            "unreadable_or_empty",
            "pdf_direct_failed",
            "direct_text",
            "not_needed",
        )
        ocr_success = pipeline.ExtractionResult(
            "texto recuperado",
            "ok",
            "pdftoppm+tesseract",
            "ocr_text",
            "attempted_success",
        )
        with patch.object(pipeline, "extract_pdf_direct", return_value=direct_failure), patch.object(
            pipeline,
            "ocr_pdf",
            return_value=ocr_success,
        ) as ocr_mock:
            result = pipeline.extract_text(Path("scan.pdf"), enable_ocr=True)
            self.assertEqual(result.reading_method, "ocr_text")
            ocr_mock.assert_called_once()

    def test_missing_input_fails_instead_of_scanning_user_directories(self) -> None:
        with self.assertRaises(ValueError):
            pipeline.resolve_input_paths([])


if __name__ == "__main__":
    unittest.main()
