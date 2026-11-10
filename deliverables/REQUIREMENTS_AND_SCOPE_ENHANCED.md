# Enhanced scope and acceptance baseline

Accountable reviewer: Zheyuan Huai, System Analyst and Document Pre-review Lead. This revised baseline defines responsibility and acceptance for the enhanced release, rather than claiming exclusive historical authorship of shared code. Jun retains integration coordination, Rongkai the shared AI service, and each module retains its original owner.

| Module | Enhanced acceptance condition | Evidence and boundaries |
| --- | --- | --- |
| M1.1 / Rongkai | Save/switch conversations, continue after refresh, retrieve fresh sources per turn, show original excerpts and service links | Browser and backend checks. Latest ten prior turns only. No automatic booking or application submission. |
| M1.2 / Dequn | Save interest/goal, rank eligible courses, maintain a named-term plan, remove entries and enforce credit limits | Rules use explicit reasons. Three credits per seed course, maximum twelve per term. No trained risk model. |
| M2.1 / Jun | Filter rooms, show UTC-day availability, reject overlaps, offer available alternatives, modify own reservation and retain cancellation reason | Backend tests cover concurrent modifications and failed-update preservation. No occupancy prediction. |
| M2.2 / Lexi | Suggest fault category with human confirmation, filter repairs, save ETA/logs/expenses, filter persistent energy by room/date | Real AI suggestion checked. Energy has seven seeded synthetic dates and does not represent real equipment. |
| M3.1 / Zheyuan | Upload TXT/text PDF, inspect material checklist, confirm supported AI field candidates, save evidence checks by version, compare edits and retain outdated reviews | Upload limits and invalid files tested. Structured live AI checked separately. OCR and automatic approval excluded. |
| M3.2 / Shiran | Search/filter private applications, show timeline, return with explanation, revise/resubmit, notify involved accounts and expose processing statistics | Complete correction workflow checked. Notifications are in-app after refresh. Staff assignment and email remain future work. |

## Shared acceptance

All three subsystems and six modules remain accessible from the same application. Persistent records connect booking/fault intake to maintenance and versioned pre-review to application processing. Additive migration preserves existing records and credentials without reset. Ownership and staff permissions are enforced server-side for both old and new endpoints.

Two original AI paths and additional classification/extraction paths have actual connectivity evidence, but response quality remains a separate evaluation task. A fallback remains visibly labelled. Recommendations, risk flags and credit limits remain rules. Campus/user/course records and energy readings are synthetic. The AI adapter never executes approval or other business actions on its own.

Zheyuan reviews feature claims against this baseline, maintains module acceptance conditions and flags scope changes before they enter the classroom presentation. The updated report keeps each speaker at two minutes and selects one enhanced workflow per member.

## Later work

Evaluate a wider question and material dataset, repeat installation on another physical computer, rehearse classroom equipment and configure the team repository. Subsequent features may include semantic retrieval, trained ranking/risk models, occupancy prediction, predictive maintenance, OCR, sensor integration, notification delivery and staff workload allocation after suitable data and tests exist.
