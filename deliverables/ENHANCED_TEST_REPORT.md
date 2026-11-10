# Enhanced release verification

Verification date: 10 November 2026. Local Windows Python 3.12 application, SQLite and Chrome. All test and demonstration material is fictional. Credentials are kept only in the private local configuration, never included in this report or release archives.

## Automated backend checks

34 cases passed, with no failed cases. Machine-readable results: `enhanced-test-results.xml`. The suite covers authentication and ownership, basic workflows, repeated additive migrations, a preserved copy of the original local database, conversation context capped at ten turns, private conversation histories, interest preferences, semester-plan duplicates/prerequisites/credit limits, facility filters, booking alternatives, atomic concurrent modifications, cancellation reasons, work logs/costs and persistent energy filters.

Upload cases cover UTF-8 TXT, a generated text-based PDF, scan-only pages, more than 20 pages, encryption, bad signatures, unsupported extensions, empty files, excessive size and binary text. Other cases cover AI candidate evidence, invalid structured output, stale in-flight reviews, immutable versions, correction requests, notifications, resubmission and decisions. Old expectations that reviews disappear after an edit were replaced by outdated-version assertions.

The original database migration test compares account password hashes and original row counts without displaying them, then applies the migration again to check idempotence. The test uses a copy of the backup rather than modifying the live database. That case skips on distributed installations without the original local backup. `pip check` found no broken dependency requirements. One Starlette TestClient deprecation warning remains and did not affect the results.

## Browser verification

The final `enhanced-browser-results.json` reports zero unexpected page or console errors. The browser completed saved conversations and refresh persistence, an interest-based saved plan, room search/conflict alternatives/modification, confirmed AI fault classification, local TXT upload with AI field candidates, versioned pre-reviews, return/notify/revise/resubmit/approve, repair logs and expenses, room/date energy filters, and a 390px mobile layout check.

An actual browser recording is available as `SmartCampus-enhanced-demo.webm`. It is silent and faster than a spoken classroom demonstration. The recording preserves actual result modes, including any rule-only fallback. It is not a claim that every AI call always succeeds. Full-page captures and additional focused captures are available under `enhanced-screenshots`.

During verification, an AI-suggestion confirmation button was found to submit its surrounding fault form unintentionally. It now explicitly uses button type, keeping suggestion application separate from final submission. The final browser run confirms the corrected workflow.

## Real AI checks, separate from mocks

- Conversation: actual DeepSeek answers included retrieved source IDs, including a follow-up question.
- Fault classification: actual structured category and priority suggestions appeared; applying them required a user action, followed by separate form confirmation.
- Field extraction: actual candidates included source excerpts, with explicit selection/application controls.
- Structured pre-review: a separate HTTP request returned `live_ai`, rule and AI checks, and an explanation of a mismatched fictional student ID. Some recorded requests fell back to rules when no valid structured/evidence-supported result was available; the UI keeps that limitation visible.

These checks establish working sample operations, not comprehensive model accuracy or perfect detection. AI network calls retain a timeout; invalid structured results do not replace deterministic validation or human decisions.

## Presentation and remaining checks

The enhanced deck retains thirteen slides and 720 seconds of planned speaking time, six speakers at 120 seconds each. Earlier decks and reports remain historical versions. Package, font, geometry and re-import checks accompany the deck build; rendered pages are visually reviewed before handoff. Actual spoken timing, PowerPoint rendering, classroom equipment and installation on a second physical computer still require team rehearsal.

The enhanced database is backed up locally before migration. The private `.env`, database/backup files, virtual environment, caches and intermediate recordings are excluded from distribution. Trained prediction models, real devices, OCR, mail delivery and per-staff workload assignment remain outside this release.
