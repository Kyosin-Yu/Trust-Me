# Trust Me — Complete UI/UX Design Specification for Codex

> **Status:** Implementation design contract, version 1.0 (15 October 2026)  
> **Project:** Trust Me — AI-powered Product Trust Analysis and Decision Support Platform  
> **Purpose:** Codex must use this file as the primary visual and interaction specification when implementing the web UI.  
> **Scope:** Frontend presentation, navigation, user workflows, accessible UI states, and backend-integration contracts; **not** an authorization to invent features, train ML models, or change the scoring algorithm.

## Instructions for Codex (Read First)

1. **Inspect the existing repository before editing.** Identify actual routes, components, API contracts, database models, auth implementation, and existing design tokens. Do not assume a blank repository.
2. **Make a short implementation plan before writing code**, including files likely to change, screens, reusable components, mocked vs. connected data, and verification steps.
3. Follow the **Original Apple Design Reference** in Appendix A as the canonical visual source. The Trust Me adaptation rules in this document govern **product semantics** when Apple's marketing patterns are inappropriate for a data-rich assessment application.
4. Implement the **five FYP modules** faithfully. Do not add AI chatbots, marketplace checkout, seller administration, payments, browser extensions, price tracking, or social features without an explicit requirement.
5. Preserve any working features and data migrations. Do not replace production API calls with mock data. If backend endpoints do not exist, clearly isolate fixtures in a development-only adapter.
6. Use **Next.js, React, TypeScript, Tailwind CSS** for frontend and integrate with **FastAPI/Python + PostgreSQL** as existing code permits. Do not introduce Supabase, Firebase, Prisma, new component frameworks, or state libraries unless already in the repository or specifically approved.
7. Use server-side processing for intelligence and reasoning; do not fabricate trust scores in the UI or implement unreviewed scoring rules in TypeScript.
8. All product analysis conclusions must be grounded in returned evidence. Use explicit **Not available / Insufficient evidence / Analysis failed** states instead of inventing metrics.
9. Responsive and accessible behavior is required, not optional. Include keyboard navigation, visible focus indicators, readable contrast, labels, status announcements and reduced-motion handling.
10. Build in small, verifiable steps. Report what was implemented, what is mocked, what is blocked by missing API contracts, and what tests passed.

## A. Product identity and boundaries

**Product name:** Trust Me  
**Positioning:** Evidence-driven AI support for evaluating the trustworthiness of e-commerce product information.  
**Primary user:** An online shopper who wants an interpretable assessment before making a purchase.  
**Primary job-to-be-done:** Submit a product and understand its trust score, evidence confidence, supporting evidence, suspicious review patterns, material risks, and recommendation.

### Five modules and ownership

| Module | Owner | User-visible responsibility |
|---|---|---|
| User Workspace & Analysis Management | Er Kim Wen | Product submission, analysis list/history, report access, account interactions |
| Product Intelligence Agent | Er Kim Wen | Structured product observations and product evidence presented inside assessment |
| Knowledge & Evidence Repository | Er Kim Wen | Evidence source/records, provenance, finding details, link from conclusion to evidence |
| Review Intelligence Agent | Koh Huai Yu | Review sentiment, duplication/suspicious patterns, possible fake/AI-generated review signals, credibility indicators |
| Trust Reasoning & Recommendation Agent | Koh Huai Yu | Explainable score, confidence, risks, evidence synthesis, Recommended/Caution/Avoid outcome |

**Architecture:** The UI initiates and presents analysis; backend APIs coordinate data ingestion, intelligence, evidence storage and trust reasoning. Agents are **not** five separate consumer dashboards. Analysis outputs appear together in the product's report. The platform provides **decision support**, not a guarantee of quality, safety, authenticity, or merchant legitimacy.

### Evidence- and uncertainty-aware language

- Say **“Potentially suspicious reviews”**, not “These reviews are fake” unless verified evidence explicitly supports that assertion.
- Say **“Possible AI-generated patterns”** rather than certifying that authors used AI.
- Distinguish **Product Trust Score (0–100)** from **Assessment Confidence**; they answer different questions.
- Do not assume a fixed low/medium/high confidence mapping, score weighting, or recommendation threshold. These are defined by backend methodology, not by this UI specification.
- When report data lacks a metric, show “Not available” and a short explanation. **Never** silently substitute 0, 50, 100, or a fabricated percentage.
- Cite data origin and analysis timestamp where available; state clearly when external evidence cannot be retrieved.

## B. Visual application of the Apple reference

Appendix A contains the **original, unedited Apple design reference**, including its YAML tokens and component specifications. Use it as the source of truth for palette, typography, radii, general layout, and restraint.

### Priority order when designing

1. Accuracy and readability of evidence, uncertainty, and recommendation.
2. User journey clarity and accessible controls.
3. Consistency with Appendix A's exact token values.
4. A premium, calm, photography-first visual mood, especially on landing and product preview.

The Apple reference is a **marketing/store design study**, not an evidence-report interaction specification. Adapt its principles rather than cloning Apple logos, products, proprietary screenshots, or brand assets. Trust Me must have its own identity.

### Theme rules

- Default application mode: light (`#ffffff`, `#f5f5f7`), with `#1d1d1f` body copy.
- Primary interactive accent: `#0066cc`; dark canvas link: `#2997ff`; focus variant: `#0071e3`.
- Use near-black full-bleed sections **mainly on landing/feature storytelling**, not as competing backgrounds inside dense evidence tables.
- Use blue exclusively for *interactive accent*. For report semantics, discrete accessible green/amber/red status treatments are permissible only for Recommended/Caution/Avoid and risk severity, **not** additional brand colors. Labels and iconography must carry meaning without color alone.
- No decorative CSS gradients. No shadows on cards, text, buttons, sticky navigation or dashboard chrome. The reference's sole photographic product shadow may be used on product imagery.
- Distinguish analytical groupings using whitespace, light background changes, headings, and soft dividers—not heavy borders or elevated cards.
- Product photos must be sourced from permitted product data or local licensed/placeholder assets. Do not hotlink arbitrary unlicensed commercial photography.

### Design tokens (Tailwind / CSS variables)

Use CSS variables with semantic names; map to Tailwind theme or utilities (prefer existing project conventions):

```css
:root {
  --tm-primary: #0066cc;
  --tm-primary-focus: #0071e3;
  --tm-primary-dark-surface: #2997ff;
  --tm-ink: #1d1d1f;
  --tm-ink-subtle: #333333;
  --tm-muted: #7a7a7a;
  --tm-canvas: #ffffff;
  --tm-parchment: #f5f5f7;
  --tm-pearl: #fafafc;
  --tm-tile-dark-1: #272729;
  --tm-tile-dark-2: #2a2a2c;
  --tm-tile-dark-3: #252527;
  --tm-black: #000000;
  --tm-divider: #f0f0f0;
  --tm-hairline: #e0e0e0;
  --tm-on-dark: #ffffff;
  --tm-on-dark-muted: #cccccc;
  --tm-radius-utility: 8px;
  --tm-radius-card: 18px;
  --tm-radius-pill: 9999px;
  --tm-max-content: 1440px;
}
```

Do not treat the token example as permission to override existing repository configuration; centralize token declarations in its established theme file. For precise typography/spacing, follow Appendix A.

### Typography

- Prefer the platform's SF Pro Display / SF Pro Text **when legally available**; use native system-font stacks otherwise. **Do not bundle or redistribute proprietary fonts**.
- Hero: 56px / 600 / line-height 1.07 / letter-spacing -0.28px on large desktop.
- Feature heading: 40px / 600 / line-height 1.1.
- Standard article/paragraph body: 17px / 400 / line-height 1.47.
- Caption: 14px / 400; metadata/legal: 12px / 400 where readable.
- Dashboard dense tabular values may use a compact 14–16px scale **only when it improves scanning and meets accessibility**. This is an intentional product-specific exception to marketing paragraph typography.
- Numeric trust scores should use tabular numerals for alignment; never rely on color alone.

### Layout composition

- Landing: large editorial hero, spacious full-bleed sections, product/report mockup central visual, short CTAs, alternating parchment/dark surfaces.
- App: calm fixed-height top navigation and optional left sidebar on desktop; a compact breadcrumb/context bar as needed. Max-width content centered, with reading-width limits for paragraphs. Avoid full-bleed banners on every dashboard route.
- Report: single clear summary above the fold; scrollable explanation sections; sticky jump navigation *if useful*, but do not obscure the score or headings.
- Interactive forms: left-aligned labels, compact guidance, pill CTA, enough whitespace and consistent error placement.
- All click targets at least 44 × 44px on touch devices.
- Respect OS reduced-motion preferences; never use pulsing or looping animations as the only indication of status.

## C. Information architecture and routes

These are **suggested routes**; inspect the existing repo and preserve established paths if they differ. Routes that require unsupported backend behavior must be designed but gated/deferred, not faked as operational.

| Route (suggested) | Screen | Access | Main content |
|---|---|---|---|
| `/` | Landing | Public | Product value, demonstration report, CTA, how it works |
| `/sign-in` | Sign In | Public | Email/password and form states |
| `/sign-up` | Sign Up | Public | Registration and validation |
| `/workspace` | Dashboard | Authenticated (if auth is implemented) | Recent analyses, new-analysis CTA, empty state |
| `/analyses/new` | Submit Product | Authenticated (if required) | URL/manual product intake, preview, submit |
| `/analyses/[id]/progress` | Progress | Owner of analysis | Backend-reported analysis stages |
| `/analyses/[id]` | Trust Report | Owner of analysis | Score, confidence, risks, evidence, recommendation |
| `/analyses` | Analysis History | Authenticated (if implemented) | Previous runs, filtering, ordering, reopen |
| `/analyses/[id]/evidence` | Evidence Details | Owner of analysis | Evidence source/provenance, findings and links |
| `/settings` | Settings/Profile | Authenticated | Supported profile/account controls only |

Do **not** automatically create these APIs or routes if they conflict with documented functional requirements. It is acceptable to consolidate report and evidence into one page with anchors if this matches the current implementation better.

### Global navigation model

**Public nav:** Trust Me, Home, How It Works, Features, Sign In, Get Started.  
**Authenticated nav:** Workspace, New Analysis, History, Settings/Profile.  
**Report sub-navigation:** Overview, Reviews, Product, Evidence, Risks, Recommendation, Confidence (only sections with actual content).  
**Mobile:** Collapsed menu; clear and direct access to New Analysis; no overcrowded top row.

## D. Screen-by-screen UI specifications

### D1. Landing page (`/`)

**Goal:** explain the product, communicate evidence-first trust analysis, and move users into analysis.

Sections in order:
1. **Global nav:** restrained, compact; public navigation and CTA.
2. **Hero:** headline “Shop Smarter. Trust with Evidence.”; subtitle “Understand product credibility through AI-powered analysis, transparent evidence, and actionable insights.”; primary “Analyze a Product”; secondary “Explore How It Works”.
3. **Hero composition:** one visually dominant illustrative e-commerce product paired with a simplified, *clearly labeled example* Trust Me assessment. Preserve substantial whitespace; imagery is the focal point.
4. **How it works:** Submit Product → Analyze Evidence → Understand Trust Report. Describe what users provide and what the analysis can and cannot conclude.
5. **Four core abilities:** Product Intelligence, Review Intelligence, Evidence Transparency, Explainable Recommendation. Use clean editorial tiles, not more than necessary.
6. **Report preview:** score, confidence, evidence and top warning in a clear layout. Values must be marked sample/demo.
7. **Final CTA and footer:** About, privacy/terms only if actual routes or approved placeholder content exist.

**Important:** This is a marketing view; it may use alternating light/dark full-bleed bands. Never borrow Apple's identity assets.

### D2. Authentication (`/sign-in`, `/sign-up`)

- Centered restrained form on parchment or white background, no distracting product imagery.
- Labeled email/password; reveal/hide password; email format validation; required field validation; server validation displayed inline; loading and disabled duplicate-submit protection.
- Register: only fields supported by actual auth specification. Avoid inventing Google/Apple OAuth, phone verification, account roles, or enterprise SSO.
- Forgot-password link **only if supported**; otherwise defer it visibly in dev plan instead of dead-ending.
- Safe error copy: do not leak whether an email account exists where privacy/security could be affected.

### D3. Workspace dashboard (`/workspace`)

**Goal:** find results and start a new assessment in seconds.

- Welcome heading and one obvious primary `New Product Analysis` action.
- Recent analyses grid/table responsive to width: product thumbnail, name, store/source where available, created/updated time, analysis state, score, recommendation, View Report.
- Statuses: queued, processing, completed, failed (match actual API values through explicit adapter).
- Text search and filters only when supported; otherwise implement client-side filtering on fetched, already-authorized results without inventing server behavior.
- Empty state: “No analyses yet” + CTA; no fake history.
- Loading skeleton, request error with retry, no access, and long-name overflow.
- No commercial business analytics metrics unrelated to product trust.

### D4. New product analysis (`/analyses/new`)

- Input: product URL when supported, or structured manual fields when extraction isn't available.
- Form fields may include product name, source/platform, product description, attributes, available reviews—**only according to the actual ingestion contract**.
- Validate URL safely, required inputs and length. Never scrape arbitrary sites from the browser or claim universal automatic product extraction.
- Explain what data will be used and potential limitations before analysis.
- Preview summary before `Analyze Product`; show submit-pending state and duplicate-submit protection.
- Display unsupported-site, invalid URL, extraction-failed and insufficient-information states; permit manual input or retry if backend supports it.
- Do not collect payment, delivery addresses or unrelated PII.

### D5. Analysis progress (`/analyses/[id]/progress`)

Use an understandable **stage-based** status component:

1. Preparing Product Information
2. Product Intelligence Analysis
3. Review Intelligence Analysis
4. Evidence Retrieval and Organization
5. Trust Reasoning
6. Generating Explainable Trust Report

- Stages are **illustrative pipeline labels**, not a promise of sequential execution; map to real backend stage codes/order. If the backend runs stages in parallel, show parallel status correctly.
- Use Pending / In Progress / Completed / Failed, with optional timestamp and actionable error details.
- Never show a fake “73%” or fabricated ETA. A determinate percentage requires a backend-supported denominator.
- Accessible `role=status` / `aria-live` for important changes without repeatedly interrupting the user.
- Show a retry action only where the API safely supports retries.

### D6. Explainable Trust Report (`/analyses/[id]`) — highest priority

**Hierarchy:** Product header and recommendation immediately visible → assessment summary → evidence details → risk/context → decision support.

#### Above-the-fold summary

- Product photo or graceful image fallback; name, source, URL when safe, analysis timestamp.
- **Trust Score** as prominent 0–100 *only when returned and validated*; numeric label outside any visual chart.
- **Assessment Confidence** displayed independently; do not use it as the product score or infer it from score.
- **Recommendation** pill with text `Recommended`, `Caution`, `Avoid` (or “Undetermined” if no recommendation).
- Summary explaining the main positive and negative factors. No unexplained “AI says buy” language.
- “Evidence available” count only if returned and consistently defined.

#### Report section 1 — Trust overview

- Main strengths, main concerns and explanation of the reported score.
- If backend exposes factors and contributions, list them with labels and provenance; otherwise show narrative provided by API, without inventing mathematical weights.
- Optional tasteful score track or ring; never substitute a visual gauge for the numerical label.

#### Report section 2 — Review intelligence

- Sentiment summary with positive/neutral/negative values only if returned.
- Suspected duplication, unusual review pattern signals, possible AI-generated/fake review indicators, credibility assessment.
- Display `Reviewed sample N` or coverage notes if provided by backend.
- For any uncertainty signal, phrase “potential,” “may,” or “flagged for review”; explain model limitations and sample bias where known.
- Show inspectable examples with truncated review text and expandable detail if API permits; never generate fake testimonials as real evidence.
- Visualizations: minimalist labeled stacked sentiment bar, small comparison rows; avoid more than two charts in this section.

#### Report section 3 — Product intelligence

- Structured title, product metadata, attributes, claims, and source as returned.
- Highlight inconsistent or incomplete product information, where the backend explicitly detects it.
- Keep product specifications in a readable definition list / grouped table; no seller price plausibility or unrelated feature unless in validated requirements.

#### Report section 4 — Supporting evidence

- Each `EvidenceCard`: title, type/category, provenance/source, observation, relevance (supports/challenges/context), time when available, `View details`.
- If evidence supports a report conclusion, allow navigation/scroll to that record.
- “Evidence unavailable” rather than dummy source links or inferred citations.
- Clearly distinguish external primary sources, extracted review content, and model-generated interpretations when data allows.

#### Report section 5 — Risk factors

- Show risks with severity only if provided; accessible label + explanation + related evidence link(s).
- Examples of **categories**, not assumed detected findings: unusual duplication, inconsistent product claims, insufficient independent evidence.
- No accusatory language about merchants, sellers, or reviewers based purely on probabilistic ML classifications.

#### Report section 6 — Recommendation

- One clear Recommended/Caution/Avoid conclusion with *why* and what to verify before purchase.
- If evidence is insufficient, prefer a backend-backed uncertainty/undetermined message. Do not manufacture a recommendation.
- Small decision-support disclaimer: “This assessment supports informed shopping decisions and does not guarantee product quality or authenticity.”

#### Report section 7 — Assessment confidence

- Explain confidence **separately from trust**: coverage, availability, source consistency, model uncertainty, or whichever factors are explicitly supported by backend.
- Do not introduce low/medium/high thresholds without an approved method; render returned confidence label or value verbatim with unit/scale.
- Disclose missing inputs and caveats that reduce interpretability.

**Report interactive behavior:** Anchor navigation, accessible evidence expand/collapse, expandable review examples, optional share/export **only if requirement/API exists**. Do not fabricate PDF downloads, score recomputation, or report editing.

### D7. Analysis history (`/analyses`)

- Responsive compact table on desktop; stacked list items on phone.
- Fields: product, source, date, state, score (if completed), recommendation, view.
- Search/filter/sort if data fetching semantics allow; never imply server-wide querying with a client-only page subset.
- Proper placeholders for unfinished/failed cases; no score or verdict while processing.
- Confirmation for destructive actions only if deletion is authorized by official requirements.

### D8. Evidence detail (`/analyses/[id]/evidence`)

- Readable source record with evidence type, associated product, source, captured/analyzed time when provided, extraction context, evidence content, interpretation and referenced conclusions.
- Group by `Product evidence`, `Review evidence`, `Contextual evidence` only when those categories exist in actual data; otherwise derive from verified documented categories.
- Provide outward source link only for safe/validated URLs; use `rel="noopener noreferrer"` for external targets.
- Avoid exposing internal storage IDs, raw stack traces, API secrets, private reviewer metadata or internal model chain-of-thought.
- A consumer evidence browser **is not** an admin CRUD console.

### D9. Settings/profile (`/settings`)

- Show available account profile fields, relevant privacy/settings controls, and logout.
- Password change/account deletion only if backend explicitly supports it and user requirements include it.
- Display accurate save feedback and inline errors. No fake toggles or buttons.

## E. Shared components

Favor the existing UI conventions. The component names below are suggestions, not required folder paths.

| Component | Responsibility | Important states |
|---|---|---|
| `AppShell` | Authenticated nav + content frame | Wide / collapsed mobile |
| `GlobalNavigation` | Public header and CTAs | Menu open / closed |
| `PrimaryButton` | Action Blue pill | Default / pressed / disabled / loading / focus |
| `SecondaryButton` | Pearl utility action | Default / pressed / disabled / focus |
| `ProductPreview` | Safe image, product identity, source | Loaded / image unavailable |
| `AnalysisStatus` | Current backend-reported stage | Pending / processing / complete / failed |
| `TrustScoreDisplay` | Exact 0–100 reported score | Value / unavailable |
| `ConfidenceIndicator` | Independent confidence explanation | Value / insufficient data |
| `RecommendationBadge` | Verdict label with semantic treatment | Recommended / Caution / Avoid / undetermined |
| `SentimentBreakdown` | Labelled sentiment visuals | Values / not supplied |
| `ReviewSignalCard` | Uncertainty-aware review analysis | Flagged / no finding / missing data |
| `EvidenceCard` | Provenance and explanation | Collapsed / expanded / missing source |
| `RiskFactorItem` | Risk with severity/evidence | Severity supplied / unknown |
| `ReportSection` | Consistent section header/layout | Empty / content |
| `StatePanel` | Empty, error, permission and retry patterns | State-appropriate action |
| `FormField` | Label, help, validation | Default / error / disabled / pending |
| `ResponsiveDataList` | History | Table desktop / stacked phone |
| `Skeleton` | In-progress content placeholder | Reduced-motion safe |

### Component constraints

- Reuse AppShell, cards and tokens; avoid cloned markup and arbitrary one-off colors.
- Icons should be consistent stroke icons; keep icon use purposeful and pair semantic indicators with text.
- Apple reference defines no hover spec; do not invent flashy effects. Standard accessible hover affordances and clearly visible keyboard focus are allowed when necessary.
- Buttons/links must actually navigate or perform a supported action; no dead-end decorative controls.
- Do not expose internal model/debugging interfaces to normal shoppers.

## F. API/data contract guidance (illustrative, not a backend mandate)

Codex must **inspect and adapt to real backend schemas**. The following is a frontend **view-model suggestion** to keep presentation consistent, not an instruction to create arbitrary DB columns or change scoring methods.

```ts
type AnalysisStatus = 'queued' | 'processing' | 'completed' | 'failed';
type Recommendation = 'recommended' | 'caution' | 'avoid' | 'undetermined';

type TrustReportViewModel = {
  analysisId: string;
  product: {
    name: string;
    imageUrl?: string | null;
    sourceName?: string | null;
    productUrl?: string | null;
  };
  status: AnalysisStatus;
  analyzedAt?: string | null;
  trustScore?: number | null; // 0..100; validated numeric API data only
  confidence?: {
    display: string; // backend-defined score/level & scale
    explanation?: string | null;
  } | null;
  recommendation?: Recommendation | null;
  overview?: string | null;
  productEvidence?: Array<unknown>;
  reviewInsights?: Array<unknown>;
  supportingEvidence?: Array<unknown>;
  riskFactors?: Array<unknown>;
  reasoning?: string | null;
  limitations?: string[];
};
```

The `unknown` placeholders are intentional: define safe types **from actual FastAPI schemas**, not guesses. Ensure null and partial-result states are supported. Distinguish network/validation/API failure from a legitimate “no suspicious patterns found” observation. Do not render unknown data as a successful finding.

### Data safety and integrity

- Validate at API boundary; clamp/reject out-of-range trust scores without silently displaying invalid values.
- Sanitize review text as untrusted content; do not use `dangerouslySetInnerHTML` to display extracted web descriptions.
- If auth exists, every analysis/report lookup must be scoped to the authorized user on the server.
- Avoid persisting scraped raw personal review identifiers unless it is already justified in official requirements.
- Log technical errors without revealing secrets or private content to the browser.

## G. Responsive requirements

Create and verify at **1440px desktop, 834px tablet, 390px mobile**; preserve Appendix A's full breakpoint behavior where practical.

- At 1440px: nav/sidebar, 2-column report summary if helpful, product preview + score side-by-side, compact history table.
- At 834px: 2-column grids collapse; navigation changes appropriately; report always remains readable without horizontal scrolling.
- At 390px: single-column content, 28px hero heading where applicable, stacked trust header with score prominently visible, wrapped button labels, evidence accordions, history cards instead of wide tables.
- No horizontal scroll on document body or evidence sections (except deliberately scrollable accessible tables with clear affordances).
- Images preserve ratio; use object-fit contain for product renders, avoid layout shift, provide descriptive or empty alt text as appropriate.
- Contrast and keyboard navigation should remain valid in both light/dark marketing sections.

## H. Functional state coverage

For each data-driven screen, build UI for all states that matter:

| State | What user should see |
|---|---|
| First visit | Clear explanation and next action |
| Empty workspace | No prior analyses, new analysis CTA |
| Loading | Stable skeleton or textual loading state |
| Input invalid | Inline actionable validation error |
| URL/extraction unsupported | Limitation + permitted alternative/manual entry |
| Queued/in progress | Actual reported state and current stage if available |
| Analysis failed | Error summary, retry only when supported |
| Analysis completed | Score, confidence, verdict and evidence if available |
| Partial/inadequate evidence | Transparent missing sections, caveats and no invented data |
| Conflicting evidence | Contradictory sources visibly separated if API identifies them |
| Review signal uncertain | Probabilistic explanation, never definitive fraud accusation |
| Network offline/API error | Retry/recovery without wiping input |
| Unauthorized/expired login | Non-leaking access message and route back to sign-in |
| Long values / missing imagery | Graceful layout and fallback; no overflow |

## I. Four Incremental Agile development increments

**Do not introduce Scrum terminology or ceremonies.** Coordinate work across two developers in four increments; these are **recommended sequencing**, to be reconciled with the team's official submitted schedule.

| Increment | Kim Wen focus | Huai Yu focus | Joint UI validation |
|---|---|---|---|
| 1 — Foundation | Tokens, AppShell, auth/workspace shell, product submission skeleton | Define review output contracts and report data needs | Shared route map, fixture shape, accessibility and baseline layout |
| 2 — Product and Review Intelligence | Product preview, product intelligence section, evidence storage integration | Review analysis pipeline and review insight API output | Evidence/report placeholders replaced by real supported fields |
| 3 — Trust Report | History, evidence detail/navigation, API integration | Trust reasoning output (score, confidence, risks, recommendation) and explanations | End-to-end submit → process → view report with missing-data states |
| 4 — Integration and Evaluation | Responsive polish, exception handling, performance and repository integration | Model evaluation, confidence/scoring validation, reasoning correctness | Usability, accessibility, integration tests, report evidence consistency |

### Feasibility guidance

- Implement critical path first: **Submit → Process → Trust Report → Reopen**.
- Complete genuine functionality before decorative animation or charts.
- Prefer deterministic render states and small reusable components over complex client global state.
- Add no new frontend dependencies unless clearly justified by a required feature.

## J. Acceptance criteria and test checklist

Codex should not mark the UI complete until it can demonstrate:

- [ ] All core routes/screens required by actual current FRs are reachable and navigable.
- [ ] Landing leads to genuine sign-in / analysis entry, not dead CTAs.
- [ ] An authenticated user can view only their own workspace and analyses where auth is implemented.
- [ ] Product submission validates required fields and preserves entered data on errors.
- [ ] Progress states reflect backend truth; no fake percentages or completion.
- [ ] A completed report displays **trust score, independent confidence, recommendation, evidence, risks** when provided.
- [ ] Missing report data is represented transparently without fake values.
- [ ] Review suspicion/AI-generated indicators are described as signals, not verified accusations.
- [ ] Evidence links/expanders are functional and attributed to actual source records.
- [ ] No analysis history is invented; no report is shown to unauthorized users.
- [ ] Responsive layouts work at 390/834/1440px without clipped score content or horizontal overflow.
- [ ] Buttons/links, keyboard focus, labels and error announcements are usable.
- [ ] Loading, empty, error, failed analysis and partial-evidence states are tested.
- [ ] `npm run lint`, typecheck, and any relevant tests/build complete when scripts exist (report failures accurately).
- [ ] Existing backend integrations remain intact; mocks, if any, are explicitly declared and isolated.

## K. Recommended Codex execution instruction

When asked to implement UI from this file, follow this order:

1. Inspect repository files, existing route structure, API documentation, and any official FR IDs/specs.
2. Write a concise execution plan and note any differences from this document.
3. Establish tokens/layout components without rewriting unrelated application logic.
4. Build workspace, submission, progress, and trust report UI using typed backend response adapters.
5. Add history, evidence details, auth/profile **only to the extent required/supported**.
6. Complete all fallback/loading/error/uncertainty states.
7. Verify UI at the three target viewport widths, test keyboard flow, and run existing checks.
8. Summarize changes, tests, and known API/backend blockers.

---

# Appendix A — Original Apple Design Reference (user-provided)

This section reproduces the supplied Apple-design-analysis design context for fidelity. The original descriptive references to Apple store/product component examples **do not imply those commercial features must be implemented in Trust Me**. The adaptation and product requirements above take precedence for Trust Me workflows.

---
version: alpha
name: Apple-design-analysis
description: A photography-first interface that turns marketing into a museum gallery. Edge-to-edge product tiles alternate light and dark canvases, framed by SF Pro Display headlines with negative letter-spacing and a single Action Blue (#0066cc) interactive color. UI chrome recedes so the product can speak — no decorative gradients, no shadows on chrome, only the one signature drop-shadow under product imagery resting on a surface.

colors:
  primary: "#0066cc"
  primary-focus: "#0071e3"
  primary-on-dark: "#2997ff"
  ink: "#1d1d1f"
  body: "#1d1d1f"
  body-on-dark: "#ffffff"
  body-muted: "#cccccc"
  ink-muted-80: "#333333"
  ink-muted-48: "#7a7a7a"
  divider-soft: "#f0f0f0"
  hairline: "#e0e0e0"
  canvas: "#ffffff"
  canvas-parchment: "#f5f5f7"
  surface-pearl: "#fafafc"
  surface-tile-1: "#272729"
  surface-tile-2: "#2a2a2c"
  surface-tile-3: "#252527"
  surface-black: "#000000"
  surface-chip-translucent: "#d2d2d7"
  on-primary: "#ffffff"
  on-dark: "#ffffff"

typography:
  hero-display:
    fontFamily: "SF Pro Display, system-ui, -apple-system, sans-serif"
    fontSize: 56px
    fontWeight: 600
    lineHeight: 1.07
    letterSpacing: -0.28px
  display-lg:
    fontFamily: "SF Pro Display, system-ui, -apple-system, sans-serif"
    fontSize: 40px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: 0
  display-md:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 34px
    fontWeight: 600
    lineHeight: 1.47
    letterSpacing: -0.374px
  lead:
    fontFamily: "SF Pro Display, system-ui, -apple-system, sans-serif"
    fontSize: 28px
    fontWeight: 400
    lineHeight: 1.14
    letterSpacing: 0.196px
  lead-airy:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 24px
    fontWeight: 300
    lineHeight: 1.5
    letterSpacing: 0
  tagline:
    fontFamily: "SF Pro Display, system-ui, -apple-system, sans-serif"
    fontSize: 21px
    fontWeight: 600
    lineHeight: 1.19
    letterSpacing: 0.231px
  body-strong:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 17px
    fontWeight: 600
    lineHeight: 1.24
    letterSpacing: -0.374px
  body:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 17px
    fontWeight: 400
    lineHeight: 1.47
    letterSpacing: -0.374px
  dense-link:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 17px
    fontWeight: 400
    lineHeight: 2.41
    letterSpacing: 0
  caption:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.43
    letterSpacing: -0.224px
  caption-strong:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.29
    letterSpacing: -0.224px
  button-large:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 18px
    fontWeight: 300
    lineHeight: 1.0
    letterSpacing: 0
  button-utility:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.29
    letterSpacing: -0.224px
  fine-print:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: -0.12px
  micro-legal:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 10px
    fontWeight: 400
    lineHeight: 1.3
    letterSpacing: -0.08px
  nav-link:
    fontFamily: "SF Pro Text, system-ui, -apple-system, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.0
    letterSpacing: -0.12px

rounded:
  none: 0px
  xs: 5px
  sm: 8px
  md: 11px
  lg: 18px
  pill: 9999px
  full: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 17px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 80px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: 11px 22px
  button-primary-focus:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
  button-primary-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
  button-secondary-pill:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: 11px 22px
  button-dark-utility:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-dark}"
    typography: "{typography.button-utility}"
    rounded: "{rounded.sm}"
    padding: 8px 15px
  button-pearl-capsule:
    backgroundColor: "{colors.surface-pearl}"
    textColor: "{colors.ink-muted-80}"
    typography: "{typography.caption}"
    rounded: "{rounded.md}"
    padding: 8px 14px
  button-store-hero:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-large}"
    rounded: "{rounded.pill}"
    padding: 14px 28px
  button-icon-circular:
    backgroundColor: "{colors.surface-chip-translucent}"
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    size: 44px
  text-link:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    typography: "{typography.body}"
  text-link-on-dark:
    backgroundColor: transparent
    textColor: "{colors.primary-on-dark}"
    typography: "{typography.body}"
  global-nav:
    backgroundColor: "{colors.surface-black}"
    textColor: "{colors.on-dark}"
    typography: "{typography.nav-link}"
    height: 44px
  sub-nav-frosted:
    backgroundColor: "{colors.canvas-parchment}"
    textColor: "{colors.ink}"
    typography: "{typography.tagline}"
    height: 52px
  product-tile-light:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.display-lg}"
    rounded: "{rounded.none}"
    padding: 80px
  product-tile-parchment:
    backgroundColor: "{colors.canvas-parchment}"
    textColor: "{colors.ink}"
    typography: "{typography.display-lg}"
    rounded: "{rounded.none}"
    padding: 80px
  product-tile-dark:
    backgroundColor: "{colors.surface-tile-1}"
    textColor: "{colors.on-dark}"
    typography: "{typography.display-lg}"
    rounded: "{rounded.none}"
    padding: 80px
  product-tile-dark-2:
    backgroundColor: "{colors.surface-tile-2}"
    textColor: "{colors.on-dark}"
    rounded: "{rounded.none}"
  product-tile-dark-3:
    backgroundColor: "{colors.surface-tile-3}"
    textColor: "{colors.on-dark}"
    rounded: "{rounded.none}"
  store-utility-card:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-strong}"
    rounded: "{rounded.lg}"
    padding: 24px
  configurator-option-chip:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 12px 16px
  configurator-option-chip-selected:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  search-input:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: 12px 20px
    height: 44px
  floating-sticky-bar:
    backgroundColor: "{colors.canvas-parchment}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    height: 64px
    padding: 12px 32px
  environment-quote-card:
    backgroundColor: "{colors.surface-tile-1}"
    textColor: "{colors.on-dark}"
    typography: "{typography.display-lg}"
    rounded: "{rounded.none}"
    padding: 80px
  footer:
    backgroundColor: "{colors.canvas-parchment}"
    textColor: "{colors.ink-muted-80}"
    typography: "{typography.fine-print}"
    padding: 64px
---

## Overview

Apple's web presence is a masterclass in **reverent product photography framed by near-invisible UI**. Every page is a stack of edge-to-edge product "tiles" — alternating light and dark canvases, each centered on a hero headline, a one-line tagline, two tiny blue pill CTAs, and an impossibly crisp product render. Nothing competes with the product. Typography is confident but quiet; color is either pure white, an off-white parchment, or a near-black tile; interactive elements are a single, quiet blue.

Density is unusually low even by contemporary SaaS standards. Each tile occupies roughly one viewport, and there is no decorative chrome — no borders, no gradients, no decorative frames, no shadows on headlines. Elevation appears only when a product image rests on a surface (a single soft `rgba(0, 0, 0, 0.22) 3px 5px 30px` drop for visual weight). The result is a catalog that feels more like a museum gallery: the wall disappears and the artifact takes over.

Store and shop surfaces retain the same chassis but switch modes. The product configurator (iPhone 17 Pro, accessories grid) introduces a tight grid of white utility cards at `{rounded.lg}` (18px) radius with a thin border, paired with a persistent thin sub-nav strip. The environment page leans darker and more editorial. Across all five surfaces the typographic system, spacing rhythm, and the single blue accent are consistent — this is one design language expressed at different volumes.

**Key Characteristics:**
- Photography-first presentation; UI recedes so the product can speak.
- Alternating full-bleed tile sections: white/parchment ↔ near-black, with the color change itself acting as the section divider.
- Single blue accent (`{colors.primary}` — #0066cc) carries every interactive element. No second brand color exists.
- Two button grammars: tiny blue pill CTAs (`{rounded.pill}`) and compact utility rects (`{rounded.sm}`).
- SF Pro Display + SF Pro Text — negative letter-spacing at display sizes for the signature "Apple tight" headline feel.
- Whisper-soft elevation used only when a product image needs to breathe — exactly one drop-shadow in the entire system.
- Tight two-row nav: slim `{component.global-nav}` + product-specific `{component.sub-nav-frosted}` with persistent right-aligned primary CTA.
- Section rhythm across multiple pages: light hero → dark product tile → light utility tile → dark tile → parchment footer — a predictable pulse.

## Colors

> **Source pages analyzed:** homepage, environment, store, iPhone 17 Pro buy page, accessories index. The color system is identical across all five surfaces; only the surface-mode mix differs.

### Brand & Accent
- **Action Blue** (`{colors.primary}` — #0066cc): The single brand-level interactive color. All text links, all blue pill CTAs ("Learn more", "Buy"), and the focus ring root. This is Apple's quiet but universal "click me" signal. Press state shifts to a slightly darker variant via the active scale transform rather than a hex change.
- **Focus Blue** (`{colors.primary-focus}` — #0071e3): A marginally brighter sibling of Action Blue, reserved for the keyboard focus ring on buttons (`outline: 2px solid`).
- **Sky Link Blue** (`{colors.primary-on-dark}` — #2997ff): A brighter blue used on dark surfaces for in-copy links and inline callouts, where Action Blue would disappear against the tile background.

### Surface
- **Pure White** (`{colors.canvas}` — #ffffff): The dominant canvas. Content, utility cards, store tiles, configurator grids.
- **Parchment** (`{colors.canvas-parchment}` — #f5f5f7): The signature Apple off-white. Used for alternating light tiles, footer region, and the default page canvas in store utility sections. Just different enough from white to create rhythm.
- **Pearl Button** (`{colors.surface-pearl}` — #fafafc): A near-white used as the fill for secondary "ghost" buttons — lighter than the parchment canvas so the button still reads as a button against `{colors.canvas-parchment}`.
- **Near-Black Tile 1** (`{colors.surface-tile-1}` — #272729): The primary dark-tile surface on the homepage product grid.
- **Near-Black Tile 2** (`{colors.surface-tile-2}` — #2a2a2c): A micro-step lighter — used where a dark tile sits directly above or below Tile 1 to create the faintest separation.
- **Near-Black Tile 3** (`{colors.surface-tile-3}` — #252527): A micro-step darker — used at the bottom of the stack and in embedded video/player frames.
- **Pure Black** (`{colors.surface-black}` — #000000): Reserved for true void — video player backgrounds, edge-to-edge photographic overlays, the global nav bar background.
- **Translucent Chip Gray** (`{colors.surface-chip-translucent}` — #d2d2d7): The base hex of the translucent gray chip used over photography for circular control buttons. In production, applied at ~64% alpha as `rgba(210, 210, 215, 0.64)`.

### Text
- **Near-Black Ink** (`{colors.ink}` — #1d1d1f): The voice of every headline, every body paragraph, and the dark utility button's fill. Chosen instead of pure black to keep the page feeling photographic rather than printed.
- **Body** (`{colors.body}` — #1d1d1f): Same hex as ink — Apple uses one near-black tone for all text on light surfaces.
- **Body On Dark** (`{colors.body-on-dark}` — #ffffff): All text on dark tiles and on the global nav bar.
- **Body Muted** (`{colors.body-muted}` — #cccccc): Secondary copy on dark tiles where pure white would be too loud.
- **Ink Muted 80** (`{colors.ink-muted-80}` — #333333): Body text on the white Pearl Button surface — slightly softer than pure black.
- **Ink Muted 48** (`{colors.ink-muted-48}` — #7a7a7a): Disabled button text and legal fine-print.

### Hairlines & Borders
- **Divider Soft** (`{colors.divider-soft}` — #f0f0f0): The "border" tone on secondary buttons — functions as a ring shadow rather than a hard line. In production, often applied as `rgba(0, 0, 0, 0.04)`.
- **Hairline** (`{colors.hairline}` — #e0e0e0): The 1px hairline border on store utility cards and configurator chips.

### Brand Gradient
**No decorative gradients.** Atmospheric depth on product photography (the iPhone 17 Pro camera plate, the Apple Watch bands, AirPods reflections) is inherent to the imagery, not a CSS gradient overlay. The environment page's hero uses photographic atmosphere (mountain vista at dawn) but no gradient tokens are defined. Apple is the rare luxury-brand site with zero gradient-based design tokens.

## Typography

### Font Family
- **Display**: `SF Pro Display, system-ui, -apple-system, sans-serif` — Apple's proprietary display face, optimized for sizes ≥ 19px. Defines the voice of every headline.
- **Body / UI**: `SF Pro Text, system-ui, -apple-system, sans-serif` — the text-optimized variant used for body copy, captions, buttons, and links below 20px.
- **OpenType features**: `font-variant-numeric: numerator` is enabled on numeric links (pricing tables, spec sheets). Display sizes rely on tight tracking rather than contextual ligatures.

### Hierarchy

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| `{typography.hero-display}` | 56px | 600 | 1.07 | -0.28px | Hero headline; the signature "Apple tight" tracking |
| `{typography.display-lg}` | 40px | 600 | 1.10 | 0 | Tile headlines atop every product tile |
| `{typography.display-md}` | 34px | 600 | 1.47 | -0.374px | Section heads (SF Pro Text at display proportions) |
| `{typography.lead}` | 28px | 400 | 1.14 | 0.196px | Product tile subcopy |
| `{typography.lead-airy}` | 24px | 300 | 1.5 | 0 | Environment-page lead paragraphs (the rare weight 300) |
| `{typography.tagline}` | 21px | 600 | 1.19 | 0.231px | Sub-tile tagline; sub-nav category name |
| `{typography.body-strong}` | 17px | 600 | 1.24 | -0.374px | Inline strong emphasis |
| `{typography.body}` | 17px | 400 | 1.47 | -0.374px | Default paragraph |
| `{typography.dense-link}` | 17px | 400 | 2.41 | 0 | Footer / store utility link lists (relaxed leading) |
| `{typography.caption}` | 14px | 400 | 1.43 | -0.224px | Secondary captions, button text |
| `{typography.caption-strong}` | 14px | 600 | 1.29 | -0.224px | Emphasized captions |
| `{typography.button-large}` | 18px | 300 | 1.0 | 0 | Store hero CTAs (the rare weight 300) |
| `{typography.button-utility}` | 14px | 400 | 1.29 | -0.224px | Utility/nav button labels |
| `{typography.fine-print}` | 12px | 400 | 1.0 | -0.12px | Fine-print, footer body |
| `{typography.micro-legal}` | 10px | 400 | 1.3 | -0.08px | Micro legal disclaimers |
| `{typography.nav-link}` | 12px | 400 | 1.0 | -0.12px | Global nav menu items |

### Principles

- **Negative letter-spacing at display sizes.** Every headline at 17px and up carries a slight tracking tighten (`-0.12 → -0.374px`). This produces the iconic "Apple tight" headline cadence. Never used at 12px or below.
- **Body copy at 17px, not 16px.** Apple breaks the SaaS convention and runs paragraph text at 17px. The extra pixel gives the page an unmistakable "reading, not scanning" pace.
- **Weight 300 is real and rare.** Used deliberately on a handful of large-size reads (`{typography.button-large}` at 18px/300 and `{typography.lead-airy}` at 24px/300). It's not an accident — it's a light-atmosphere cue reserved for moments where the content should feel airy.
- **Weight 600, not 700, for headlines.** Apple's headlines sit at weight 600. Weight 700 is used sparingly for `{typography.tagline}` (21px) when a touch more assertion is needed.
- **Line-height is context-specific.** Display sizes use 1.07–1.19 (tight). Body uses 1.47. Utility link stacks in the footer/store use an unusually relaxed 2.41 (`{typography.dense-link}`). The 2.41 is not a bug — it's how the footer's dense link columns breathe.
- **Weight 500 is deliberately absent.** The ladder is 300 / 400 / 600 / 700. Mid-weight readings always use 600.

### Note on Font Substitutes
SF Pro is Apple's proprietary system font. When building off-system:

- Use `system-ui, -apple-system, BlinkMacSystemFont` as the first stack entry — on macOS/iOS/Safari this resolves to the real SF Pro.
- For non-Apple platforms, **Inter** (Google Fonts, variable) is the closest open-source equivalent. Inter at weight 600 with `font-feature-settings: "ss03"` approximates SF Pro's rounded "a" character.
- Nudge `letter-spacing` down by `-0.01em` on display sizes to re-create the Apple tight feel; Inter's default tracking runs slightly wider than SF Pro.
- For body text, tighten line-height by `0.03` (from 1.47 → 1.44) when substituting Inter — Inter's taller x-height needs less leading.

## Layout

### Spacing System
- **Base unit:** 8px. Sub-base values (2, 4, 5, 6, 7) are used for tight typographic adjustments; structural layout snaps to 8/12/16/20/24.
- **Tokens:** `{spacing.xxs}` 4px · `{spacing.xs}` 8px · `{spacing.sm}` 12px · `{spacing.md}` 17px · `{spacing.lg}` 24px · `{spacing.xl}` 32px · `{spacing.xxl}` 48px · `{spacing.section}` 80px.
- **Section vertical padding:** `{spacing.section}` (80px) inside a product tile; tiles stack edge-to-edge with 0 gap (the color change provides the break).
- **Card padding:** `{spacing.lg}` (24px) inside utility grid cards.
- **Button padding:** 8–11px vertical, 15–22px horizontal.
- **Universal rhythm constants:** the 17px body line-height multiplier (~25px line) and 21px tagline size show up on every analyzed page.

### Grid & Container
- **Max content width:** ~980px on text-heavy sections (environment), ~1440px on product grids (store, accessories), full-bleed for product tiles (homepage).
- **Column patterns:** 3 to 5 column utility card grid on store/accessories; 2-column side-by-side tiles on homepage occasional sections; single-column centered stack on product tile heroes.
- **Gutters:** 20–24px between cards in a utility grid.

### Whitespace Philosophy
Apple's whitespace is the product's pedestal. Every tile begins with at least 64px of air above its headline and 48–64px below. Product renders are never crowded; the nearest content to a product image is at least 40px away. The footer is the only area that breaks this — there, Apple goes deliberately dense to make the full information architecture visible at a glance.

## Elevation & Depth

| Level | Treatment | Use |
|---|---|---|
| Flat | No shadow, no border | Full-bleed tiles, global nav, footer, body sections |
| Soft hairline | 1px `rgba(0, 0, 0, 0.08)` border | Utility cards, sub-nav frosted-glass separator |
| Backdrop blur | `backdrop-filter: blur(N)` on Parchment 80% | Sub-nav and the iPhone buy floating sticky bar |
| Product shadow | `rgba(0, 0, 0, 0.22) 3px 5px 30px 0` | Product renders resting on a surface (the only true "shadow" in the system) |

**Shadow philosophy.** Apple uses **exactly one** drop-shadow, and it is applied to photographic product imagery — never to cards, never to buttons, never to text. Elevation in the UI comes from (a) surface-color change (light tile ↔ dark tile) and (b) backdrop-blur on sticky bars. The single shadow is about giving the product weight, not about UI hierarchy.

### Decorative Depth
- **Atmospheric imagery** on the environment page (photographic vista) supplies mood; no CSS gradient involved.
- **Edge-to-edge tile alternation** creates rhythm without borders or shadows — the color change itself is the divider.
- **Backdrop-filter blur** on `{component.sub-nav-frosted}` and `{component.floating-sticky-bar}` creates a "floating over content" effect that's functional, not decorative.

## Shapes

### Border Radius Scale

| Token | Value | Use |
|---|---|---|
| `{rounded.none}` | 0px | Full-bleed product tiles (no corner rounding) |
| `{rounded.xs}` | 5px | Inline links when styled as subtle chips (rare) |
| `{rounded.sm}` | 8px | Dark utility buttons (Sign In, Bag), inline card imagery |
| `{rounded.md}` | 11px | White Pearl Button capsules |
| `{rounded.lg}` | 18px | Store utility cards, accessories grid cards |
| `{rounded.pill}` | 9999px | Primary blue pill CTAs, sub-nav buy button, configurator option chips, search input — the signature Apple pill |
| `{rounded.full}` | 9999px / 50% | Circular control chips floating over photography |

### Photography Geometry
- **Hero imagery**: full-bleed, 21:9 or taller on the homepage; 16:9 on environment and shop pages. Product renders are photographic-realistic, often shot on a tinted surface that becomes the tile background.
- **Product renders**: PNG/WebP with transparency; rest on a surface tile and pick up the system shadow.
- **Accessory grid**: square 1:1 crops at `{rounded.lg}` (18px) radius, light neutral backgrounds, product centered with 20–40px internal padding.
- **No rounded imagery in hero tiles** — images are full-bleed rectangular. Rounding (`{rounded.sm}`, `{rounded.lg}`) appears only on inline card imagery.
- Lazy-loading via responsive `srcset` and `sizes` across all breakpoints; CDN-optimized WebP.

## Components

### Top Navigation

**`global-nav`** — Persistent, ultra-thin black nav bar pinned to the top of every page. Background `{colors.surface-black}`, height 44px, text `{colors.on-dark}` in `{typography.nav-link}` (12px / 400 / -0.12px tracking). Links are quiet, spaced ~20px apart, running edge-to-edge across the top. Right-aligned cluster: Search, Bag icons — always visible. On mobile, collapses to hamburger at ~834px and the Apple logo centers.

**`sub-nav-frosted`** — Surface-specific nav that sticks below the global nav. Background `{colors.canvas-parchment}` at 80% opacity with backdrop-filter blur, creating a frosted-glass effect. Height 52px. Content on left: product category name ("iPhone", "Store", "Accessories") in `{typography.tagline}` (21px / 600). Content right: inline nav links in `{typography.button-utility}` (14px), ending in a persistent `{component.button-primary}` ("Buy") or a utility link.

### Buttons

**`button-primary`** — The signature Apple action. Background `{colors.primary}` (Action Blue #0066cc), text `{colors.on-primary}` in `{typography.body}` (SF Pro Text 17px / 400), rounded `{rounded.pill}` (full pill — capsule-shaped), padding 11px × 22px. The full-pill radius IS the brand action signal.
- Active state: `{component.button-primary-active}` — `transform: scale(0.95)` (the system-wide micro-interaction).
- Focus state: `{component.button-primary-focus}` — 2px solid `{colors.primary-focus}` outline.

**`button-secondary-pill`** — Used as the second CTA when two blue pills appear together ("Learn more" / "Buy"). Background transparent, text `{colors.primary}`, 1px solid `{colors.primary}` border, rounded `{rounded.pill}`, padding 11px × 22px. Reads as a "ghost pill."

**`button-dark-utility`** — Global nav actions (Sign In, Bag, language selector). Background `{colors.ink}` (#1d1d1f), text `{colors.on-dark}` in `{typography.button-utility}` (14px / 400 / -0.224px tracking), rounded `{rounded.sm}` (8px), padding 8px × 15px. Active state shrinks via `transform: scale(0.95)`.

**`button-pearl-capsule`** — Product-card secondary button. Background `{colors.surface-pearl}` (#fafafc), text `{colors.ink-muted-80}` in `{typography.caption}` (14px), 3px solid `{colors.divider-soft}` border (functions as a soft ring rather than a visible line), rounded `{rounded.md}` (11px), padding 8px × 14px.

**`button-store-hero`** — A larger primary CTA used on store hero surfaces. Same Action Blue + Paper White as `{component.button-primary}`, but with `{typography.button-large}` (18px / 300 — note the rare weight 300) and slightly more padding (14px × 28px). Used sparingly on the store landing.

**`button-icon-circular`** — Floats over photography. 44 × 44px, background `{colors.surface-chip-translucent}` at ~64% alpha, icon in `{colors.ink}`, rounded `{rounded.full}`. Used for carousel controls, close buttons, and in-image controls (product image thumbnails on the iPhone buy page).

**`text-link`** — Inline body links in `{colors.primary}` (Action Blue). Underlined or non-underlined per context.

**`text-link-on-dark`** — Inline body links on dark tiles in `{colors.primary-on-dark}` (Sky Link Blue #2997ff) — Action Blue would disappear against `{colors.surface-tile-1}`.

### Cards & Containers

**`product-tile-light`** — Full-bleed light tile. Background `{colors.canvas}` (white), text `{colors.ink}`, rounded `{rounded.none}` (0 — tiles touch edges), vertical padding `{spacing.section}` (80px). Centered stack: product name in `{typography.display-lg}` (40px / 600) → one-line tagline in `{typography.lead}` (28px / 400) → two `{component.button-primary}` CTAs ("Learn more" / "Buy") → product render resting on the surface with the system shadow.

**`product-tile-parchment`** — Same as `{component.product-tile-light}` but on `{colors.canvas-parchment}` (#f5f5f7). Used to break two consecutive white tiles.

**`product-tile-dark`** — Full-bleed dark tile. Background `{colors.surface-tile-1}` (#272729), text `{colors.on-dark}`, rounded `{rounded.none}`, vertical padding `{spacing.section}` (80px). Same content stack as the light tile but with `{component.text-link-on-dark}` for inline copy and `{component.button-primary}` (Action Blue still works on the dark surface). Used on the homepage product grid as the alternating dark band.

**`product-tile-dark-2`** — Variant on `{colors.surface-tile-2}` (#2a2a2c). Used where a dark tile sits directly above or below `{component.product-tile-dark}` to create the faintest separation through micro-step lightness change.

**`product-tile-dark-3`** — Variant on `{colors.surface-tile-3}` (#252527). Used at the bottom of the stack and in embedded video/player frames.

**`store-utility-card`** — Used in store grid and accessories grid. Background `{colors.canvas}` (white), 1px solid `{colors.hairline}` border, rounded `{rounded.lg}` (18px), padding `{spacing.lg}` (24px). Top: product image (1:1 crop with `{rounded.sm}` (8px) inner image radius). Below: product name in `{typography.body-strong}` (17px / 600), price in `{typography.body}` (17px / 400), and a `{component.text-link}` ("Buy" or "Learn more"). No shadow by default; product render itself carries the system product-shadow.

**`configurator-option-chip`** — Pill-shaped tappable cell used in the iPhone 17 Pro buy page. Background `{colors.canvas}`, text `{colors.ink}` in `{typography.caption}`, rounded `{rounded.pill}`, padding 12px × 16px. Contains a small product thumbnail + label + price delta. Arranged in a grid of 4–5 options per row.

**`configurator-option-chip-selected`** — Selected state. Border upgrades to 2px solid `{colors.primary-focus}`. Same shape, same content.

**`environment-quote-card`** — A photographic-canvas hero specific to the environment page. Dark photographic backdrop (mountain vista at dawn) with `{colors.surface-tile-1}` as the fallback color, centered white-text headline in `{typography.display-lg}` (40px), small green "Apple 2030" pictographic logo above the headline, single `{component.button-primary}` below. Padding `{spacing.section}` (80px).

**`floating-sticky-bar`** — Floats at the bottom of the viewport on the iPhone 17 Pro buy page during scroll. Background `{colors.canvas-parchment}` at 80% opacity with `backdrop-filter: blur(N)`, height 64px, padding 12px × 32px. Left: running price total in `{typography.body}`. Right: `{component.button-primary}` ("Add to Bag").

### Inputs & Forms

**`search-input`** — The accessories search input. Background `{colors.canvas}`, text `{colors.ink}` in `{typography.body}` (17px), 1px solid `rgba(0, 0, 0, 0.08)` border, rounded `{rounded.pill}` (full pill — search is also pill-shaped, matching the CTA grammar), padding 12px × 20px, height 44px. Leading icon: search glyph at 14px, muted tint.

Error and validation states were not surfaced in the analyzed pages.

### Footer

**`footer`** — Background `{colors.canvas-parchment}` (#f5f5f7), text `{colors.ink-muted-80}`. Link columns in `{typography.dense-link}` (17px / 400 / 2.41 line-height — the relaxed leading is what makes the dense columns scannable). Column headings in `{typography.caption-strong}` (14px / 600). Legal row at the very bottom in `{typography.fine-print}` (12px / 400) with `{colors.ink-muted-48}` text. Vertical padding 64px.

## Do's and Don'ts

### Do
- Use `{colors.primary}` (Action Blue #0066cc) for every interactive element — links, pill CTAs, focus signals — and nothing else. The single accent is non-negotiable.
- Set headlines in `{typography.hero-display}` or `{typography.display-lg}` with negative letter-spacing (`-0.28 → -0.374px`) to get the signature "Apple tight" cadence.
- Run body copy at `{typography.body}` (17px / 400 / 1.47 / -0.374px) — not 16px. The extra pixel defines the brand's reading pace.
- Alternate `{component.product-tile-light}` (or parchment) and `{component.product-tile-dark}` for full-bleed section rhythm. The color change IS the divider.
- Reserve `{rounded.pill}` for the primary blue CTA and any other element that should read as an "action" (configurator chips, search input, sticky bar CTA).
- Apply the single product-shadow (`rgba(0, 0, 0, 0.22) 3px 5px 30px`) only to product renders resting on a surface — never on cards, buttons, or text.
- Use `transform: scale(0.95)` as the active/press state on every button — it's the system-wide micro-interaction.
- Keep the global nav `{colors.surface-black}` (true black) — it's the only place pure black appears on most pages.

### Don't
- Don't introduce a second accent color; every "click me" signal is `{colors.primary}` (Action Blue).
- Don't add shadows to cards, buttons, or text — shadow is reserved for product imagery.
- Don't use gradients as decorative backgrounds; atmosphere comes from photography.
- Don't set body copy at weight 500 — Apple's ladder is 300 / 400 / 600 / 700, with 500 deliberately absent. Body is always 400; strong inline is 600; display is 600.
- Don't round full-bleed tiles — tiles are rectangular and edge-to-edge; the color change is the divider.
- Don't tighten line-height below 1.47 for body copy — the editorial leading is part of the brand.
- Don't mix radii grammars — use `{rounded.sm}` for compact utility, `{rounded.lg}` for utility cards, `{rounded.pill}` for pills, and nothing in between (except the rare `{rounded.md}` Pearl Button).
- Don't use `{colors.primary-on-dark}` (Sky Link Blue) on light surfaces — it's the dark-tile-only variant. Action Blue is for light surfaces.

## Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|---|---|---|
| Small phone | ≤ 419px | Single-column tiles; sub-nav collapses to category name + primary CTA only; hero typography drops to 28px |
| Phone | 420–640px | Single-column stack; product renders scale to 80% of tile width; hero h1 drops to 34px |
| Large phone | 641–735px | Tiles transition to tighter padding (48px vertical vs 80px); fine-print wraps |
| Tablet portrait | 736–833px | Global nav collapses to hamburger; sub-nav hides category chips, keeps primary CTA |
| Tablet landscape | 834–1023px | Global nav returns fully expanded; 3-column utility grids become 2-column |
| Small desktop | 1024–1068px | Product tiles use 2/3 width with margin gutters; hero h1 stays at 40px |
| Desktop | 1069–1440px | Full layout; 4–5 column store grids; 1440px content max |
| Wide desktop | ≥ 1441px | Content locks at 1440px, margins absorb extra width |

The structural breakpoints that matter for agents: 1440px (content lock), 1068px (small-desktop), 833px (tablet landscape switch), 734px (tablet portrait), 640px (phone), 480px (small phone).

### Touch Targets
- Minimum 44 × 44px. `{component.button-primary}` lands at ~44 × 100px (with the full-pill radius making the visible hit area more generous than the label suggests).
- `{component.button-icon-circular}` is exactly 44 × 44px.
- Global nav utility links are smaller (~32 × 80px) — they deliberately sit at a tighter target because they're precision desktop actions, and the mobile hamburger replaces them at ≤ 833px.

### Collapsing Strategy
- **Global nav**: full horizontal link row on desktop → collapses to Apple logo + hamburger + bag icon at 834px and below.
- **Sub-nav**: category name + inline links + primary CTA → category name + primary CTA only at mobile; inline links move into a hamburger tray.
- **Product tiles**: stack from 2-column to 1-column at 834px; vertical padding tightens from 80px → 48px at small-phone.
- **Utility grids** (store, accessories): 5-col → 4-col (1440px) → 3-col (1068px) → 2-col (834px) → 1-col (640px).
- **Hero typography**: `{typography.hero-display}` (56px) → `{typography.display-lg}` (40px) at 1068px → 34px at 640px → 28px at 419px.

### Image Behavior
- All product imagery uses responsive `srcset` with breakpoint-matched crops.
- Hero photography may switch art direction at mobile (e.g., the environment page's vista crops to a taller aspect ratio on mobile, framing the subject differently).
- Product renders maintain their 1:1 or 4:3 aspect ratios across breakpoints; only scale changes.
- Lazy-loading is default; the above-fold hero loads eagerly.

## Iteration Guide

1. Focus on ONE component at a time. Reference its YAML key directly (`{component.product-tile-dark}`, `{component.search-input}`).
2. Variants of an existing component (`-active`, `-focus`, `-2`, `-3`) live as separate entries in `components:`.
3. Use `{token.refs}` everywhere — never inline hex.
4. Never document hover. Default and Active/Pressed states only.
5. Display headlines stay SF Pro Display 600 with negative letter-spacing. Body stays SF Pro Text 400 at 17px. The boundary is unbreakable.
6. The single drop-shadow (`rgba(0, 0, 0, 0.22) 3px 5px 30px`) is reserved for product photography only.
7. When in doubt about emphasis: alternate surface (light → dark tile) before adding chrome.

## Known Gaps

- Form validation and error states were not surfaced on the analyzed pages; only the neutral search input is documented.
- The homepage's embedded video/player frame uses `{colors.surface-black}`; interior player controls are not documented (they're a platform widget, not a web-design token).
- Some component imagery is dynamic (rotating product hero) and its specific copy varies per surface — component specs name the structure, not the rotating content.
- Dark-mode counterparts for store and accessories utility cards were not surfaced on the analyzed pages; the system documented is the daytime/light-dominant variant Apple ships by default.
- Atmospheric photography (environment page mountain vista) is a content asset, not a design token; the documented `{component.environment-quote-card}` describes the structural surface only.
- The exact backdrop-filter blur radius on `{component.sub-nav-frosted}` and `{component.floating-sticky-bar}` is platform-dependent; production CSS uses `saturate(180%) blur(20px)` as a typical baseline but the value isn't formalized as a token.



Use the design system above for all UI you generate.
