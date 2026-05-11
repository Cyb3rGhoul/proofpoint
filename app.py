from __future__ import annotations

import html
import json
import sys
import uuid
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from proofprint.core.analyzer import build_packet
from proofprint.core.llm import LocalGemmaClient
from proofprint.core.models import EvidenceItem
from proofprint.core.storage import load_evidence, save_evidence


SAMPLE_CASE = ROOT / "data" / "sample_unpaid_wages_case.json"
RIGHTS_GUIDE = ROOT / "data" / "worker_rights_guide.md"


st.set_page_config(
    page_title="ProofPrint",
    page_icon="PP",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink: #121722;
          --muted: #515c6b;
          --soft: #7b8492;
          --line: #d7dde7;
          --paper: #f6f4ee;
          --panel: #ffffff;
          --panel-soft: #fbfaf6;
          --accent: #006b5f;
          --accent-dark: #00483f;
          --accent-soft: #e7f4f1;
          --blue: #263f73;
          --warn: #9a5a12;
          --risk: #9b2f3b;
          --ok: #17633e;
        }
        .stApp { background: var(--paper); color: var(--ink); }
        .block-container { padding-top: 2.6rem; padding-bottom: 3rem; max-width: 1240px; }
        header[data-testid="stHeader"] {
          background: #0c1117;
          border-bottom: 1px solid #1d2732;
        }
        h1, h2, h3, h4, h5, h6, p, label, span { letter-spacing: 0; }
        h1, h2, h3 { color: var(--ink); }
        h2, h3 { margin-top: 0.5rem; }
        section[data-testid="stSidebar"] {
          background: #ffffff;
          border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] * { color: var(--ink); }
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] p { color: var(--muted) !important; }
        div[data-testid="stTabs"] button { font-weight: 650; }
        .pp-shell {
          border: 1px solid var(--line);
          background: var(--panel);
          border-radius: 8px;
          padding: 1.45rem 1.5rem;
        }
        .pp-topbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          border: 1px solid var(--line);
          background: #ffffff;
          border-radius: 8px;
          padding: 0.8rem 0.95rem;
          margin: 0 0 1rem 0;
        }
        .pp-brand {
          display: flex;
          align-items: center;
          gap: 0.65rem;
          min-width: 0;
        }
        .pp-logo {
          width: 2.1rem;
          height: 2.1rem;
          border-radius: 7px;
          display: grid;
          place-items: center;
          background: var(--ink);
          color: #ffffff;
          font-weight: 800;
          letter-spacing: 0;
        }
        .pp-brand-title { font-weight: 760; line-height: 1.05; }
        .pp-brand-subtitle { color: var(--muted); font-size: 0.82rem; line-height: 1.15; }
        .pp-top-actions { display: flex; gap: 0.35rem; flex-wrap: wrap; justify-content: flex-end; }
        .pp-hero {
          display: grid;
          grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.78fr);
          gap: 1rem;
          align-items: stretch;
          margin-bottom: 1.15rem;
        }
        .pp-kicker {
          color: var(--accent);
          font-size: 0.82rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0;
        }
        .pp-title {
          font-size: 2.18rem;
          line-height: 1.08;
          font-weight: 760;
          margin: 0.2rem 0 0.65rem 0;
          max-width: 850px;
        }
        .pp-subtitle {
          color: var(--muted);
          max-width: 820px;
          font-size: 0.98rem;
          line-height: 1.5;
          margin-bottom: 0.85rem;
        }
        .pp-card {
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: 8px;
          padding: 1rem;
          min-height: 100%;
        }
        .pp-card-soft {
          background: var(--panel-soft);
          border: 1px solid var(--line);
          border-radius: 8px;
          padding: 1rem;
        }
        .pp-panel-dark {
          background: linear-gradient(135deg, #102720 0%, #17202d 100%);
          color: #f6fbf9;
          border: 1px solid #203a35;
          border-radius: 8px;
          padding: 1.25rem;
          min-height: 100%;
        }
        .pp-demo-title {
          margin: 0.15rem 0 0.65rem 0;
          color: #fff;
          font-size: 1.45rem;
          line-height: 1.18;
        }
        .pp-panel-dark strong { color: #ffffff; }
        .pp-panel-dark .pp-muted { color: #b7c2bf; }
        .pp-pill {
          display: inline-block;
          border: 1px solid var(--line);
          border-radius: 999px;
          padding: 0.2rem 0.58rem;
          margin: 0.1rem 0.18rem 0.1rem 0;
          color: var(--accent-dark);
          font-size: 0.82rem;
          background: var(--accent-soft);
          border-color: #b9dad3;
        }
        .pp-pill-dark {
          display: inline-block;
          border: 1px solid #344554;
          border-radius: 999px;
          padding: 0.2rem 0.58rem;
          margin: 0.12rem 0.18rem 0.12rem 0;
          color: #d7e4df;
          font-size: 0.82rem;
          background: #17232c;
        }
        .pp-step {
          display: flex;
          gap: 0.75rem;
          align-items: flex-start;
          padding: 0.75rem 0;
          border-bottom: 1px solid var(--line);
        }
        .pp-step:last-child { border-bottom: 0; }
        .pp-num {
          flex: 0 0 auto;
          width: 1.75rem;
          height: 1.75rem;
          border-radius: 50%;
          display: grid;
          place-items: center;
          color: #fff;
          background: var(--accent);
          font-weight: 760;
          font-size: 0.86rem;
        }
        .pp-step-title { font-weight: 720; color: var(--ink); }
        .pp-step-text { color: var(--muted); font-size: 0.93rem; line-height: 1.38; }
        .pp-evidence-row {
          border: 1px solid var(--line);
          border-radius: 8px;
          background: #fff;
          padding: 0.85rem 0.95rem;
          margin-bottom: 0.55rem;
        }
        .pp-evidence-head {
          display: flex;
          justify-content: space-between;
          gap: 0.75rem;
          align-items: baseline;
        }
        .pp-evidence-title { font-weight: 720; }
        .pp-muted { color: var(--muted); }
        .pp-small { color: var(--soft); font-size: 0.86rem; }
        .pp-status {
          border: 1px solid #c5d9d4;
          color: var(--ok);
          background: #f2faf6;
          border-radius: 999px;
          padding: 0.22rem 0.65rem;
          font-size: 0.82rem;
          display: inline-block;
          font-weight: 650;
        }
        .pp-counter {
          background: #ffffff;
          border: 1px solid var(--line);
          border-radius: 8px;
          padding: 0.85rem 0.95rem;
          min-height: 5.5rem;
        }
        .pp-counter-label {
          color: var(--muted);
          font-size: 0.82rem;
          font-weight: 700;
          text-transform: uppercase;
          margin-bottom: 0.35rem;
        }
        .pp-counter-value {
          color: var(--ink);
          font-size: 1.35rem;
          font-weight: 780;
          line-height: 1.15;
        }
        .pp-upload-box {
          background: #ffffff;
          border: 1px solid var(--line);
          border-radius: 8px;
          padding: 1rem;
          margin-top: 0.8rem;
        }
        .pp-risk {
          border-left: 4px solid var(--risk);
          padding: 0.5rem 0.75rem;
          background: #fff6f5;
          margin-bottom: 0.4rem;
        }
        .pp-missing {
          border-left: 4px solid var(--warn);
          padding: 0.5rem 0.75rem;
          background: #fff8ef;
          margin-bottom: 0.4rem;
        }
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stButton"] button {
          border-radius: 7px;
          font-weight: 650;
          min-height: 2.55rem;
          color: #ffffff !important;
        }
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stButton"] button * {
          color: #ffffff !important;
        }
        button,
        button p,
        button span,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stFormSubmitButton"] button p,
        [data-testid="stFormSubmitButton"] button span,
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button p,
        [data-testid="stFileUploaderDropzone"] button span {
          color: #ffffff !important;
        }
        input, textarea, select {
          background: #ffffff !important;
          color: var(--ink) !important;
          border-color: var(--line) !important;
        }
        textarea, input, select {
          border-radius: 7px !important;
        }
        textarea::placeholder, input::placeholder {
          color: #7b8492 !important;
          opacity: 1 !important;
        }
        .stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
          color: var(--ink) !important;
          font-weight: 650 !important;
        }
        @media (max-width: 900px) {
          .pp-hero { grid-template-columns: 1fr; }
          .pp-title { font-size: 1.85rem; }
          .pp-topbar { align-items: flex-start; flex-direction: column; }
          .pp-top-actions { justify-content: flex-start; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_text_file(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("latin-1")
        except UnicodeDecodeError:
            return ""


def load_rights_guide() -> str:
    return RIGHTS_GUIDE.read_text(encoding="utf-8") if RIGHTS_GUIDE.exists() else ""


def load_sample_items() -> list[EvidenceItem]:
    payload = json.loads(SAMPLE_CASE.read_text(encoding="utf-8"))
    return [
        EvidenceItem(
            id=item["id"],
            title=item["title"],
            source_type=item["source_type"],
            raw_text=item["raw_text"],
            filename=item.get("filename", ""),
            created_on=item.get("created_on", "2026-05-11"),
        )
        for item in payload["evidence"]
    ]


def init_state() -> None:
    if "evidence" not in st.session_state:
        st.session_state.evidence = load_evidence()
    if "packet" not in st.session_state:
        st.session_state.packet = None
    if "worker_name" not in st.session_state:
        st.session_state.worker_name = "Ravi Kumar"


def add_evidence(title: str, source_type: str, raw_text: str, filename: str = "") -> None:
    if not raw_text.strip():
        return
    st.session_state.evidence.append(
        EvidenceItem(
            id=f"E{len(st.session_state.evidence) + 1:03d}",
            title=title.strip() or filename or "Untitled evidence",
            source_type=source_type,
            raw_text=raw_text.strip(),
            filename=filename,
        )
    )
    save_evidence(st.session_state.evidence)


def packet_to_markdown(packet) -> str:
    timeline = "\n".join(
        f"- {event.date}: {event.event} Evidence: {', '.join(event.evidence_ids)} Amount: {event.amount or 'N/A'}"
        for event in packet.timeline
    )
    evidence_rows = "\n".join(
        f"| {row['id']} | {row['title']} | {row['type']} | {row['key_dates']} | {row['amounts']} | {row['sensitivity']} |"
        for row in packet.evidence_table
    )
    return f"""# ProofPrint Case Packet

Worker: {packet.worker_name}
Case type: {packet.case_type}
Model status: {packet.model_status}

## Summary
{packet.summary}

## Timeline
{timeline or "No timeline events extracted."}

## Evidence Table
| ID | Title | Type | Key dates | Amounts | Sensitivity |
|---|---|---|---|---|---|
{evidence_rows}

## Missing Evidence
{chr(10).join(f"- {item}" for item in packet.missing_evidence)}

## Risk Flags
{chr(10).join(f"- {item}" for item in packet.risk_flags)}

## Privacy Notes
{chr(10).join(f"- {item}" for item in packet.privacy_notes)}

## Advocate Packet
{packet.advocate_packet}

## Complaint Draft
{packet.complaint_draft}
"""


def render_header() -> None:
    st.markdown(
        """
        <div class="pp-topbar">
          <div class="pp-brand">
            <div class="pp-logo">PP</div>
            <div>
              <div class="pp-brand-title">ProofPrint</div>
              <div class="pp-brand-subtitle">Private evidence packets for worker advocates</div>
            </div>
          </div>
          <div class="pp-top-actions">
            <span class="pp-pill">Digital Equity</span>
            <span class="pp-pill">Safety & Trust</span>
            <span class="pp-pill">Ollama Track</span>
          </div>
        </div>
        <div class="pp-hero">
          <div class="pp-shell">
            <div class="pp-kicker">Local-first justice access</div>
            <div class="pp-title">ProofPrint turns scattered worker evidence into an advocate-ready packet.</div>
            <div class="pp-subtitle">
              A private Gemma 4 workflow for wage theft, unsafe work, retaliation, and denied benefits.
              It converts chats, payment notes, shift logs, and voice transcripts into a timeline,
              risk review, and human advocate handoff.
            </div>
            <span class="pp-pill">Gemma 4 local inference</span>
            <span class="pp-pill">Ollama on device</span>
            <span class="pp-pill">Evidence-grounded output</span>
            <span class="pp-pill">No fallback generation</span>
          </div>
          <div class="pp-panel-dark">
            <div class="pp-kicker" style="color:#84d7c4;">Demo case</div>
            <div class="pp-demo-title">Ravi worked five shifts. Only Rs 1,500 arrived.</div>
            <div class="pp-muted">
              Proof is split across hiring messages, shift notes, a UPI transcript, follow-up messages,
              and a voice note. ProofPrint turns it into one reviewable packet.
            </div>
            <div style="margin-top:0.8rem;">
              <span class="pp-pill-dark">unpaid wages</span>
              <span class="pp-pill-dark">retaliation risk</span>
              <span class="pp-pill-dark">privacy redaction</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ProofPrint")
        st.caption("Local Gemma evidence kit")
        st.divider()
        st.subheader("Case setup")
        st.session_state.worker_name = st.text_input("Worker name", st.session_state.worker_name)
        model = st.text_input("Local Gemma model", "gemma4:e2b")
        st.caption("Use a local Ollama Gemma model name. Packet generation is disabled unless Gemma is reachable.")

        if st.button("Load sample case", use_container_width=True):
            st.session_state.evidence = load_sample_items()
            st.session_state.packet = None
            save_evidence(st.session_state.evidence)
            st.rerun()

        if st.button("Clear evidence", use_container_width=True):
            st.session_state.evidence = []
            st.session_state.packet = None
            save_evidence([])
            st.rerun()

        st.divider()
        st.subheader("Engine")
        st.markdown(
            """
            <span class="pp-pill">Gemma extraction</span>
            <span class="pp-pill">timeline reasoning</span>
            <span class="pp-pill">risk checks</span>
            <span class="pp-pill">packet drafting</span>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.caption("For public demos, use synthetic or anonymized evidence only.")
        return model


def render_intake() -> None:
    st.markdown("### Evidence Intake")
    st.caption("Add the fragments a worker actually has: chats, payment notes, shift logs, letters, or transcripts.")
    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        st.markdown('<div class="pp-card-soft"><strong>Paste evidence manually</strong><br/><span class="pp-muted">Use this for chats, OCR text, voice transcripts, or notes copied from an image.</span></div>', unsafe_allow_html=True)
        with st.form("manual_evidence", clear_on_submit=True):
            title = st.text_input("Evidence title", placeholder="UPI payment screenshot text, shift log, employer chat...")
            source_type = st.selectbox("Source type", ["chat", "payment", "shift log", "receipt", "letter", "photo note", "other"])
            raw_text = st.text_area("Paste text or transcript", height=210, placeholder="Paste OCR text, chat transcript, voice note transcript, or notes from an image.")
            submitted = st.form_submit_button("Add evidence", use_container_width=True)
            if submitted:
                add_evidence(title, source_type, raw_text)
                st.rerun()

    with right:
        st.markdown(
            """
            <div class="pp-card-soft">
              <div class="pp-step">
                <div class="pp-num">1</div>
                <div><div class="pp-step-title">Collect proof</div><div class="pp-step-text">Bring in the messy material exactly as it exists.</div></div>
              </div>
              <div class="pp-step">
                <div class="pp-num">2</div>
                <div><div class="pp-step-title">Run Gemma locally</div><div class="pp-step-text">Extract facts without sending worker data to a hosted model.</div></div>
              </div>
              <div class="pp-step">
                <div class="pp-num">3</div>
                <div><div class="pp-step-title">Export packet</div><div class="pp-step-text">Give advocates a timeline, risk review, missing-proof list, and draft.</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="pp-upload-box"><strong>Upload text evidence</strong><br/><span class="pp-muted">Import .txt, .md, or .csv evidence files.</span></div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Choose evidence files",
            accept_multiple_files=True,
            type=["txt", "md", "csv"],
        )
        if uploaded_files:
            st.caption(f"{len(uploaded_files)} file(s) ready to import.")
            if st.button("Import uploaded files", use_container_width=True):
                for uploaded_file in uploaded_files:
                    add_evidence(uploaded_file.name, uploaded_file.type or "uploaded file", read_text_file(uploaded_file), uploaded_file.name)
                st.rerun()


def render_evidence_list() -> None:
    st.markdown("### Evidence Board")
    if not st.session_state.evidence:
        st.markdown('<div class="pp-card-soft"><strong>No evidence yet.</strong><br/><span class="pp-muted">Load the sample case from the sidebar or add evidence manually.</span></div>', unsafe_allow_html=True)
        return

    for item in st.session_state.evidence:
        preview = html.escape(item.raw_text[:180] + ("..." if len(item.raw_text) > 180 else ""))
        title = html.escape(item.title)
        source_type = html.escape(item.source_type)
        st.markdown(
            f"""
            <div class="pp-evidence-row">
              <div class="pp-evidence-head">
                <div><span class="pp-small">{item.id} / {source_type}</span><br/><span class="pp-evidence-title">{title}</span></div>
                <span class="pp-status">stored locally</span>
              </div>
              <div class="pp-muted" style="margin-top:0.45rem;">{preview}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"{item.id} - {item.title}", expanded=False):
            st.write(f"Type: `{item.source_type}`")
            st.text_area("Raw evidence", item.raw_text, height=130, key=f"raw_{item.id}", disabled=True)


def render_packet(packet) -> None:
    st.markdown("### Generated Case Packet")
    top = st.columns(4)
    counters = [
        ("Case type", packet.case_type),
        ("Evidence items", str(len(packet.evidence_table))),
        ("Timeline events", str(len(packet.timeline))),
        ("Missing checks", str(len(packet.missing_evidence))),
    ]
    for column, (label, value) in zip(top, counters):
        column.markdown(
            f"""
            <div class="pp-counter">
              <div class="pp-counter-label">{html.escape(label)}</div>
              <div class="pp-counter-value">{html.escape(value)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(f'<span class="pp-status">{packet.model_status}</span>', unsafe_allow_html=True)

    st.markdown(f'<div class="pp-card-soft"><strong>Case summary</strong><br/><span class="pp-muted">{html.escape(packet.summary)}</span></div>', unsafe_allow_html=True)

    timeline_tab, evidence_tab, risks_tab, packet_tab, draft_tab = st.tabs(
        ["Timeline", "Evidence", "Risk checks", "Advocate packet", "Complaint draft"]
    )

    with timeline_tab:
        for event in packet.timeline:
            event_text = html.escape(event.event)
            event_date = html.escape(str(event.date))
            event_amount = html.escape(event.amount or "N/A")
            evidence_ids = html.escape(", ".join(event.evidence_ids))
            st.markdown(
                f"""
                <div class="pp-card">
                  <span class="pp-small">{event_date}</span><br/>
                  <strong>{event_text}</strong><br/>
                  <span class="pp-pill">Evidence: {evidence_ids}</span>
                  <span class="pp-pill">Amount: {event_amount}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with evidence_tab:
        st.dataframe(packet.evidence_table, use_container_width=True, hide_index=True)

    with risks_tab:
        st.markdown("##### Missing evidence")
        for item in packet.missing_evidence:
            st.markdown(f'<div class="pp-missing">{item}</div>', unsafe_allow_html=True)
        st.markdown("##### Risk and privacy flags")
        for item in packet.risk_flags:
            st.markdown(f'<div class="pp-risk">{item}</div>', unsafe_allow_html=True)
        st.markdown("##### Privacy notes")
        for item in packet.privacy_notes:
            st.write(f"- {item}")

    with packet_tab:
        st.markdown(packet.advocate_packet)

    with draft_tab:
        st.text_area("Draft", packet.complaint_draft, height=340)

    markdown = packet_to_markdown(packet)
    st.download_button(
        "Download advocate packet",
        data=markdown,
        file_name=f"proofprint_packet_{uuid.uuid4().hex[:8]}.md",
        mime="text/markdown",
        use_container_width=True,
    )


def main() -> None:
    apply_theme()
    init_state()
    model_name = render_sidebar()
    render_header()

    stats = st.columns(3)
    stats[0].markdown('<div class="pp-card"><div class="pp-kicker">Problem</div><strong>Scattered proof blocks justice.</strong><br/><span class="pp-muted">Workers often have evidence, but not a usable case packet.</span></div>', unsafe_allow_html=True)
    stats[1].markdown('<div class="pp-card"><div class="pp-kicker">Gemma 4</div><strong>Private local reasoning.</strong><br/><span class="pp-muted">Facts are extracted on device through Ollama and Gemma 4 E2B.</span></div>', unsafe_allow_html=True)
    stats[2].markdown('<div class="pp-card"><div class="pp-kicker">Output</div><strong>Advocate-ready handoff.</strong><br/><span class="pp-muted">Timeline, evidence index, missing proof, risk flags, and draft.</span></div>', unsafe_allow_html=True)

    st.divider()
    render_intake()
    render_evidence_list()

    st.divider()
    can_generate = bool(st.session_state.evidence)
    st.markdown("### Packet Builder")
    st.caption("This step calls the local Gemma model. On your laptop, the sample case can take a few minutes.")
    if st.button("Build advocate packet with Gemma", type="primary", disabled=not can_generate, use_container_width=True):
        llm = LocalGemmaClient(model=model_name)
        try:
            st.session_state.packet = build_packet(
                worker_name=st.session_state.worker_name,
                evidence_items=st.session_state.evidence,
                llm=llm,
                rights_guide=load_rights_guide(),
            )
            save_evidence(st.session_state.evidence)
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))

    if st.session_state.packet:
        render_packet(st.session_state.packet)


if __name__ == "__main__":
    main()
