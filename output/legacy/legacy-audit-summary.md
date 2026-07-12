# Resumo de Cobertura da Auditoria Legada

## 1. Visão geral do lote
- Total de arquivos escaneados: `4`
- Modo de auditoria: `strict-explicit-decision-record`
- Data de geração: `2026-07-11T16:40:00`
- Base técnica registrada: `TCRIA legacy compliance coverage audit (sanitized example)`

## 2. Cobertura da leitura
- Arquivos com `extraction_status = ok`: `3`
- Arquivos `unreadable` ou `unreadable_or_empty`: `1`
- Arquivos parcialmente aproveitáveis: `2`
- Arquivos sem texto suficiente: `1`
- Texto extraido diretamente: `2`
- Texto obtido por OCR: `1`
- OCR falhou: `1`

## 3. Classificações
| Classificação | Quantidade |
| --- | ---: |
| `ACCUSATORY_CANDIDATE` | `2` |
| `SUPPORTING_EVIDENCE_RELEVANT` | `1` |
| `UNREADABLE` | `1` |
- `accusation_set_count`: `2`
- `non_accusation_set`: `2` documento(s)

## 4. Outcomes
- `PARTIAL_PASS`: `1`
- `BLOCKED`: `1`
- `PASS`: `1`
- Gates com `WARN`: `2`
- Gates com `NOT_EVALUATED`: `2`

## 5. Mapa de documentos
| Documento | Classificação | Extraction status | Text quality | Metodo de leitura | OCR status | Confianca | Overall outcome | Gates principais |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `contract-adjustment-alpha.pdf` | `ACCUSATORY_CANDIDATE` | `ok` | `medium` | `direct_text` | `not_needed` | `medium` | `BLOCKED (complianceGate)` | complianceGate=BLOCKED; prescriptiveGate=PASS; traceabilityCheck=WARN |
| `supplier-review-note-beta.pdf` | `ACCUSATORY_CANDIDATE` | `ok` | `medium` | `ocr_text` | `attempted_success` | `medium` | `PARTIAL_PASS (traceability warning; static audit)` | complianceGate=PASS; prescriptiveGate=PASS; traceabilityCheck=WARN |
| `control-checklist-gamma.csv` | `SUPPORTING_EVIDENCE_RELEVANT` | `ok` | `high` | `direct_text` | `not_applicable` | `high` | `PASS` | not exposed in legacy item |
| `unreadable-scan-delta.pdf` | `UNREADABLE` | `unreadable_or_empty` | `low` | `ocr_failed` | `attempted_failed` | `low` | `NOT_EVALUATED` | complianceGate=NOT_EVALUATED; prescriptiveGate=NOT_EVALUATED |

## 6. Principais sinais encontrados
- Datas: 2026-06-02, 2026-06-03, 2026-06-18, 2026-06-21, 2026-06-27
- Valores monetários: R$ 148.000,00, R$ 12.500,00
- Menções a Pix: `3` ocorrência(s) em `2` documento(s)
- Marcadores de evidência: checklist=6, approval id=4, evidence ref=3, approval note=1, decisionrecord=1, purchase order=1
- Termos de acusação: approval gap=2, exception request=1, incomplete verification=1

## 7. Limitações
- `BLOCKED` não significa descarte; significa que o lote pede revisão técnica ou complemento antes de um juízo mais forte.
- `NOT_EVALUATED` não significa falha; significa que aquele gate não pôde ser concluído com o material disponível.
- `WARN` significa leitura com ressalva; o documento ainda pode carregar sinal útil para compliance e rastreabilidade.
- Documento sem `DecisionRecord` pode continuar útil em perfil exploratório ou empresarial, mesmo fora do modo estrito.

## 8. Observação final
Este resumo é uma ponte de migração do legado. Ele organiza cobertura de leitura, classificação e sinais técnicos, mas não substitui o relatório executivo principal do produto.
