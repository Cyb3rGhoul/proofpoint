# ProofPrint Submission Strategy

## One-line pitch

ProofPrint turns scattered worker evidence into a private, structured, advocate-ready packet so informal workers can get help faster.

## Problem

Informal workers often do not have contracts, HR systems, or clean payroll records. When wages are withheld or unsafe work is ignored, their proof is spread across chats, payment screenshots, shift notes, voice messages, and receipts. Advocates must reconstruct the case manually before taking action.

## Solution

ProofPrint gives workers and advocates a local-first evidence organizer. It extracts dates, amounts, people, promises, harms, and risks; builds a timeline; identifies missing evidence; and drafts a complaint or NGO handoff packet.

## Why Gemma 4

Gemma 4 is valuable here because the evidence is sensitive and often messy. Local inference keeps private worker data on device. Multimodal reasoning can support screenshots, receipts, forms, and document photos. Function-style checks help turn model output into reliable structured workflow steps.

## Architecture

- Streamlit frontend for evidence intake and packet review
- Local Python analysis pipeline
- Ollama-compatible Gemma client
- Gemma-required generation path for authentic local inference
- SQLite local evidence store
- Markdown packet export
- Local rights guide used as grounded context

## Demo story

Ravi is a delivery sorting worker who was promised Rs 850 per day plus overtime. After five shifts, he received only Rs 1,500 and was warned not to complain. His evidence is scattered across chat screenshots, shift notes, UPI payment text, and a voice note. ProofPrint turns that material into a timeline, missing evidence checklist, privacy warning, and advocate packet.

## Judging fit

Impact & Vision:
ProofPrint improves access to justice for workers who cannot easily prove what happened.

Video Pitch & Storytelling:
The demo has a clear human story: scattered proof becomes usable power.

Technical Depth:
The project uses local model inference, structured extraction, privacy flags, grounded drafting, and a functional packet export workflow.

## Video outline under 3 minutes

1. 0:00-0:25 - Show the problem: scattered screenshots, payment notes, and threats.
2. 0:25-0:45 - Introduce ProofPrint as a local-first evidence kit.
3. 0:45-1:40 - Run the sample case and build the packet.
4. 1:40-2:20 - Show timeline, missing evidence, risk flags, and complaint draft.
5. 2:20-2:50 - Explain Gemma 4 architecture and privacy value.
6. 2:50-3:00 - Close with impact: clean evidence helps people reach real advocates.

## What to submit

- Kaggle writeup under 1,500 words
- YouTube video under 3 minutes
- Public GitHub repository
- Live Streamlit or Hugging Face Spaces demo
- Cover image and screenshots in Media Gallery
