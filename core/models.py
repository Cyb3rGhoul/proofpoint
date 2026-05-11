from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class EvidenceItem:
    id: str
    title: str
    source_type: str
    raw_text: str
    filename: str = ""
    created_on: str = field(default_factory=lambda: date.today().isoformat())
    extracted: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEvent:
    date: str
    event: str
    evidence_ids: list[str]
    amount: str = ""
    people: list[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class CasePacket:
    worker_name: str
    case_type: str
    summary: str
    timeline: list[TimelineEvent]
    evidence_table: list[dict[str, str]]
    missing_evidence: list[str]
    risk_flags: list[str]
    advocate_packet: str
    complaint_draft: str
    privacy_notes: list[str]
    model_status: str
