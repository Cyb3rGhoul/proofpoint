# ProofPrint Kaggle Submission Checklist

## Done locally

- Working app prototype: Streamlit app in `proofprint/app.py`
- Local Gemma 4 inference: `gemma4:e2b` through Ollama
- No fallback packet generation: app requires the configured Gemma model
- Sample case: unpaid-wages worker evidence in `data/sample_unpaid_wages_case.json`
- Evidence workflow: manual intake, text upload, local storage, packet builder
- Generated outputs: timeline, evidence table, missing-evidence checks, risk flags, advocate packet, complaint draft
- Project docs: `README.md`, `docs/writeup_draft.md`, `docs/submission_strategy.md`

## Still needed before Kaggle submission

- Public code repository
- Public live demo URL
- YouTube video under 3 minutes
- Kaggle writeup under 1,500 words
- Media Gallery cover image and screenshots
- Final Kaggle Writeup submission before the deadline

## Recommended track choices

- Primary: Digital Equity & Inclusivity
- Secondary: Safety & Trust
- Special Technology Track: Ollama

## Public repository checklist

- Create a GitHub repository named `proofprint`
- Push the `proofprint` folder contents
- Include clear setup instructions from `README.md`
- Do not commit real private evidence
- Keep the sample case synthetic

## Live demo checklist

Recommended free option:

- Hugging Face Spaces with Docker

Use these settings:

- SDK: Docker
- Hardware: CPU Basic
- Port: 7860
- Repository contents: this `proofprint` project

The Space may take several minutes to start because it pulls `gemma4:e2b`. If the free CPU tier is too slow during judging, keep the local Gemma run visible in the video and describe the hosted demo constraints clearly.

## Video checklist

Keep it under 3 minutes:

1. Show the problem: scattered proof from an informal worker.
2. Open ProofPrint and load the sample case.
3. Build the packet using `gemma4:e2b`.
4. Show timeline, evidence index, missing proof, risk flags, and complaint draft.
5. Explain local privacy: worker evidence stays on device.
6. End with impact: advocates get a clean packet faster.

## Kaggle writeup checklist

Include:

- Problem and target users
- Why Gemma 4 is central
- Architecture
- Local-first/privacy explanation
- Demo workflow
- Limitations and safety boundary
- Links to GitHub, video, and live demo

Keep the writeup under 1,500 words.
