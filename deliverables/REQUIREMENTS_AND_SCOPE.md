# Requirements and prototype scope baseline

Prepared for the 12 November 2026 progress presentation. Revised accountable owner: Zheyuan Huai, System Analyst and Document Pre-review Lead. This document supplies an initial baseline for his review and ongoing maintenance; it does not assert that he previously authored all system analysis or implementation.

## Required coverage and acceptance

| Domain / module | Primary owner | Progress-report acceptance condition | Current evidence / limitation |
| --- | --- | --- | --- |
| Learning / M1.1 Assistant | Rongkai Cheng | Question produces supporting excerpts, an appropriately labelled response or no-evidence referral | Retrieval and fallback verified. AI adapter logic tested with mocks. Real model call pending. |
| Learning / M1.2 Learning path | Dequn Shang | Suggestions obey prerequisite rules and support flags explain their triggers | Rules implemented and locally tested. No trained recommendation or risk model. |
| Facilities / M2.1 Booking and faults | Jun Yang | Create/cancel own booking, reject overlaps, create a shared fault ticket | Local browser and backend checks passed, including simultaneous requests. No occupancy prediction or AI fault classification. |
| Facilities / M2.2 Energy and maintenance | Lexi Shu | Staff advance shared repair tickets and record cost; energy source is visible | Ticket flow checked. Energy readings simulated. No real control or predictive maintenance. |
| Administration / M3.1 Pre-review | Zheyuan Huai | Save draft, flag field/identity problems, show advisory analysis, correct and rerun checks | Rule fallback, result saving and invalidation after editing implemented. Live AI analysis pending verification. |
| Administration / M3.2 Portal | Shiran Yuan | Submit own application, staff decide, student sees updated status and explanation | Connected browser workflow checked. Refresh-based updates; workload assignment and email delivery deferred. |

Course baseline: all three subsystems, at least six modules, at least two modules applying AI, and a clear module responsibility for each member. The prototype implements two AI integration paths, but the team must verify real AI operation before claiming the AI requirement is demonstrated. A connected adapter alone is not proof of a successful AI feature.

## Scope status

- Implemented local business functions: authentication and role checks, module navigation, bookings, shared tickets, draft editing, saved pre-reviews, submission, staff decisions and persisted records.
- Rule-based functions: prerequisite eligibility, support reminders, required fields and identity checks.
- Simulated data: all user/course/campus records and electricity/occupancy readings.
- Pending validation: both real DeepSeek features, second physical computer setup and presentation-device rehearsal.
- Future capabilities: voice, semantic retrieval evaluation, trained recommendation/risk models, occupancy prediction, AI fault classification, predictive maintenance, sensors, OCR, email notifications and staff workload allocation.

## Revised responsibilities and boundaries

Zheyuan owns requirement-to-module mapping, scope/status clarity, acceptance criteria maintenance and M3.1 pre-review. He reviews changes against this baseline and coordinates the related report sections. Jun retains system integration and shared database coordination. Rongkai retains the shared AI adapter. Shiran retains the portal and approval interface. Lexi retains QA coordination. Dequn retains learning recommendation/risk logic. The allocation specifies responsibility, not exclusive historical authorship.

Before enlarging scope, record the requirement, owner, acceptance condition, dependencies and effect on demonstration time. For the two-day progress milestone, prioritise completing the pending checks and correcting defects in existing workflows.

## Completion evidence

Use the existing test report, browser results and actual screenshots for local implementation claims. Record real API results separately after a team key is configured. An AI pre-review remains advisory: deterministic field checks can prevent invalid submission, but an AI suggestion does not constitute approval or guarantee that all inconsistencies were found.
