# Bevy + egui Parity Specification

**Status:** Draft for implementation
**Revision:** 1
**Date:** 2026-11-20
**Target:** `bevy_egui_test`, using Bevy 0.19.1, `bevy_egui` 0.42.0, egui 0.36.2, and `egui_plot` 0.37.0
**Implementation plan:** `docs/bevy-parity-implementation-plan.md`

## 1. Purpose

Define the bounded work required for Bevy + egui to participate directly in the Slint/QML comparison without discarding its ECS, GPU rendering, numerical capabilities, or existing independent demonstrations.

Parity means equivalent **observable behavior, input data, workload dimensions, interactions, and evidence**. It does not mean identical source architecture, rendering algorithms, widget internals, or pixels.

The key words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative. A requirement marked MUST is part of full parity even if Slint or QML currently needs a corresponding correction. Existing stubs and deviations do not redefine the target.

This document does not activate any benchmark scenario. Activation remains governed by `specifications/comparison-contract.md`.

## 2. References and precedence

When requirements conflict, use this order:

1. An active, versioned scenario in the parent repository.
2. `specifications/comparison-contract.md` and this parity specification.
3. The common feature specification, `docs/UI_Framework_Comparison_Test_App_Specification.md`, in Slint/QML.
4. Slint behavior as the page-structure and stable-ID reference.
5. QML behavior as an additional behavioral reference.
6. Existing implementation deviations, which describe current reality but do not relax parity requirements.

No existing historical measurement is an acceptance oracle.

## 3. Goals

The completed parity pass MUST provide:

- The canonical 3 Browser / 3 Charting / 11 Quantitative Visualization shell.
- Stable programmatic page selection and common navigation behavior.
- Common Browser 1, Browser 2, Browser 3, analytical-chart, stock-chart, and pivot-chart workloads.
- Common-fixture modes for all eleven quantitative views.
- Equivalent mouse, keyboard, editing, selection, reset, and live-update behavior for active scenarios.
- Light, Dark, and System theme selection with documented rendering coverage.
- Explicit initialization and hidden-view behavior suitable for startup and idle comparisons.
- Reproducible diagnostics, smoke tests, screenshots, and raw scenario evidence.
- Preservation of existing Bevy GPU and numerical demonstrations as separately identified extensions.

## 4. Non-goals

The parity pass MUST NOT:

- Replace Bevy GPU rendering with Slint-style software rasterization merely for implementation similarity.
- Replace `egui_plot` or egui rendering with Qt or Slint adapters.
- Port Slint's `ModelNotify`, `RefCell`, thread-local diagnostics, or callback architecture.
- Reproduce QML's C++ object model, timers, or placeholder pages.
- Delete working Line, Scatter, Histogram, computed-PCA, exact-frontier, or other existing demonstrations.
- Add networking, remote market feeds, persistence, provider configuration, or credential handling.
- Require pixel-identical output across font rasterizers, software canvases, Qt Graphs, and Bevy GPU scenes.
- Require the legacy 25-column Browser 2 workload for functional parity.
- Treat a page title, placeholder, logging stub, or static screenshot as functional parity.

## 5. Parity levels and gates

### 5.1 Development parity

A view has development parity when its fixture, state, controls, and interactions are implemented and unit-tested. Its scenario status remains `unverified` until runtime evidence exists.

### 5.2 Full functional parity

Full functional parity requires all MUST requirements in this document, except those explicitly deferred by an approved scenario deviation. Each deviation MUST identify the scenario, affected implementations, reason, and evidence.

### 5.3 Controlled-comparison readiness

A controlled comparison additionally requires:

- Shared fixture/generator revisions and SHA-256 verification in all participating implementations.
- Active scenario revisions with executable actions and expected results.
- Exact source commits and build/environment manifests.
- Successful smoke tests and equivalent screenshots.
- Compatible startup, memory, timing, and update-rate definitions.
- Immutable raw results.

Bevy MAY participate in a core subset before every close-twin extension is complete, but unsupported behavior MUST remain `partial` or `not-implemented` rather than disappearing from the matrix.

## 6. Canonical decisions

These decisions resolve conflicts found in the existing specifications and implementations.

| Topic | Canonical parity decision |
|---|---|
| Page structure | 3 primary areas; 3 Browser, 3 Charting, and 11 Quantitative secondary pages |
| Stable IDs | Use Slint's IDs in Bevy; retain QML IDs only as aliases |
| Controlled viewport | 1600×1000 logical pixels at 100% scaling unless a scenario says otherwise |
| Resize checks | 1200×750 for normal desktop use and 660×750 for constrained navigation; 640-wide legacy tests remain non-gating until all minimum sizes are normalized |
| Browser 2 columns | 19 columns; a 25-column performance variant requires a separate fixture and six explicitly defined additional columns |
| String ordering | Deterministic ordinal/lexical ordering for the common ASCII fixture; locale-aware collation is an extension |
| Analytical default | 500 business days, initial equity 100,000, base date 2021-01-04, seed input 20260819 to the common generator |
| Analytical stress sizes | 2,500 / 20,000 / 100,000 / 1,000,000 source points, with 500 as the default functional size |
| Model accuracy | Common controlled fixture is a 3×3 confusion matrix; binary-classifier metrics MAY remain extensions |
| Stock fixture | ACME; 1,260 daily bars plus 20,000 intraday bars; C-P4 uses 20,000 source candles and 500–2,000 visible candles |
| Existing Slint stock sizes | 750/30,000 remain stress profiles until the shared canonical profile is available; they do not replace the common stock fixture |
| Pivot fixture | Nine Slint symbols × 1,500 business days, base seed input 20260821, per-symbol deterministic derivation fixed by the common generator |
| Global live cadence | 500 ms / 2 Hz for Browser 2, Browser 3, analytical optimization, and common stock updates |
| Quantitative live rates | Preserve specialized 1/10/30 Hz controls where defined; do not flatten them into the global 500 ms scheduler |
| Reset View | Reset only the active view's transient presentation state |
| Reset Demo Data | Restore deterministic source data and clear dependent edits/history/caches without resetting unrelated navigation or theme |
| Export | In-app export is optional unless promoted by an active scenario; external screenshot evidence is mandatory |
| Numeric algorithms | Common rendering fixtures and exact numerical demonstrations are separate scenario classes |
| Pixel comparison | Use structural/state oracles and human-reviewed equivalent screenshots, not cross-framework pixel golden files |

Any change to these decisions that affects results requires new fixture or scenario revisions.

## 7. Canonical page identity and navigation

### 7.1 Page IDs

Bevy MUST expose these IDs through a programmatic selection API:

| Page | Canonical Bevy/Slint ID | Existing QML alias |
|---|---|---|
| Browser primary | `primary.browser` | Same |
| Charting primary | `primary.charting` | Same |
| Quant primary | `primary.quantviz` | Same |
| Browser 1 | `browser.browser1` | Same |
| Browser 2 | `browser.browser2` | Same |
| Browser 3 | `browser.browser3` | Same |
| Analytical chart | `chart.analytical` | `chart.basic` |
| Stock chart | `chart.stock` | `chart.streaming` |
| Pivot chart | `chart.pivot` | `chart.multiseries` |
| Volatility surface | `quant.vol-surface` | `quant.volsurface` |
| Factor structure | `quant.factor-structure` | `quant.factorstructure` |
| Correlation surface | `quant.correlation` | Same |
| Efficient frontier | `quant.frontier` | `quant.efficientfrontier` |
| PCA manifold | `quant.pca` | `quant.pcamanifold` |
| Regime map | `quant.regime` | `quant.regimemap` |
| Projection | `quant.projection` | Same |
| Network graph | `quant.network` | `quant.networkgraph` |
| Knowledge graph | `quant.knowledge` | `quant.advanced` |
| Monte Carlo | `quant.monte-carlo` | `quant.distribution` |
| Order book | `quant.order-book` | `quant.heatmap` |

QML's `browser.browser4` and `chart.layout` placeholders are excluded.

### 7.2 Shell requirements

**PAR-SHELL-001:** Bevy MUST retain independent secondary-page selection for each primary area.

**PAR-SHELL-002:** Programmatic selection MUST update content, selection indication, and accessibility state. Unknown IDs MUST return failure without changing selection.

**PAR-SHELL-003:** The toolbar MUST expose Reset View, Reset Demo Data, Live Simulation, Light/Dark/System, Diagnostics, and Advanced Tab enablement. Export MAY be exposed only when functional.

**PAR-SHELL-004:** Disabling the advanced target applies to `quant.order-book`. Programmatic selection of the disabled target MUST select `quant.monte-carlo`; ordinary next/previous navigation MUST skip disabled entries.

**PAR-SHELL-005:** Tab bars MUST support Left/Right, Home/End, Enter/Space, and Ctrl+Tab/Ctrl+Shift+Tab. Tab/Shift+Tab MUST follow a documented focus order without stealing editing keys. Focus movement and selected-page activation MUST remain distinct.

**PAR-SHELL-006:** Navigation and command events MUST enter a bounded log containing at least timestamp/order, source, target stable ID, and result. The target capacity is 200 entries.

**PAR-SHELL-007:** Selection and diagnostics MUST survive resize and theme changes without resetting source data.

## 8. Common fixture contract

### 8.1 Fixture authority

Parent-owned fixture manifests are authoritative. Existing Slint SplitMix64, QML LCG/QRandomGenerator, and Bevy generators are implementation-specific until their normalized output matches a published manifest.

Each fixture revision MUST define:

- RNG algorithm and state transitions, if generated.
- Numeric conversions, normal-distribution transform, and random-consumption order.
- Schema, column order, null representation, dates, calendars, and formulas.
- Stable source/entity IDs independent of display position.
- Dimensions and expected golden samples.
- SHA-256 of a canonical binary or textual serialization.

Seed equality alone is insufficient. Implementations MAY generate equivalent data internally or load shared files, but active scenarios MUST verify the same normalized content hash before measurement.

### 8.2 Startup and large fixtures

Default construction MUST NOT create Browser 2's 100,000-row fixture or an analytical 100,000/1,000,000-point fixture. Large workloads are created on explicit selection.

Startup scenarios MUST use the canonical small default state. Any fixture-loading work included in startup MUST be disclosed and applied consistently by the scenario.

Hidden views SHOULD defer heavy regeneration until reactivated, provided their state and revision are correct when shown.

### 8.3 Canonical fixture summary

| Fixture | Canonical content |
|---|---|
| Browser 1 | 2,000×12; seed input 20260819; special WA row at zero-based source ordinal 123; nullable RSI |
| Browser 2 | 1,000 or 100,000×19; source-stable row IDs; Target Weight conditional on Enabled |
| Browser 3 / correlation surface | Eight symbols, 250 return observations, symmetric 8×8 matrix |
| Analytical | 500-day default plus five controlled source sizes; common derived-series oracles |
| Stock | ACME, 1,260 daily plus 20,000 intraday; explicit session/calendar and indicator formulas |
| Pivot | Nine symbols, 1,500 business days, common OHLCV and pivot oracles |
| Volatility | 100×100, 250×250, 500×500 surfaces |
| Factor | 240-point ordinary baseline; 1K/10K/100K controlled sizes |
| Frontier | 12 assets, 2,500 portfolios, 40-bin sampled envelope, risk-free rate 0.02 |
| PCA rendering | 500 explicitly synthetic coordinates; computed PCA remains separate |
| Regime | 400 observations and five fixed regime classes |
| Projection | 5,000 points, five categories, three fixed layout families |
| Network | 100 nodes/300 edges and 1,000 nodes/5,000 edges |
| Knowledge | Versioned entities, relations, labels, types, initial visibility, and expansion oracle |
| Monte Carlo rendering | 600 paths×120 steps, initial value 1.0, defined 5/50/95 percentiles and histogram bins |
| Order book | 1,000 time columns×200 price levels with a common event stream |

## 9. Browser 1 — standard financial grid

### 9.1 Schema and presentation

**PAR-B1-001:** Columns MUST appear initially as:

`Symbol, Company, Sector, Price, Change %, Volume, Market Cap, RSI, Volatility, Signal, Score, Last Update`.

Initial logical widths are 90, 220, 140, 100, 100, 120, 130, 80, 110, 110, 90, and 170 respectively. Scenario-specific minimum widths may be added without changing data identity.

**PAR-B1-002:** The 2,000 rows MUST be virtualized or otherwise displayed without creating an unbounded per-frame full-table UI reconstruction.

**PAR-B1-003:** The WA row MUST retain stable identity through sorting and scrolling. Selection MUST use source identity, not visible position.

### 9.2 Behavior

**PAR-B1-010:** First sort activation is ascending, second descending, and subsequent activation alternates. Only the active column displays a direction marker.

**PAR-B1-011:** Numeric, string, and chronological values MUST use their appropriate types. Missing RSI values sort last in both directions. Ties use a deterministic stable-source or Symbol rule defined by the fixture oracle.

**PAR-B1-012:** Header-edge drag resizes without reordering. Other header drag reorders with insertion feedback and preserves logical/model mapping. Reset View restores column order and widths without regenerating data.

**PAR-B1-013:** Row selection, selected-column styling, and horizontal header/body scrolling MUST remain synchronized.

**PAR-B1-014:** Background precedence is special row, selected row, selected column, then alternating row. Selection and special status MUST NOT rely on color alone.

**PAR-B1-015:** Keyboard navigation MUST include arrows, Page Up/Down, Home/End, and Ctrl+Home/End once the grid owns focus.

## 10. Browser 2 — advanced editable grid

### 10.1 Schema and state

**PAR-B2-001:** Columns MUST appear initially as:

`Symbol, Company, Sector, Price, Change %, Volume, RSI, Signal, Score, Shares, Entry Price, Target Weight %, P/L %, Enabled, Strategy, Listed, Last Update, Notes, Trend`.

**PAR-B2-002:** The 1,000/100,000-row switch MUST replace or reset the fixture cleanly, preserve no invalid source IDs, and avoid constructing both datasets at startup.

**PAR-B2-003:** Source row IDs MUST survive sorting and filtering. Display/source mappings MUST round-trip without identity loss.

**PAR-B2-004:** Symbol, Last Update, and Signal are read-only. Target Weight % is editable only when Enabled is true. Other editors include text, integer, decimal, percentage, checkbox, and seven-choice Strategy selection.

### 10.2 Selection and editing

**PAR-B2-010:** Cell, Row, Column, and Range modes MUST support current cell, range anchor, extent/count status, Shift extension, and Ctrl-disjoint selection where the active scenario requires it.

**PAR-B2-011:** Editing starts through double-click, F2, or direct typing where appropriate. Enter/Tab/click-away commits valid input; Escape restores the original value. Invalid input MUST remain visible as invalid and MUST NOT mutate authoritative data.

**PAR-B2-012:** Live updates MUST preserve selection and scroll position and MUST NOT unexpectedly overwrite an active editor. Editing rows are skipped or otherwise protected according to a documented deterministic rule.

**PAR-B2-013:** Undo/redo MUST cover direct edits, checkbox changes, Delete, and paste. The history capacity is 500 mutations; behavior at the cap MUST be deterministic.

### 10.3 Formatting and operations

**PAR-B2-020:** The grid MUST demonstrate text, integer, decimal, percentage, currency, date/time, Boolean, enum, badge, progress/score, nullable, and sparkline presentations.

**PAR-B2-021:** Conditional styling includes Change % sign, RSI ≥70/≤30, Score ≥0.80, missing values, and stale Last Update. Meaning MUST NOT be encoded by color alone.

**PAR-B2-022:** Style precedence is Default, Column, Row, then Cell, with selection/dirty/editor overlays applied according to a documented priority.

**PAR-B2-023:** Global and per-column filtering MUST expose clear/count/status behavior. Sorting filtered data and changing column visibility MUST preserve source identity.

**PAR-B2-024:** Copy MUST produce correctly ordered TSV for the active contiguous range and the documented cell/row/column modes. Paste MUST route through normal validation, editing, dirty, and undo paths. Disjoint-selection copy MAY remain a disclosed limitation until promoted.

**PAR-B2-025:** The 100,000-row scenario MUST retain virtualization and report source, filtered, visible, and materialized counts.

### 10.4 Optional close-twin extensions

Frozen columns, multi-column sort, numeric selection aggregates, and content-fit autosizing are extensions unless an active scenario promotes them. QML's lack of frozen columns remains a disclosed deviation and MUST NOT cause Bevy's implementation to be scored as a common framework requirement.

## 11. Browser 3 — correlation heat map

**PAR-B3-001:** Symbols MUST be `SPY, QQQ, IWM, DIA, AAPL, MSFT, NVDA, XLE`, with 250 observations and an 8×8 matrix.

**PAR-B3-002:** The matrix MUST be symmetric with diagonal 1.00. Pearson correlation and covariance use sample denominator n−1. Pair statistics include covariance, annualized volatility using √252, and beta.

**PAR-B3-003:** Clustering uses average-linkage distance 1−correlation. Display reordering MUST NOT change symbol identity or pair statistics.

**PAR-B3-004:** The common diverging palette runs from blue #2166AC at −1 through a theme-appropriate neutral midpoint to orange #B35806 at +1. Numeric labels and selection cues MUST remain readable.

**PAR-B3-005:** Hover MUST expose exact values; cell selection MUST outline the cell and highlight corresponding headers. Header selection and 2/3-decimal display modes MUST preserve the same selected pair.

**PAR-B3-006:** Live mode MUST roll the common return window deterministically without resetting selection. Reset Demo Data restores the original 250-day window; Reset View resets only presentation/clustering state specified by the scenario.

## 12. Chart 1 — analytical chart

**PAR-C1-001:** Exactly nine canonical frames MUST be available in this order:

1. Equity Curve
2. Drawdown
3. Returns
4. Feature Importance
5. Optimization Convergence
6. Correlation Results
7. Model Accuracy
8. Risk Metrics
9. Attribution

**PAR-C1-002:** Default strategy returns follow `0.85 × benchmark + 0.0002 + idiosyncratic noise`; all numeric details are fixed by the common generator. Initial equity is 100,000 and the default is 500 business days from 2021-01-04.

**PAR-C1-003:** All line-like frames MUST share conventions for snapped crosshair, bounded tooltip, wheel zoom, drag pan, horizontal zoom, vertical autoscale, reset, and source/rendered counts.

**PAR-C1-004:** Shift-drag MUST create a trend-line preview and committed annotation with endpoints, delta/percentage, elapsed bars/time, and slope where applicable. Selection+Delete, context deletion, and Clear All MUST be supported for applicable annotations.

**PAR-C1-005:** Live optimization appends deterministic values without resetting the viewport. Follow behavior and user-panned behavior MUST be distinct.

**PAR-C1-006:** Source sizes 2,500/20,000/100,000/1,000,000 MUST use disclosed extrema-preserving LOD or equivalent rendering. Hover/statistics MUST clearly distinguish authoritative-source results from displayed samples.

**PAR-C1-007:** Feature Importance, Correlation Results, Model Accuracy, Risk Metrics, and Attribution MUST expose appropriate structured views rather than empty placeholders. Model Accuracy uses the shared 3×3 matrix in controlled runs.

## 13. Chart 2 — professional stock chart

**PAR-C2-001:** The common fixture contains ACME daily and intraday OHLCV data with explicit sessions, time zones, dates, and indicator formulas.

**PAR-C2-002:** Price, Volume, and Indicator panels MUST share one X viewport and crosshair while retaining independent Y scales and readable OHLCV/header readouts.

**PAR-C2-003:** Candlestick, OHLC, and Line renderers are mandatory. Heikin-Ashi, Renko, and hollow candles are extensions.

**PAR-C2-004:** Indicators MUST include SMA, EMA, Bollinger, VWAP/anchored VWAP, RSI, MACD, and ATR as applicable to the selected fixture. Formula parameters and warm-up/null behavior belong to the fixture oracle.

**PAR-C2-005:** Signals, fixed demonstration pattern regions, and events MUST remain distinguishable and inspectable. Pattern labels are demonstrations, not a pattern-recognition claim.

**PAR-C2-006:** Trend, horizontal, vertical, rectangle, and text annotations MUST support creation, selection, deletion, and Clear All. Keyboard Delete applies only when the chart owns focus and an annotation is selected.

**PAR-C2-007:** Live updates follow the common scheduler and deterministic event stream. They MUST preserve user viewport and annotations unless Follow is explicitly enabled.

**PAR-C2-008:** C-P4 uses 20,000 source candles and 500–2,000 visible candles. Source/rendered counts and any aggregation MUST be reported.

## 14. Chart 3 — pivot chart

**PAR-C3-001:** Symbols MUST be `SPY, SPX, QQQ, MINT, IEF, TLT, AAPL, MSFT, NVDA`, each with 1,500 business days from the common fixture.

**PAR-C3-002:** Daily, Weekly, and Monthly modes MUST produce OHLCV using first open, maximum high, minimum low, last close, and summed volume. Weekly uses the defined five-business-day index grouping; Monthly uses actual calendar year/month.

**PAR-C3-003:** High/Low Period defaults are 3 and buffers default to 0. Pivot tie handling MUST use the shared oracle; strict `>`/`<` is the preferred canonical rule and requires explicit revision if another rule is selected.

**PAR-C3-004:** Candle/OHLC/Line modes, symbol browsing, Daily/Weekly/Monthly, YTD/3M/6M/1Y/All/Custom ranges, pivots, zig-zag, derived steps, and complete crosshair readout MUST be available.

**PAR-C3-005:** The navigator MUST display the full-series overview and support center drag, edge resize with a five-bar minimum, outside-click recentering, and synchronized end-date/reset controls.

## 15. Quantitative Visualization parity

All eleven existing Bevy views MUST be retained. Common controlled scenarios MUST use shared inputs and stable selection oracles. Existing advanced computation MAY remain available as an extension, but MUST NOT silently alter a rendering-only scenario.

### 15.1 Common requirements

**PAR-Q-000:** Every view MUST expose reset, theme-aware legends/labels, meaningful hover or selection, and source/rendered diagnostics appropriate to its data.

**PAR-Q-001:** Every 3-D view MUST support orbit, pan, zoom, and reset with a scenario-defined initial camera.

**PAR-Q-002:** Offscreen cameras, animation, and expensive rebuilds MUST be gated by active view and 2-D/3-D mode. Hidden-state changes MUST remain correct upon reactivation.

### 15.2 Per-view requirements

| View | Common parity requirement | Preserved Bevy extension |
|---|---|---|
| Volatility surface | 100/250/500 resolutions; surface/wireframe/color; axes; nearest-sample hover/selection; orbit/pan/zoom/reset; animation off for Q-P1 | Native Bevy 3-D and animation |
| Factor structure | 240-point ordinary baseline plus 1K/10K/100K controlled sizes; stable IDs; sector color; size policy; selected details | Custom WGSL circular-billboard renderer |
| Correlation surface | Reuse Browser 3 matrix and cluster state; same palette; 2-D/3-D and pair inspection | Native 3-D surface implementation |
| Efficient frontier | 12 assets, 2,500 portfolios, 40-bin sampled envelope, 0.02 risk-free rate; special portfolios; stable selection; live view preservation | Exact long-only QP and larger populations |
| PCA manifold | 500 synthetic coordinates for rendering parity; selection and 2-D/3-D presentation | Computed PCA, explained variance, and larger workloads |
| Regime map | 400 observations; Bull/Bear×Low/High Volatility plus Transitional; fixed assignments; history/current/hover and non-color cues | Larger populations and numerical analysis |
| Projection | 5,000 points; five categories; fixed PCA-like/t-SNE-like/UMAP-like layouts; rectangle/group selection | Larger populations; lasso remains separately scoped |
| Network graph | 100/300 and 1,000/5,000; hashed edges/weights; fixed initial positions and budgets; drag/select/neighbor highlight | Existing layout/filter/statistics tooling |
| Knowledge graph | Shared entities/relations and stable IDs; search, expand/collapse, drag, selection, pan/zoom/reset | Existing label budgets and typed-relationship details |
| Monte Carlo | 600×120; 5/50/95 bands; histogram; path selection; defined display LOD | Larger GBM populations and numerical benchmarks |
| Order book | 1,000×200 at 10–30 updates/s; common event stream; best bid/ask/mid/trades; pause/resume; historical inspection; price zoom | Existing retained-texture and overlay path |

Labels MUST NOT imply that fixed projection layouts execute t-SNE/UMAP or that synthetic PCA coordinates are a computed decomposition.

## 16. Cross-cutting interaction and accessibility

### 16.1 Input priority

Keyboard input MUST be routed in this order:

1. Active text editor.
2. Focused grid, chart, canvas, or tab bar.
3. Global shell shortcuts.

Selection alone MUST NOT imply keyboard focus. Shell shortcuts MUST NOT consume editor commit/cancel, grid navigation, or chart annotation keys.

### 16.2 Shared mouse and keyboard conventions

Unless a scenario documents an exception:

- Left-click selects.
- Left-drag pans a chart/canvas.
- Wheel zooms.
- Shift+left-drag creates a chart trend where supported.
- Shift+click/drag extends a range.
- Ctrl+click creates disjoint selection where supported.
- Double-click/F2 starts editing.
- Enter/Tab commits; Escape cancels.
- Delete removes the selected annotation or invokes the documented safe cell-delete behavior.
- Right-click opens the relevant context menu.
- Home/Reset restores the documented chart/view state.

### 16.3 Clipboard

Use native egui/platform copy facilities and paste events. TSV parsing MUST preserve row/column order and route all pasted values through Browser 2 validation and undo. No Qt clipboard bridge is required.

### 16.4 Themes and scaling

Light/Dark/System MUST resolve to one shell palette per frame and apply to egui visuals, custom plots, browser colors, and native scene backgrounds. Hard-coded browser color pairs MUST be replaced by semantic palette values.

System MUST follow actual platform lightness where supported; an unresolved system theme MUST be reported as `partial`, not silently presented as complete.

Functional/visual checks MUST include 100%, 125%, 150%, and 200% scaling. Fixed offscreen textures MUST remain readable and their scaling behavior disclosed.

### 16.5 Accessibility

Use egui/AccessKit integration for roles, names, focus, values, and selection where supported. Custom grids and charts MUST expose textual summaries and keyboard-operable selection; painted pixels alone are insufficient.

An accessibility gap in a third-party integration MUST be recorded with the exact feature configuration and platform evidence.

## 17. Lifecycle, diagnostics, and export

### 17.1 Initialization and hidden views

Default UI state SHOULD retain lightweight per-view configuration, but MUST NOT eagerly construct the explicitly prohibited large Browser 2 or analytical fixtures.

Initial native scenes MAY remain during early parity work, but startup/idle measurements MUST disclose them. Before controlled idle/performance scenarios, hidden offscreen cameras MUST be inactive and hidden volatility animation MUST NOT advance.

Revision-based rebuild guards SHOULD remain so hidden changes are applied on reactivation.

### 17.2 Diagnostics

Diagnostics MUST distinguish:

- Source, filtered, visible, cached, submitted, and rendered counts.
- Application CPU update/build/hover/submission time.
- Bevy frame diagnostics and cadence.
- External compositor/presentation measurements.
- Startup-to-first-frame and startup-to-first-interactive.
- Actual renderer/backend where available.
- Linux RSS and model-payload estimates.
- Zoom, selection, stable page ID, and achieved live-update rate.

`egui_plot::Plot::show` duration and texture-enqueue duration MUST NOT be labeled GPU time.

### 17.3 Reset and export

Reset View MUST NOT regenerate unrelated source data or reset other pages. Reset Demo Data MUST invalidate dependent caches/revisions and clear edit/live history required by the scenario. Hidden heavy views SHOULD rebuild on activation rather than during reset.

Native window screenshots MAY provide Export View. Captured output MUST include the composited egui/native scene; a logging-only export is not functional.

## 18. Performance-scenario mapping

| Scenario | Canonical parity workload |
|---|---|
| B-P1 | 100,000×19 continuous scroll; legacy 25-column version is separate |
| B-P2 | Sort 100K by string, float, and date with source identity verification |
| B-P3 | Filter 100K to approximately 10K with a published exact predicate and expected count |
| B-P4 | Update 1,000 random values/s across visible and non-visible rows while preserving selection/editor state |
| C-P1 | 2,500/20,000/100,000/1,000,000 analytical source points; report source/rendered counts |
| C-P2 | Ten-second continuous analytical crosshair without source regeneration |
| C-P3 | Rapid chart pan/zoom with interaction and presentation timing |
| C-P4 | 20,000 stock source candles with 500–2,000 visible |
| Q-P1 | 100×100, 250×250, and 500×500 surfaces; 500×500 controlled stress |
| Q-P2 | 1K/10K/100K factor or explicitly mapped point-cloud workload |
| Q-P3 | 100/300 and 1,000/5,000 network workloads |
| Q-P4 | 1,000×200 order book at 10–30 updates/s with measured achieved rate |

Performance acceptance includes correct output and stable selection, not merely a timing value.

## 19. Acceptance evidence and status

Every parity claim MUST link to:

- Requirement ID and scenario ID/revision.
- Bevy source commit and stable page ID.
- Fixture/generator revision and SHA-256.
- Exact dimensions and action oracle.
- Build and machine environment.
- Unit/smoke-test result.
- Equivalent screenshot or recording where visual behavior matters.
- Raw measurements for performance claims.
- Approved deviations.

Use `unverified`, `supported`, `partial`, `not-implemented`, `not-applicable`, and `not-comparable` according to the comparison contract. Provision remains independently classified as NATIVE, COMPOSED, CUSTOM, EXTERNAL, or EXPERIMENTAL.

## 20. Required Slint/QML normalization outside Bevy

The following are shared-comparison dependencies, not reasons to reproduce current discrepancies in Bevy:

- Adopt common fixture hashes despite different existing RNG implementations.
- Support the canonical analytical default and Model Accuracy oracle, or record a scenario deviation.
- Support the canonical stock daily/intraday profile, or record a scenario deviation.
- Align global live/reset behavior with active scenarios rather than retaining logging stubs.
- Correct Slint System-theme custom rendering before claiming full System parity.
- Keep QML frozen-column and other limitations visible.
- Add equivalent stable-ID automation and runtime evidence where absent.

Bevy parity alone does not activate a controlled three-framework comparison.

## 21. Optional extensions

Unless explicitly promoted, the following do not block common parity:

- Locale-aware/ICU collation.
- Multi-column sorting, frozen columns, and numeric selection aggregates.
- Advanced chart renderer modes and optional annotations beyond the mandatory set.
- Heikin-Ashi, Renko, and hollow candles.
- ROC/PR or binary confusion-matrix extensions.
- Perspective/orthographic switching beyond a scenario's fixed camera.
- Factor arrows/standardization controls.
- Computed PCA, trajectories, and explained variance in common rendering scenarios.
- Projection lasso and parallel coordinates.
- Additional force-layout controls.
- 3-D or animated Monte Carlo.
- In-app export where external screenshot evidence is available.

These remain valuable framework-specific demonstrations and MUST NOT be silently dropped from the existing Bevy application.
