from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from investigation_engine.contradictions import build_legacy_contradictions, build_report_contradictions
from render_legacy_audit_summary import build_report


class ContradictionsEngineTests(unittest.TestCase):
    def test_build_report_contradictions_detects_all_new_keyword_groups(self) -> None:
        result = build_report_contradictions(
            {
                "findings": [
                    {
                        "title": "Conflicting clauses and discrepancy in scope",
                        "what_identified": "The appendix is not aligned; texto divergente, difere do texto principal.",
                        "why_matters": "This contradiction changes the obligation.",
                        "supporting_evidence": [],
                    },
                    {
                        "title": "Exception request",
                        "what_identified": "Waiver requested with contratação direta.",
                        "why_matters": "No formal basis was attached.",
                        "supporting_evidence": [],
                    },
                    {
                        "title": "Commercial terms",
                        "what_identified": "Entrega a combinar e prazo indefinido.",
                        "why_matters": "Values remain subject to change.",
                        "supporting_evidence": [],
                    },
                    {
                        "title": "Supplier award",
                        "what_identified": "Único fornecedor with undisclosed relationship and kickback risk.",
                        "why_matters": "Selection looks directed.",
                        "supporting_evidence": [],
                    },
                    {
                        "title": "Liability section",
                        "what_identified": "The vendor states não nos responsabilizamos and hold harmless.",
                        "why_matters": "Accountability is weakened.",
                        "supporting_evidence": [],
                    },
                    {
                        "title": "Execution record",
                        "what_identified": "Retroactive date with assinatura divergente.",
                        "why_matters": "The copy may have been fabricated.",
                        "supporting_evidence": [],
                    },
                ]
            },
            [],
        )

        self.assertEqual(
            result["items"],
            [
                "O documento apresenta trechos internamente divergentes ou incompatíveis.",
                "Foi identificada dispensa ou exceção de processo sem fundamentação formal clara.",
                "Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.",
                "Há sinais de direcionamento ou irregularidade na seleção ou pagamento ao fornecedor.",
                "O documento diluiu ou omitiu responsabilidades que deveriam estar claramente atribuídas.",
                "Foram identificados sinais de possível adulteração ou irregularidade formal no documento.",
            ],
        )

    def test_build_legacy_contradictions_uses_signals_and_document_text_when_available(self) -> None:
        report = {
            "coverage": {"ok_count": 0, "insufficient_text_count": 0},
            "document_outcomes": {"PASS": 0, "BLOCKED": 0},
            "gate_counts": {"NOT_EVALUATED": 0},
            "signals": {
                "accusation_terms": {"exception request": 1},
                "evidence_markers": {},
            },
            "documents": [
                {
                    "file_name": "memo-1.pdf",
                    "summary": "Versões diferentes aparecem no anexo e no corpo principal.",
                    "classification_reasons": [],
                    "gate_summary": "complianceGate=WARN",
                },
                {
                    "file_name": "memo-2.pdf",
                    "summary": "Preço a combinar e prazo indefinido até nova discussão verbal.",
                    "classification_reasons": ["sem responsável designado"],
                    "gate_summary": "traceabilityCheck=WARN",
                },
            ],
        }

        result = build_legacy_contradictions(report, [])

        self.assertEqual(
            result["items"],
            [
                "O documento apresenta trechos internamente divergentes ou incompatíveis.",
                "Foi identificada dispensa ou exceção de processo sem fundamentação formal clara.",
                "Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.",
            ],
        )

    def test_build_report_preserves_legacy_document_text_for_investigation(self) -> None:
        payload = {
            "non_accusation_set": [
                {
                    "file_name": "pedido.pdf",
                    "classification": "SUPPORTING_EVIDENCE_RELEVANT",
                    "summary": "Registro com prazo indefinido.",
                    "classification_reasons": ["conforme combinado"],
                    "overall_outcome": "PASS",
                    "text_quality": "high",
                    "extraction_status": "ok",
                    "reading_method": "direct_text",
                    "ocr_status": "not_needed",
                    "reading_confidence": "high",
                    "extractable_text_chars": 120,
                    "key_signals": {
                        "dates_found": [],
                        "currency_values_found": [],
                        "pix_mentions": 0,
                        "evidence_marker_hits": {},
                        "accusation_keyword_hits": {},
                    },
                }
            ]
        }

        report = build_report(payload)

        self.assertEqual(report["documents"][0]["summary"], "Registro com prazo indefinido.")
        self.assertEqual(report["documents"][0]["classification_reasons"], ["conforme combinado"])
        self.assertIn(
            "Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.",
            report["investigation"]["contradictions"]["items"],
        )


if __name__ == "__main__":
    unittest.main()
