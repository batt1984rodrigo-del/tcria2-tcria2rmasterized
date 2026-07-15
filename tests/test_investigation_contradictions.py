from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from investigation_engine.contradictions import build_legacy_contradictions, build_report_contradictions


class InvestigationContradictionsTests(unittest.TestCase):
    def test_build_report_contradictions_preserves_existing_messages(self) -> None:
        result = build_report_contradictions(
            {
                "findings": [
                    {
                        "title": "Pending approval",
                        "what_identified": "pending",
                        "why_matters": "urgency without closing",
                        "supporting_evidence": ["authorization is missing", "approved without source documents", "only by email"],
                    }
                ]
            },
            [],
        )

        self.assertEqual(
            result["items"],
            [
                "Existe registro marcado como pendente onde deveria haver fechamento documental.",
                "A urgencia aparece no material, mas a autorizacao final nao aparece nas provas reunidas.",
                "Algo aparece como aprovado, mas a prova que sustentaria essa aprovacao segue incompleta.",
                "Parte do que deveria estar formalizado aparece apenas em e-mail.",
            ],
        )

    def test_build_report_contradictions_detects_all_new_groups(self) -> None:
        result = build_report_contradictions(
            {
                "findings": [
                    {
                        "title": "Conflicting versions",
                        "what_identified": "The clause is inconsistent and presents versões diferentes.",
                    },
                    {
                        "title": "Exception handling",
                        "what_identified": "This exception request allowed contratação direta by bypass.",
                    },
                    {
                        "title": "Open commercial definition",
                        "what_identified": "Delivery remains a definir with prazo indefinido and best effort execution.",
                    },
                    {
                        "title": "Procurement red flags",
                        "what_identified": "The batch cites único fornecedor, bid rigging and kickback risk.",
                    },
                    {
                        "title": "Liability waiver",
                        "what_identified": "The supplier isento de responsabilidade under a hold harmless clause.",
                    },
                    {
                        "title": "Formal irregularity",
                        "what_identified": "The file appears falsified with assinatura divergente and retroactive date.",
                    },
                    {
                        "title": "Repeated inconsistency",
                        "what_identified": "Another discrepancy appears in the annex.",
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

    def test_build_legacy_contradictions_uses_available_textual_legacy_signals(self) -> None:
        result = build_legacy_contradictions(
            {
                "coverage": {},
                "document_outcomes": {},
                "gate_counts": {"WARN": 1},
                "classification_counts": {"ACCUSATORY_CANDIDATE": 1},
                "signals": {
                    "accusation_terms": {
                        "exception request": 1,
                        "a definir": 1,
                    }
                },
                "documents": [
                    {
                        "gate_summary": "traceabilityCheck=WARN",
                        "summary": "Documento com divergence e mismatch internos.",
                        "classification_reasons": ["Prazo indefinido no aditivo."],
                    }
                ],
            },
            [],
        )

        self.assertEqual(
            result["items"],
            [
                "O documento apresenta trechos internamente divergentes ou incompatíveis.",
                "Foi identificada dispensa ou exceção de processo sem fundamentação formal clara.",
                "Partes do documento usam linguagem vaga onde deveriam existir valores ou prazos definidos.",
            ],
        )

    def test_build_legacy_contradictions_does_not_force_new_checks_without_text(self) -> None:
        result = build_legacy_contradictions(
            {
                "coverage": {},
                "document_outcomes": {},
                "gate_counts": {"WARN": 1},
                "classification_counts": {"ACCUSATORY_CANDIDATE": 2},
                "signals": {"accusation_terms": {}},
                "documents": [{"gate_summary": ""}],
            },
            [{"status": "em aberto"}],
        )

        self.assertEqual(
            result["items"],
            ["A leitura atual ainda mistura material util com limites que impedem fechamento completo."],
        )


if __name__ == "__main__":
    unittest.main()
