from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    document: str
    observation: str


class TcriaAnalysis(BaseModel):
    recommended_decision: Literal[
        "PROCEED",
        "PROCEED_WITH_CONDITIONS",
        "HOLD_FOR_REVIEW",
        "DO_NOT_PROCEED_YET",
    ]
    rationale: str
    confirmed_facts: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    verification_signals: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    human_validation_required: list[str] = Field(default_factory=list)


class AnalysisStatus(BaseModel):
    analysis_id: str
    state: Literal["queued", "processing", "completed", "failed"]
    stage: str
    progress: int = Field(ge=0, le=100)
    question: str
    accepted_files: list[str]
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
