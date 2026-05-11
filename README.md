---
title: ProofPrint
emoji: 📄
colorFrom: teal
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# ProofPrint

ProofPrint is a local-first evidence packet builder for informal workers and advocates. It turns scattered chats, payment notes, shift logs, voice transcripts, and receipts into a structured timeline, evidence index, missing-proof checklist, risk flags, and advocate-ready complaint draft.

The project is designed for the Gemma 4 hackathon theme: high-impact local intelligence where privacy, low connectivity, and real-world utility matter.

## Why this matters

Informal workers often lose wage, safety, retaliation, or benefit claims because their proof is scattered across screenshots, receipts, notebooks, and voice notes. Legal aid teams and NGOs spend valuable time reconstructing the facts before they can even start helping.

ProofPrint gives workers and advocates a private first step: organize the evidence, find gaps, and prepare a clean handoff packet.

## Gemma 4 role

ProofPrint is built around local Gemma-style inference through Ollama:

- extract facts from messy evidence
- classify case type
- identify dates, amounts, people, promises, harms, and sensitivity
- generate an advocate-ready packet
- support future multimodal analysis of screenshots and document photos

Packet generation requires Ollama plus a configured Gemma 4 model. The app does not silently generate packets through fallback extraction.

## Local setup

```powershell
cd "H:\pro\kaggale comp\proofprint"
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal.

## Optional Ollama setup

Install Ollama and pull the competition-approved Gemma 4 model variant when available:

```powershell
ollama pull gemma4:e2b
```

Then run the app and set the model name in the sidebar to `gemma4:e2b`.

## Demo flow

1. Click `Load sample wage-theft case`.
2. Click `Build ProofPrint packet`.
3. Show the extracted case type, timeline, evidence table, missing evidence checklist, risk flags, and complaint draft.
4. Download the advocate packet as Markdown.

## Free-tier deployment

Recommended free demo options:

- Hugging Face Spaces with Docker for the real local Ollama/Gemma path
- Streamlit Community Cloud only for a UI preview, because it does not run an Ollama sidecar
- GitHub repository for source code
- YouTube for the 3-minute video

For public deployment, use synthetic/anonymized sample evidence only.

## Hugging Face Spaces deployment

Create a new Hugging Face Space with these settings:

- SDK: Docker
- Hardware: CPU Basic
- App port: 7860

Upload or sync this repository. The Docker container installs Ollama, pulls `gemma4:e2b`, starts Ollama, and launches Streamlit.

First startup can take several minutes because the Gemma model is downloaded inside the Space.

## Hackathon tracks

Best fit:

- Digital Equity & Inclusivity
- Safety & Trust
- Main Track

Potential technology fit:

- Ollama
- llama.cpp, if packaged with a local quantized model runner

## Safety boundary

ProofPrint does not provide legal advice, verify evidence authenticity, or replace a lawyer or trained advocate. It organizes evidence and prepares a structured handoff packet for human review.
