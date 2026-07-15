from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from correlation_engine import build_correlation


class CorrelationEngineTests(unittest.TestCase):
    def test_compares_only_equivalent_keys_inside_confirmed_group(self) -> None:
        result = build_correlation(
            [
                {
                    "document_id": "A",
                    "document_name": "Contrato.pdf",
                    "group_id": "contrato-1",
                    "deadlines": {"prazo_dias": 90},
                    "values": {"valor_total": "R$ 850.000,00"},
                    "statuses": {"aprovacao": "approved"},
                },
                {
                    "document_id": "B",
                    "document_name": "Aditivo.pdf",
                    "group_id": "contrato-1",
                    "deadlines": {"prazo_dias": "120 dias"},
                    "values": {"valor_total": 850000},
                    "statuses": {"aprovacao": "aprovado"},
                },
            ]
        )

        signal_types = [signal["signal_type"] for signal in result["signals"]]
        self.assertEqual(result["groups_compared"], 1)
        self.assertIn("prazo_divergente", signal_types)
        self.assertNotIn("valor_divergente", signal_types)
        self.assertNotIn("status_divergente", signal_types)

    def test_does_not_compare_unrelated_documents_by_generic_subject(self) -> None:
        result = build_correlation(
            [
                {
                    "document_id": "A",
                    "document_name": "Fornecedor A.pdf",
                    "subject": "contrato",
                    "values": {"valor_total": 100},
                },
                {
                    "document_id": "B",
                    "document_name": "Fornecedor B.pdf",
                    "subject": "contrato",
                    "values": {"valor_total": 200},
                },
            ]
        )

        self.assertEqual(result["groups_compared"], 0)
        self.assertEqual(result["signals"], [])

    def test_detects_temporal_impossibility_and_missing_reference(self) -> None:
        result = build_correlation(
            [
                {
                    "document_id": "EXEC-1",
                    "document_name": "Execucao.pdf",
                    "group_id": "processo-1",
                    "dates": {"data_de_execucao": "10/04/2026"},
                    "required_references": ["APR-1"],
                },
                {
                    "document_id": "INDEX-1",
                    "document_name": "Indice.xlsx",
                    "group_id": "processo-1",
                    "dates": {"data_de_aprovacao": "2026-04-15"},
                },
            ]
        )

        signal_types = {signal["signal_type"] for signal in result["signals"]}
        self.assertIn("sequencia_temporal", signal_types)
        self.assertIn("referencia_ausente", signal_types)

    def test_resolves_required_reference_by_document_id(self) -> None:
        result = build_correlation(
            [
                {
                    "document_id": "CONTRACT-1",
                    "document_name": "Contrato.pdf",
                    "group_id": "processo-1",
                    "required_references": ["APR-1"],
                },
                {
                    "document_id": "APR-1",
                    "document_name": "Aprovacao.pdf",
                    "group_id": "processo-1",
                },
            ]
        )

        signal_types = {signal["signal_type"] for signal in result["signals"]}
        self.assertNotIn("referencia_ausente", signal_types)

    def test_detects_pattern_outlier_and_procedure_change(self) -> None:
        documents = []
        for index in range(1, 4):
            documents.append(
                {
                    "document_id": f"P-{index}",
                    "document_name": f"Processo {index}.pdf",
                    "pattern_group": "compras",
                    "features": {"assinatura": index < 3},
                    "process_steps": (
                        ["solicitacao", "assinatura", "aprovacao"]
                        if index == 3
                        else ["solicitacao", "aprovacao", "assinatura"]
                    ),
                }
            )

        result = build_correlation(documents)

        signal_types = {signal["signal_type"] for signal in result["signals"]}
        self.assertEqual(result["groups_compared"], 1)
        self.assertIn("quebra_de_padrao", signal_types)
        self.assertIn("procedimento_diferente", signal_types)


if __name__ == "__main__":
    unittest.main()
