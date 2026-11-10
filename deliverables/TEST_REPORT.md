# SmartCampus verification record

Date: 10 November 2026. Environment: Windows, Python 3.12.9, local SQLite, Chrome automation. All records are fictional. No real AI credential was available during verification.

## Backend

`python -m pytest -q` passed 12 collected cases. `test-results.xml` contains the machine-readable results.

| Area | Evidence |
| --- | --- |
| Authentication | Anonymous requests rejected, wrong password rejected, cookie login and logout checked |
| Learning rules | Low-grade/attendance flag checked, unmet prerequisites excluded |
| Source retrieval | CS202 returns K02, unrelated world-cup question returns no evidence |
| Booking | Conflict rejected, another student's cancellation rejected, cancellation releases slot, duration limit checked |
| Concurrent bookings | Two simultaneous requests for one slot yield one success and one conflict |
| Maintenance | Fault becomes a shared ticket, student update rejected, sequential transitions and cost checked |
| Applications | Missing purpose prevents submission, other student's access rejected, correction removes old review, admin decision visible to student |
| AI integration logic | Mocked cited answer and review success paths checked, uncited answer falls back |
| AI adapter | Mock transport covers timeout, HTTP 401, malformed response and success |
| Persistence | Idempotent initialization preserves records and fixture counts |
| Request origin | Cross-origin mutation rejected |

One dependency deprecation warning comes from Starlette's HTTPX-backed TestClient. It did not cause test failures. Tests use HTTPX mock transport and do not make paid model requests.

## Actual browser interactions

`browser-results.json` records zero unexpected console errors or uncaught page errors in the final run. Expected HTTP 401 before login and HTTP 409 for the deliberate conflict are not failures.

The browser opened all six student modules, requested source retrieval, inspected learning rules, created and duplicated a reservation, reported a fault, completed the repair as maintenance staff, pre-reviewed and corrected a draft, submitted it, approved it as admin and confirmed the student's updated status. Refresh persistence and a 390-pixel mobile layout also passed.

`SmartCampus-demo-offline.webm` records these actual browser interactions. It is a silent fallback recording with `retrieval_only` and `rules_only` modes visible. It does not demonstrate real DeepSeek access.

After stopping and starting the actual Uvicorn process, `tools/check-restart.py` confirmed that the approved application, active booking and completed repair with recorded cost remained accessible via HTTP.

## Presentation

The 10-slide editable PPTX passed package integrity, geometry, font-policy and first-party re-import checks. All ten slide previews were inspected. PowerPoint itself and the classroom display have not been checked. Module screenshots are actual browser captures using fallback AI modes.

## Required team checks

- Configure a real DeepSeek key locally. Verify `live_ai` for both question answering and material pre-review, including correct sources and useful inconsistency feedback.
- Repeat setup and launch on a second physical computer. This has not been claimed as completed.
- Create the team repository and push reviewed source. No GitHub remote was provided or published.
- Rehearse the deck, live demonstration and fallback playback on the presentation equipment.

The seeded rules and keyword retrieval are suitable for a constrained classroom prototype. Evaluation on broader queries, production security, real data integrations and model accuracy benchmarking remain future work.
