# Slint/QML fixture normalization tasks

These are shared-comparison dependencies for BP-01, not Bevy deviations and not permission to change implementation repositories as part of the parent-repository fixture work. The parent manifests and `tools/generate_fixtures.py` are authoritative. Each task is complete only when the relevant implementation reproduces the published golden rows and normalized SHA-256 hashes, or the scenario records an explicit deviation.

Source references use the audited trees: Slint paths are relative to `SlintUiTest/slintuitest/`; QML paths are relative to `QmlUiTest/QmlUITest/`. These are inspection references, not attached submodules or immutable implementation attestations.

## Execution record (2026-11-21)

**Status: NT-01 through NT-11 are complete at the headless/model-evidence level in Slint and QML.** Together with the existing Bevy adapters, all three implementations now reproduce every applicable one of the 73 parent artifacts with the unchanged row counts, ordered columns, golden rows, and SHA-256 hashes. The observations below describe the pre-normalization audit and are retained as history.

Executed validation:

- Parent: repository validation found 3 schemas, 17 manifests, 29 variants, 73 artifacts, 4 scenarios, and 0 result documents; 11 generator unit tests passed; `generate_fixtures.py check` verified all 73 artifacts without writing payload files.
- Slint: the locked ordinary suite reported 83 passed, 0 failed, 4 ignored; all 4 explicit large release tests passed; the locked release application build passed.
- QML: all 12 ordinary CTest entries and all 7 explicit large CTest entries passed. The canonical cases comprise 50 ordinary plus 23 large artifacts (73 total), each checking rows, columns, golden samples, and the exact parent hash. The complete production-model Qt Test invocation reported 18 passed, 0 failed (16 test functions plus initialization/cleanup), and the Release application target built successfully.
- Bevy + egui: the locked ordinary suite reported 563 passed, 0 failed, 1 ignored; the explicit large analytical hash test passed; the locked release application build passed.

Slint and QML construction tests demonstrate Browser 2 1K rather than 100K startup, analytical 500 rather than 100K/1M startup, stock daily-only startup, pivot SPY-only startup, and explicit selection of nondefault quantitative sizes. QML also tests explicit large replacement/selection paths and root-owned Browser 3/correlation sharing. These results do not satisfy NT-12 or establish runtime interaction, screenshot, accessibility, cadence, controlled-performance, or scenario acceptance.

## NT-01 — Replace seed-only claims with canonical adapters

**Observed:** Slint uses SplitMix64 in `src/data.rs` and related modules. QML uses at least three incompatible mechanisms: `QRandomGenerator` in `browser1model.cpp`/`browser2model.cpp`, the 32-bit LCG plus three-uniform `n3()` in `lcg.h`, and local equivalents in chart models. Comments that equal seeds reproduce identical Rust/QML data are therefore incorrect for the current content.

**Required in Slint and QML:**

- Implement the manifest's wrapping SplitMix64 state transition, `uniform`, modulo-only `below`, and two-draw cosine-only Box–Muller `normal` semantics.
- Reproduce the exact per-family seed and draw-order contract; do not substitute a library normal distribution or cache the unused sine value.
- Expose an adapter/test path that emits or streams the canonical `artifact_id`/`columns`/`rows` bytes in `fixtures/README.md`.
- Verify row count, column order, golden rows, and SHA-256 before scenario activation. Display formatting and pixel output are not substitutes.

## NT-02 — Browser 1: common 2,000×12 source and identity

**Observed:** Slint `src/data.rs` is the basis of the canonical formulas and WA special row. QML `browser1model.cpp` uses `QRandomGenerator`, numeric-suffixed 3–4-character symbols, `Company N`, a different sector order, four signals, independent formulas, and random missing values across numeric/date fields. Only RSI is nullable in the canonical artifact.

**Required:**

- Match `browser1.rows.2000`, including source row 123 = `WA`, its length-draw/letter-skip exception, all twelve typed columns, and the nullable-RSI draw order.
- Derive `b1-{source_ordinal:06d}` independently of display position; WA is `b1-000123`.
- Sort numerics, strings, and datetimes by type. Null RSI sorts last in both directions; ties use ascending source ordinal.
- Keep the stable ID out of the displayed twelve columns and preserve it through QML proxy sorting and Slint view sorting/scrolling.

**Acceptance:** `python3 tools/generate_fixtures.py check --family browser1` remains clean and each implementation reports the same artifact hash.

## NT-03 — Browser 2: common editable 19-column model

**Observed:** Slint `src/data2.rs` supplies the canonical field/draw structure and explicit binary32 trend operations. QML `browser2model.cpp` uses a different generated schema and missing-value pattern, six strategies instead of seven, independently derived entry/P&L fields, and a per-row `QRandomGenerator` trend with different update semantics. It does not reproduce the canonical seven binary32 trend values.

**Required:**

- Match `browser2.rows.1000` first: nineteen columns in manifest order, seven strategy choices, nullable RSI, deterministic notes/dates, and `b2-{source_ordinal:06d}` identity.
- Apply binary32 rounding after every specified trend conversion, arithmetic operation, and clamp; emit seven values and normalize them as fixed nine-decimal numbers only for hashing.
- Keep Symbol, Last Update, and Signal read-only; gate Target Weight on Enabled without changing source identity.
- Add `browser2.rows.100000` as an explicitly selected replacement, not an eagerly constructed second startup model. Sort/filter/display mappings must round-trip to source IDs.

**Acceptance:** both size hashes and golden rows match, and default construction is demonstrated not to instantiate the 100K source.

## NT-04 — Browser 3 and correlation surface: one numerical source

**Observed:** Slint `src/data3.rs` provides the canonical two-factor structure, sample statistics, and cluster-order reference. QML `browser3model.cpp` uses a different LCG/n3 factor model, different loadings/scales, and day-major rather than canonical block draw order. `correlationsurfacemodel.cpp` must not become a second independent numerical source.

**Required:**

- Match `browser3.returns.250`: generate all 250 market normals, then all tech normals, then each symbol's idiosyncratic normals in SPY-through-XLE order.
- Match sample covariance denominator 249, symmetric correlation with exact diagonal 1, annualized volatility `sqrt(sample variance)*sqrt(252)`, and beta `cov(a,b)/var(b)`.
- Match average-linkage `1-correlation`, strict-smaller tie scanning, node replacement, and leaf traversal for `browser3.cluster-order.8`.
- Continue the same RNG state for `browser3.live.16`; rolling live windows must preserve selected symbol identity.
- Reuse `browser3.returns.250`, `browser3.correlation.8x8`, and `browser3.cluster-order.8` for the quantitative correlation surface. No separate correlation payload hash is published.

**Acceptance:** all seven Browser 3 artifacts match, matrices are symmetric with the required diagonal, and clustering changes display order only.

## NT-05 — Analytical: common returns, risk, and static frames

**Observed:** Slint `src/data4.rs` and `src/chart1.rs` are the primary reference. QML `chart1model.cpp` generates different benchmark/strategy returns using LCG/n3, uses different optimization/correlation streams, represents warm-ups with NaN and omits them from some QML point lists, and derives a binary TP/FN/TN/FP matrix from final-fold metrics. The controlled oracle is the shared 3×3 matrix, not that binary derivation.

**Required:**

- Match `analytical.returns.500` and `analytical.core.500`: all benchmark normals precede strategy normals; strategy = `0.85*benchmark+0.0002+0.007*N`; equity begins at 100,000 and applies the first return at row 0.
- Preserve source dates, high-water/drawdown semantics, SMA20 warm-up nulls before index 19, and full source ordering independently of rendered LOD.
- Compute full 60-day risk series from the manifest formulas and validate against `analytical.risk-oracles.500`; use null before index 59 rather than NaN sentinels in canonical content.
- Match the seven default static artifacts, including `analytical.confusion.3x3` and Correlation Results derived from Browser 3 SPY/QQQ returns.
- Add on-demand 2,500/20,000/100K/1M adapters. Neither 100K nor 1M may be constructed by default; rendering LOD is excluded from source hashes and must preserve extrema.

**Acceptance:** all size-specific returns/core/risk artifacts and all seven static artifacts match, including warm-up null positions and the 3×3 confusion matrix.

## NT-06 — Stock: common ACME bars, sessions, indicators, and events

**Observed:** QML `financialchartmodel.h` already declares 1,260 daily and 20,000 intraday bars with 390-bar sessions, but `financialchartmodel.cpp` uses the incompatible LCG and different OHLCV/event generation. Its Bollinger standard deviation divides by 19; the canonical population form divides by 20. Its daily VWAP is rolling-20; canonical daily has one bar per session, so session VWAP resets at every daily bar. Slint `src/data5.rs` supplies the canonical indicator structure, but both implementations still need normalized content evidence.

**Required:**

- Match `stock.bars.daily.1260` and `stock.bars.intraday.20000`, using independent seeds 20260820/20260821 and the published normal/uniform draw order.
- Use weekday-only dates with no holiday claim and synthetic UTC sessions 09:30 through 16:00 exclusive, minute indices 0–389.
- Match SMA/EMA seeding, population Bollinger bands, cumulative session VWAP, Wilder RSI14/ATR14, MACD 12/26/9, every warm-up null, and all marker/live artifacts.
- Use deterministic 16-bar continuation streams. Do not infer fixture equality from matching bar counts or indicator names.

**Acceptance:** all eight stock artifacts match, including session-boundary rows, first valid indicator indices, marker order, and live timestamps.

## NT-07 — Pivot: nine symbols, calendar aggregation, strict ties, no lookahead

**Observed:** QML `pivotchartmodel.cpp` has five symbols (`SPY,SPX,QQQ,MINT,IEF`), a different per-symbol seed derivation, fixed-length monthly grouping, and asymmetric neighbor comparisons that can accept equal extrema on one side. Slint `src/data6.rs` has the nine-symbol/1,500-day reference but uses non-strict `>=`/`<=` candidate comparisons. Neither existing tie rule overrides the canonical strict oracle.

**Required:**

- Match all nine symbols and per-symbol seed `20260821 + source_index*7919`, with one normal followed by high/low/volume uniforms per day.
- Match `pivot.daily.9x1500`; weekly groups are consecutive source-index groups of five, and monthly groups are actual ISO year/month. OHLCV uses first open, max high, min low, last close, and summed volume.
- Require strict `>`/`<` against every other bar in the available two-sided window. Equal extrema are not candidates; the final `period` bars are not candidates.
- Accept buffered candidates in source order, expose `candidate+period` confirmation indices, and change step values only at confirmation. Apply the same formulas after weekly/monthly aggregation for their derived displays.
- Match the alternating zig-zag replacement rules without treating equal same-type values as more extreme.

**Acceptance:** all five pivot artifacts match, with targeted tests for ties, partial windows, final weekly groups, calendar-month transitions, and confirmation timing.

## NT-08 — Volatility and factor rendering inputs

**Observed:** QML `volsurfacemodel.cpp` shares the moneyness range but uses maturity domain 0.02–2.00 and different base/skew/smile/term formulas. The canonical maturity domain is 0.05–2.00 with quadratic grid spacing and explicit calm/stressed equations. Slint `src/data7.rs` is the reference for the published rendering formulas and factor streams.

**Required:**

- Match all three volatility resolutions and maturity-major/strike-minor row order. Q-P1 animation remains off; selection uses actual grid samples.
- Match factor sizes 240/1K/10K/100K, source-index sector assignment, normal/normal/normal/uniform draw order, and stable `S{source_index+1:03d}` IDs without truncating larger IDs.
- Keep 250/500 surfaces and nondefault factor sizes on-demand. Custom rendering remains an extension, not a fixture change.

**Acceptance:** three `volatility.surface.*` and four `factor.points.*` hashes match.

## NT-09 — Frontier, PCA, regime, and projection separation

**Observed:** QML `pcamanifoldmodel.cpp` uses centroid/noise and smoothing behavior different from `pca.synthetic.500`. Slint `src/data7.rs` provides the canonical reference for these rendering fixtures. Existing exact solvers or computed projections are not interchangeable with these fixed inputs.

**Required:**

- Match `frontier.assets.12`, `frontier.portfolios.2500`, half-open 40-bin envelope behavior, earliest-source tie handling, and the three special portfolios at risk-free rate 0.02.
- Match the 500 synthetic PCA coordinates, 400 five-class regime observations, and the three independently restarted 5,000-point projection layouts with exact draw order.
- Label PCA/projection fixtures honestly: synthetic PCA is not a computed decomposition and PCA-like/t-SNE-like/UMAP-like layouts do not execute those algorithms.
- Keep exact long-only QP, computed PCA/explained variance, larger populations, actual projection algorithms, and lasso behavior separately scoped.

**Acceptance:** four frontier, one PCA, one regime, and three projection artifact hashes match without changing the rendering/numerical classification.

## NT-10 — Network, knowledge, and Monte Carlo rendering inputs

**Observed:** Slint `src/data7.rs` is the reference implementation for the published structures. Equivalent dimensions in QML models do not establish equivalent node/edge IDs, layout positions, expansion state, paths, percentiles, or histogram counts.

**Required:**

- Match network node/edge construction order, duplicate-edge identity, fixed initial/final positions, and 120/40 layout budgets for 100/300 and 1,000/5,000 respectively.
- Match all 24 knowledge entities and 22 relations, including nullable parent IDs, three initially visible roots, expansion/collapse behavior, and fixed positions. Parent ID zero is a valid ID and must not be treated as missing.
- Match 600×120 post-update Monte Carlo values, nearest-index 5/50/95 bands at indices 29/299/569, and the 40 terminal-value histogram bins. Display path LOD must not change summaries.

**Acceptance:** four network, two knowledge, and three Monte Carlo artifact hashes match; advanced analysis remains separate from the rendering paths.

## NT-11 — Order book: common snapshots and event continuation

**Observed:** QML `orderbookmodel.cpp` uses integer mid/spread movement, separate bid/ask exponential depth draws, and a variable random trade process. The canonical fixture instead uses continuous mid prices, one signed 200-level snapshot per event, two depth draws per level, and two trade-level modulo draws per event. These are different event semantics, not merely different formatting.

**Required:**

- Match the 1,000 initial events and 32 continuation events in `order-book.events.1032`, including the post-source RNG state.
- Match `order-book.snapshots.1000x200` and the equivalent long-form `order-book.levels.1000x200`; each nested snapshot contains exactly 200 signed sizes.
- Use stable event IDs while shifting history, preserve pause/resume without extra RNG consumption, and distinguish synthetic touch/best bid/ask oracles from liquidity inference.
- Keep 10–30 Hz presentation scheduling separate from deterministic content generation.

**Acceptance:** all three order-book hashes match and historical inspection retains source event identity.

## NT-12 — Cross-framework runtime evidence before activation

Fixture equality is necessary but not sufficient. Before activating a controlled three-framework scenario:

- Verify default/on-demand construction and hidden-view behavior, especially Browser 2 100K and analytical 100K/1M.
- Align global live/reset behavior with the active scenario instead of retaining logging-only stubs.
- Add equivalent stable-ID automation and runtime evidence where absent.
- Correct Slint System-theme custom rendering before claiming full System parity.
- Keep QML frozen-column and other disclosed limitations visible; do not convert them into Bevy requirements or silently drop them from reports.
- Record verified artifact IDs/revisions/hashes in the scenario evidence. Do not populate source attestations until the implementation repositories have authorized immutable revisions.

### Initial development launch probe (2026-11-21)

On the audited GNOME Wayland session, all three existing Release executables created their on-screen application windows. Slint and QML used their existing metrics-mode three-second timed exits and returned success; the emitted startup/RSS values are not retained as controlled measurements. QML's navigation log reported initial `browser.browser1` followed by `primary.browser`. Bevy reported an NVIDIA RTX 4500 Ada GPU, driver 580.178.04, and the Vulkan backend, then remained resident for a ten-second probe without asset or rendering errors when launched with `BEVY_ASSET_ROOT` set to its project root. Bevy was terminated by the probe timeout, so this was not a clean window-close test.

Two initial direct Bevy launches without that environment setting reported the expected direct-executable asset-base problem: `assets/shaders/factor_point_cloud.wgsl` was sought beneath `target/release`. Setting `BEVY_ASSET_ROOT` corrected the launch configuration; no source change was made. Slint and QML rendering backends and scale factors were not captured.

No OS-level input or accessibility automation tool was available. This probe therefore does not establish runtime stable-ID navigation for Slint or Bevy, rendered Browser 1 content, pointer/keyboard interaction, clean Bevy exit, screenshots, accessibility, cadence, performance, or scenario acceptance. No scenario was activated.

### Common stable-ID development smoke (2026-11-21)

The standard-library parent runner and opt-in application adapters were exercised sequentially on the audited GNOME Wayland session, without metrics or offscreen/renderer overrides:

```bash
python3 /run/media/john/data/Experimental/UITests/ui-framework-comparison/tools/runtime_smoke.py \
  --slint /run/media/john/data/Experimental/UITests/SlintUiTest/slintuitest/target/release/slintuitest \
  --qml /run/media/john/data/Experimental/UITests/QmlUiTest/QmlUITest/build-fixture-tests/appQmlUITest \
  --bevy-egui /run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test/target/release/bevy_egui_test \
  --bevy-asset-root /run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test \
  --timeout 30 \
  --jsonl /tmp/ui-framework-runtime-smoke.jsonl
```

The result was `PASS slint: passed`, `PASS qml: passed`, and `PASS bevy-egui: passed`. Each implementation reported initial `primary.browser/browser.browser1`; successful canonical selection of Browser 2, Stock, and Monte Carlo; retained Browser 2/Stock/Monte Carlo selections after primary-only selection; and a successful idempotent Monte Carlo reselection. `not.a-route` returned `unknown-id` with `primary.quantviz/quant.monte-carlo` unchanged in both the selection reply and a follow-up `state` reply. Each run then restored `browser.browser1`, acknowledged `quit`, and exited with status 0. QML responses were canonicalized by the parent from its local IDs. The flushed JSONL log is development smoke evidence, not a controlled result.

This establishes programmatic stable-ID navigation and semantic active-route readback only. It does not establish OS-level pointer/keyboard input, rendered content or presented-frame correctness, screenshots, accessibility, theme/DPI behavior, cadence, performance, disabled-route behavior, or scenario acceptance. No scenario was activated and no implementation hash attestation was added.

No scenario activation or implementation hash attestation is part of this parent-only BP-01 fixture deliverable.
