# Team contribution guide

Use Python 3.12 and the installation instructions in README.md. All accounts and business examples are synthetic. Every member owns one module; shared starter code does not establish exclusive historical authorship.

| Branch | Accountable owner | Scope |
| --- | --- | --- |
| module/assistant | Rongkai Cheng / 程荣凯 | Study assistant and shared AI adapter |
| module/learning | Dequn Shang / 尚得群 | Learning preferences, rules and plans |
| module/facilities | Jun Yang / 杨骏 | Bookings, fault intake and integration |
| module/maintenance | Lexi Shu / 舒乐熙 | Work orders, synthetic energy and QA |
| module/reviews | Zheyuan Huai / 怀喆元 | Requirements, scope and document pre-review |
| module/applications | Shiran Yuan / 袁诗然 | Portal, decisions, notifications and shared UI |

Create changes on your module branch and open a pull request to main. Jun coordinates integration and database/API changes. Shiran coordinates shared navigation/styles. Rongkai coordinates the shared AI adapter. Zheyuan keeps requirements, acceptance criteria and presentation claims consistent with actual behavior.

Before a PR, run `python tools/check-readiness.py` and `.\.venv\Scripts\python.exe -m pytest -q`. Include relevant UI evidence and failure cases. Do not reset another member's data to demonstrate a feature. Keep additive migration compatible with existing records.

`.env` and the whole `data/` directory are private local state. Use `.env.example` for configuration instructions. Do not add keys to workflow secrets for these tests: automated checks intentionally use mocks and fallbacks. Real AI calls are separately verified manually against fictional examples.

The checked-in Office files and recordings can be used directly. Their optional authoring tools require additional document/presentation runtimes; installing the application dependencies does not install those authoring tools. The application itself needs no Office, Node or browser-automation package.
