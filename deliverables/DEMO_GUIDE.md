# SmartCampus rehearsal guide

Presentation date: 12 November 2026. Language: English. Target: 10 minutes. All data and campus policies are fictional. The fallback video has no live AI results and no narration.

## Before the session

1. Run setup on the presentation computer and on a teammate's computer. Only the current machine has been checked during implementation.
2. Stop the server and reset the demo database if you want clean state. Start it again, sign in, check that every page opens.
3. Configure the DeepSeek key privately and verify both AI modules return `live_ai`. Keep the API key out of the projected screen.
4. Open the deck and fallback video. Practice switching between them and the browser. Confirm the room's display size and audio/video compatibility.
5. Assign one operator. Each member explains their assigned module; do not claim sole authorship of generated starter code. Each member must review and understand their module.

## 3.5-minute demonstration

**Learning, 45 seconds.** Sign in as `student`. Open Study assistant. Ask “What are the prerequisites for CS202?” Point to the source excerpt and response mode. Open Learning path. Explain that CS202 is not suggested until CS102 has been passed, and MA101 triggers support due to low mark/attendance. Do not call these rules a trained model.

**Facilities, 70 seconds.** Open Spaces & bookings. Use the default next-day 10:00–11:00 slot and confirm. Submit again to show conflict rejection. Report “Demo projector has a flickering image.” Sign out and sign in as `maintenance`. Open Energy & maintenance, find the new report, start work, then complete it with a cost of 35. Explain that the energy readings are simulated.

**Applications, 95 seconds.** Sign in as `student`. Open Document pre-review. The sample text says S9999 while the signed-in student's ID is S1001. Save and pre-review. Point out deterministic findings separately from the AI explanation. Correct the material to “My student ID is S1001. Please provide my transcript for an internship.” Save and review again. Open the service portal and submit. Sign in as `admin`, add a decision explanation and approve that application. Return to `student`, open the portal and show the status and decision note.

## Recovery during the presentation

- If a model request takes too long, explain the visible fallback after its 30-second timeout and continue the business workflow. The offline mode is a designed limitation, not a successful AI demonstration.
- If a room conflicts with existing data, choose another room or time. Never reset in the middle of the presentation.
- If a role is denied, check the username in the header. Staff actions require the correct staff account.
- If the server or display fails, play `SmartCampus-demo-offline.webm`. It records real browser interactions with deterministic checks and clearly labelled AI unavailability.

## Team checklist for the remaining two days

H0–H3: review the scaffold, configure GitHub and verify DeepSeek. H3–H12: each owner reviews and extends their module. H12–H18: merge and repeat the three workflows. H18–H24: rehearse using the English deck. H24–H34: run tests and second-machine setup. H34–H40: freeze features and record a live-AI demonstration if configured. H40–H48: repair only blockers and rehearse to ten minutes.
