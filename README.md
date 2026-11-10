# SmartCampus working prototype

CSIT883, GlobalConnect University (fictional). Six connected modules for a progress presentation on 12 November 2026. All accounts, campus policies and records are synthetic.

## Run on Windows

Install Python 3.12 and Git. In PowerShell, open this directory and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\start.cmd
```

Open http://127.0.0.1:8000. Keep the server window open. Stop with Ctrl+C. Setup requires internet to download packages. Subsequent basic workflows run locally without internet. Python dependencies live in `.venv`, not your global environment.

| Username | Role | Password |
| --- | --- | --- |
| student | Alex Morgan, S1001 | Campus2026! |
| student2 | Jamie Chen, S1002 | Campus2026! |
| admin | Administrative staff | Campus2026! |
| maintenance | Maintenance staff | Campus2026! |

These public demo passwords are for local synthetic data only. The launcher binds to 127.0.0.1.

## Enable DeepSeek

Setup copies `.env.example` to `.env` if the file does not already exist. Set `DEEPSEEK_API_KEY` in `.env` locally, keep `DEEPSEEK_BASE_URL=https://api.deepseek.com`, and set a model available to your account (`deepseek-flash` is the default). Restart the server after editing. Never paste keys into GitHub, slides or screenshots.

1. Sign in as `student`, open Study assistant, ask “What are the prerequisites for CS202?”
2. Confirm `live_ai`, an answer citing `[K02]`, and actual retrieved source excerpts.
3. Open Document pre-review. Run the sample mismatched-ID application. Confirm `live_ai`, field findings and model commentary.
4. If `retrieval_only` or `rules_only` appears, AI is unavailable or output validation failed. Check your key, balance, model and network locally. The UI never substitutes a canned answer for a live call.

The 30-second adapter handles network, authentication and malformed-response failures. A response with no valid source citation falls back to excerpts. Saved conversations supply at most ten previous turns as context; each new turn retrieves fresh evidence. Structured AI operations validate model JSON and supported evidence, or fall back to manual/rule operations. Live connectivity has been tested, but model accuracy is not guaranteed. AI cannot approve an application or create a reservation.

## Data and reset

SQLite is stored at `data/campus.sqlite`. Initialization is idempotent. To restore fixtures, stop the server, then run:

```powershell
.\.venv\Scripts\python.exe manage.py --reset --yes
```

This deletes ALL local demo state, including conversations, plans, logs, application versions, notifications and sessions, then restores seed data. Never reset to upgrade: normal startup or `python manage.py` performs a versioned additive migration and preserves previous data. A local pre-upgrade backup has been retained under `data`, which is excluded from Git and distribution. Existing records without timestamps are explicitly marked as imported rather than assigned invented history.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

API reference: inspect the router files or `/openapi.json`. The restrictive page policy intentionally blocks FastAPI's CDN-based Swagger UI; no application feature needs a CDN.

Enhanced browser verification and silent recording use `tools/browser-enhanced.cjs`. It requires Node, Chrome and Playwright (`npm install --no-save playwright`, then `npx playwright install ffmpeg`). Start the server and configure the local AI key first: the workflow expects actual classification and field-extraction candidates. It creates clearly fictional demonstration records and does not reset existing data. `PLAYWRIGHT_MODULE` can point to an existing Playwright installation. Earlier `browser-check.cjs` and the offline video document the original release and are not the enhanced UI test. Current evidence distinguishes actual live calls from fallback results and mock tests.

## Project ownership

| Owner | Backend | Frontend | Responsibility |
| --- | --- | --- | --- |
| Rongkai Cheng | assistant.py, ai.py | assistant.js | Retrieval and shared AI adapter |
| Dequn Shang | learning.py | learning.js | Rule-based course and risk suggestions |
| Jun Yang | facilities.py, main.py, db.py | facilities.js | Bookings, faults and shared integration |
| Lexi Shu | maintenance.py | maintenance.js | Repair lifecycle, simulated energy, QA |
| Zheyuan Huai | reviews.py | reviews.js | System Analyst and Document Pre-review Lead: requirements analysis, scope management and material pre-review |
| Shiran Yuan | applications.py | applications.js, shared styles | Service portal and common UI |

Backend modules live under `app/routers`; page modules under `static/modules`. `auth.py`, `db.py`, `main.py`, `shared.js` and shared styles are integration surfaces. Coordinate changes before editing them.

## GitHub collaboration

The target team repository is [hahahayasahiro/883-PROJECT](https://github.com/hahahayasahiro/883-PROJECT). This application directory is the repository root. See [GitHub preparation](GITHUB_UPLOAD.md) for the local preparation and publishing steps; configuring a remote does not itself publish files. Use branches `module/assistant`, `module/learning`, `module/facilities`, `module/maintenance`, `module/reviews`, `module/applications`. Open PRs against `main`; Jun Yang integrates after tests pass. Keep `.env`, `.venv`, local databases, caches and temporary builds out of commits. Share `.env.example`, not `.env`.

Public API groups: `/api/assistant`, `/api/learning`, `/api/facilities`, `/api/maintenance`, `/api/reviews`, `/api/applications`. JSON schemas are generated at `/openapi.json`. Auth uses HttpOnly SameSite cookies with an eight-hour server-side session. Roles and ownership are checked server-side. The local demo uses HTTP; public deployment and production authentication hardening are outside this release.

## Current boundaries

The enhanced release adds saved conversations, interest-ranked semester plans, time/capacity/equipment room search, conflict alternatives, editable bookings, AI classification suggestions, ticket logs/expenses/ETA, seven days of persistent simulated energy, TXT/text-PDF uploads, confirmed AI field candidates, evidence checks, immutable application versions, return/revise/resubmit workflows, timelines and in-app notifications. Student records remain private and staff actions are enforced server-side.

Learning rules and the 12-credit cap are synthetic. Uploaded files are limited to 5MB, 20 PDF pages and 60,000 extracted text characters. Scan-only or mixed pages without text, encrypted PDFs and unsupported formats are rejected. Original files are processed transiently rather than retained on disk. Uploading text does not itself call AI; candidates are never applied without user selection. Reviews attach to a version and remain visible as outdated after revisions. Already-deleted historical reviews cannot be reconstructed.

Energy is simulated, notifications require a portal refresh, and processing-time statistics cover recorded latest submission cycles only. Voice, trained models, real sensors, OCR, email delivery and per-staff workload assignment remain future work. Daily booking timetable dates are UTC; timestamp display follows the device timezone.

## Presentation package

For the enhanced release, use `deliverables/SmartCampus-enhanced-presentation.pptx`, `SPEAKER_NOTES_ENHANCED.md`, `ENHANCED_GUIDE.md` and `ENHANCED_TEST_REPORT.md`. The deck remains 13 slides, with six speakers at two minutes each and no additional demo slot. Zheyuan owns slides 10–11 on requirements/scope and pre-review. Jun retains integration and Rongkai retains shared AI ownership. Earlier decks and reports remain historical versions. Use the enhanced video for the new workflows; old offline video remains explicitly a fallback-mode recording.

Presentation: 12 November 2026 during Tutorial. The group leader submits slides to Moodle by 23:59 on 13 November 2026.

See [the delivery index](deliverables/README.md) for the current deck, notes, demonstration video, bilingual manual and historical versions. Local live DeepSeek sample calls have been verified separately from mock tests. Broader model accuracy, actual spoken timing, installation on a second physical computer and classroom equipment still require team follow-up.

See [the completeness review](deliverables/COMPLETENESS_REVIEW.md) for the distinction between this progress release and later final-course submissions. Repository CI checks run without an AI key; a green CI result does not establish live AI availability.
