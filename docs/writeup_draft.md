# ProofPrint: Local Evidence Kits for Informal Workers

## Subtitle

A private Gemma 4 app that turns scattered worker evidence into advocate-ready case packets.

## Writeup

Informal workers often lose access to justice before anyone reviews the merits of their case. Their proof may exist, but it is scattered across WhatsApp messages, payment screenshots, handwritten shift notes, receipts, voice notes, and photos. A worker may know exactly what happened, yet still struggle to answer the questions an advocate needs first: What was promised? When did the work happen? What was paid? What is missing? Is there retaliation risk? Which evidence should be protected before it is shared?

ProofPrint is a local-first Gemma 4 application for that gap. It helps informal workers, unions, worker centers, legal-aid clinics, and NGOs turn messy evidence into a structured first-review packet. The app extracts key facts from evidence fragments, builds a timeline, creates an evidence index, identifies missing proof, flags privacy and safety risks, and drafts a complaint or advocate handoff note.

The demo follows Ravi, a delivery sorting worker who was promised Rs 850 per day plus overtime. After five shifts, he received only Rs 1,500 and was warned not to complain. His evidence is fragmented across a hiring chat, shift notes, a payment transcript, follow-up messages, and a voice note. ProofPrint turns those fragments into a packet an advocate can review quickly.

Gemma 4 is central to the product because this workflow requires reasoning over sensitive, messy, real-world material. Worker evidence can contain phone numbers, payment records, health details, threats, and personal identifiers. Sending that material to a hosted model is often inappropriate. ProofPrint runs Gemma 4 locally through Ollama, keeping the evidence workflow on device while still enabling structured extraction, summarization, timeline reasoning, and grounded packet drafting.

The current prototype uses `gemma4:e2b` with Ollama on a local laptop. The Streamlit interface handles evidence intake and packet review. The Python backend calls the local Gemma model for each evidence item and requires valid structured output before building the packet. A local analysis layer then assembles the timeline, evidence table, missing-evidence checklist, risk flags, privacy notes, advocate packet, and complaint draft. SQLite is used for local evidence storage, and the final packet can be exported as Markdown.

ProofPrint intentionally avoids silent fallback generation. If the configured Gemma model is not reachable, the app refuses to generate a packet. This keeps the demo honest: the submitted workflow depends on local Gemma inference, not a hidden substitute.

The safety boundary is also explicit. ProofPrint does not provide legal advice, verify evidence authenticity, or replace a lawyer or trained advocate. It organizes evidence and prepares a structured handoff for human review. This boundary matters because the goal is not to automate justice decisions. The goal is to help people reach real help with clearer facts, less delay, and less risk of exposing private information.

The real-world impact is practical. Worker centers and legal-aid teams often spend precious intake time reconstructing timelines from screenshots and notes. ProofPrint can reduce that first-pass burden and help workers preserve the right evidence before deadlines, retaliation, or data loss make a case harder to pursue. The same pattern can extend beyond unpaid wages to unsafe work, retaliation, denied benefits, disaster-related compensation, and other situations where people have proof but no clean way to organize it.

ProofPrint shows how local frontier intelligence can serve communities where privacy, trust, and access matter most. For informal workers, clean evidence is power. ProofPrint helps turn scattered proof into something a human advocate can act on.
