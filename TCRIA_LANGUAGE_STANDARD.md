# TCRIA Language Standard

This document defines the mandatory language standard for every TCRIA output intended for client reading.

It is not a translation glossary only.

It defines a change of philosophy:

- TCRIA must not speak like an engine when addressing a client.
- TCRIA must not expose internal field names as if they were explanations.
- TCRIA must explain what matters, what is missing, what can be used now, and what should happen next.

This standard applies to:

- PDF outputs;
- Markdown outputs;
- HTML outputs;
- timeline summaries;
- case preparation summaries;
- blocked document reviews;
- any other delivery intended for a non-technical reader.

This standard does not forbid technical JSON.

Technical JSON may remain detailed and machine-oriented.

The rule is:

- technical JSON is a source artifact;
- client-facing output is a translated explanation artifact.

## Core Principle

Client output must feel like a careful conversation, not like an API dump.

The reader should quickly understand:

- what this document or batch is;
- whether it helps the case;
- whether it can be used now;
- what is still missing;
- what risk or limitation exists;
- what should be done next.

If the reader cannot answer those questions within a few seconds, the output has failed its language goal.

## Golden Rule

TCRIA must describe the case in the language of first reading.

That means:

- less engine terminology;
- less classification jargon;
- less gate/status language;
- more direct questions and answers;
- more plain language;
- more explanation of practical consequence.

## Layer Separation

TCRIA has two valid language layers.

### 1. Technical Source Layer

This layer may keep fields such as:

- `classification`
- `artifact_type`
- `overall_outcome`
- `complianceGate`
- `traceabilityCheck`
- `traceability_status`
- `timeline_confidence`
- `blocked_artifacts_review`

This layer is for:

- runtime logic;
- compatibility;
- internal traceability;
- debugging;
- auditability;
- structured integrations.

### 2. Client-Facing Language Layer

This layer must translate technical structure into natural language.

This layer is for:

- reports;
- client summaries;
- lawyer-facing reading material;
- first-pass human understanding;
- operational next steps.

Client-facing output must never assume the reader knows the technical source layer.

## Required Questions

Whenever TCRIA presents a document, finding, blocked item, timeline item, or case summary, it should prefer questions like these:

- What is this document?
- Does this document help the case?
- Can it be used now?
- Is anything missing?
- Is there any relevant risk?
- What should be done next?

Whenever possible, the answer should be explicit and short.

Examples:

- `Can it be used now?` `Not yet.`
- `Does this document help the case?` `Yes, but it needs better organization.`
- `Is anything missing?` `Yes. The document lacks clear responsibility and purpose metadata.`

## Forbidden Client-Facing Patterns

Client-facing output must not expose the following as primary reading language:

- raw enum names such as `ACCUSATORY_CANDIDATE`;
- raw gate names such as `complianceGate`;
- raw engine structures such as `blockedArtifactReview`;
- booleans such as `True` and `False`;
- internal status words such as `PASS`, `WARN`, `BLOCKED`, `NOT_EVALUATED`;
- mixed Portuguese-English labels like `Identity`, `decision_artifact`, or `recommended_action`;
- titles that require prior knowledge of TCRIA internals.

These may still exist in technical appendices or source JSON when necessary.

They must not be the main language of client understanding.

## Canonical Vocabulary

The following translations are the preferred client-facing standard.

| Technical term | Client-facing standard | Usage note |
| --- | --- | --- |
| `ACCUSATORY_CANDIDATE` | `Pode indicar problema` | Use only when the document suggests a relevant issue but is not a final conclusion. |
| `SUPPORTING_EVIDENCE_RELEVANT` | `Prova importante` | Prefer when the document materially supports the case. |
| `SUPPORTING_EVIDENCE` | `Prova` | Simple preferred term. |
| `SUPPORTING_PROOF` | `Comprovação` | Use when the document confirms a fact or support point. |
| `EVIDENTIARY_SUPPORT_GENERAL` | `Outras provas` | Use for supporting material that is helpful but not central. |
| `artifact_type` | `Tipo de documento` | Never show `artifact` to the client. |
| `artifact_identity` | `Identificação do documento` | Use only when document identity matters operationally. |
| `classification` | `Resultado da análise` | Avoid using `classificação` by itself if a question-based wording is clearer. |
| `classification_reasons` | `Por que chegamos a esse resultado` | Prefer explanation over technical causality language. |
| `artifact_type_reason` | `Por que foi classificado assim` | Use only when useful for human review. |
| `complianceGate` | `Verificação de regras` | Do not surface the gate name raw. |
| `traceabilityCheck` | `Verificação da origem` | Better than `checagem de rastreabilidade`. |
| `traceability_status` | `Origem confirmada?` | Prefer question form. |
| `traceability_gap_reason` | `O que faltou para confirmar melhor a origem` | Prefer gap explanation. |
| `accountability_support_hits` | `Referências a responsáveis identificados` | Avoid raw `accountability`. |
| `confidence` | `Quanto confiamos nesta análise` | Better than `confidence`. |
| `timeline_confidence` | `Confiança na linha do tempo` | Keep the context explicit. |
| `blocked_artifacts_review` | `Documentos com pendências` | Better than `artefatos bloqueados`. |
| `blockedArtifactReview` | `Detalhes da pendência` | Use plain language. |
| `blocked_reason` | `Motivo da pendência` | Must be explained without gate jargon. |
| `overall_outcome` | `Pode ser usado agora?` | Prefer question form. |
| `official_outcome` | `Situação oficial atual` | Use only when official status matters. |
| `case_readiness` | `O caso está pronto para avançar?` | Must be answered directly. |
| `top_evidence_files` | `Documentos que mais ajudam` | More natural than `top evidence files`. |
| `top_narrative_files` | `Documentos que melhor explicam o caso` | Focus on usefulness. |
| `blocked_but_relevant` | `Documentos úteis, mas com pendências` | Very important category for human review. |
| `governance_gaps` | `Lacunas de organização` | Prefer everyday language. |
| `timeline_candidates` | `Documentos que ajudam a montar a linha do tempo` | Plain explanation. |
| `recommended_next_actions` | `Próximos passos` | Use action language. |

## Canonical Answer Conversions

The following status conversions are mandatory in client-facing output.

| Technical value | Client-facing answer |
| --- | --- |
| `PASS` | `Sim` or `Está adequado` |
| `WARN` | `Parcialmente` or `Há ressalvas` |
| `BLOCKED` | `Ainda não` or `Não pode ser usado agora` |
| `NOT_EVALUATED` | `Ainda não foi possível avaliar` |
| `NOT_APPLICABLE` | `Não se aplica` |
| `True` | `Sim` |
| `False` | `Não` |
| `mixed` | `Ajuda em parte, mas exige cuidado` |
| `high` | `Alta` |
| `medium` | `Média` |
| `low` | `Baixa` |

## Family-Specific Output Rules

### Strict Audit Outputs

Strict audit outputs may keep machine detail internally, but client presentation should prefer:

- `Que tipo de documento é este?`
- `Esse documento ajuda o caso?`
- `Pode ser usado agora?`
- `O que impediu o uso imediato?`
- `O que fazer agora?`

Client-facing output must not show raw phrases such as:

- `ACCUSATORY_CANDIDATE`
- `NEUTRAL_OR_CONTEXT`
- `SUPPORTING_EVIDENCE_RELEVANT`
- `CIVIL_CRIMINAL_INVESTIGATIVE`

unless they are moved to a technical appendix and clearly labeled as internal vocabulary.

### Blocked Artifacts Review

Blocked review is the area with the highest risk of engine leakage.

The preferred presentation pattern is:

1. `Documento`
2. `Pode ser usado agora?`
3. `O que impediu o uso?`
4. `Ele ainda ajuda o caso?`
5. `O que está faltando?`
6. `O que fazer agora?`

Example conversion:

- raw: `official_outcome = BLOCKED (complianceGate)`
- client-facing: `Pode ser usado agora? Ainda não.`

- raw: `blocked_reason = DecisionRecord header not found in strict mode.`
- client-facing: `O que impediu o uso? Falta registro claro de responsabilidade e objetivo do documento.`

- raw: `recommended_action = Add explicit DecisionRecord metadata...`
- client-facing: `O que fazer agora? Informar quem assumiu o documento, qual é o objetivo dele e anexar referências rastreáveis.`

### Timeline Outputs

Timeline outputs should not read like scoreboards.

They should answer:

- `Esse documento ajuda a montar a linha do tempo?`
- `Com que nível de confiança?`
- `Quais datas ou marcos ele oferece?`
- `A origem está bem sustentada?`

Avoid exposing raw labels such as:

- `timeline_signal_score`
- `date_anchors_hint`
- `target_entity_hits`

These may inform ranking internally, but should not dominate the visible narrative.

### Case Preparation Summary

Case preparation outputs should feel like strategic briefing, not system state.

They should answer:

- `O caso está pronto para avançar?`
- `Quais documentos mais ajudam?`
- `Quais documentos explicam melhor a história?`
- `Quais documentos ainda têm pendências?`
- `Quais lacunas de organização precisam ser resolvidas?`
- `Quais são os próximos passos?`

Avoid raw expressions such as:

- `case_readiness = low`
- `top_evidence_files`
- `blocked_but_relevant`
- `governance_gaps`

These should be translated into direct briefing language.

## Client Of First Use Filter

Every client-facing PDF or report must pass the `Cliente de primeira viagem` filter.

The rule is simple:

- if a person who has never heard of TCRIA cannot understand the title in five seconds, the title must be rewritten;
- if the opening section does not immediately explain what was reviewed and what matters, the opening section must be rewritten;
- if internal vocabulary appears where a plain-language phrase would work, the plain-language phrase must replace it;
- if the reader cannot tell what to do next, the output is incomplete.

## Title Standard

Client-facing titles should prefer:

- concrete scope;
- practical consequence;
- plain language;
- readable phrasing.

Avoid:

- internal route names;
- raw gate names;
- overly abstract labels;
- titles that sound like middleware outputs.

Bad examples:

- `Blocked Artifacts Review`
- `Strict Audit Coverage`
- `ComplianceGate Summary`

Better examples:

- `Documentos com pendências que ainda ajudam o caso`
- `O que já pode ser usado e o que ainda precisa de ajuste`
- `Resumo da análise documental para primeira leitura`

## Tone Standard

The tone of client-facing output must be:

- clear;
- calm;
- prudent;
- practical;
- direct;
- understandable without prior TCRIA knowledge.

It must not be:

- theatrical;
- over-technical;
- accusatory without context;
- engine-like;
- cold to the point of obscurity.

## Uncertainty Standard

Plain language does not allow false certainty.

When the system is uncertain, it must say so clearly.

Preferred examples:

- `Ainda não foi possível confirmar.`
- `O documento ajuda, mas ainda não sustenta uma conclusão sozinho.`
- `Há indícios úteis, mas faltam elementos de organização e origem.`

Avoid:

- raw `WARN`
- raw `NOT_EVALUATED`
- vague phrases with no practical meaning.

## Technical Appendix Rule

When detailed machine language is needed for traceability, it must be moved to a clearly labeled technical appendix.

The main reading flow must remain human-first.

That means:

- the main body explains;
- the appendix proves;
- the source JSON preserves machine detail.

## Implementation Guidance

Any runtime layer that renders client-facing output should:

- translate internal field names before display;
- convert status enums into direct human answers;
- replace booleans with plain-language responses;
- prefer question-and-answer blocks over raw field dumps;
- rewrite recommendations into action language;
- fail validation when a client-facing title still sounds like an engine title.

## Design Intent

The purpose of this standard is not to make TCRIA softer.

The purpose is to make TCRIA more understandable, more commercially legible, and more useful on first reading.

TCRIA should continue to preserve rigor, traceability, and caution.

It should simply express them in a language that a client can understand without learning the engine first.
