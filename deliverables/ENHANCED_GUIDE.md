# Enhanced system demonstration

Use `SmartCampus-enhanced-presentation.pptx` and `SPEAKER_NOTES_ENHANCED.md`. Each person has two minutes including any clicks. The cover adds no speaking time. Class presentation: 12 November 2026. Group leader submits to Moodle by 23:59 on 13 November. Earlier decks and reports remain historical versions.

## One new workflow per person

- Rongkai: start a conversation, ask about CS202, ask a follow-up, expand a source, refresh and reopen history. A booking or transcript question also offers a service shortcut without executing it.
- Dequn: set interest to AI, save the goal, open a named semester and add CS102. Show the 3/12 credit total and the explanation. Recommendations, reminders and the credit cap are demonstration rules.
- Jun: filter by projector and time, reserve a room, attempt a conflict, choose an alternative or modify a booking. Cancellation keeps a reason. The daily timetable uses UTC dates while timestamps display in the browser's local time.
- Lexi: filter the work queue, set a priority/ETA, move an open ticket to in progress, add a log with an expense and complete it. Show a room/date energy filter and explain that the stored readings are synthetic.
- Zheyuan: upload `sample-materials/conflicting-application.txt`. Text extraction is local. Request AI field suggestions, inspect evidence and explicitly apply only selected values. Save and pre-review; correct S9999 to S1001, save again and compare versions. Historical reviews remain labelled outdated. TXT and text-based PDF only; 5MB, 20 PDF pages and 60,000 extracted characters maximum. Scanned, encrypted or unreadable PDFs are rejected.
- Shiran: submit the application, return it as admin with a correction explanation, inspect the student notification, revise and resubmit, approve as admin and open the student's timeline. For the timed talk, use the captured screenshots rather than performing every role switch live.

## Before rehearsal

Run setup again to install the added PDF and multipart dependencies. Starting the enhanced server performs an additive schema upgrade automatically. Existing data and the private `.env` are preserved. The local pre-upgrade backup is under `data` and is not distributed. Do not reset the database when upgrading. Reset remains an explicit destructive demo-data operation.

Use the real AI mode label shown by each operation. A successful call confirms only that sample's operation, not general model accuracy. If an AI call fails or its structured output cannot be validated, manual fields/classification and deterministic checks remain available.

Refresh the portal to load updated notifications. A notification is an in-app record, not an email. A returned application must first be saved as a draft revision before resubmission. Editing a material or field creates a new version only if content actually changes, except that returning to draft after staff feedback creates a revision even when the content is unchanged.

Current live-AI checks are recorded separately from automated mock tests. Review `ENHANCED_TEST_REPORT.md` for the final status. Repeat installation on another physical computer and rehearse with PowerPoint/classroom display before presenting.
