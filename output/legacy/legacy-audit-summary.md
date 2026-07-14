# Resumo para primeira leitura do lote legado

## 1. O que ja da para ver
- Arquivos analisados: `4`
- Documentos que ja podem ser usados agora: `1`
- Documentos que pedem cuidado ou complemento: `1`
- Documentos que ainda nao podem ser usados agora: `1`
- Documentos que ainda nao foi possivel avaliar: `1`

## 2. Como os arquivos puderam ser lidos
- Arquivos lidos sem dificuldade relevante: `3`
- Arquivos lidos com aproveitamento parcial: `2`
- Arquivos com texto insuficiente: `1`
- Arquivos que dependeram de OCR: `1`
- Arquivos em que o OCR nao recuperou texto suficiente: `1`

## 3. O que o lote mostra
| Leitura para o cliente | Quantidade |
| --- | ---: |
| Pode indicar problema | `2` |
| Prova importante | `1` |
| Nao foi possivel ler | `1` |
- Documentos que podem indicar problema: `2`
- Documentos de apoio ou contexto: `2`

## 4. Documento por documento
| Documento | Esse documento ajuda o caso? | Pode ser usado agora? | Como foi a leitura? | Regras e origem |
| --- | --- | --- | --- | --- |
| `contract-adjustment-alpha.pdf` | Pode indicar problema | Ainda nao | Leitura direta do texto. Confianca de leitura: Media. OCR nao foi necessario. | Verificacao de regras: Ainda nao; Linguagem do documento: Sim; Verificacao da origem: Ha ressalvas |
| `supplier-review-note-beta.pdf` | Pode indicar problema | Parcialmente | Leitura por OCR. Confianca de leitura: Media. OCR ajudou a recuperar o texto. | Verificacao de regras: Sim; Linguagem do documento: Sim; Verificacao da origem: Ha ressalvas |
| `control-checklist-gamma.csv` | Sim, traz prova importante | Sim | Leitura direta do texto. Confianca de leitura: Alta. OCR nao se aplica. | Nao ha detalhe tecnico suficiente sobre regras e origem. |
| `unreadable-scan-delta.pdf` | Ainda nao foi possivel saber | Ainda nao foi possivel avaliar | OCR nao recuperou texto suficiente. Confianca de leitura: Baixa. OCR nao conseguiu recuperar o texto. | Verificacao de regras: Ainda nao foi possivel avaliar; Linguagem do documento: Ainda nao foi possivel avaliar |

## 5. Sinais que apareceram com mais forca
- Datas encontradas: 2026-06-02, 2026-06-03, 2026-06-18, 2026-06-21, 2026-06-27
- Valores monetarios encontrados: R$ 148.000,00, R$ 12.500,00
- Mencoes a Pix: `3` ocorrencia(s) em `2` documento(s)
- Marcadores de prova: checklist=6, approval id=4, evidence ref=3, approval note=1, decisionrecord=1, purchase order=1
- Termos que indicam problema: approval gap=2, exception request=1, incomplete verification=1

## 6. Pendencias e cautelas
- Preservar incerteza: `sim`
- Pedir mais documentos: `sim`
- Nota de cautela: O material atual ainda nao sustenta uma conclusao mais forte.
- Documento bloqueado nao e documento inutil. Ele apenas ainda nao sustenta um juizo mais forte.
- Documento ainda nao avaliado nao significa falha final. Significa limite de leitura ou de estrutura.

## 7. Apendice tecnico resumido
- Modo tecnico registrado: `strict-explicit-decision-record`
- Base tecnica registrada: `TCRIA legacy compliance coverage audit (sanitized example)`
- Gates com `WARN`: `2`
- Gates com `NOT_EVALUATED`: `2`
- Policy de raciocinio: `generic_reasoning_policy`

| Documento | Classificacao tecnica | Extraction status | Text quality | Metodo de leitura | OCR status | Confianca | Overall outcome | Gates principais |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `contract-adjustment-alpha.pdf` | `ACCUSATORY_CANDIDATE` | `ok` | `medium` | `direct_text` | `not_needed` | `medium` | `BLOCKED (complianceGate)` | complianceGate=BLOCKED; prescriptiveGate=PASS; traceabilityCheck=WARN |
| `supplier-review-note-beta.pdf` | `ACCUSATORY_CANDIDATE` | `ok` | `medium` | `ocr_text` | `attempted_success` | `medium` | `PARTIAL_PASS (traceability warning; static audit)` | complianceGate=PASS; prescriptiveGate=PASS; traceabilityCheck=WARN |
| `control-checklist-gamma.csv` | `SUPPORTING_EVIDENCE_RELEVANT` | `ok` | `high` | `direct_text` | `not_applicable` | `high` | `PASS` | not exposed in legacy item |
| `unreadable-scan-delta.pdf` | `UNREADABLE` | `unreadable_or_empty` | `low` | `ocr_failed` | `attempted_failed` | `low` | `NOT_EVALUATED` | complianceGate=NOT_EVALUATED; prescriptiveGate=NOT_EVALUATED |

## 8. Observacao final
Este resumo organiza o legado em linguagem de primeira leitura, mas preserva um apendice tecnico para rastreabilidade.
