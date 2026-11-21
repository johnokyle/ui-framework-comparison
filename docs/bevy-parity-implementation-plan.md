# Bevy + egui Parity Implementation Plan

**Status:** Draft for implementation
**Revision:** 1
**Date:** 2026-11-20
**Normative target:** `specifications/bevy-parity.md`

## 1. Implementation strategy

Use an incremental parity pass around the existing Bevy application. Do not rewrite it as a Slint or QML architectural imitation.

The strategy is:

1. Preserve and test the current application.
2. Establish common fixtures and stable-ID navigation.
3. Add the common shell, theme, focus, diagnostics, and lifecycle behavior.
4. Extend existing Browser 1/2 and line-chart infrastructure.
5. Add Browser 3, stock, and pivot as focused new modules.
6. Retain all quantitative views and their native rendering paths.
7. Activate scenarios only after cross-framework fixture and runtime validation.

Every phase must leave the application buildable. Model/state changes land before corresponding UI interaction work, and large visual changes do not share a phase with broad fixture or lifecycle rewrites.

## 2. Current architecture and disposition

| Current source | Disposition for parity |
|---|---|
| `src/app/application.rs` | Extend window geometry and startup instrumentation only; keep feature logic elsewhere |
| `src/ui/plugin.rs` | Register shell state, navigation/live systems, and diagnostics; avoid heavy fixture construction |
| `src/ui/main_window/main_window.rs` | Add common toolbar and diagnostics around the existing active-view dispatch |
| `src/ui/state/ui_state.rs` | Retain persistent per-view state; prevent heavy Browser 2/analytical defaults |
| `src/ui/tab_bar/tab_definition.rs` | Retain typed enum identity and add canonical stable string IDs and shell metadata |
| `src/ui/tab_bar/tab_bar.rs` | Add scoped IDs, keyboard focus, activation, disabled skipping, and wrapping |
| `src/ui/tabs/main_tabs.rs` | Map the three primary IDs |
| `src/ui/tabs/browser/mod.rs` | Add Browser 3 and canonical Browser IDs |
| `src/ui/tabs/quantitative_visualization.rs` | Keep eleven views; add canonical IDs and order-book disabled fallback |
| `src/ui/state/browser_1_state.rs` | Extend source identity, columns, sorting, selection, and reset behavior |
| `src/ui/tabs/browser/browser_1.rs` | Retain `egui_extras::TableBuilder`; extend to 2,000×12 common fixture |
| `src/ui/tabs/browser/browser_1_model.rs` | Reuse deterministic typed sorting and tie-breaking |
| `src/ui/tabs/browser/browser_1_visuals.rs` | Replace fixed color pairs with resolved semantic palette values |
| `src/ui/state/browser_2_state.rs` | Extend existing editing state into common 19-column model, mappings, selection, history, and live mutation |
| `src/ui/tabs/browser/browser_2.rs` | Retain virtualized rows/editor behavior; add selection, clipboard, filters, and column controls |
| `src/ui/state/charting_state.rs` | Extend toward nine analytical frames; preserve viewport/LOD/selection mechanisms |
| `src/plots/line/model.rs` | Reuse authoritative series and viewport model |
| `src/plots/line/decimation.rs` | Reuse extrema-preserving LOD and add source/rendered oracles |
| `src/plots/line/plot.rs` | Reuse native egui plot interactions and overlays |
| `src/ui/tabs/charting/line.rs` | Use as initial analytical controller; avoid a cosmetic large-file rename during behavior changes |
| `src/ui/tabs/charting/scatter.rs` | Retain as a framework-specific demonstration; do not force it into the analytical chart |
| `src/ui/tabs/charting/histogram.rs` | Retain as a framework-specific demonstration; do not delete during parity |
| `src/renderer/plugin.rs` | Add active-scene registration/gating; retain native renderer architecture |
| `src/renderer/surfaces/` | Gate cameras/animation by active view; retain revision-guarded rebuilds |
| `src/renderer/point_clouds/` | Retain native Bevy/WGSL rendering and add common fixture/reset integration |
| Existing quantitative UI/state modules | Extend with common fixtures and oracles; do not replace advanced numerical implementations |

New modules are intentionally feature-specific. Do not introduce a generic grid, chart, plugin, or fixture framework beyond what the parity scenarios require.

## 3. Dependency overview

```text
BP-00 baseline
  └─ BP-01 fixture contract
       └─ BP-02 shell and stable-ID navigation
            └─ BP-03 lifecycle, focus, diagnostics, and capture
                 ├─ BP-04 Browser 1 + Browser 3
                 ├─ BP-05 Browser 2
                 ├─ BP-06 analytical chart
                 │    ├─ BP-07 stock chart
                 │    └─ BP-08 pivot chart
                 └─ BP-09 quantitative common-fixture integration

All implementation phases → BP-10 runtime evidence and pilot comparison
```

Browser and quantitative work can proceed independently after their dependencies, but each integration should remain small enough to isolate fixture, navigation, and rendering regressions.

## 4. BP-00 — Preserve and verify the pre-parity baseline

### Scope

- Review the complete Bevy working tree and identify all untracked implementation, asset, lockfile, and test content.
- Exclude credentials, local settings, unrelated provider scripts, and generated build output.
- Establish an authorized complete source commit before restructuring.
- Record current compiler, framework lockfile, OS, GPU/driver, build profile, and graphics backend.
- Run the existing test inventory and record actual pass/fail results; the current count of 315 test attributes is not a test result.
- Capture current startup/idle behavior and representative screenshots as a development reference, not a controlled comparison result.
- Create a requirement-to-issue traceability table using the IDs in the parity specification.

### Commands

From the Bevy repository after the clean baseline is established:

```bash
cargo fmt -- --check
cargo test --locked
cargo build --release --locked
```

Run Clippy with the repository's agreed warning policy and record any pre-existing warnings separately from new regressions.

### Exit gate

- Complete source is committed and reproducible.
- Existing tests have an actual recorded result.
- A pre-parity source revision is available for regression comparison.
- No formal comparison metrics are claimed from this development baseline.

## 5. BP-01 — Establish canonical fixtures and oracles

### Parent-repository work

1. Define the common generator or serialized fixtures required by `specifications/bevy-parity.md`.
2. Publish manifests for Browser 1/2/3, analytical, stock, pivot, and quantitative fixtures.
3. Include normalized schema, dimensions, stable IDs, golden samples, formulas, and SHA-256.
4. Define the canonical 500-day analytical fixture and 1,260-daily/20,000-intraday stock fixture.
5. Keep exact numerical scenarios separate from rendering-only fixtures.
6. Add corresponding Slint/QML normalization tasks; do not make Bevy reproduce their current disagreements.

### Bevy source targets

- Extend `src/data/models/market_snapshot.rs` for Browser 1's typed 12-column fixture.
- Add focused fixture adapters beside the relevant models rather than one global fixture manager.
- Add `src/data/models/browser_3_fixture.rs` for returns/correlation input.
- Add `src/data/models/stock_chart.rs` for OHLCV, sessions, indicators, and deterministic live events.
- Add `src/data/models/pivot_chart.rs` for nine-symbol OHLCV, resampling, and pivot oracles.
- Add explicit common-fixture conversion functions for existing quantitative models.
- Keep 100K Browser 2 and 100K/1M analytical payloads out of `Default` construction.

### Tests

- Exact fixture dimensions and column order.
- Stable-ID uniqueness and persistence.
- WA symbol at source ordinal 123.
- Nullable RSI and missing-value sort oracle.
- Browser 3 symmetry, diagonal, covariance denominator, and clustering invariants.
- Analytical equity/drawdown/risk golden samples.
- Stock OHLCV/session and indicator golden samples.
- Pivot weekly/monthly aggregation and confirmation-window oracles.
- Normalized content hashes in all three implementations before scenario activation.

### Exit gate

Bevy model tests pass against parent-owned fixture manifests. Any Slint/QML mismatch is tracked as shared normalization work rather than encoded as a Bevy deviation.

## 6. BP-02 — Add the common shell and stable-ID navigation

### New source targets

- `src/ui/state/shell_state.rs`
  - Theme choice, global live state, diagnostics visibility, advanced enablement, reset requests, and bounded event log.
  - Configuration and commands only; no chart/grid payloads.
- `src/ui/main_window/app_toolbar.rs`
  - Reset View, Reset Demo Data, Live, Light/Dark/System, Advanced Tab, Diagnostics, and functional Export when available.
- `src/ui/navigation.rs`
  - Stable-ID lookup, active-ID query, next/previous enabled selection, fallback, and event emission.

### Existing source targets

- Extend `src/ui/tabs/main_tabs.rs` with the three primary IDs.
- Extend `src/ui/tabs/browser/mod.rs` with three browser IDs and Browser 3 dispatch.
- Extend `src/ui/state/charting_tab.rs` to canonical Analytical, Stock, and Pivot routes.
- Extend `src/ui/tabs/quantitative_visualization.rs` with eleven canonical IDs.
- Extend `src/ui/tab_bar/tab_definition.rs` and `tab_bar.rs` while retaining typed enums internally.
- Extend `src/ui/main_window/main_window.rs` to compose toolbar, active content, and diagnostics.
- Change the controlled window geometry in `src/app/application.rs` to 1600×1000 and apply the chosen minimum-size policy.

### Navigation behavior

- `select_by_id` returns false for unknown IDs without changing state.
- Primary changes restore that primary's previous secondary selection.
- Disabling `quant.order-book` produces the Monte Carlo fallback.
- Keyboard focus and selected page are separate states.
- Arrow/Home/End movement, Enter/Space activation, Ctrl+Tab navigation, disabled skipping, and wrapping are deterministic.
- Event log is bounded to 200 entries.

### Theme integration

Resolve the shell palette centrally, apply egui visuals, and define semantic colors for browser/grid/plot/native-scene use. Verify available platform System-theme support before choosing an implementation; do not add a new dependency solely to avoid inspecting existing Bevy/winit support.

### Tests

- Exactly 17 unique secondary IDs plus three primary IDs.
- Canonical ID-to-enum mapping and QML alias table correctness where used by parent tooling.
- Unknown-ID rejection.
- Secondary-state persistence per primary.
- Disabled-target and next/previous fallback.
- Focus versus selection, wrapping, and event-log cap.
- Toolbar commands reach the intended active view.

### Exit gate

All canonical pages have routes, even if new pages initially display an explicit development placeholder. Placeholders are not marked supported. Existing quantitative navigation and tests continue to pass.

## 7. BP-03 — Normalize lifecycle, focus, diagnostics, and capture

### Lifecycle work

In `src/renderer/plugin.rs` and the surface/point-cloud renderer modules:

- Map active primary/secondary/view mode to each offscreen `Camera::is_active`.
- Gate camera synchronization and volatility animation when hidden.
- Retain dimension/transform/revision guards for rebuild systems.
- Apply changes made while hidden upon reactivation.
- Keep default analytical and Browser 2 construction lightweight.
- Measure the existing eager native-scene cost before attempting any broader lazy-scene conversion.

Do not combine this work with visual renderer redesign.

### Input routing

Implement the priority defined by PAR input rules:

1. Active text editor.
2. Focused grid/chart/canvas/tab bar.
3. Global shell.

Browser 2's existing editor-focus and Tab handling should remain authoritative while editing. Add a definite grid/plot focus owner before consuming arrows, Delete, Home, or chart shortcuts.

### Clipboard and accessibility

- Use native egui clipboard output and `Event::Paste` handling.
- Add TSV parsing at the Browser 2 boundary, then route through normal mutation/validation.
- Verify the selected egui/AccessKit feature configuration on the target platform.
- Add roles/names/values for shell controls and textual summaries/selection details for custom canvases.
- Record unsupported accessibility behavior explicitly rather than simulating compliance.

### Diagnostics and capture

Add explicit Bevy resources/systems for:

- Startup-to-first-frame and first-interactive hooks.
- Frame diagnostics and active stable page ID.
- Existing source/rendered/cache/LOD counters.
- Actual backend where exposed.
- Linux RSS behind the metrics/scenario path.
- Native composited-window screenshot/export if selected.

Do not label plot-submission or texture-enqueue duration as GPU time.

### Tests and exit gate

- Hidden cameras are inactive and hidden animation does not advance.
- Hidden revisions rebuild correctly on activation.
- Default construction does not create prohibited large fixtures.
- Editor, grid, chart, and shell keyboard-priority tests pass.
- Startup and screenshot evidence can be captured without a logging-only stub.
- Post-change startup/idle observations are compared with BP-00 for unintended regressions.

## 8. BP-04 — Implement Browser 1 and Browser 3

### 8.1 Browser 1

#### Source targets

- `src/data/models/market_snapshot.rs`
- `src/ui/state/browser_1_state.rs`
- `src/ui/tabs/browser/browser_1_model.rs`
- `src/ui/tabs/browser/browser_1.rs`
- `src/ui/tabs/browser/browser_1_visuals.rs`

#### Work sequence

1. Replace the six-column sample with the common 2,000×12 model.
2. Retain TableBuilder row virtualization and source-index selection.
3. Extend typed sort metadata, ascending/descending cycling, missing-last behavior, and deterministic ties.
4. Separate resize handles from reorder drag and preserve visual/model mapping.
5. Add stable WA identity and background precedence.
6. Add grid focus, keyboard navigation, and horizontal header/body synchronization.
7. Connect Reset View to column order/widths and transient selection state as defined by the scenario.

#### Acceptance evidence

Fixture and sorting unit tests, stable selection after sort/reorder, keyboard smoke test, and screenshots at light/dark and 100%/200% scaling.

### 8.2 Browser 3

#### New source targets

- `src/data/models/browser_3_fixture.rs`
- `src/ui/state/browser_3_state.rs`
- `src/ui/tabs/browser/browser_3.rs`

#### Work sequence

1. Consume the common 8-symbol, 250-day return fixture.
2. Implement/test correlation, covariance, annualized volatility, beta, and average-linkage ordering independently of painting.
3. Add responsive 8×8 egui rendering with the common diverging palette.
4. Add hover values, cell/header selection, value visibility, and 2/3-decimal modes.
5. Add pair statistics and cluster/display-order mapping.
6. Add deterministic rolling updates through the common 500 ms scheduler without resetting selection.
7. Connect view reset and demo-data reset separately.

#### Acceptance evidence

Numerical/clustering tests, selected-pair stability after clustering/live updates, and equivalent Slint/QML/Bevy screenshots.

### Exit gate

PAR-B1 and PAR-B3 requirements are supported or explicitly marked partial with linked evidence.

## 9. BP-05 — Extend Browser 2

This is the largest grid phase. Land it in independently testable steps.

### Step 1 — Fixture, metadata, and source/display mappings

Targets:

- `src/ui/state/browser_2_state.rs`
- Existing Browser 2 data/model modules, retaining useful current code.

Implement the 19-column schema, 1K/100K switch, stable row IDs, column metadata, conditional editability, and source/display round trips. Do not retain both large payloads in startup state.

### Step 2 — Sorting, filtering, and virtualization

Add global/per-column filters, clear/count/status, typed sorting, visibility reset/chooser, and source/filtered/visible/materialized diagnostics. Preserve identity through combined sort/filter/visibility operations.

Profile before optimizing. Avoid whole-dataset clones in per-frame rendering; visible-row copies may remain only if measurements show they are harmless.

### Step 3 — Selection and editing

Retain current edit buffer, validation, dirty tracking, and focus behavior. Add Cell/Row/Column/Range modes, anchors/extents/counts, Shift extension, and Ctrl-disjoint behavior required by scenarios.

Implement the common editors, invalid-state behavior, Enter/Tab/click-away commit, Escape cancel, safe Delete, and conditional Target Weight editing.

### Step 4 — Undo/redo and clipboard

Route direct edit, checkbox, Delete, and paste through one mutation path with a 500-entry history. Implement TSV copy/paste and ordered range behavior. Disjoint-copy limitations remain explicit until implemented or promoted.

### Step 5 — Formatting and live updates

Add common cell presentations and conditional style precedence without color-only meaning. Add deterministic 500 ms updates, 1,000-values/s B-P4 behavior, active-editor protection, and stable scroll/selection.

### Tests

- Fixture-size switching and source/display mapping.
- Sort/filter combinations and exact filter count.
- Every editor type and invalid input.
- Selection modes, anchors, and identity after live updates.
- Dirty/save/reset semantics.
- Undo/redo ordering and capacity.
- TSV copy/paste, including validation failure.
- Live updates skip active editors and avoid scroll jumps.
- 100K virtualization/materialization counts.

### Exit gate

PAR-B2 requirements have model tests and runtime interaction evidence. B-P1 through B-P4 remain draft until fixture/action oracles are active.

## 10. BP-06 — Convert the line infrastructure into the analytical chart

### Source targets

- `src/ui/state/charting_state.rs`
- `src/plots/line/model.rs`
- `src/plots/line/decimation.rs`
- `src/plots/line/plot.rs`
- `src/ui/tabs/charting/line.rs`
- Focused new analytical-state/view modules only where the nine frames require distinct structured content.

### Work sequence

1. Replace shell routing with `chart.analytical`; retain existing Scatter/Histogram source and tests as framework-specific demonstrations.
2. Add the nine canonical frames in order.
3. Load the 500-day common fixture and derived-series oracles.
4. Reuse viewport slicing, binary-search narrowing, extrema-preserving LOD, pan/zoom, crosshair, selection, and overlays.
5. Add structured Feature Importance, Correlation, 3×3 Model Accuracy, Risk, and Attribution content.
6. Add Shift-drag trend preview/commit, statistics, deletion, and Clear All.
7. Add deterministic optimization append, Follow behavior, and viewport preservation.
8. Add 2,500/20,000/100,000/1,000,000 source selection on demand and report source/rendered counts.

Do not generate large analytical fixtures in `Default`, replace native egui plotting with software rasterization, or move `line.rs` merely for naming symmetry during the same change.

### Tests

- Nine-frame dispatch and initial order.
- Derived analytical golden samples.
- LOD extrema preservation and authoritative statistics.
- Crosshair does not regenerate source data.
- Trend coordinates and deletion behavior.
- Live append preserves user viewport unless Follow is active.
- Large fixtures are constructed only on demand.

### Exit gate

PAR-C1 requirements are evidenced; C-P1 through C-P3 pass a development dry run with correct source/rendered accounting.

## 11. BP-07 — Add the professional stock chart

### New source targets

- `src/data/models/stock_chart.rs`
- `src/ui/state/stock_chart_state.rs`
- `src/ui/tabs/charting/stock.rs`
- Focused financial drawing helpers under `src/plots/financial/` only where shared primitives are actually needed.

### Work sequence

1. Consume ACME daily/intraday fixtures and deterministic live events.
2. Build one shared X viewport model for Price, Volume, and Indicator panels.
3. Implement Candlestick/OHLC/Line and independent Y scaling.
4. Add synchronized crosshair, OHLCV/header readouts, and panel resizing if promoted by the scenario.
5. Add SMA/EMA/Bollinger/VWAP/anchored VWAP and RSI/MACD/ATR with tested warm-up/null behavior.
6. Add inspectable signals, fixed pattern regions, and events without claiming pattern recognition.
7. Add trend/horizontal/vertical/rectangle/text annotations and deletion/Clear All.
8. Add live updates with viewport preservation and optional Follow.
9. Implement the C-P4 20,000-source/500–2,000-visible workload and aggregation diagnostics.

### Tests and exit gate

Indicator and session golden samples pass; all panels share X state; annotations survive data ticks; C-P4 source/rendered counts and interaction evidence are available. Optional renderer modes do not block the mandatory profile.

## 12. BP-08 — Add the pivot chart

### New source targets

- `src/data/models/pivot_chart.rs`
- `src/ui/state/pivot_chart_state.rs`
- `src/ui/tabs/charting/pivot.rs`

### Work sequence

1. Consume the nine-symbol, 1,500-business-day fixture.
2. Implement/test daily, five-business-day weekly, and calendar-monthly OHLCV aggregation.
3. Implement pivot confirmation, strict tie rule, buffers, alternating swings, zig-zag, and derived steps in model code.
4. Add Candle/OHLC/Line, symbol browsing, interval and six range modes.
5. Add crosshair/readout, pan/zoom, end-date, and reset behavior.
6. Add full-series navigator with center drag, eight-logical-pixel edge targets, five-bar minimum, and outside-click recentering.
7. Synchronize navigator and main viewport through one state owner.

### Tests and exit gate

Aggregation, pivot-window/tie, range, and navigator tests pass. Runtime evidence confirms synchronized view/navigator behavior and correct symbol/range reset semantics.

## 13. BP-09 — Integrate common quantitative fixtures

### Approach

Retain every existing Bevy view and renderer. Add common-fixture modes and scenario oracles without flattening advanced computation or specialized update rates.

| Work item | Required action |
|---|---|
| Volatility | Verify 100/250/500 inputs, common camera actions, nearest-sample oracle; hidden animation gating already required by BP-03 |
| Factor | Add 240 baseline and 1K/10K/100K common positions/IDs; preserve WGSL renderer |
| Correlation | Consume Browser 3's hashed matrix and clustering state; synchronize pair inspection |
| Frontier | Add 12-asset/2,500-portfolio/40-bin sampled-envelope mode; retain exact QP separately |
| PCA | Add 500-point synthetic rendering mode; retain computed PCA as a numerical extension |
| Regime | Add 400-observation/five-regime fixture and fixed selection/history oracle |
| Projection | Add 5,000-point/five-category/three-layout fixture; labels explicitly say fixed or “-like” layouts |
| Network | Hash 100/300 and 1,000/5,000 graphs; fix initial positions and iteration/label budgets |
| Knowledge | Publish entity/relation stable IDs and search/expand/drag oracle; preserve label budgeting |
| Monte Carlo | Add 600×120 rendering fixture, 5/50/95 bands, histogram bins, and path-selection oracle |
| Order book | Consume common 1,000×200 event stream; preserve 1/10/30 Hz and retained-texture rendering |

### Tests and exit gate

Existing numerical, stable-ID, cache-budget, transform, and deterministic-streaming tests remain passing. Each view has common-fixture verification, reset/selection evidence, and source/rendered diagnostics. Q-P1 through Q-P4 complete development dry runs without becoming active until all three fixture hashes agree.

## 14. BP-10 — Runtime evidence and pilot comparison

### Functional evidence

For each requirement group:

- Run model/unit tests.
- Navigate by stable ID using the external scenario harness.
- Execute mouse/keyboard actions and assert state or diagnostics.
- Capture equivalent light/dark and 100%/200% screenshots.
- Exercise constrained 1200×750 and 660×750 layouts.
- Record accessibility support and gaps.
- Update capability cells from source-observed to supported/partial only with linked evidence.

### Pilot measurements

Run a non-public pilot of:

- Cold/warm startup and first-interactive.
- Idle memory after common warm-up.
- B-P1 through B-P4.
- C-P1 through C-P4.
- Q-P1 through Q-P4.

Record raw samples, source commits, scenario revisions, machine/rendering environment, and all deviations. Use the pilot to fix scenario defects; do not present it as a controlled final baseline.

### Activation review

A scenario becomes active only when:

1. Fixture hashes match across participating implementations.
2. Action and expected-result definitions are executable.
3. Environment and measurements are normalized.
4. Any partial behavior or algorithmic difference is disclosed.
5. A dry run produces complete schema-valid raw results.

## 15. Test strategy

### Inline Rust model/state tests

Keep tests beside existing modules. Do not create a library crate solely to move tests. Focus on deterministic fixtures, formulas, identity, selection, caches, state transitions, history, and lifecycle guards.

### Native UI smoke tests

Use the parent scenario harness for stable-ID navigation and OS-level input. Prefer semantic/state assertions over pixels. Where Bevy cannot expose a semantic oracle, add a narrowly scoped diagnostics field rather than a broad new automation protocol.

### Visual evidence

Use human-reviewed equivalent screenshots. Do not use cross-framework pixel golden files because GPU tessellation, font rasterization, Qt Graphs, Slint raster images, and egui rendering differ legitimately.

### Performance evidence

Retain raw values and distributions. Application CPU timings are supplementary. External presentation timing, achieved update rates, and memory must use the definitions in `docs/methodology.md`.

### Regression command gate

At each phase:

```bash
cargo fmt -- --check
cargo test --locked
cargo build --release --locked
python tools/validate_repository.py   # from the parent repository when its documents change
```

Record platform-specific UI smoke results separately because a successful Cargo test does not prove GUI parity.

## 16. Risk register and controls

| Risk | Control |
|---|---|
| Parity becomes an unbounded rewrite | Use requirement IDs, phased gates, and explicit optional extensions |
| Different data invalidates comparisons | Parent-owned manifests, normalized hashes, and cross-language activation checks |
| Eager state distorts startup/idle | Lightweight defaults, on-demand large fixtures, before/after measurements |
| Hidden GPU scenes consume resources | Camera/animation run conditions and reactivation revision tests |
| Immediate-mode UI reconstructs too much | Retain virtualization/cache guards and profile before optimizing |
| Editor/grid/chart/global shortcuts conflict | Explicit focus ownership and input-priority tests |
| Rendering differences become false defects | State oracles plus reviewed screenshots, not pixel equality |
| Existing Bevy demonstrations regress | Preserve source/tests and reintroduce extras through separately reviewed routes |
| Slint/QML discrepancies are copied into Bevy | Track shared normalization tasks and keep canonical decisions explicit |
| Accessibility is claimed without evidence | Verify egui/AccessKit configuration and record actual platform behavior |
| Advanced numerical work contaminates rendering benchmarks | Separate common rendering fixtures from exact-computation scenarios |
| Large chart phases become unreviewable | Land fixture, state, interaction, and stress workloads in separate changes |

## 17. Suggested issue breakdown

Create one issue per BP phase and child issues for substantial steps:

1. `BP-00` Complete and verify pre-parity baseline.
2. `BP-01` Publish common fixture manifests and Bevy adapters.
3. `BP-02` Add canonical shell, stable IDs, toolbar, and theme state.
4. `BP-03` Add lifecycle gating, focus routing, diagnostics, and capture.
5. `BP-04a` Align Browser 1.
6. `BP-04b` Add Browser 3 correlation heat map.
7. `BP-05a` Add Browser 2 schema and source/display model.
8. `BP-05b` Add Browser 2 filtering, sorting, and virtualization evidence.
9. `BP-05c` Add Browser 2 selection, editing, undo/redo, and clipboard.
10. `BP-05d` Add Browser 2 formatting and deterministic live updates.
11. `BP-06` Add nine-frame analytical chart and C-P1–C-P3 support.
12. `BP-07` Add professional stock chart and C-P4 support.
13. `BP-08` Add pivot chart and navigator.
14. `BP-09a` Align volatility, factor, correlation, frontier, and PCA fixtures.
15. `BP-09b` Align regime, projection, network, knowledge, Monte Carlo, and order-book fixtures.
16. `BP-10` Add runtime evidence and execute the pilot comparison.

Each issue MUST list requirement IDs, source revision, tests, screenshots/evidence, and deviations. Closing an issue means evidence exists, not merely that code was added.

## 18. Definition of done

The Bevy parity effort is complete when:

- [ ] A complete pre-parity baseline and all parity source revisions are reproducible.
- [ ] Three primary and 17 canonical secondary IDs navigate correctly.
- [ ] Browser 1, Browser 2, Browser 3, analytical, stock, and pivot MUST requirements have runtime evidence.
- [ ] All eleven quantitative views consume common controlled fixtures without losing their existing extensions.
- [ ] Shared fixture hashes and numerical/visual oracles pass in all participating implementations.
- [ ] Light/Dark/System behavior is verified or explicitly marked partial.
- [ ] Keyboard, clipboard, focus, accessibility, resize, and scale-factor behavior is documented with evidence.
- [ ] Default construction avoids prohibited large fixtures.
- [ ] Hidden offscreen cameras/animation are gated and reactivation remains correct.
- [ ] Reset View and Reset Demo Data have distinct tested behavior.
- [ ] Existing Bevy model/numerical tests and new parity tests pass.
- [ ] Equivalent screenshots and schema-valid raw pilot results exist.
- [ ] Capability statuses and deviations are updated in the parent repository.
- [ ] No controlled performance claim relies on a draft scenario or mismatched fixture.
- [ ] Existing Bevy GPU and numerical demonstrations remain available as framework-specific evidence.

Completion of this plan establishes **full functional parity with declared deviations**. Formal benchmark publication still requires the parent project's controlled-comparison readiness gate.
