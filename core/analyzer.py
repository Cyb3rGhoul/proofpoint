from __future__ import annotations

import re
from collections import Counter
from datetime import date
from typing import Any

from .llm import LocalGemmaClient, extract_json_block
from .models import CasePacket, EvidenceItem, TimelineEvent


DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)
AMOUNT_PATTERN = re.compile(r"(?:Rs\.?|INR|₹|\$)\s?[\d,]+(?:\.\d{1,2})?|\b\d{3,6}\s?(?:rupees|rs)\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d -]{8,}\d)\b")
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

CASE_TYPES = {
    "Unpaid wages": ["salary", "wage", "payment", "paid", "unpaid", "shift", "overtime", "invoice"],
    "Unsafe work": ["injury", "unsafe", "accident", "protective", "helmet", "gloves", "hazard"],
    "Harassment or retaliation": ["threat", "harass", "retaliation", "fired", "terminated", "abuse"],
    "Denied benefit": ["claim", "benefit", "denied", "rejected", "eligibility", "scheme"],
}


def classify_case(text: str) -> str:
    lowered = text.lower()
    scores = {
        case_type: sum(1 for keyword in keywords if keyword in lowered)
        for case_type, keywords in CASE_TYPES.items()
    }
    best, score = max(scores.items(), key=lambda pair: pair[1])
    return best if score else "Worker evidence packet"


def extract_entities(text: str) -> dict[str, Any]:
    dates = DATE_PATTERN.findall(text)
    amounts = AMOUNT_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    emails = EMAIL_PATTERN.findall(text)
    words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", text)
    names = [word for word, count in Counter(words).most_common(8) if word.lower() not in {"I", "The", "This"}]
    return {
        "dates": sorted(set(dates)),
        "amounts": sorted(set(amounts)),
        "contacts": sorted(set(phones + emails)),
        "possible_people_or_orgs": names,
    }


def analyze_evidence_item(item: EvidenceItem, llm: LocalGemmaClient) -> tuple[EvidenceItem, str]:
    prompt = f"""
You are ProofPrint, a local-first evidence organizer for worker advocates.
Extract only facts supported by the evidence. Return valid compact JSON only, with keys:
case_type, one_sentence_summary, dates, amounts, people_or_orgs, promises, harms, contradictions, sensitivity.
Use arrays for dates, amounts, people_or_orgs, promises, harms, and contradictions.

Evidence title: {item.title}
Evidence text:
{item.raw_text[:5000]}
"""
    response, status = llm.generate(prompt)
    if not response:
        raise RuntimeError(f"Gemma analysis failed for {item.id}: {status}")
    parsed = extract_json_block(response)
    if not parsed:
        raise RuntimeError(f"Gemma did not return valid JSON for {item.id}. Raw response: {response[:400]}")

    item.extracted = {
        "case_type": str(parsed.get("case_type") or "Worker evidence packet"),
        "one_sentence_summary": str(parsed.get("one_sentence_summary") or ""),
        "dates": ensure_list(parsed.get("dates")),
        "amounts": ensure_list(parsed.get("amounts")),
        "people_or_orgs": ensure_list(parsed.get("people_or_orgs")),
        "promises": ensure_list(parsed.get("promises")),
        "harms": ensure_list(parsed.get("harms")),
        "contradictions": ensure_list(parsed.get("contradictions")),
        "sensitivity": str(parsed.get("sensitivity") or "unknown"),
    }
    return item, status


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def summarize_text(text: str) -> str:
    clean = " ".join(text.split())
    if len(clean) <= 220:
        return clean
    return clean[:217].rsplit(" ", 1)[0] + "..."


def find_lines(text: str, keywords: list[str]) -> list[str]:
    lines = [line.strip() for line in re.split(r"[\n\r.]+", text) if line.strip()]
    matches = []
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in keywords):
            matches.append(line[:240])
    return matches[:5]


def infer_sensitivity(text: str) -> str:
    lowered = text.lower()
    if EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text):
        return "high: contains personal contact information"
    if any(word in lowered for word in ["injury", "medical", "threat", "harass"]):
        return "high: contains safety or health details"
    if AMOUNT_PATTERN.search(text):
        return "medium: contains payment details"
    return "low"


def build_packet(
    worker_name: str,
    evidence_items: list[EvidenceItem],
    llm: LocalGemmaClient,
    rights_guide: str,
) -> CasePacket:
    if not llm.available():
        raise RuntimeError(
            f"Local Gemma model '{llm.model}' is not reachable through Ollama. "
            "Start Ollama and pull the configured Gemma model before building a packet."
        )

    analyzed = []
    statuses = []
    for item in evidence_items:
        analyzed_item, status = analyze_evidence_item(item, llm)
        analyzed.append(analyzed_item)
        statuses.append(status)

    full_text = "\n\n".join(item.raw_text for item in analyzed)
    case_type = classify_case(full_text)
    timeline = build_timeline(analyzed)
    evidence_table = build_evidence_table(analyzed)
    missing = missing_evidence_for(case_type, analyzed)
    risks = risk_flags_for(analyzed)
    privacy = privacy_notes_for(analyzed)
    summary = build_case_summary(worker_name, case_type, analyzed)
    advocate_packet = build_advocate_packet(worker_name, case_type, summary, timeline, evidence_table, missing, risks, rights_guide)
    complaint_draft = build_complaint_draft(worker_name, case_type, summary, timeline, missing)

    return CasePacket(
        worker_name=worker_name or "Worker",
        case_type=case_type,
        summary=summary,
        timeline=timeline,
        evidence_table=evidence_table,
        missing_evidence=missing,
        risk_flags=risks,
        advocate_packet=advocate_packet,
        complaint_draft=complaint_draft,
        privacy_notes=privacy,
        model_status=most_relevant_status(statuses),
    )


def build_timeline(items: list[EvidenceItem]) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for item in items:
        dates = item.extracted.get("dates") or [item.created_on]
        amounts = item.extracted.get("amounts") or []
        people = item.extracted.get("people_or_orgs") or []
        summary = item.extracted.get("one_sentence_summary") or summarize_text(item.raw_text)
        for event_date in dates[:3]:
            events.append(
                TimelineEvent(
                    date=str(event_date),
                    event=summary,
                    evidence_ids=[item.id],
                    amount=", ".join(map(str, amounts[:3])),
                    people=[str(person) for person in people[:4]],
                )
            )
    return sorted(events, key=lambda event: event.date)[:12]


def build_evidence_table(items: list[EvidenceItem]) -> list[dict[str, str]]:
    rows = []
    for item in items:
        extracted = item.extracted
        rows.append(
            {
                "id": item.id,
                "title": item.title,
                "type": item.source_type,
                "key_dates": ", ".join(map(str, extracted.get("dates", [])[:4])) or "Not found",
                "amounts": ", ".join(map(str, extracted.get("amounts", [])[:4])) or "Not found",
                "summary": str(extracted.get("one_sentence_summary", "")),
                "sensitivity": str(extracted.get("sensitivity", infer_sensitivity(item.raw_text))),
            }
        )
    return rows


def missing_evidence_for(case_type: str, items: list[EvidenceItem]) -> list[str]:
    text = "\n".join(item.raw_text.lower() for item in items)
    checks = {
        "Unpaid wages": [
            ("employment terms or hiring chat", ["hired", "contract", "joining", "rate", "salary"]),
            ("work dates or shift records", ["shift", "attendance", "worked", "hours"]),
            ("payment proof or bank/UPI screenshot", ["upi", "bank", "paid", "payment", "transfer"]),
            ("final demand or employer response", ["asked", "request", "reply", "will pay", "refused"]),
        ],
        "Unsafe work": [
            ("photo or record of the hazard", ["photo", "unsafe", "hazard", "broken"]),
            ("injury or incident date", ["injury", "accident", "hurt", "hospital"]),
            ("manager notification proof", ["reported", "informed", "manager", "supervisor"]),
        ],
        "Harassment or retaliation": [
            ("original message or witness note", ["message", "witness", "threat", "abuse"]),
            ("timeline of retaliation", ["fired", "removed", "blocked", "terminated"]),
        ],
        "Denied benefit": [
            ("denial letter or rejection message", ["denied", "rejected", "not eligible"]),
            ("eligibility proof", ["eligible", "income", "identity", "document"]),
        ],
    }
    selected = checks.get(case_type, checks["Unpaid wages"])
    missing = [label for label, keywords in selected if not any(keyword in text for keyword in keywords)]
    return missing or ["No obvious missing evidence detected. Advocate should still verify authenticity and deadlines."]


def risk_flags_for(items: list[EvidenceItem]) -> list[str]:
    text = "\n".join(item.raw_text.lower() for item in items)
    flags = []
    if "threat" in text or "abuse" in text:
        flags.append("Possible retaliation or safety risk. Escalate to a trusted advocate before direct confrontation.")
    if "injury" in text or "hospital" in text:
        flags.append("Health or injury details detected. Preserve medical records and avoid public sharing.")
    if not DATE_PATTERN.search(text):
        flags.append("No clear dates found. Timeline needs stronger date evidence.")
    if not AMOUNT_PATTERN.search(text):
        flags.append("No clear money amounts found. Payment claim may need wage or invoice proof.")
    if PHONE_PATTERN.search(text) or EMAIL_PATTERN.search(text):
        flags.append("Personal contact details detected. Redact before public upload.")
    return flags or ["No major risk flags detected from the provided evidence."]


def privacy_notes_for(items: list[EvidenceItem]) -> list[str]:
    notes = [
        "Keep original evidence files unchanged.",
        "Share the generated packet only with a trusted advocate, union, NGO, or official channel.",
    ]
    if any("high" in str(item.extracted.get("sensitivity", "")) for item in items):
        notes.append("High-sensitivity evidence detected. Redact phone numbers, addresses, and health details for public demos.")
    return notes


def build_case_summary(worker_name: str, case_type: str, items: list[EvidenceItem]) -> str:
    summaries = [str(item.extracted.get("one_sentence_summary", "")) for item in items if item.extracted]
    name = worker_name or "The worker"
    return f"{name} appears to have a {case_type.lower()} matter supported by {len(items)} evidence item(s). " + " ".join(summaries[:3])


def build_advocate_packet(
    worker_name: str,
    case_type: str,
    summary: str,
    timeline: list[TimelineEvent],
    evidence_table: list[dict[str, str]],
    missing: list[str],
    risks: list[str],
    rights_guide: str,
) -> str:
    timeline_lines = "\n".join(
        f"- {event.date}: {event.event} Evidence: {', '.join(event.evidence_ids)} Amount: {event.amount or 'N/A'}"
        for event in timeline
    )
    evidence_lines = "\n".join(
        f"- {row['id']} | {row['title']} | {row['type']} | Dates: {row['key_dates']} | Amounts: {row['amounts']}"
        for row in evidence_table
    )
    missing_lines = "\n".join(f"- {item}" for item in missing)
    risk_lines = "\n".join(f"- {item}" for item in risks)
    guide_excerpt = rights_guide[:900].strip()
    return f"""# ProofPrint Advocate Packet

Generated: {date.today().isoformat()}
Worker: {worker_name or "Worker"}
Case type: {case_type}

## Plain-language summary
{summary}

## Timeline
{timeline_lines or "- No dated events found yet."}

## Evidence index
{evidence_lines}

## Missing evidence checklist
{missing_lines}

## Risk and privacy flags
{risk_lines}

## Local rights guide context
{guide_excerpt}

## Important limitation
ProofPrint organizes evidence and drafts support material. It does not provide legal advice, verify authenticity, or replace a qualified advocate.
"""


def build_complaint_draft(
    worker_name: str,
    case_type: str,
    summary: str,
    timeline: list[TimelineEvent],
    missing: list[str],
) -> str:
    timeline_text = "\n".join(f"- {event.date}: {event.event}" for event in timeline[:8])
    missing_text = "\n".join(f"- {item}" for item in missing)
    return f"""Subject: Request for assistance with {case_type.lower()}

I am requesting help reviewing a worker rights matter.

Worker: {worker_name or "Worker"}
Issue: {case_type}

Summary:
{summary}

Timeline:
{timeline_text or "- Dates are still being collected."}

Evidence still needed:
{missing_text}

I understand this draft is only an evidence organization aid and should be reviewed by a qualified advocate before submission.
"""


def most_relevant_status(statuses: list[str]) -> str:
    for status in statuses:
        if status.startswith("local Gemma"):
            return status
    return statuses[-1] if statuses else "local Gemma status unavailable"
