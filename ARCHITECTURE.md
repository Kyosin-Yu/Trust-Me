# ARCHITECTURE.md — Trust Me

> **Status:** Proposed logical architecture, not an implemented topology. This document explains the diagram in words so human developers and coding agents interpret it consistently. Update provisional decisions when approved.

## 1. Architectural intent

Trust Me is a **full-stack, AI-powered decision-support web application**. A frontend requests product assessments through a backend API. Backend logic coordinates product evidence, review evidence, persistent records, and an explainable trust assessment.

**Selected technologies:** Next.js + React + TypeScript + Tailwind CSS; FastAPI + Python; PostgreSQL; LangGraph, Hugging Face Transformers, and scikit-learn where justified. Exact service layout, packages, orchestration, deployment, and persistence schema are **not finalized**.

## 2. Logical data flow (proposed)

```text
Consumer
   |
   v
Next.js web UI (workspace, submission, report)
   |
   | API requests (contract TBD)
   v
FastAPI application / request validation
   |
   +--> Product Intelligence Agent ------+
   |                                      |
   +--> Review Intelligence Agent -------+--> Structured evidence
   |                                      |         |
   +--> Knowledge & Evidence Repository <-+---------+
   |                                                |
   +--> Trust Reasoning & Recommendation Agent <----+
   |             |
   |             +--> Product Trust Score (0–100)
   |             +--> Assessment Confidence
   |             +--> Evidence + Risk Factors
   |             +--> Recommended / Caution / Avoid
   |
   v
Validated explainable report response
   |
   v
Next.js web UI

PostgreSQL: intended persistent storage; exact tables and access patterns TBD.
```

This is a **logical flow**, not a claim that separate microservices, queues, APIs, or LangGraph nodes already exist. Execution may be sequential or orchestrated; decide after requirements and performance constraints are reviewed.

## 2.1 How to read the diagram (important for coding agents)

The diagram represents **responsibilities and information dependencies**, not an exact call graph. In particular:

- A line from FastAPI to an intelligence module means the backend **coordinates** that module; it does **not** mandate a separate HTTP service, LangGraph agent, or independently deployed process.
- Product Intelligence and Review Intelligence are **independent evidence producers**. They both contribute to a single assessment but neither computes the final Product Trust Score.
- The Knowledge & Evidence Repository is an **evidence storage/retrieval responsibility**, not a third classifier or a source that automatically makes claims. The storage technology is planned as PostgreSQL; table layout remains undecided.
- Trust Reasoning consumes **validated evidence** from the producer modules and, when needed, existing repository evidence. Only Trust Reasoning produces the **overall** trust assessment and final recommendation.
- A completed response is returned through the backend to the frontend. Persisting an analysis/report so it appears in history is a desired user-facing capability, but the exact transaction boundaries are **TBD**.
- Arrows do **not** assert synchronous execution, concurrency, data scraping, external APIs, queues, retries, or model availability. These require explicit design decisions.

## 2.2 End-to-end logical execution flow (reference behavior)

The following numbered stages define the **intended observable behavior**. They are not implemented endpoints or function names. A coding agent should follow this ordering of responsibilities without inventing infrastructure.

| Step | Responsible boundary | What happens | Logical result |
|---|---|---|---|
| **1 — Submit** | User → Workspace UI | The user provides a product reference (e.g., URL) and/or product/review information supported by the eventual requirements. UI validates basic input and submits a request. | User-provided analysis input |
| **2 — Validate and initiate** | FastAPI | Backend validates input, checks authorization if applicable, and establishes an analysis context/identifier **if designed**. | Validated request or explicit validation error |
| **3 — Prepare available data** | Backend coordination / approved ingestion | Determine which product details and review records are actually available. Do not silently assume a URL can be scraped or reviews can be fetched. | Product input, review input, and availability metadata |
| **4A — Analyze product** | Product Intelligence Agent (Kim Wen) | Extract/assess supported product characteristics and flag evidence-backed observations or inconsistencies. | Structured product evidence with provenance |
| **4B — Analyze reviews** | Review Intelligence Agent (Huai Yu) | Assess supported review signals, such as sentiment, duplication, suspicious patterns, possible AI-generation, and credibility; preserve uncertainty. | Structured review evidence and model/quality indicators |
| **5 — Collect and retrieve evidence** | Knowledge & Evidence Repository (Kim Wen) | Validate and organize relevant evidence, preserve its source/lineage, and expose records to downstream reasoning. Persist/retrieve only according to the approved schema and lifecycle. | Unified, attributable evidence collection |
| **6 — Assess sufficiency** | Backend coordination + Trust Reasoning | Check whether enough relevant evidence exists to justify a meaningful assessment; distinguish unavailable evidence from negative evidence. | Reasonable assessment input or insufficient-evidence outcome |
| **7 — Reason and recommend** | Trust Reasoning & Recommendation Agent (Huai Yu) | Apply an explicitly documented, reproducible scoring and confidence method to the available evidence; explain risks and recommendation. | Trust Score, separate Confidence Level, evidence references, risk factors, Recommended/Caution/Avoid **when warranted** |
| **8 — Validate report** | Backend | Validate result shape, allowed labels, evidence references, and absence of fabricated values before exposing a report. | Validated report or failure/limited-result status |
| **9 — Present and access later** | Workspace UI / backend persistence | Display a comprehensible report with limitations and source context; optionally support history/reopen when persistence is implemented. | User-visible assessment and, when enabled, a saved record |

**Parallelism note:** Steps **4A** and **4B** may be independent and could eventually execute concurrently. For the initial implementation, **sequential execution is acceptable**. Do not introduce async workers, distributed processing, or LangGraph solely because the diagram shows two branches. Step 5 can involve reading existing evidence before analysis or saving new evidence afterward; the exact read/write order is an implementation decision, provided provenance and consistency are maintained.

## 2.3 Data crossing each module boundary

Use **explicit, validated data structures** (e.g., Python/Pydantic at the backend boundary) once implementation starts. The examples below are *conceptual fields, not approved database columns, APIs, or class definitions*.

1. **Analysis input:** submitted product information, product source, optional user-provided review records, and availability/error metadata.
2. **Product evidence:** claim/observation, evidence source, product association, applicable limitations, and quality indicators.
3. **Review evidence:** review or aggregated review association, signal type, classification/metric when justified, uncertainty or confidence where calibrated, and supporting provenance.
4. **Evidence bundle:** all relevant product and review evidence, source attribution, missing-data indicators, possible contradictions, and traceable identifiers where supported.
5. **Trust assessment:** numeric score **only when defensible**, confidence reported separately with a defined meaning, documented risk factors, linked supporting evidence, recommendation if permitted by the agreed decision rules, and explanation of limitations.
6. **Report representation:** validated presentation data suitable for frontend rendering; frontend displays it and **does not recompute scoring**.

**Contract rule:** When two modules integrate, first agree on the producer's outputs, consumer's required inputs, optional fields, error semantics, and one shared sample payload. Do not make up precise field names in downstream code while contracts remain unsettled.

## 2.4 Failure and insufficient-evidence behavior

An assessment is **not always guaranteed**. Supported outcomes should be differentiated:

| Situation | Expected behavior | Prohibited behavior |
|---|---|---|
| Invalid product submission | Explain the input issue and allow correction. | Proceed using guessed product details. |
| Product information unavailable | Record the missing source/input; continue only if the remaining evidence supports a meaningful result. | Fabricate specifications or product findings. |
| Reviews unavailable or too few | Mark review analysis unavailable or limited; reduce/qualify assessment confidence according to the eventual documented model. | Generate invented review metrics or fake-review percentages. |
| One intelligence stage errors | Preserve the error/partial-result status; continue only if the approved policy allows partial analysis. | Treat a failed module as though it returned a clean bill of health. |
| Contradictory evidence | Keep both findings visible and account for disagreement in confidence/reasoning. | Silently discard conflicting findings to simplify the report. |
| Evidence insufficient for a score | Show an **insufficient evidence / unable to assess** state rather than a fabricated precise number or forced recommendation. | Default to score 50, high confidence, or Recommended. |
| Source provenance unavailable | Mark attribution as unknown and limit claims accordingly. | Invent links, citations, or evidence source names. |
| Persistence or backend failure | Return an explicit actionable error and avoid claiming a report was saved. | Display a false saved/success state. |

The precise eligibility rules for partial reports, confidence adjustments, retries, and task statuses remain **TBD**. Codex must propose those rules for approval rather than hardcode them implicitly.

## 2.5 Concrete walk-through (illustrative, not a product claim)

1. A shopper opens **New Product Analysis** and submits a product URL and any supported supplementary information.
2. The backend validates the request and checks whether information needed for product and review analysis can be obtained from **approved** inputs or sources.
3. Product Intelligence records factual observations based on available information. Review Intelligence processes only **actual available reviews** and returns uncertain suspicious-pattern indicators where appropriate.
4. The repository associates evidence with its source and product/analysis context, making it accessible for audit and downstream reasoning.
5. Trust Reasoning evaluates the collected evidence. If information is adequate, it calculates the documented Trust Score and separately represents assessment confidence, risks, supporting evidence, and decision recommendation. If not, it returns an explicitly limited or insufficient-evidence assessment.
6. The backend validates the result. The UI displays the report so the shopper can inspect *why* a recommendation was made, not just the label. If analysis history is enabled, the shopper can reopen a saved report.

**This does not mean** the system already supports arbitrary e-commerce URL ingestion, live scraping, a specific review-count threshold, calibrated probability scores, or a particular API response format.

## 2.6 Implementation and orchestration constraints

- **Default starting point:** A modular application with a Next.js frontend and FastAPI backend. Modules are **logical packages/components within the backend**, unless independent deployment is explicitly justified later.
- **Proposed backend coordinator:** An application-level use case/service coordinates validation, evidence producers, repository interactions, and reasoning. Its name and code location are not predefined.
- **LangGraph:** In the selected AI/ML toolset but **not a requirement to turn every module into a free-form autonomous agent**. Adopt it only if state transitions, conditional routing, or recovery justify the extra abstraction.
- **Hugging Face / scikit-learn:** Possible Review Intelligence implementation tools, not assurances that pretrained models or training datasets already exist.
- **Determinism:** Given the same validated evidence, model output snapshot, formula version, and thresholds, the numerical reasoning stage should produce the same result. Do not allow an LLM to invent numeric scores or override a documented formula.
- **Single source of truth:** Backend assessment data and evidence references define report content. Frontend components do not infer confidence, recommendation, or unavailable evidence.
- **Security/privacy:** Keep source data and user information within approved access boundaries; never expose secrets or another user's private reports.

## 2.7 Explicitly unresolved sequencing decisions

Before production implementation, the two developers should agree on: supported product/review ingestion, whether analyses run synchronously or as jobs, when and how evidence/reports are persisted, permitted partial-result behavior, request/response contracts, authentication, source attribution fields, and model/scoring versions. **Until then, the numbered flow is a behavioral specification, not a mandate for specific endpoints or libraries.**

## 3. Module ownership and contracts

| Module | Owner | Input (logical) | Output (logical) |
|---|---|---|---|
| User Workspace & Analysis Management | Er Kim Wen | User actions, product submissions | Analysis requests, history/report views |
| Product Intelligence Agent | Er Kim Wen | Available product information | Structured observations and product evidence |
| Knowledge & Evidence Repository | Er Kim Wen | Evidence records and metadata | Stored/retrievable, attributable evidence |
| Review Intelligence Agent | Koh Huai Yu | Available review text and metadata | Sentiment, suspicious-pattern indicators, credibility-related evidence |
| Trust Reasoning & Recommendation Agent | Koh Huai Yu | Product/review evidence, availability and quality signals | Score, confidence, risk factors, evidence explanation, recommendation |

These are **conceptual contracts**; concrete field names, Pydantic models, database relations, and API routes require approval. Preserve provenance and distinguish absent evidence from negative evidence.

## 4. Responsibilities and dependency rules

- **Frontend:** user interaction, form validation, report presentation, navigation, accessibility, and explicit pending/error/insufficient-evidence states. No production scoring logic in the browser.
- **FastAPI:** validated API boundary, application-level coordination, authorization, and errors. Do not assume endpoint URLs until implemented.
- **AI/ML:** reusable processing modules; model outputs are probabilistic signals with recorded provenance/limitations.
- **Trust reasoning:** documented deterministic calculation for numerical results, explicit treatment of missing/conflicting evidence, and traceability from conclusions to evidence. Define formulas and thresholds before coding them.
- **Persistence:** PostgreSQL for approved records; no schema assumed yet. Never use the database as an implicit unvalidated messaging protocol.
- **LangGraph:** optional orchestration within the selected stack; use only where stateful orchestration benefits from it. Avoid agent-to-agent complexity with no practical value.

## 5. Non-negotiable integrity requirements

1. **Trust score != confidence.** A low trust score is not the same as low evidence confidence.
2. Never fabricate supporting evidence, sources, review counts, or confidence percentages.
3. Suspected fake/AI-generated reviews must be described as uncertain model indications, not proven fraud.
4. Every displayed risk/recommendation must be connected to available evidence or explicitly state limitations.
5. Missing inputs produce a clear insufficient-information outcome, not a fake precise result.
6. User/session authorization, secret management, and safe persistence are required when those features are implemented.

## 6. Suggested boundaries (not a directory mandate)

Organize by concerns: `frontend`, `backend` (API, application services), ML/review processing, product analysis, reasoning, and evidence persistence. **Do not create directories solely because this diagram mentions them.** Confirm actual repository structure before adding files.

## 7. Four-increment development approach

Use **Incremental Agile Development**, not Scrum. The following is a *planning proposal*, not an agreed timetable:

| Increment | Candidate focus | Shared integration checkpoint |
|---|---|---|
| 1 | Project foundation, UI shell, validated interfaces, baseline persistence plan | Both developers agree on input/evidence contracts |
| 2 | Workspace/product intelligence + initial review processing | Structured product/review evidence is interchangeable |
| 3 | Evidence repository + review evaluation + trust reasoning baseline | Reproducible score and evidence-linked report |
| 4 | End-to-end validation, quality improvements, evaluation, documentation | Full demonstration and defensible evaluation results |

Agree on scope and acceptance criteria per increment before implementing. Do not introduce Scrum ceremonies, roles, or artifacts.

## 8. Open architecture decisions

- Authentication and user/session design
- Concrete API endpoints and request/response schemas
- Review ingestion method and supported e-commerce sources
- AI datasets, model selection, and evaluation procedure
- Evidence record structure and PostgreSQL schema
- Background processing vs. synchronous analysis
- LangGraph orchestration need and node boundaries
- Trust-scoring mathematics, confidence calibration, and recommendation thresholds
- CI/testing framework and deployment model

Document the decision, rationale, and impact here once each question is resolved. Create `SCHEMA.md` only once there is a concrete schema worth maintaining.
