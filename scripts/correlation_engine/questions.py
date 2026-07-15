from __future__ import annotations

from typing import Any


QUESTIONS = {
    "data_divergente": "Qual data deve ser considerada valida para este evento?",
    "valor_divergente": "Qual valor foi efetivamente aprovado e executado?",
    "prazo_divergente": "Qual prazo esta vigente e qual documento formalizou a mudanca?",
    "status_divergente": "Qual e a situacao atual e qual registro tem autoridade para confirma-la?",
    "responsavel_divergente": "Quem era o responsavel valido por este ato no periodo analisado?",
    "aprovacao_divergente": "A aprovacao foi concluida e onde esta a comprovacao valida?",
    "identificador_divergente": "Qual identificador pertence corretamente a esta operacao?",
    "referencia_ausente": "Onde esta o documento mencionado e ele faz parte do lote analisado?",
    "sequencia_temporal": "Por que a execucao aparece antes da aprovacao e qual data esta correta?",
    "quebra_de_padrao": "Por que este item segue um padrao diferente dos demais?",
    "procedimento_diferente": "Qual procedimento era o esperado e por que a sequencia mudou?",
}


def question_for(candidate: dict[str, Any]) -> str:
    explicit = str(candidate.get("what_to_verify") or "").strip()
    if explicit:
        return explicit
    return QUESTIONS.get(
        str(candidate.get("signal_type") or ""),
        "Qual contexto ou documento adicional explica esta diferenca?",
    )
