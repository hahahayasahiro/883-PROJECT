# SmartCampus English speaking notes

Target duration: 10 minutes including a 3.5-minute browser demonstration. These are suggested speaking assignments, not claims about work already completed individually by team members. Owners should review and adapt the notes after understanding their modules.

## 1. SmartCampus working prototype — Rongkai, 20 seconds

Good morning. We are presenting SmartCampus, our working prototype for a fictional GlobalConnect University. Our goal is to connect learning support, facilities and administrative services. Today we will show six modules and three complete workflows. All accounts, policies and records in this demonstration are synthetic.

## 2. Architecture and current scope — Jun, 70 seconds

The application runs on one local FastAPI server with an SQLite database. The browser loads local HTML, CSS and JavaScript, so basic campus workflows do not depend on external assets. Each module has its own page and router. Shared records connect faults to maintenance and pre-review to application processing. A common backend adapter calls DeepSeek for two AI-assisted features. The backend checks account roles and record ownership. We deliberately reduced our proposal to a prototype scope that we can test and explain in this progress report.

## 3. Study assistant — Rongkai, 30 seconds

My assigned module is the study assistant and shared AI service. Retrieval searches fifteen fictional campus documents and passes relevant excerpts to DeepSeek. The answer must include a matching source ID. If no evidence matches, the assistant refers the question to staff. If the API is unavailable, it shows source excerpts and labels the result as retrieval only. A citation is useful evidence, but it does not prove every generated statement is correct.

## 4. Learning path — Dequn, 30 seconds

My assigned module is learning support through course suggestions and risk reminders. A student qualifies for a course after passing its prerequisite. A mark below fifty or attendance below seventy-five percent triggers a support reminder with an explanation. These are transparent demonstration rules. We have not trained a recommendation or prediction model in this version.

## 5. Spaces and bookings — Jun, 30 seconds

My assigned module manages room bookings and fault reports. A reservation lasts at most two hours, and overlapping reservations for the same room are rejected. The conflict check and insert run within one database transaction. A student can cancel their own reservation. Fault reports become shared maintenance tickets rather than separate copies of the same issue.

## 6. Energy and maintenance — Lexi, 30 seconds

My assigned module tracks repair work from open to in progress and completed, including a recorded cost. Only maintenance staff can advance tickets. The energy display uses clearly labelled synthetic electricity and occupancy data. It does not control real equipment or predict failures. I also own the team testing checklist and regression checks before integration.

## 7. Document pre-review — Zheyuan, 30 seconds

My assigned module combines deterministic field checks with AI analysis of supporting text. A sample application deliberately includes a mismatched student ID. The system explains missing fields and identity mismatches, while DeepSeek can comment on less structured inconsistencies. The student can correct the saved draft and run the review again. Staff retain the final decision. This version accepts pasted text rather than scanned files.

## 8. Service portal — Shiran, 30 seconds

My assigned module handles application submission, progress tracking and staff decisions. Students see only their own applications. Administrative staff see the work queue and can approve or reject submitted applications with an explanation. The student then sees the updated decision. The dashboard counts application states. Per-staff workload assignment and email delivery remain future work.

## 9. Live demonstration — Operator and module owners, 210 seconds

We will first ask a course question and inspect its sources. Next, we will show a room reservation, a rejected overlap, and a fault moving into the maintenance queue. Finally, we will correct an application after pre-review, submit it, approve it as staff, and inspect the result as a student. The response label tells us whether AI ran. Please refer to DEMO_GUIDE.md for exact clicks and recovery steps.

## 10. Verification and next steps — Lexi and Zheyuan, 120 seconds

Our verification covers authentication, ownership, booking conflicts, ticket transitions and application decisions. Backend tests also simulate successful AI replies, timeouts, authentication errors and malformed responses. Browser checks exercise the connected workflows and refresh persistence. Mocked success checks verify integration logic, not the model service itself. We still need to verify real DeepSeek access with our team key and repeat installation on a second computer.

For the final system, we will first expand and evaluate the knowledge base, measure answer support and review quality, and collect user feedback. We will then consider more advanced recommendations and maintenance prediction when suitable data exists. Voice, sensor integration, OCR and email delivery follow after the core workflows are stable. Each module owner is responsible for reviewing their implementation, tests and final report section. Our immediate priority is a reproducible demonstration and a clear distinction between implemented features, simulated data and planned work.
