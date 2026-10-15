# AGENTS.md — Trust Me Coding Instructions

> Status: Initial repository guidance. Update this file when tooling and implementation decisions are confirmed.
> Applies to: Entire repository. Primary coding assistant: Codex.

## 1. Project mission

**Trust Me** is a full-stack, AI-powered e-commerce product trust assessment and decision-support platform. It provides a **Product Trust Score (0–100)**, **Assessment Confidence**, **Supporting Evidence**, **Risk Factors**, and a **Recommended / Caution / Avoid** recommendation. These outputs must be evidence-based, explainable, and honest about uncertainty. The system supports purchasing decisions; it does not guarantee product authenticity, quality, or safety.

## 2. Sources of truth

1. User-approved requirements and explicit task instructions determine **what** to build.
2. `ARCHITECTURE.md` defines module ownership, boundaries, and the intended data flow.
3. `DESIGN.md` (or the existing file's exact casing) governs frontend UX, layout, design tokens, and accessibility.
4. `README.md` records confirmed setup and execution instructions.
5. Existing working code and tests show the **implemented** state; do not confuse it with a **planned** design.

When documents conflict or a requirement is unclear, explain the conflict and ask before implementing a consequential assumption. Do not silently add scope.

## 3. Confirmed stack

| Area | Technology | Status |
|---|---|---|
| Frontend | TypeScript, React, Next.js, Tailwind CSS | Selected; repository setup not confirmed |
| Backend | Python, FastAPI | Selected; repository setup not confirmed |
| Database | PostgreSQL | Selected; schema not finalized |
| AI / ML | LangGraph, Hugging Face Transformers, scikit-learn | Selected; specific uses and models not finalized |
| Testing | Not finalized | Do not assume pytest, Jest, Vitest, Playwright, etc. |
| Package managers / tooling | Not finalized | Inspect repository manifests before selecting commands |

Do not install additional frameworks, ORMs, state libraries, UI kits, agent frameworks, or infrastructure without a demonstrated need and approval.

## 4. Mandatory workflow for Codex

1. **Inspect first.** Read this file, the relevant requirements, `ARCHITECTURE.md`, `DESIGN.md`, existing source, manifests, and tests. Identify what actually exists.
2. **Plan before coding.** Summarize scope, affected files, dependencies, API/data contracts, edge cases, and verification steps. For substantial changes, wait for user approval.
3. **Keep changes narrow.** Implement only the requested increment or task. Prefer small, reviewable changes; preserve existing behavior.
4. **Respect ownership and boundaries.** Frontend renders and requests data; FastAPI coordinates validated requests; AI/ML modules produce structured evidence; trust reasoning consumes evidence and generates explainable outputs; PostgreSQL stores approved persistent data.
5. **Verify honestly.** Run only commands supported by the actual repository. State which checks ran, passed, failed, or could not run, and why.
6. **Update docs only when reality changes.** Record confirmed commands, schema decisions, interfaces, and architecture changes. Do not label proposals as implemented.

## 5. Build / dev / test / lint commands

**No exact CLI commands are confirmed.** The repository currently contains only the design template/specification. Do not present example commands as project-ready commands, and do not fabricate scripts.

| Activity | Confirmed command | Action for Codex |
|---|---|---|
| Install frontend dependencies | **NOT CONFIGURED** | Inspect `package.json` and lockfile after initialization |
| Start frontend development server | **NOT CONFIGURED** | Read `package.json` scripts after initialization |
| Build frontend | **NOT CONFIGURED** | Read `package.json` scripts after initialization |
| Frontend lint / typecheck | **NOT CONFIGURED** | Discover configured scripts and `tsconfig.json` |
| Install backend dependencies | **NOT CONFIGURED** | Inspect `pyproject.toml` / requirements files if added |
| Start FastAPI backend | **NOT CONFIGURED** | Discover app entry point and documented runner |
| Backend tests | **NOT CONFIGURED** | Wait for selected framework and test setup |
| AI/ML evaluation | **NOT CONFIGURED** | Require an explicit evaluation protocol |
| Database migrations | **NOT CONFIGURED** | Require selected migration tooling and approved schema |

When the repository is initialized, replace each `NOT CONFIGURED` with an **exact, verified command**, including its execution directory. Never invent a successful test result.

## 6. Coding guardrails

### TypeScript / Next.js

- Enable and preserve **TypeScript strict mode** when creating the project; avoid `any` unless justified and documented.
- Keep UI components focused; avoid mixing database access, trust-score mathematics, and model inference into React components.
- Validate external data at the appropriate boundary and handle loading, empty, error, and insufficient-evidence states.
- Follow `DESIGN.md` for component patterns, accessibility, responsive behavior, and visual tokens.
- Do not invent product scores, confidence percentages, citations, or risk findings for production UI.

### Python / FastAPI / ML

- Use Python type hints and clear module responsibilities.
- Validate API inputs and outputs; make failures explicit instead of masking them with successful-looking fallbacks.
- Keep model inference, data preparation, evidence normalization, and trust reasoning testable as separate concerns.
- Use deterministic, reproducible trust-scoring logic when scoring rules are approved; specify the mathematical formulation and assumptions **before** writing scoring code.
- Track input evidence and score derivation; avoid untraceable LLM-generated numerical judgments.
- Treat fake-review and AI-generated-review detection as **fallible signals**, not verified accusations.
- Separate assessment **confidence** from product **trustworthiness**.
- Do not claim a model is trained, calibrated, validated, or accurate without measured evidence.

### Data, security, and reliability

- No hardcoded secrets, passwords, API keys, or connection strings. Use environment variables and a safe example configuration when appropriate.
- Never commit real personal information, credentials, or sensitive raw datasets without approval.
- Use parameterized queries or approved safe data-access mechanisms; validate authorization and access boundaries.
- Preserve evidence provenance, timestamps (when available), and clear missing/contradictory evidence states.
- Avoid destructive schema changes or migrations without explicit approval and a migration/rollback plan.

## 7. Five modules and owners

| Module | Owner | Responsibility |
|---|---|---|
| User Workspace & Analysis Management | Er Kim Wen | Product submissions, workspace, history, report access |
| Product Intelligence Agent | Er Kim Wen | Structured product information analysis and evidence |
| Knowledge & Evidence Repository | Er Kim Wen | Organized evidence, provenance, retrieval and storage |
| Review Intelligence Agent | Koh Huai Yu | Review NLP/ML, sentiment, similarity, suspicious patterns, credibility |
| Trust Reasoning & Recommendation Agent | Koh Huai Yu | Evidence integration, deterministic scoring, confidence, risks, explainable recommendation |

Both developers collaborate on interface contracts and end-to-end integration. Module ownership is a coordination guideline, not a reason to prohibit reviewed cross-module changes.

## 8. Scope and process boundaries

- Use **Incremental Agile Development with four increments**. Do not introduce Scrum terminology or ceremonies.
- Optimize for an academically defensible **two-person undergraduate FYP**, not an enterprise platform.
- No unapproved marketplace checkout, payments, seller portals, price tracking, browser extensions, or chatbots.
- LangGraph is an available tool, not a requirement to wrap every deterministic function in an agent node.
- Prefer explainable baselines and measurable evaluation over unnecessary multi-agent complexity.
- Mock fixtures may be used for frontend development only when isolated, labeled, and never presented as real assessment outputs.

## 9. Completion checklist for every change

- [ ] Requirements and scope checked
- [ ] Small implementation plan provided
- [ ] Types, boundaries, error states, and missing-data behavior considered
- [ ] No fabricated score, confidence, review claim, or evidence
- [ ] Relevant existing checks run, or blockers reported accurately
- [ ] Documentation updated only for confirmed changes
- [ ] Unresolved assumptions explicitly listed
