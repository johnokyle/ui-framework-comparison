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

The standard-library parent runner and opt-in application adapters were exercised sequentially on the audited GNOME Wayland session, without metrics or offscreen/renderer overrides. This checkout-independent rendering replaces the original machine-specific paths with root variables:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --timeout 30 \
  --jsonl "$TMPDIR/ui-framework-runtime-smoke.jsonl"
```

The result was `PASS slint: passed`, `PASS qml: passed`, and `PASS bevy-egui: passed`. Each implementation reported initial `primary.browser/browser.browser1`; successful canonical selection of Browser 2, Stock, and Monte Carlo; retained Browser 2/Stock/Monte Carlo selections after primary-only selection; and a successful idempotent Monte Carlo reselection. `not.a-route` returned `unknown-id` with `primary.quantviz/quant.monte-carlo` unchanged in both the selection reply and a follow-up `state` reply. Each run then restored `browser.browser1`, acknowledged `quit`, and exited with status 0. QML responses were canonicalized by the parent from its local IDs. The flushed JSONL log is development smoke evidence, not a controlled result.

This establishes programmatic stable-ID navigation and semantic active-route readback only. It does not establish OS-level pointer/keyboard input, rendered content or presented-frame correctness, screenshots, accessibility, theme/DPI behavior, cadence, performance, disabled-route behavior, or scenario acceptance. No scenario was activated and no implementation hash attestation was added.

### OS-level keyboard development smoke (2026-11-21)

The parent-owned `tools/runtime_os_smoke.py` used the host's PyGObject `Gio`/`GLib` bindings and an authorized `org.freedesktop.portal.RemoteDesktop` keyboard session to inject actual Ctrl+Tab key events. The existing stable-ID adapters supplied readback and clean quit only; they did not synthesize the navigation being tested. No application source or dependency changed.

The passing QML and Bevy + egui invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_os_smoke.py" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --timeout 30
```

QML and Bevy + egui each started at `primary.browser/browser.browser1`, then produced `primary.charting/chart.analytical`, their default quantitative route, and the initial Browser 1 route after three successive Ctrl+Tab presses. QML's quantitative route was `quant.order-book`, canonicalized from its local `quant.heatmap`; Bevy + egui's was `quant.vol-surface`. Both acknowledged `quit` and exited with status 0. Five dependency-free unit tests also passed for the OS sequence and its assertions; the existing 22 stable-ID runner tests remained passing.

The corresponding Slint invocation did not pass: after real portal Ctrl+Tab input, semantic readback remained `primary.browser/browser.browser1` rather than changing to `primary.charting/chart.analytical`. Additional Tab/focus-traversal probes did not establish a working Slint keyboard route. These observations did not distinguish window focus, event delivery, and the focus-scoped tab handler, and were not evidence of a semantic stable-ID regression.

A 2026-11-22 follow-up reproduced the failure with both real input and a focused Slint regression test. Slint's shortcut had been local to tab-bar focus scopes, with no initially focused shell handler; the grid also consumes ordinary Tab/Backtab. The narrow fix gives the application shell initial focus and captures only Ctrl+Tab/Ctrl+Shift+Backtab before focused controls, leaving other key handling unchanged. The new test drives actual Slint `WindowEvent` key press/release records through three forward route transitions. The passing sequential invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_os_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --timeout 30
```

Slint, QML, and Bevy + egui each passed all three Ctrl+Tab transitions and exited cleanly. Slint and Bevy + egui used `quant.vol-surface`; QML used canonical `quant.order-book`. Tested executable SHA-256 hashes were Slint `a10ea3c566ff809837fa218f2ae2526a4ea469aea5c71e1956d8a20da1b16132`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. The test-time dirty Slint tree was subsequently committed unchanged as `af9bfb3f740b9bf95b7ffa6dcf071059da872e94`, which exactly identifies the tested source and is the new parent pin. Verification comprised 93 active Slint tests with four isolated large cases, format/diff checks, locked Release build, all 58 parent Python tests, and repository validation.

A later 2026-11-22 run extended the same runner with real Ctrl+Shift+Tab input and reverse actual-route assertions. Repeating the sequential invocation above, Slint, QML, and Bevy + egui each passed forward Charting → quantitative default → Browser 1, then reverse quantitative default → Charting → Browser 1, acknowledged `quit`, and exited with status 0. Slint's `WindowEvent` regression now covers both forward Tab and reverse Backtab with Control/Shift. All 59 parent Python tests, 93 active Slint tests with four isolated large cases, format/diff checks, locked Release build, and repository validation passed. Tested executable SHA-256 hashes were Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. No common secondary-tab activation was added: QML retains its separate AT-SPI-assisted focused-tab Right/Return evidence, while no deterministic process-scoped focus path was established for Slint or Bevy + egui. No blind key or pointer activation was used.

This is development OS-keyboard evidence only. It does not establish common secondary-tab activation, pointer/touch input, rendered content or presented frames, screenshots, accessibility-tree behavior, theme/DPI behavior, cadence, performance, or controlled scenario acceptance. No scenario was activated.

### External Browser 1 development screenshots (2026-11-21)

The parent-owned `tools/runtime_screenshot.py` used the host PyGObject bindings and a non-interactive `org.freedesktop.portal.Screenshot` request to capture each Release application at its initial `primary.browser/browser.browser1` route. The existing stable-ID adapters verified the same route before and after capture and supplied clean quit only; they did not generate the images. No application source or dependency changed.

The passing sequential invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-21-01 \
  --timeout 30
```

All three applications acknowledged `quit` and exited with status 0. The default two-second settling delay was used. Every raw capture is a 5120×2160 full-desktop PNG; the exact source and artifact identities are:

- Slint source `510fb6c2740ca84b84a7467691be5ae538b6635d`, executable SHA-256 `c1bd8b690b9e497949c3fd0fe65bca2ba2833412549425b3789f44be210ae0e5`, raw capture `109e69df712973922af05fb93f684396b484c1a836091eb46769c9ee2c800937`, and window review copy `41924c0e2219641cc3020e48d7b6a2592ac74ae64ddb357db1a78653ea753556`.
- QML source `84760e4b0e74997084bd2a4c89860690da0b1e3b`, executable SHA-256 `7fa6e28a9b024b6c8b0df8ceda9bda3485152f495272101ae0d6a11e97dddbb8`, raw capture `d0b9c8f0669b28388e459ae3929e90eda5fc4d88c87c1c905869c3f7dd895c0a`, and window review copy `9da7b503159309123aa5a638e79003d938c98bdfa7f191baf8abafefbb69337f`.
- Bevy + egui source `63767a424990c69980fa2443c8dd11f2b8e9e08d`, executable SHA-256 `ae874feac30f81e731cde84b7ed0aa9aeb77094ad543075f95ade3f4678be502`, raw capture `ae55485c96e31900fb65c8310616b6bf405258b1443970e28148a2734964d93d`, and window review copy `4025b05eee4239c7780e2284b8a87faff94dbf24bed2e9c1b50f4eb7e17d41f6`.

Host Pillow 12.1.1 produced the three 2667×1756 window review copies with the half-open crop rectangle `(1280, 216, 3947, 1972)`. Assistant visual inspection found the intended Browser 1 application window, table, and controls in each isolated copy, without unrelated desktop content. Slint and QML displayed light System rendering; Bevy + egui displayed dark System rendering. This is not an equivalent light/dark or 100%/200% screenshot set, and the required human review has not occurred.

The raw desktop captures include unrelated desktop content and are not publication artifacts. `manifest.jsonl`, `review-captures.jsonl`, `assistant-review.jsonl`, and the PNGs remain only under `/tmp/ui-framework-screenshots-2026-11-21-01`; no durable CI/release attachment or controlled result document was created. Six new dependency-free runner tests passed. No capability status, scenario activation, or implementation hash attestation changed.

### Explicit Browser 1 theme/scale development screenshots (2026-11-21)

Narrow startup-only capture overrides were added to the existing opt-in adapters: `SLINTUITEST_CAPTURE_THEME`, `QMLUITEST_CAPTURE_THEME`, and `BEVY_EGUI_CAPTURE_THEME` accept `light`, `dark`, or `system`; Slint scale uses its existing `SLINT_SCALE_FACTOR`, QML scale uses `QT_SCALE_FACTOR` normalized against the measured host scale, and `BEVY_EGUI_CAPTURE_SCALE_PERCENT` accepts exactly `100` or `200`. The parent runner applies these only to child environments, while continuing to force automation on and scrub metrics. Invalid new theme values and invalid Bevy scale values fail startup rather than silently selecting another variant. Ordinary non-automation startup is unchanged.

The passing sequential twelve-capture invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-21-02 \
  --timeout 30 \
  --settle 2 \
  --themes light dark \
  --scales 100 200 \
  --qml-host-scale 1.6666666269302368
```

Slint, QML, and Bevy + egui each passed light/dark × 100%/200% captures in fresh processes. Every case reported `primary.browser/browser.browser1` before and after capture, acknowledged `quit`, and exited with status 0. The measured Mutter host scale was `1.6666666269302368`; QML's requested relative factors were `0.6000000143051151` and `1.2000000286102301`. All raw desktop PNGs measured 5120×2160, which is desktop geometry rather than proof of application scale.

Host Pillow 12.1.1 produced isolated review copies using half-open crop `(1815, 579, 3415, 1639)` at 100%, yielding 1600×1060 including decorations, and `(1015, 53, 4215, 2140)` at 200%, yielding 3200×2087 including decorations. Assistant inspection of all twelve isolated copies and three labeled contact sheets found the selected light/dark rendering and doubled 200% window geometry, with Browser 1 controls/table present and no unrelated desktop content in the review copies. This verifies the collected variants at a development visual-inspection level; it is not human-reviewed cross-framework equivalence acceptance.

Exact executable and raw/review PNG SHA-256 identities, requested variants, QML normalization values, route preservation, clean exits, crop rectangles, and review dimensions are recorded in `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl` under `/tmp/ui-framework-screenshots-2026-11-21-02`. Executable hashes are Slint `9e5b6529b611eacab56f850a1c9f55f3d9949ab25d33fb54574c41d3dda477ba`, QML `a29bac748c67fca0bf9693e66f2aeb0698edc241fddd51721f7ed71f641c40be`, and Bevy + egui `cd5615eec171df01ee6445a220cc32e9cf2b6161784040d6d02ac39f21f48370`. Their capture-time dirty working trees were subsequently committed unchanged as Slint `a8cfd98fc49c424195ee827545afaf3c08158dd6`, QML `2f5b3ab3880802db62a62bace4518a61356c33b1`, and Bevy + egui `af5a301e067507da6ad4e24a19436c17e31cf026`; these immutable revisions exactly identify the tested source.

Verification comprised 23 stable-ID runner tests, five OS-smoke tests, nine screenshot-runner tests, repository validation, 91 Slint ordinary tests plus Release build, all 12 QML ordinary CTest entries, and 569 Bevy + egui ordinary tests plus Release build. Raw desktop images contain unrelated content and are not publication artifacts. All matrix artifacts remain only under `/tmp`; no durable CI/release attachment, controlled result, scenario activation, capability-status change, or human equivalence claim was created.

### Constrained Browser 1 development screenshots (2026-11-21)

The opt-in adapters now accept startup-only `SLINTUITEST_CAPTURE_SIZE`, `QMLUITEST_CAPTURE_SIZE`, and `BEVY_EGUI_CAPTURE_SIZE` values of exactly `1200x750` or `660x750`; invalid values fail startup. QML applies its size before root creation, Bevy + egui combines size with its optional scale override, and Slint applies a one-shot post-configure physical-pixel request derived from its effective scale. The last detail is necessary on the measured host: an earlier logical-size probe followed Wayland's native 5/3 scale rather than the requested absolute 100%. The parent runner exposes these values through `--sizes`, uses a fresh process for every combination, and gives size-qualified captures distinct names and manifest metadata. Ordinary non-automation startup remains unchanged.

The passing sequential six-capture invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-21-06 \
  --timeout 30 \
  --settle 2 \
  --themes light \
  --scales 100 \
  --sizes 1200x750 660x750 \
  --qml-host-scale 1.6666666269302368
```

Every case reported `primary.browser/browser.browser1` before and after capture, acknowledged `quit`, and exited with status 0. QML's relative scale factor was `0.6000000143051151`. All raw desktop PNGs measured 5120×2160. Host Pillow 12.1.1 produced decorated review copies using half-open crop `(2015, 704, 3215, 1514)` at 1200×750, yielding 1200×810, and `(2285, 704, 2945, 1514)` at 660×750, yielding 660×810. The 60-pixel decoration allowance and isolated window content are consistent with the requested logical client sizes at absolute 100%; raw desktop dimensions alone were not used as geometry evidence.

Assistant inspection of all six isolated copies found Browser 1 controls and tables present at both sizes. At 660×750, Slint retained its primary and secondary tabs but clipped right-side toolbar/reset controls and table columns; QML truncated its title and right-side toolbar and clipped table columns; Bevy + egui retained all three primary and secondary tabs but clipped right-side shell controls and table columns, with a horizontal table scrollbar visible. These observations establish captured constrained-layout behavior, not working scroll interaction, responsive-layout acceptance, or human-reviewed equivalence.

Executable SHA-256 hashes are Slint `7254d2dc8f349a08c4523f3ef7066f4bfbd74efd3b2c57eada43033106dc2a91`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. The capture-time dirty trees were subsequently committed unchanged as Slint `875e30c3776ff201f75033d25472306cdcdaf50e`, QML `00abd57eeb0f601011a79216d36223d0fb288673`, and Bevy + egui `77f200b8a9a1a67756d7fec5316c38e229320a3d`; these immutable revisions exactly identify the tested source and are the new parent pins. Exact raw/review capture hashes, requested variants, QML normalization, crop boxes, route preservation, clean exits, and assistant observations are recorded in `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl` under `/tmp/ui-framework-screenshots-2026-11-21-06`. Earlier `-03`, `-04`, and `-05-slint` directories are diagnostic probes, not accepted constrained-geometry evidence.

Verification comprised 23 stable-ID runner tests, five OS-smoke tests, ten screenshot-runner tests, repository validation, 92 Slint ordinary tests plus Release build and format check, all 12 QML ordinary CTest entries, and 569 Bevy + egui ordinary tests plus Release build. Raw desktop images contain unrelated content and are not publication artifacts. All matrix artifacts remain only under `/tmp`; no durable CI/release attachment, controlled result, scenario activation, capability-status change, or human equivalence claim was created.

### Analytical-chart development screenshots (2026-11-22)

The parent screenshot runner now accepts `--route` from the canonical secondary-ID registry. It still requires the initial Browser 1 route, selects a noninitial route through the existing stable-ID automation adapter, requires an exact successful selection reply, and checks the same actual route again after external capture. QML alias translation and response canonicalization remain parent-owned. Route-qualified filenames and manifest fields distinguish these programmatic selections from initial-default captures; the default Browser 1 behavior and filenames are unchanged.

The passing sequential invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-22-chart-analytical-01 \
  --route chart.analytical \
  --themes light \
  --scales 100 \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30
```

Slint, QML, and Bevy + egui each selected and retained `primary.charting/chart.analytical`, acknowledged `quit`, and exited with status 0. All raw desktop PNGs measured 5120×2160. Host Pillow produced 1600×1060 decorated review copies using half-open crop `(1815, 579, 3415, 1639)`. Assistant inspection found a populated multi-series analytical chart and light shell in each isolated copy. Slint and QML devote most of the window to the plot; Bevy + egui's extensive diagnostics and controls leave a shorter plot. This is a captured-layout observation, not human-reviewed equivalence or presented-frame timing evidence.

Executable SHA-256 hashes were Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. Exact capture/review hashes, crop boxes, route metadata, clean exits, and assistant observations are in `manifest.jsonl` and `assistant-review.jsonl` under `/tmp/ui-framework-screenshots-2026-11-22-chart-analytical-01`. All 61 parent Python tests passed, including twelve screenshot-runner tests, and repository validation passed. No implementation source changed. Raw desktop images contain unrelated content and are not publication artifacts; durable attachment, OS-input behavior, active accessibility, human equivalence acceptance, controlled results, and scenario activation remain unestablished.

### Stock and pivot development screenshots (2026-11-22)

The unchanged route-aware runner completed the remaining common charting routes with these two sequential invocations:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-22-chart-stock-01 \
  --route chart.stock \
  --themes light \
  --scales 100 \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30

python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-22-chart-pivot-01 \
  --route chart.pivot \
  --themes light \
  --scales 100 \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30
```

All six cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. QML responses were canonicalized from its local `chart.streaming` and `chart.multiseries` IDs. Every raw desktop PNG measured 5120×2160; isolated decorated review copies measured 1600×1060 using half-open crop `(1815, 579, 3415, 1639)`. Assistant inspection found populated Stock price/volume/indicator panels and populated Pivot charts with navigators in all three implementations, with no stale initial Browser content. Bevy + egui retains denser diagnostic/control content. These observations complete light/100% external capture coverage for the three common charting routes, not human-reviewed equivalence, input behavior, or frame-timing acceptance.

The tested executable hashes remained Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. Exact capture/review hashes, route metadata, crop boxes, clean exits, and assistant observations are in each directory's `manifest.jsonl` and `assistant-review.jsonl`. No source or test code changed in this batch. All 61 parent Python tests and repository validation remained passing. Raw desktop images are not publication artifacts; durable attachment, other variants, active accessibility, human equivalence acceptance, controlled results, and scenario activation remain unestablished.

### Browser 2 and Browser 3 development screenshots (2026-11-22)

The unchanged route-aware runner completed the remaining common Browser routes with these two sequential invocations:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-22-browser2-01 \
  --route browser.browser2 \
  --themes light \
  --scales 100 \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30

python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --output-dir /tmp/ui-framework-screenshots-2026-11-22-browser3-01 \
  --route browser.browser3 \
  --themes light \
  --scales 100 \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30
```

All six cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. Default construction remained on the existing small Browser 2 and Browser 3 datasets; no large/on-demand variant was constructed. Every raw desktop PNG measured 5120×2160, and each isolated decorated review copy measured 1600×1060 using half-open crop `(1815, 579, 3415, 1639)`.

Assistant inspection found populated Browser 2 advanced grids and populated 8×8 Browser 3 correlation matrices with canonical symbol order and visible values in all three implementations. Slint uses a large correlation matrix with right-side controls, QML centers its matrix beside pair statistics, and Bevy + egui uses a compact upper-left matrix. These are captured-layout observations, not interaction, human-equivalence, or frame-timing acceptance.

The tested executable hashes remained Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. Exact capture/review hashes, route metadata, crop boxes, clean exits, and assistant observations are in each directory's `manifest.jsonl` and `assistant-review.jsonl`. No source or test code changed. All 61 parent Python tests and repository validation remained passing. Raw desktop images are not publication artifacts; durable attachment, other variants, active accessibility, human equivalence acceptance, controlled results, and scenario activation remain unestablished.

### Browser 2 and Browser 3 theme/scale screenshot variants (2026-11-22)

The accepted native-size matrix used 24 separate runner invocations: two routes × three implementations × light/dark × 100%/200%. Every variant had a fresh application process and a fresh Screenshot portal connection. The checkout-independent invocation pattern was:

```bash
set -e
for route in browser.browser2 browser.browser3; do
  root="/tmp/ui-framework-screenshots-2026-11-22-${route//./-}-fresh-matrix-01"
  for implementation in slint qml bevy-egui; do
    case "$implementation" in
      slint) executable=(--slint "$SLINT_ROOT/target/release/slintuitest") ;;
      qml) executable=(--qml "$QML_ROOT/build-fixture-tests/appQmlUITest") ;;
      bevy-egui) executable=(--bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" --bevy-asset-root "$BEVY_ROOT") ;;
    esac
    for theme in light dark; do
      for scale in 100 200; do
        python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
          "${executable[@]}" \
          --output-dir "$root/$implementation-$theme-$scale" \
          --route "$route" \
          --themes "$theme" \
          --scales "$scale" \
          --sizes native \
          --qml-host-scale 1.6666666269302368 \
          --timeout 30
      done
    done
  done
done
```

All 24 cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. Each raw desktop PNG measured 5120×2160. Pillow 12.1.1 produced isolated decorated review copies using half-open crop `(1815, 579, 3415, 1639)` at 100%, yielding 1600×1060, and `(1015, 53, 4215, 2140)` at 200%, yielding 3200×2087. QML's relative factors were normalized against the measured `1.6666666269302368` host scale; the fixed raw desktop dimensions are not application-scale evidence.

Individual assistant inspection of every raw capture and review crop found the requested light/dark shell, expected relative 100%/200% geometry, and selected route content without unrelated desktop content in the crops. Browser 2 showed populated advanced grids with filters, colored cells, and implementation-specific controls/diagnostics. Browser 3 showed populated 8×8 correlation matrices with visible values and canonical SPY/QQQ/IWM/DIA/AAPL/MSFT/NVDA/XLE order; the previously recorded large-Slint, centered-QML, and compact-upper-left-Bevy layouts remained visible. No stale initial Browser 1 content was observed. Together with the earlier Browser 1 matrix, this completes explicit light/dark × 100%/200% native-size development captures for all common Browser routes.

The tested executable hashes were Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Exact source/review hashes, crop boxes, requested variants, route results, executable identities, clean exits, and assistant observations are aggregated in each root's `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl` under `/tmp/ui-framework-screenshots-2026-11-22-browser-browser2-fresh-matrix-01` and `/tmp/ui-framework-screenshots-2026-11-22-browser-browser3-fresh-matrix-01`.

Earlier explicit-size and shared-portal matrices were exploratory and are not cited for final visual acceptance. This accepted set contains one capture per variant and is not a repeated-run reliability result. Programmatic stable-ID selection supplied no OS-input evidence. No large/on-demand variant was constructed and no source or test code changed. All 77 parent Python tests, repository validation, and the parent whitespace check passed. No human-reviewed equivalence, presented-frame timing, numerical equivalence, active accessibility, durable attachment, controlled result, or scenario acceptance was established.

### Enabled Quantitative development screenshots (2026-11-22)

The unchanged route-aware runner captured all ten enabled common Quantitative routes with this sequential loop:

```bash
set -e
for route in quant.vol-surface quant.factor-structure quant.correlation quant.frontier quant.pca quant.regime quant.projection quant.network quant.knowledge quant.monte-carlo; do
  python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
    --slint "$SLINT_ROOT/target/release/slintuitest" \
    --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
    --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
    --bevy-asset-root "$BEVY_ROOT" \
    --output-dir "/tmp/ui-framework-screenshots-2026-11-22-${route//./-}-01" \
    --route "$route" \
    --themes light \
    --scales 100 \
    --qml-host-scale 1.6666666269302368 \
    --timeout 30
done
```

All 30 cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. Quantitative views used their existing startup defaults; no large/on-demand Browser or analytical stress variant was constructed. Every raw desktop PNG measured 5120×2160, and each isolated decorated review copy measured 1600×1060 using half-open crop `(1815, 579, 3415, 1639)`.

Assistant inspection found populated expected visualizations on all ten routes in all three implementations. Layouts are not equivalent: Slint's Knowledge Graph is a small three-node cluster with a clipped bottom legend; QML's Regime Map is sparse and its Advanced knowledge alias shows only a small central cluster; Bevy + egui's Network Graph and lower Monte Carlo histogram are truncated at the capture bottom. Compact 3D plots, dense networks/traces, and whitespace-heavy layouts are also recorded in the individual observations. These are captured-layout findings, not interaction, numerical-equivalence, human-equivalence, or frame-timing acceptance.

The `quant.order-book` route was deliberately excluded. This batch does not capture its disabled fallback as an Order Book result or change its existing capability status. Exact artifacts are under `/tmp/ui-framework-screenshots-2026-11-22-quant-<route>-01` for `vol-surface`, `factor-structure`, `correlation`, `frontier`, `pca`, `regime`, `projection`, `network`, `knowledge`, and `monte-carlo`.

The tested executable hashes remained Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. Exact capture/review hashes, route metadata, crop boxes, clean exits, and assistant observations are in each directory's `manifest.jsonl` and `assistant-review.jsonl`. No source or test code changed. All 61 parent Python tests and repository validation passed. Raw desktop images are not publication artifacts; durable attachment, other variants, active accessibility, human equivalence acceptance, controlled results, and scenario activation remain unestablished.

### Charting theme/scale screenshot variants (2026-11-22)

The accepted native-size Charting matrix used 36 separate runner invocations: three routes × three implementations × light/dark × 100%/200%. Every variant had a fresh application process and a fresh Screenshot portal connection. The checkout-independent invocation pattern was:

```bash
set -e
for route in chart.analytical chart.stock chart.pivot; do
  root="/tmp/ui-framework-screenshots-2026-11-22-${route//./-}-fresh-matrix-01"
  for implementation in slint qml bevy-egui; do
    case "$implementation" in
      slint) executable=(--slint "$SLINT_ROOT/target/release/slintuitest") ;;
      qml) executable=(--qml "$QML_ROOT/build-fixture-tests/appQmlUITest") ;;
      bevy-egui) executable=(--bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" --bevy-asset-root "$BEVY_ROOT") ;;
    esac
    for theme in light dark; do
      for scale in 100 200; do
        python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
          "${executable[@]}" \
          --output-dir "$root/$implementation-$theme-$scale" \
          --route "$route" \
          --themes "$theme" \
          --scales "$scale" \
          --sizes native \
          --qml-host-scale 1.6666666269302368 \
          --timeout 30
      done
    done
  done
done
```

All 36 cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. QML responses were canonicalized from its local aliases. Each raw desktop PNG measured 5120×2160. Pillow 12.1.1 produced isolated decorated review copies using half-open crop `(1815, 579, 3415, 1639)` at 100%, yielding 1600×1060, and `(1015, 53, 4215, 2140)` at 200%, yielding 3200×2087. QML's relative factors were normalized against the measured `1.6666666269302368` host scale.

Individual assistant inspection of every review crop found the requested light/dark shell, expected relative 100%/200% geometry, and selected route content without unrelated desktop content. Analytical showed populated multi-series charts; Stock showed populated price, volume, and indicator panels; Pivot showed populated charts with controls and navigators. Bevy + egui retained denser diagnostics/readouts and a shorter Analytical plot. No stale initial Browser content was observed. Together with the Browser matrices, all common Browser and Charting routes now have explicit light/dark × 100%/200% native-size development captures.

The tested executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Exact source/review hashes, crop boxes, requested variants, route results, executable identities, clean exits, and assistant observations are in each root's `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl` under `/tmp/ui-framework-screenshots-2026-11-22-chart-analytical-fresh-matrix-01`, `/tmp/ui-framework-screenshots-2026-11-22-chart-stock-fresh-matrix-01`, and `/tmp/ui-framework-screenshots-2026-11-22-chart-pivot-fresh-matrix-01`.

Default construction remained at analytical 500 days, stock daily-only data, and pivot SPY-only data; no analytical 100K/1M, stock 20K intraday, or all-nine-symbol pivot variant was constructed. No source or test code changed. All 77 parent Python tests, repository validation, and the parent whitespace check passed. This single-capture-per-variant set is not repeated-run reliability, OS-input, presented-frame timing, numerical-equivalence, active-accessibility, human-equivalence, durable-attachment, controlled-result, or scenario-acceptance evidence.

### Quantitative theme/scale screenshot variants (2026-11-22)

The accepted native-size Quantitative matrix used 120 separate runner invocations: ten enabled routes × three implementations × light/dark × 100%/200%. Every variant had a fresh application process and a fresh Screenshot portal connection. The checkout-independent invocation pattern was:

```bash
set -e
for route in quant.vol-surface quant.factor-structure quant.correlation quant.frontier quant.pca quant.regime quant.projection quant.network quant.knowledge quant.monte-carlo; do
  root="/tmp/ui-framework-screenshots-2026-11-22-${route//./-}-fresh-matrix-01"
  for implementation in slint qml bevy-egui; do
    case "$implementation" in
      slint) executable=(--slint "$SLINT_ROOT/target/release/slintuitest") ;;
      qml) executable=(--qml "$QML_ROOT/build-fixture-tests/appQmlUITest") ;;
      bevy-egui) executable=(--bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" --bevy-asset-root "$BEVY_ROOT") ;;
    esac
    for theme in light dark; do
      for scale in 100 200; do
        python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
          "${executable[@]}" \
          --output-dir "$root/$implementation-$theme-$scale" \
          --route "$route" \
          --themes "$theme" \
          --scales "$scale" \
          --sizes native \
          --qml-host-scale 1.6666666269302368 \
          --timeout 30
      done
    done
  done
done
```

All 120 cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. QML responses were canonicalized from its local aliases. Each raw desktop PNG measured 5120×2160. Pillow 12.1.1 produced isolated decorated review copies using half-open crop `(1815, 579, 3415, 1639)` at 100%, yielding 1600×1060, and `(1015, 53, 4215, 2140)` at 200%, yielding 3200×2087. QML's relative factors were normalized against the measured `1.6666666269302368` host scale; the fixed raw desktop dimensions are not application-scale evidence.

Individual assistant inspection of every review crop found the requested light/dark shell, expected relative 100%/200% geometry, and selected route content without stale initial Browser content or unrelated desktop content. Volatility Surface, Factor Structure, Correlation, and PCA showed populated 3D surfaces/scatters; Efficient Frontier and Projection showed populated point clouds. Regime retained substantial implementation differences: Slint showed colored regime regions and a trajectory, QML showed a sparse central path without apparent colored regions, and Bevy + egui showed dense overlapping traces. Network showed dense Slint/QML graphs and Bevy + egui's circular graph; Bevy's lower graph was clipped at 100% but fully visible within the 200% decorated bounds. Slint Knowledge remained a small three-node cluster with a clipped bottom legend, QML's Advanced alias showed a small central cluster with overlapping labels, and Bevy + egui showed a sparse connected labelled graph. Monte Carlo showed populated simulation fans; Slint included its terminal distribution, while Bevy + egui's lower histogram remained clipped at both scales. Compact 3D plots, dense diagnostics, and whitespace-heavy layouts remain visible in the individual observations.

The tested executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Exact source/review hashes, crop boxes, requested variants, route results, executable identities, clean exits, and assistant observations are aggregated in each root's `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl`. Roots follow `/tmp/ui-framework-screenshots-2026-11-22-quant-<route>-fresh-matrix-01` for `vol-surface`, `factor-structure`, `correlation`, `frontier`, `pca`, `regime`, `projection`, `network`, `knowledge`, and `monte-carlo`. Together with the earlier matrices, all enabled common routes now have explicit native-size light/dark × 100%/200% development captures.

The `quant.order-book` route was deliberately excluded; its disabled fallback was not represented as an enabled Order Book result. Quantitative views used their existing startup defaults, and no large/on-demand Browser, analytical, stock, or pivot variant was constructed. No source or test code changed. All 77 parent Python tests, repository validation, and the parent whitespace check passed. This single-capture-per-variant set is not repeated-run reliability, OS-input, presented-frame timing, numerical-equivalence, active-accessibility, human-equivalence, durable-attachment, controlled-result, or scenario-acceptance evidence.

### Constrained common-route screenshot variants (2026-11-22)

The accepted constrained matrix used 90 separate runner invocations: Browser 2/3, all three common Charting routes, and all ten enabled common Quantitative routes × three implementations × 1200×750/660×750. Every variant used explicit light/100%, a fresh application process, and a fresh Screenshot portal connection. The checkout-independent invocation pattern was:

```bash
set -e
for route in browser.browser2 browser.browser3 chart.analytical chart.stock chart.pivot quant.vol-surface quant.factor-structure quant.correlation quant.frontier quant.pca quant.regime quant.projection quant.network quant.knowledge quant.monte-carlo; do
  root="/tmp/ui-framework-screenshots-2026-11-22-${route//./-}-constrained-01"
  for implementation in slint qml bevy-egui; do
    case "$implementation" in
      slint) executable=(--slint "$SLINT_ROOT/target/release/slintuitest") ;;
      qml) executable=(--qml "$QML_ROOT/build-fixture-tests/appQmlUITest") ;;
      bevy-egui) executable=(--bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" --bevy-asset-root "$BEVY_ROOT") ;;
    esac
    for size in 1200x750 660x750; do
      python3 "$COMPARISON_ROOT/tools/runtime_screenshot.py" \
        "${executable[@]}" \
        --output-dir "$root/$implementation-light-100-$size" \
        --route "$route" \
        --themes light \
        --scales 100 \
        --sizes "$size" \
        --qml-host-scale 1.6666666269302368 \
        --timeout 30 \
        --settle 2
    done
  done
done
```

All 90 cases returned the requested canonical route, retained it after capture, acknowledged `quit`, and exited with status 0. QML responses were canonicalized from its local aliases. Each raw desktop PNG measured 5120×2160. Pillow 12.1.1 produced isolated decorated review copies using half-open crop `(2015, 704, 3215, 1514)` at 1200×750, yielding 1200×810, and `(2285, 704, 2945, 1514)` at 660×750, yielding 660×810. QML's relative scale factor remained `0.6000000143051151` against the measured `1.6666666269302368` host scale.

Individual assistant inspection covered all 90 crops, and subsequent verification checked all 90 review records and 180 source/review SHA-256 identities. The principal route-specific observations were:

- Browser 2 grids and Browser 3 8×8 matrices remained populated at both sizes. At 660×750, Browser 2 navigation/toolbars/table columns were clipped; Bevy + egui retained visible primary/secondary tabs. Slint Browser 3 controls overlapped the final matrix column, QML pair statistics were clipped, and Bevy + egui controls wrapped.
- Slint and QML Analytical retained populated charts with right-side clipping; Bevy + egui had a short populated chart at 1200×750, but its chart canvas was below the visible area at 660×750. Slint/QML Stock retained price, volume, and indicator panels; Bevy + egui retained price/volume at 1200×750, but its indicator was below the visible area and volume reached the bottom boundary at 660×750. Slint Pivot's navigator was below the visible area at both sizes; QML retained its chart and navigator with right clipping and bottom text overlap at 660×750; Bevy + egui had a full navigator at 1200×750 but only its upper portion at 660×750.
- Slint and Bevy + egui retained full Volatility Surfaces. QML showed only a narrow inspector portion at 1200×750 and clipped the surface's right side plus inspector at 660×750. Slint and Bevy + egui retained full Factor Structure scatters; QML's 660×750 crop showed only the left portion of its right-aligned scatter. Slint Correlation peaks remained top-clipped, QML clipped the right surface edge at 660×750, and Bevy + egui retained its full compact peak field.
- Slint/QML Efficient Frontier retained left-concentrated clouds; QML clipped right axis/legend/status content at 660×750. Bevy + egui retained its wide cloud and frontier. Slint and Bevy + egui retained full PCA scatters; QML's scatter was outside the visible 660×750 area except for a narrow axis-grid portion at the right boundary. Slint Regime retained colored regions and trajectory; QML remained sparse without apparent colored regions and clipped the positive axis/current-state area at 660×750; Bevy + egui retained dense overlapping traces. Slint Projection retained both diagonal clouds, QML clipped right-hand cloud portions and legend/hints at 660×750, and Bevy + egui retained its clustered scatter.
- Network retained dense populated graphs, with QML's right-hand graph/controls clipped at 660×750 and later secondary tabs clipped in the narrow layouts. Slint/QML Knowledge retained sparse small central company-node clusters with substantial empty canvas; Bevy + egui showed a populated connected graph at 1200×750 but only its upper portion at 660×750 beneath extensive controls and legends. Monte Carlo retained populated path fans; QML clipped its right-side histogram, replay controls, and guidance at 660×750, while Slint retained its terminal histogram and Bevy + egui retained its path fan and right-side legend.

The tested executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Exact source/review hashes, crop boxes, requested variants, route results, executable identities, clean exits, and per-variant observations are aggregated in each root's `manifest.jsonl`, `review-captures.jsonl`, and `assistant-review.jsonl`. Roots follow `/tmp/ui-framework-screenshots-2026-11-22-<route>-constrained-01` for `browser-browser2`, `browser-browser3`, `chart-analytical`, `chart-stock`, `chart-pivot`, `quant-vol-surface`, `quant-factor-structure`, `quant-correlation`, `quant-frontier`, `quant-pca`, `quant-regime`, `quant-projection`, `quant-network`, `quant-knowledge`, and `quant-monte-carlo`.

Together with the six existing Browser 1 captures, these 90 variants provide 96 constrained development captures covering every enabled common route at both requested sizes. The `quant.order-book` route remained excluded. Existing startup defaults were retained, no large/on-demand variant was constructed, and no source or test code changed. All 77 parent Python tests, repository validation, and the parent whitespace check passed. This single-capture-per-variant set is not repeated-run reliability, OS-input, presented-frame timing, numerical-equivalence, active-accessibility, working-scroll, responsive-layout-acceptance, human-equivalence, durable-attachment, controlled-result, or scenario-acceptance evidence.

### Browser 1 AT-SPI and focused-keyboard development evidence (2026-11-21)

A parent-only `tools/runtime_accessibility_smoke.py` runner reads the host AT-SPI `IsEnabled` status without changing it, launches fresh light/100% 1200×750 processes, and restricts desktop traversal to each child's PID. QML alone receives `QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`, in addition to its existing capture overrides. The runner uses QML's AT-SPI `SetFocus` action only to establish initial tab focus; subsequent Right, Return, and Left input is delivered through the existing authorized RemoteDesktop keyboard session. Stable-ID route readback remains the application-state oracle. No absolute coordinates, pointer events, direct selection calls, screenshots, or host settings changes are used.

The passing sequential invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_accessibility_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30 \
  --settle 1 \
  --jsonl /tmp/ui-framework-accessibility-2026-11-21.jsonl
```

The host reported `org.a11y.Status IsEnabled=false`. Slint and Bevy + egui exposed no populated process-scoped AT-SPI application and are recorded as gaps, not accessibility passes. Slint's locked default feature graph does include `accesskit` 0.24.1 and `accesskit_unix` 0.22.1 through `i-slint-backend-winit/accessibility`; its inspected adapter subscribes to AT-SPI enablement, so this disabled-host result does not prove behavior with a running screen reader. Bevy + egui explicitly enables `bevy_egui/accesskit`, but its locked graph contains no Linux `accesskit_unix` adapter. Both preserved `primary.browser/browser.browser1`, acknowledged `quit`, and exited with status 0.

With forced Qt accessibility, QML exposed an application and named frame, visible primary/secondary page tabs, Browser 1 labels including `Symbol` and `Change %`, and the visible stable-ID route label. AT-SPI `SetFocus` focused Browser #1. A real Right key moved focus to Browser #2 while canonical state remained `browser.browser1`; Return then selected `browser.browser2` and the AT-SPI checked states followed. Left moved focus back without changing Browser 2 selection, and Return restored `browser.browser1`. QML acknowledged `quit` and exited with status 0. The JSONL records the exact initial/final summaries, focus and checked states, key sequence, route sequence, host status, clean exits, and executable hashes: Slint `7254d2dc8f349a08c4523f3ef7066f4bfbd74efd3b2c57eada43033106dc2a91`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. These hashes match the currently pinned constrained-capture executables.

Verification comprised all 58 parent runtime-harness tests, including nine focused AT-SPI/focused-keyboard tests, plus repository validation of 3 schemas, 17 fixture manifests, 29 variants, 73 artifacts, 4 scenarios, and 0 result documents. Application sources and binaries were unchanged, so implementation test suites were not rerun for this parent-only evidence batch.

This is focused semantic/accessibility evidence, not an actual screen-reader session, standards-compliance assessment, pointer/touch result, or human-reviewed visual equivalence claim. Other routes and controls remain unverified. No capability cell, controlled result, or inactive performance scenario changed.

### Common focused-secondary-tab OS keyboard evidence (2026-11-22)

The extended `tools/runtime_accessibility_smoke.py` completed one common semantic Browser sequence in all three implementations: focus Browser 2 without selecting it, activate Browser 2, focus Browser 1 without changing the Browser 2 selection, activate Browser 1, traverse to and activate Browser 3, use Home without changing that selection, restore Browser 1, and exit cleanly. RemoteDesktop was started before any application launch. Every application ran as a fresh light/100% 1200×750 process, and the stable-ID adapter supplied state readback and clean quit only.

```bash
python3 "$COMPARISON_ROOT/tools/runtime_accessibility_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --qml-host-scale 1.6666666269302368 \
  --timeout 30 \
  --settle 2 \
  --jsonl /tmp/ui-framework-accessibility-2026-11-22-08.jsonl
```

Slint now gives each displayed secondary tab bar ordinary keyboard focus when its primary page is initialized, and `TabBar` forwards that focus to its existing `FocusScope`. This replaces blind native Tab-count attempts and preserves forward/reverse primary cycling when the previously focused page is destroyed. Real `Right, Return, Left, Return` input produced the route sequence `browser.browser1 → browser.browser1 → browser.browser2 → browser.browser2 → browser.browser1`. The separate native primary runner also passed three Ctrl+Tab and three Ctrl+Shift+Tab transitions. Slint's locked suite passed 94 tests with four explicit large cases ignored, formatting passed, and the locked Release executable was rebuilt without the temporary navigation diagnostics.

QML retained its verified AT-SPI `SetFocus` plus real `Right, Return, Left, Return` sequence and checked-state assertions. Bevy + egui used eleven ordinary Tab presses to focus Browser 1 without selection, then real `Right, Return, Left, Return` input. Right and Left each preserved the current selection while moving focus; the two Return presses selected Browser 2 and restored Browser 1. Its tab bar now cancels egui's pending cardinal spatial-focus movement before requesting the logical adjacent tab, preventing pass-end spatial navigation from overriding that target. The focused regression failed without this production fix and passes with it. Bevy + egui's locked suite passed 570 tests with one ignored, formatting and the locked Release build passed, and the separate native primary runner passed three Ctrl+Tab and three Ctrl+Shift+Tab transitions. All three then received `Right, Right, Return, Home, Return`: both Right presses retained Browser 1 selection, Return selected Browser 3, Home retained Browser 3 selection, and the final Return restored Browser 1. Each restored `primary.browser/browser.browser1`, acknowledged `quit`, and exited with status 0.

Host `org.a11y.Status IsEnabled` remained `false`. Slint and Bevy + egui still exposed no populated process-scoped AT-SPI application, recorded as nested gaps separate from their passing keyboard results. QML's child-only accessibility behavior was unchanged. Executable hashes were Slint `80cf5569e15dea92652440b018b9f28a5ecd083359c9134329c25b670beba58b`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `c52a235cb47e792eede869e27e62734c50e47a8c7e19adc550a3406f02d8b6f0`. All 66 parent Python tests and repository validation passed. End and arrow wraparound are not part of this common pass: Browser 4 is a QML-only extension outside the canonical registry, and QML's Quantitative tab ordering differs from the canonical order. The JSONL remains development evidence under `/tmp`; it establishes no pointer/touch input, active-screen-reader behavior, other-tab-bar keyboard behavior, rendered-frame correctness, human equivalence, durable attachment, controlled result, or scenario acceptance.

### Common Charting End and arrow-wrap keyboard evidence (2026-11-22)

The same runner then extended the passing Browser sequence with real `Ctrl+Tab, End, Right, Right, Return, Home, Return, Left, Left, Return, Home, Return` input. The checkout-independent invocation changed only the JSONL destination to `/tmp/ui-framework-accessibility-2026-11-22-09.jsonl`; it retained light/100% 1200×750 fresh processes, `--settle 2`, and the same executable arguments shown above. Every focus-only End, Home, and arrow step preserved the selected canonical route, every Return activated the intended route, and all three applications acknowledged `quit` and exited with status 0.

After Ctrl+Tab selected Charting while retaining Analytical, Slint and Bevy + egui followed `End` to Pivot, wrapped Right to Analytical, focused and selected Stock, then restored Analytical. Left from Analytical wrapped to Pivot, the next Left focused Stock without selection, Return selected Stock, and Home/Return restored Analytical. QML's physical order is Basic Charts, Multi-Series, Live / Streaming, and the QML-only Chart Layout. Consequently its End focused Chart Layout without selection, Right wrapped to Basic Charts, and the next Right/Return selected canonical Pivot; the left-wrap portion selected Stock and Home/Return restored Analytical. Chart Layout was never activated. The JSONL records these exact differences rather than treating the first Charting activation as a common route.

Bevy + egui now leaves Ctrl+Tab unclaimed by focused secondary tab bars so the shell's primary-cycle fallback receives it. A one-shot state flag focuses the active secondary tab after keyboard primary cycling and is consumed by the displayed Browser, Charting, or Quantitative page. The unchanged `tools/runtime_os_smoke.py` separately passed three Ctrl+Tab and three Ctrl+Shift+Tab transitions and clean exits in all three implementations after this dispatch change. QML used AT-SPI `SetFocus` to focus Basic Charts after its primary switch; subsequent Charting movement and activation used only real RemoteDesktop keys.

Executable hashes were Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Slint's locked suite passed 95 tests with four explicit large cases ignored, Bevy + egui's locked suite passed 571 tests with one ignored, and both locked Release builds passed. All 15 focused parent accessibility tests, all 67 parent discovery tests, and repository validation passed. Host AT-SPI remained disabled and the Slint/Bevy process-scoped gaps remained unchanged. At that point Quantitative secondary keyboard behavior remained unestablished. Pointer/touch and scrolling, active-screen-reader behavior, rendered-frame correctness, human equivalence, durable attachment, controlled results, and scenario acceptance remain unestablished.

### Common Quantitative End and arrow-wrap keyboard evidence (2026-11-22)

The runner then extended the complete Browser and Charting sequence through a second Ctrl+Tab into Quantitative Visualization and repeated the same real `End, Right, Right, Return, Home, Return, Left, Left, Return, Home, Return` focus/activation sequence. The checkout-independent invocation changed only the JSONL destination to `/tmp/ui-framework-accessibility-2026-11-22-10.jsonl`; executable arguments, fresh light/100% 1200×750 processes, `--settle 2`, and RemoteDesktop setup remained as shown above. Every focus-only End, Home, and arrow step preserved the selected canonical route, every Return activated the intended route, and all three applications restored their initial Quantitative route, acknowledged `quit`, and exited with status 0.

Slint and Bevy + egui entered with Volatility Surface selected. End focused Order Book without selection, Right wrapped to Volatility Surface, and the next Right/Return selected Factor Structure. Home/Return restored Volatility Surface; Left then wrapped to Order Book, the next Left focused Monte Carlo without selection, and Return selected Monte Carlo before Home/Return restored Volatility Surface. Advanced functionality was enabled, so Order Book participated as an enabled focus target; this run did not test disabled-route fallback behavior.

QML entered with its canonical Order Book default. AT-SPI `SetFocus` established focus on Volatility Surface without changing that selection; subsequent movement and activation used only real RemoteDesktop keys. QML's physical order made End focus Network Graph, Right wrap to Order Book, and the next Right/Return select canonical Monte Carlo. Home/Return restored Order Book; Left wrapped to Network Graph, the next Left/Return selected canonical Projection, and Home/Return restored Order Book. QML-only extension routes were not activated. The JSONL records these implementation-specific canonical routes rather than requiring identical physical tab positions.

Executable hashes were unchanged from the Charting run: Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. A native Slint regression covered the Quantitative focus and activation sequence; its locked suite passed 96 tests with four explicit large cases ignored, and formatting passed. All 16 focused parent accessibility tests, all 68 parent discovery tests, repository validation, and parent/Slint whitespace checks passed. No production application source changed in this batch. Host AT-SPI remained disabled, Slint and Bevy + egui retained their separate process-scoped AT-SPI gaps, and no active screen reader was used. Pointer/touch and scrolling, disabled-route behavior, rendered-frame correctness, human equivalence, durable attachment, controlled results, and scenario acceptance remain unestablished.

### Common OS-pointer Browser and Charting tab activation (2026-11-22)

The new `tools/runtime_pointer_smoke.py` completed real pointer-only tab activation in all three implementations. It requests RemoteDesktop device type 2 without keyboard or ScreenCast access. Before each click, two large negative `NotifyPointerMotion` deltas normalize the pointer to the desktop's top-left; a subsequent relative delta reaches the supplied compositor-logical target, followed by left-button press/release. The stable-ID adapter is used only for state readback and acknowledged quit, never route selection. Every application was a fresh light/100% 1200×750 process. The coordinates are specific to the audited desktop layout and are not resolution-independent application geometry.

The passing sequential invocation was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_pointer_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --qml-host-scale 1.6666666269302368 \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --target slint:browser.browser2=1414.2,523.2 \
  --target slint:browser.browser3=1546.2,523.2 \
  --target slint:primary.charting=1452.6,498 \
  --target slint:primary.browser=1296.6,498 \
  --target slint:browser.browser1=1282.2,523.2 \
  --target qml:browser.browser2=1303.2,522 \
  --target qml:browser.browser3=1372.2,522 \
  --target qml:primary.charting=1324.8,498 \
  --target qml:primary.browser=1246.8,498 \
  --target qml:browser.browser1=1242,522 \
  --target bevy-egui:browser.browser2=1317.3,516 \
  --target bevy-egui:browser.browser3=1390.2,516 \
  --target bevy-egui:primary.charting=1416,472.2 \
  --target bevy-egui:primary.browser=1281.9,472.2 \
  --target bevy-egui:browser.browser1=1248.9,516 \
  --timeout 30 \
  --settle 1 \
  --jsonl /tmp/ui-framework-pointer-2026-11-22-11.jsonl
```

Each implementation produced the canonical route sequence `browser.browser1 → browser.browser2 → browser.browser3 → chart.analytical → browser.browser3 → browser.browser1`. Thus pointer input selected Browser 2 and Browser 3, switched to Charting with Analytical retained, restored Browser with Browser 3 retained, and restored Browser 1. All three acknowledged `quit` and exited with status 0. Earlier absolute-motion attempts did not activate the intended targets and are not counted as passes. The successful relative-motion diagnostic first exposed QML hover, press, and release on Browser 2 without selection; `NavTabButton.qml` now explicitly calls the existing `activateIndex` helper from `onClicked`, after which the complete QML sequence passed.

Executable hashes were Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c` after the pointer-fix rebuild, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Nine focused pointer tests, six existing OS-keyboard tests, all 77 parent discovery tests, repository validation, QML's 12 fixture/model tests, and parent/QML whitespace checks passed. The JSONL records every logical target, route sequence, clean exit, and executable hash.

This establishes only five common tab targets in the audited desktop configuration. It does not establish pointer interaction with page content or other controls, touch input, scrolling, drag behavior, pointer behavior at other geometries or scales, rendered-frame correctness, active-screen-reader behavior, human-reviewed visual equivalence, durable evidence attachment, controlled results, or scenario acceptance. Slint and Bevy + egui retain their previously recorded process-scoped AT-SPI gaps. No scenario was activated.

### Extended common OS-pointer Charting and Quantitative tab activation (2026-11-22)

The unchanged pointer runner then covered all three Browser routes, all three Charting routes, and nine common visible Quantitative routes. An initial same-route Browser-primary click focuses the fresh window and is verified as a selection no-op; every subsequent route change uses real pointer input with stable-ID state readback only. The passing invocation used a temporary `/tmp/run_pointer_with_failure_capture.py` wrapper around the unchanged runner to preserve a desktop capture only if a failure occurred. No failure occurred, so the wrapper added no successful-path screenshots, input, route selection, or settling delays.

The passing sequential invocation was:

```bash
python3 /tmp/run_pointer_with_failure_capture.py \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --qml-host-scale 1.6666666269302368 \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --target slint:browser.browser2=1414.2,523.2 \
  --target slint:browser.browser3=1546.2,523.2 \
  --target slint:primary.charting=1452.6,498 \
  --target slint:chart.stock=1407,523.2 \
  --target slint:chart.pivot=1539,523.2 \
  --target slint:chart.analytical=1278,523.2 \
  --target slint:primary.browser=1296.6,498 \
  --target slint:browser.browser1=1282.2,523.2 \
  --target slint:primary.quantviz=1551,498 \
  --target slint:quant.factor-structure=1314,523.2 \
  --target slint:quant.correlation=1377,523.2 \
  --target slint:quant.frontier=1440,523.2 \
  --target slint:quant.pca=1503,523.2 \
  --target slint:quant.regime=1566,523.2 \
  --target slint:quant.projection=1629,523.2 \
  --target slint:quant.knowledge=1755,523.2 \
  --target slint:quant.monte-carlo=1818,523.2 \
  --target slint:quant.vol-surface=1246.2,523.2 \
  --target qml:browser.browser2=1303.2,522 \
  --target qml:browser.browser3=1372.2,522 \
  --target qml:primary.charting=1324.8,498 \
  --target qml:chart.stock=1374,522 \
  --target qml:chart.pivot=1310,522 \
  --target qml:chart.analytical=1245,522 \
  --target qml:primary.browser=1246.8,498 \
  --target qml:browser.browser1=1242,522 \
  --target qml:primary.quantviz=1482,498 \
  --target qml:quant.factor-structure=1610,522 \
  --target qml:quant.correlation=1400,522 \
  --target qml:quant.frontier=1700,522 \
  --target qml:quant.pca=1790,522 \
  --target qml:quant.regime=1860,522 \
  --target qml:quant.projection=1910,522 \
  --target qml:quant.knowledge=1440,522 \
  --target qml:quant.monte-carlo=1320,522 \
  --target qml:quant.vol-surface=1520,522 \
  --target bevy-egui:browser.browser2=1317.3,516 \
  --target bevy-egui:browser.browser3=1390.2,516 \
  --target bevy-egui:primary.charting=1416,472.2 \
  --target bevy-egui:chart.stock=1318.2,516 \
  --target bevy-egui:chart.pivot=1383,516 \
  --target bevy-egui:chart.analytical=1251,516 \
  --target bevy-egui:primary.browser=1281.9,472.2 \
  --target bevy-egui:browser.browser1=1248.9,516 \
  --target bevy-egui:primary.quantviz=1483.2,472.2 \
  --target bevy-egui:quant.factor-structure=1300,516 \
  --target bevy-egui:quant.correlation=1360,516 \
  --target bevy-egui:quant.frontier=1440,516 \
  --target bevy-egui:quant.pca=1520,516 \
  --target bevy-egui:quant.regime=1580,516 \
  --target bevy-egui:quant.projection=1660,516 \
  --target bevy-egui:quant.knowledge=1840,516 \
  --target bevy-egui:quant.monte-carlo=1920,516 \
  --target bevy-egui:quant.vol-surface=1251,516 \
  --timeout 30 \
  --settle 1 \
  --jsonl /tmp/ui-framework-pointer-extended-2026-11-22-12.jsonl
```

Each implementation passed 20 real clicks: the initial focus/no-op plus 19 route steps. The common route sequence was `browser.browser1 → browser.browser2 → browser.browser3 → chart.analytical → chart.stock → chart.pivot → chart.analytical → browser.browser3 → browser.browser1 → quantitative-default → quant.factor-structure → quant.correlation → quant.frontier → quant.pca → quant.regime → quant.projection → quant.knowledge → quant.monte-carlo → quant.vol-surface → browser.browser1`. The Quantitative default was `quant.vol-surface` for Slint and Bevy + egui and canonical `quant.order-book` for QML. This verified Browser 3 retention, Stock/Pivot/Analytical activation and restoration, nine direct common Quantitative secondary activations, and final Browser 1 retention. All three acknowledged `quit` and exited with status 0.

Direct Network Graph and Order Book activation are excluded: QML's Network Graph tab and Bevy + egui's Order Book tab are outside the visible clickable area at this requested geometry. QML's canonical Order Book default is checked after Quantitative primary activation, but that is not direct Order Book pointer activation or disabled-route fallback evidence. Earlier candidate extended runs included coordinate failures and intermittent initial/early-tab misses; they are not counted as passes and their cause is not established. The successful run establishes one complete sequence in this audited configuration, not repeated-run reliability.

Executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Nine focused pointer tests, six OS-keyboard tests, all 77 parent discovery tests, repository validation, and parent/QML whitespace checks passed. The JSONL records every target, canonical route, clean exit, and executable hash.

This remains setup-specific semantic tab-selection evidence only. It does not establish pointer interaction with page content or other controls, touch input, scrolling, drag behavior, other geometries or scales, rendered-frame correctness, active-screen-reader behavior, human-reviewed visual equivalence, durable evidence attachment, controlled results, or scenario acceptance. No scenario was activated.

### Advanced pointer toggling and disabled-route requests (2026-11-22)

`tools/runtime_pointer_smoke.py` now provides an opt-in `--disabled-controls` phase with separate `--control-target` coordinates. The accepted runtime evidence used `/tmp/run_disabled_control_phase.py` to invoke that tested phase directly, rather than claiming another complete tab-matrix pass. Each implementation ran as a fresh unchanged Release process at light/100% 1200×750 with `--settle 2`. Two same-route Browser-primary clicks established focus without changing selection. The exact accepted invocations were:

```bash
python3 /tmp/run_disabled_control_phase.py slint \
  --settle 2 \
  --jsonl /tmp/ui-framework-disabled-phase-2026-11-22-slint.jsonl
python3 /tmp/run_disabled_control_phase.py qml \
  --settle 2 \
  --jsonl /tmp/ui-framework-disabled-phase-2026-11-22-qml-02.jsonl
python3 /tmp/run_disabled_control_phase.py bevy-egui \
  --settle 2 \
  --jsonl /tmp/ui-framework-disabled-phase-2026-11-22-bevy-egui.jsonl
```

All three start with Advanced enabled; their disabled targets and fallbacks are not identical. The setup-specific compositor-logical targets and verified behavior were:

| Implementation | Setup target | Advanced target | Disabled target | Automatic fallback | Disabled request |
|---|---|---|---|---|---|
| Slint | Show Diagnostics `(1626,470.4)` | `(1791,866.4)` | `quant.order-book` | `quant.monte-carlo` | `ok`, actual Monte Carlo |
| QML | None | Advanced Tab label `(1716,471)` | canonical `quant.knowledge` | `quant.vol-surface` | `rejected`, actual Volatility Surface |
| Bevy + egui | None | `(1540.2,493.2)` | `quant.order-book` | `quant.monte-carlo` | `ok`, actual Monte Carlo |

For each implementation, programmatic stable-ID selection first required `ok` at the enabled target. Real pointer input then turned Advanced off and semantic state readback required the listed fallback. A programmatic request for the disabled target required the listed status and actual fallback, followed by an independent `state` request proving no additional mutation. Real pointer input re-enabled Advanced; readback required the retained fallback, and a new stable-ID request then required `ok` at the original target. Finally, a real Browser-primary click restored retained Browser 1, `quit` was acknowledged, and every process exited with status 0. Slint's Show Diagnostics click was separately checked as a route-selection no-op before its diagnostics-panel Advanced checkbox was used.

The recorded canonical route sequences were `browser.browser1 → quant.order-book → quant.monte-carlo → quant.order-book → browser.browser1` for Slint and Bevy + egui, and `browser.browser1 → quant.knowledge → quant.vol-surface → quant.knowledge → browser.browser1` for QML. Slint and Bevy's `ok` disabled replies explicitly identify Monte Carlo and are not counted as selecting Order Book. QML's `rejected` reply and unchanged Volatility Surface are not common-equivalence evidence for a different disabled target.

Executable hashes were Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. The JSONL records every accepted focus/control click, programmatic-selection use, canonical route sequence, disabled status, clean exit, and executable hash. Twelve focused pointer tests and all 80 parent discovery tests passed.

An initial QML checkbox-target attempt disabled Knowledge and selected Volatility Surface but missed the re-enable click; it is retained as a failed diagnostic, not a pass. Candidate full-pointer-sequence attempts also stopped before this phase at previously documented tab misses. These are one successful isolated phase run per implementation, not repeated-run pointer-reliability evidence. No page-content interaction, direct pointer selection of the clipped Order Book/Network tabs at 1200×750, touch, scrolling, drag, other geometries or scales, presented-frame correctness, active-screen-reader behavior, human-reviewed equivalence, durable artifact attachment, controlled result, or scenario acceptance is established by that isolated phase. The later native-size direct-tab run is recorded below. No application source, large/on-demand fixture, scenario, or controlled result changed.

### Native complete Quantitative pointer tab activation (2026-11-22)

`tools/runtime_pointer_smoke.py` now has independent `--size {1200x750,native}` and `--complete-quantitative` options. The default invocation and route sequence remain unchanged. The complete option inserts real Network Graph and Order Book clicks after Volatility Surface and before final Browser-primary restoration; native size omits only the fixed capture-size override while retaining explicit light/100%. Fourteen focused pointer tests and all 82 parent discovery tests passed before the desktop run.

Targets were measured from the existing native-size light/100% review crops. Their common raw decorated-crop origin was `(1815,579)` on the 5120×2160 desktop. Raw global pixel centers were divided by the measured `1.6666666269302368` host scale to obtain compositor-logical RemoteDesktop coordinates. These coordinates are specific to this desktop and window placement, not resolution-independent application geometry.

The accepted sequential invocation, rendered with checkout variables, was:

```bash
python3 "$COMPARISON_ROOT/tools/runtime_pointer_smoke.py" \
  --slint "$SLINT_ROOT/target/release/slintuitest" \
  --qml "$QML_ROOT/build-fixture-tests/appQmlUITest" \
  --qml-host-scale 1.6666666269302368 \
  --bevy-egui "$BEVY_ROOT/target/release/bevy_egui_test" \
  --bevy-asset-root "$BEVY_ROOT" \
  --size native \
  --complete-quantitative \
  --target slint:primary.browser=1128.0,423.6 \
  --target slint:browser.browser1=1149.0,449.4 \
  --target slint:browser.browser2=1293.0,449.4 \
  --target slint:browser.browser3=1428.0,449.4 \
  --target slint:primary.charting=1287.0,423.6 \
  --target slint:chart.analytical=1149.0,449.4 \
  --target slint:chart.stock=1293.0,449.4 \
  --target slint:chart.pivot=1428.0,449.4 \
  --target slint:primary.quantviz=1485.0,423.6 \
  --target slint:quant.vol-surface=1137.0,449.4 \
  --target slint:quant.factor-structure=1227.0,449.4 \
  --target slint:quant.correlation=1317.0,449.4 \
  --target slint:quant.frontier=1401.0,449.4 \
  --target slint:quant.pca=1485.0,449.4 \
  --target slint:quant.regime=1551.0,449.4 \
  --target slint:quant.projection=1647.0,449.4 \
  --target slint:quant.network=1740.0,449.4 \
  --target slint:quant.knowledge=1827.0,449.4 \
  --target slint:quant.monte-carlo=1917.0,449.4 \
  --target slint:quant.order-book=1998.0,449.4 \
  --target qml:primary.browser=1128.0,422.4 \
  --target qml:browser.browser1=1128.0,446.4 \
  --target qml:browser.browser2=1200.0,446.4 \
  --target qml:browser.browser3=1266.0,446.4 \
  --target qml:primary.charting=1203.0,422.4 \
  --target qml:chart.analytical=1128.0,446.4 \
  --target qml:chart.stock=1278.0,446.4 \
  --target qml:chart.pivot=1197.0,446.4 \
  --target qml:primary.quantviz=1317.0,422.4 \
  --target qml:quant.vol-surface=1401.0,446.4 \
  --target qml:quant.factor-structure=1485.0,446.4 \
  --target qml:quant.correlation=1257.0,446.4 \
  --target qml:quant.frontier=1563.0,446.4 \
  --target qml:quant.pca=1665.0,446.4 \
  --target qml:quant.regime=1743.0,446.4 \
  --target qml:quant.projection=1833.0,446.4 \
  --target qml:quant.network=1923.0,446.4 \
  --target qml:quant.knowledge=1329.0,446.4 \
  --target qml:quant.monte-carlo=1191.0,446.4 \
  --target qml:quant.order-book=1125.0,446.4 \
  --target bevy-egui:primary.browser=1161.0,396.6 \
  --target bevy-egui:browser.browser1=1128.0,441.0 \
  --target bevy-egui:browser.browser2=1203.0,441.0 \
  --target bevy-egui:browser.browser3=1275.0,441.0 \
  --target bevy-egui:primary.charting=1296.0,396.6 \
  --target bevy-egui:chart.analytical=1128.0,441.0 \
  --target bevy-egui:chart.stock=1203.0,441.0 \
  --target bevy-egui:chart.pivot=1275.0,441.0 \
  --target bevy-egui:primary.quantviz=1428.0,396.6 \
  --target bevy-egui:quant.vol-surface=1128.0,441.0 \
  --target bevy-egui:quant.factor-structure=1206.0,441.0 \
  --target bevy-egui:quant.correlation=1278.0,441.0 \
  --target bevy-egui:quant.frontier=1356.0,441.0 \
  --target bevy-egui:quant.pca=1419.0,441.0 \
  --target bevy-egui:quant.regime=1488.0,441.0 \
  --target bevy-egui:quant.projection=1596.0,441.0 \
  --target bevy-egui:quant.network=1675.8,441.0 \
  --target bevy-egui:quant.knowledge=1750.8,441.0 \
  --target bevy-egui:quant.monte-carlo=1824.0,441.0 \
  --target bevy-egui:quant.order-book=1905.0,441.0 \
  --timeout 30 \
  --settle 2 \
  --jsonl /tmp/ui-framework-pointer-native-complete-2026-11-22-01.jsonl
```

Each fresh unchanged Release process passed 22 real clicks: one initial focus/no-op plus 21 route steps. The common route sequence was `browser.browser1 → browser.browser2 → browser.browser3 → chart.analytical → chart.stock → chart.pivot → chart.analytical → browser.browser3 → browser.browser1 → quantitative-default → quant.factor-structure → quant.correlation → quant.frontier → quant.pca → quant.regime → quant.projection → quant.knowledge → quant.monte-carlo → quant.vol-surface → quant.network → quant.order-book → browser.browser1`. The default was `quant.vol-surface` for Slint and Bevy + egui and canonical `quant.order-book` for QML. QML's final Order Book step was a separate real-pointer activation of its Heatmap tab, not the earlier default readback. Every click had exact semantic active-route readback, every final Browser-primary click restored retained Browser 1, and all three acknowledged `quit` and exited with status 0. Every JSONL record has `complete_quantitative_pointer_verified=true`, `programmatic_route_selection=false`, `keyboard_input=false`, and `rendered_frame_verified=false`.

Executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. The accepted development log is `/tmp/ui-framework-pointer-native-complete-2026-11-22-01.jsonl`. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

This closes the previous direct Network Graph and Order Book shell-tab pointer gap only at the audited native geometry. It is one passing complete run per implementation, not repeated-run reliability. It does not establish page-content or other-control interaction, touch, scrolling, drag, behavior at other geometries or scales, rendered-frame correctness, presented-frame timing, active-screen-reader behavior, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance.

### Repeated native complete pointer sequences (2026-11-22)

Three additional scheduled attempts per implementation reused the full native light/100% invocation above with unchanged Release executables, coordinates, `--timeout 30`, and `--settle 2`. Runs 02 and 04 changed only the JSONL output to `/tmp/ui-framework-pointer-native-complete-2026-11-22-02.jsonl` and `/tmp/ui-framework-pointer-native-complete-2026-11-22-04.jsonl`. Run 03 initially used the same full invocation with `/tmp/ui-framework-pointer-native-complete-2026-11-22-03.jsonl`. Because the sequential runner stops at the first failure, its Slint failure prevented QML and Bevy + egui from launching. Their single scheduled run-03 attempts were then completed without retrying Slint: the same command omitted Slint and its targets and wrote `/tmp/ui-framework-pointer-native-complete-2026-11-22-03-qml-bevy.jsonl`; after QML failed, the final Bevy-only command omitted Slint/QML, their targets, and the QML scale argument and wrote `/tmp/ui-framework-pointer-native-complete-2026-11-22-03-bevy.jsonl`. No failed attempt was rerun.

| Scheduled attempt | Slint | QML | Bevy + egui |
|---|---|---|---|
| 01 (original) | Pass | Pass | Pass |
| 02 | Pass | Pass | Pass |
| 03 | **Fail: Browser 2 click left Browser 1 active** | **Fail: Browser 2 click left Browser 1 active** | Pass |
| 04 | Pass | Pass | Pass |

The additional-run totals are therefore Slint 2/3 passes, QML 2/3, and Bevy + egui 3/3. Including the original run, the totals are Slint 3/4, QML 3/4, and Bevy + egui 4/4 at this audited desktop placement. Both failures occurred at the first route-changing click after the successful initial same-route focus/no-op: expected `primary.browser/browser.browser2`, received `primary.browser/browser.browser1`. QML diagnostics recorded Browser 2 hover entry/leave without a press/release; Slint's record has no equivalent diagnostic, so neither failure's cause is established. Failure records contain only evidence type, implementation, status, and error; they do not establish an acknowledged quit or exit status for those failed processes. QML and Bevy + egui were not silently credited for the invocation that stopped before launching them, and no selective retry replaced either failure.

Every passing record retained the exact 22-click/22-route sequence described above, `complete_quantitative_pointer_verified=true`, no programmatic route selection or keyboard input, final Browser 1 restoration, acknowledged `quit`, and status 0. Executable hashes remained Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `881597209f79148d8b5b807d22cf6cdd483cef54f636f1ab32df8117e148801c`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Independent validation checked every passing record's click/route counts, flags, final route, clean exit, and executable hash, and both failure records' exact error and limited fields. JSONL SHA-256 values were `e6601d1a5e4485902488127b4ead840de9fc21cbfb4f11f76baec48513747544` for both 02 and 04, `f82431cbfe6a3d8191f647a22325a70273fbbb30732b9cd81184fe5cd799967d` for 03, `e7ab60b84209e933fbd77629d33cc9b5f1144e3355b0322eca4e9a3e82cd215f` for 03-qml-bevy, and `83a6d27ebc603496216d42d57451021307da669a658ff73490f845d3616393a2` for 03-bevy.

This small repeat matrix demonstrates that complete pointer navigation did not repeat consistently for Slint and QML in this setup. Bevy + egui's 4/4 passes are only the observed result for these four fresh processes, not generalized reliability. All 82 parent discovery tests, repository validation, and `git diff --check` passed after the documentation update. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed. Page-content/other-control input, touch, scrolling, drag, other geometries/scales, rendered-frame correctness, presented-frame timing, active-screen-reader behavior, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished.

### Browser 1 Price-header page-content pointer captures (2026-11-22)

A development-only `/tmp/run_browser1_price_pointer.py` driver combined the existing RemoteDesktop pointer, Screenshot Portal, semantic route readback, and clean-quit primitives without changing application source. Browser 1's first activation of a new header requests ascending sort in Slint (`src/browser1.rs:175-188` and `ui/grid.slint:479-497`), QML (`Browser1Page.qml:40-52,118-160` and `browser1sortproxymodel.cpp:11-56`), and Bevy + egui (`src/ui/tabs/browser/browser_1.rs:505-591` and `src/ui/state/browser_1_state.rs:157-166`). The canonical initial leading prices are `IM 350.88`, `BEDD 584.32`, `AZFF 593.91`, `MTM 679.39`, and `UI 788.88`; one ascending Price activation should instead lead with `NHP 2.39`, `MJC 4.33`, `IRQK 4.54`, `ACFN 4.56`, and `HPQB 4.78` and show Price's ascending marker.

Each fresh native light/100% process received one same-route Browser-primary focus click, parked the pointer at logical `(100,100)` outside the application before the before-capture, sent exactly one Price-header click, parked there again before the after-capture, and required Browser 1 at all five state checks. Neutral parking prevents hover-only differences from being treated as sorting. The run-02 invocation for each implementation was:

```bash
python3 /tmp/run_browser1_price_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-price-pointer-2026-11-22-02/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-price-pointer-2026-11-22-02/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The initial Slint-only attempt used the same command with root `01`; the centered Bevy + egui diagnostic used root `03`. Coordinates were measured from the common native review crop and converted with the same `(1815,579)` raw origin and `1.6666666269302368` host scale as the native shell-tab runs:

| Implementation | Browser-primary focus logical point | Price review-crop point | Price logical point |
|---|---:|---:|---:|
| Slint | `(1128,423.6)` | `(500,243)` | `(1389,493.2)` |
| QML | `(1128,422.4)` | `(500,271)` | `(1389,510)` |
| Bevy + egui run 02 | `(1161,396.6)` | `(500,263)` | `(1389,505.2)` |
| Bevy + egui run 03 | `(1161,396.6)` | `(540,263)` | `(1413,505.2)` |

Every external desktop PNG is 5120×2160. The isolated half-open crop `(1815,579,3415,1639)` produced 1600×1060 review PNGs. Procedural JSONL `status=passed` means only that both clicks were attempted, Browser 1 was preserved, two decodable distinct capture pairs were produced, and `quit` was acknowledged with status 0. It deliberately retains `price_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection, not image inequality or route readback, is the sorting oracle.

| Attempt | Subsequent visual review | Clean exit |
|---|---|---|
| Slint 01 | Before-capture and Price click completed, but the after-capture failed; sorting not verified | Not claimed |
| Slint 02 | Expected ascending Price marker and leading rows | Acknowledged quit, status 0 |
| QML 02 | Expected ascending Price marker and leading rows; prices display `$` prefixes | Acknowledged quit, status 0 |
| Bevy + egui 02 | Original row order retained; no ascending Price sort observed | Acknowledged quit, status 0 |
| Bevy + egui 03 | Original row order retained again with the centered target | Acknowledged quit, status 0 |

Slint 01's after-capture returned portal response 2. Host journals showed `xdg-desktop-portal-gnome` exhausting file descriptors, failing Vulkan/GL allocations, crashing, and being restarted by systemd. This is retained as host infrastructure failure, not a Slint sorting failure or clean exit. Slint 02 was a fresh post-restart attempt in a separate directory, not evidence that the original attempt passed. Bevy + egui 03 changed only the Price x-coordinate after the run-02 coordinate grid inspection; it was not a repeat of the same accepted result. No further Bevy retry was made. Both Bevy attempts had pixel differences only in review rectangle `(13,64,582,276)`, above the data rows, while the leading `IM 350.88 → BEDD 584.32 → AZFF 593.91` order remained unchanged. The evidence does not distinguish input-delivery failure from application behavior and does not establish a Bevy implementation defect.

Independent validation checked every JSONL executable hash, route sequence, click coordinates, flags, clean-exit claim, PNG decode/mode/dimensions/byte count, and SHA-256. Run-02/03 records have exactly two clicks, five Browser 1 readbacks, no programmatic route selection or keyboard input, and `rendered_frame_verified=false`. After-review SHA-256 values were Slint `1171393f4fccd93323877cbf98e2719074d7b87cf44af903e35aa389eb030bbb`, QML `7f3b6676a46b3d509e3b9239df7e5788a15229cc2d87dfedde0588130530dfa3`, Bevy run 02 `e5a99d31b9bafd10c47553ccc76deb7652f89af325f8c965f093d9f93e6eab3e`, and Bevy run 03 `7231066dc2efa297af336b30205610d022bf07354ccdcaeaaab103573d504a62`; the original Slint before-review hash was `8f98bc1bc6cb4680206ecefb5548541aea88ece997a64e3e6baa552bd5dc9d01`. JSONL SHA-256 values were Slint 01 `338e703a6e03ca37f7ae51812da8ad5860cf226950c894942d9634b9449b0307`, Slint 02 `e7d2fcb63d89ba5456c9cc2f865423afd8bd8b3dbb7746669ed03eb4f13e8306`, QML 02 `0f5d56a286dfd6e28f31def0c186d5f4c552760d480738abff08f50f0163a721`, Bevy 02 `653c2bfdc4e1e2a749d475cf999e0841ca8de81f9ea25339e75fd0ec0a467a62`, and Bevy 03 `54053532437a6efc538a6d8db60c8812fee6e4da0f36bbe48816bd4697a005b5`.

This establishes one real page-content Price-sort interaction for Slint and QML only. Bevy + egui page-content sorting remains unverified after two preserved unsuccessful attempts. These single positive runs do not establish repeated-run reliability, other headers or descending sort, row/cell editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after the documentation update. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 first-row page-content pointer captures (2026-11-22)

A separate `/tmp/run_browser1_row_pointer.py` driver reused the same focus, neutral-pointer parking, external-capture, route-readback, and clean-quit contract for one fresh-state click on source row `IM` in the Company column. This limited oracle is common only from the empty default with exactly one unmodified click: Slint inserts the row (`src/browser1.rs:146-160`, `ui/grid.slint:213-219,734-741`), QML toggles its stable row ID on (`Browser1Page.qml:21-38,176-219`), and Bevy + egui replaces the empty selection with that row (`src/ui/state/browser_1_state.rs:235-303`, `src/ui/tabs/browser/browser_1.rs:252-340`). A second click would toggle Slint/QML off but retain/replace Bevy's single-row selection, so no click was repeated. Exact highlight colors, checkmarks, borders, and status wording were not treated as common pixel expectations.

The accepted invocation for each implementation was:

```bash
python3 /tmp/run_browser1_row_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-row-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-row-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

| Implementation | First-row Company review-crop point | First-row Company logical point |
|---|---:|---:|
| Slint | `(200,273)` | `(1209,511.2)` |
| QML | `(200,302)` | `(1209,528.6)` |
| Bevy + egui | `(200,294)` | `(1209,523.8)` |

The Browser-primary focus points, raw/review crop conversion, and five-state-readback sequence were unchanged from the Price-header runs. Every process attempted two clicks, produced distinct decodable before/after capture pairs, preserved Browser 1, acknowledged `quit`, and exited with status 0 without programmatic selection or keyboard input. Procedural `status=passed` again does not assert page-content success; every JSONL retains `row_selection_visually_verified=false` and `capture_pixel_content_reviewed=false` for subsequent assistant review.

Assistant inspection found Slint's full `IM` row highlighted with `Rows: IM`, and QML's `IM` row highlighted with its selected-row status identifying `IM`; both before-captures had no selected row. Bevy + egui instead retained `Selected: 0`, no `IM` checkmark or selected-row highlight, and a disabled Clear Selection control after the click. Its before/after toolbar and row-detail crops confirm that the expected selection did not occur. This second unsuccessful Bevy page-content target broadens the runtime gap beyond the Price header but still does not prove universal input failure or distinguish input delivery from application behavior.

Independent validation checked all three JSONL records' exact flags, two-click/five-route sequences, executable hashes, clean exits, capture modes/dimensions/byte counts, and SHA-256 values. After-review SHA-256 values were Slint `f862793c756e564a836668e08ca2b8a98fb915d6b6c6b566de4f6de3f78f29c5`, QML `5cbb31bb5f241ac6b802d92d03b32e8efd51dd6082a579b5d9714504abac2c93`, and Bevy + egui `78c742e57739c436b7fcd0036a1f6744d822f7410cf0679bf88dbb969aa7d64d`. JSONL SHA-256 values were Slint `f8b9d3c68ccba73dfce1c527892d071ca97d533258e315362981779099b84f9c`, QML `6b87dba29549fc69fd21e0fa1873f20e26bee1dc76043628c6832fcee2ea0d25`, and Bevy + egui `bbd1e0adf44e4a500f7af37a35070ea95f20230d381a08d2fc9a4ea383883c7a`. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation.

This establishes one fresh-state row-selection interaction for Slint and QML, not repeated clicks, multi-selection, modifiers, editing, or equivalent selection semantics. Bevy + egui page-content row selection remains unverified alongside Price sorting. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed; rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished.

### Browser 1 two-click Price-toggle pointer captures (2026-11-22)

A development-only `/tmp/run_browser1_price_toggle_pointer.py` driver extended the single-click Price evidence with before, after-first-click, and after-second-click external captures. Repeated activation of the same header toggles ascending/descending in Slint (`src/browser1.rs:175-188`), QML (`Browser1Page.qml:40-52`), and Bevy + egui (`src/ui/state/browser_1_state.rs:157-167`). From a fresh canonical source-order state, the common requested sequence is therefore ascending Price followed by descending Price. The driver parked the pointer at logical `(100,100)` before every capture, required Browser 1 at seven state checks, and used semantic readback only for state and clean quit, never route selection.

The accepted invocation for each implementation was:

```bash
python3 /tmp/run_browser1_price_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-price-toggle-pointer-2026-11-22-02/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-price-toggle-pointer-2026-11-22-02/$IMPLEMENTATION.jsonl" \
  --timeout 60 \
  --settle 2
```

The Browser-primary focus points were unchanged. Slint and QML reused Price logical points `(1389,493.2)` and `(1389,510)`; Bevy + egui used its centered target `(1413,505.2)`, corresponding to review-crop points `(500,243)`, `(500,271)`, and `(540,263)`, respectively. Every process attempted one focus click and two Price clicks. Every external desktop PNG is 5120×2160, and the half-open crop `(1815,579,3415,1639)` produced 1600×1060 review PNGs for all three states.

An initial root-01 command stopped before application launch because its parent evidence directory was absent. After that directory was created, RemoteDesktop `Start` timed out at 30 seconds, again before application launch or a runtime JSONL record. D-Bus introspection then responded and an independent Screenshot Portal probe succeeded; its PNG was moved under `/tmp/ui-framework-browser1-price-toggle-pointer-2026-11-22-01/portal-probe.png`. The fresh root-02 attempts used a 60-second timeout. No root-01 sorting, page-content, or clean-exit claim is made.

Procedural `status=passed` for Slint and QML means that all three clicks were attempted, seven Browser 1 readbacks passed, three decodable pairwise-distinct capture sets were produced, and `quit` was acknowledged with status 0. Bevy + egui completed those route checks and clean exit but has `status=failed` because its after-first and after-second review captures were identical, so the driver's pairwise-distinctness requirement failed after the clean-exit flag had been recorded. Every JSONL deliberately retains `ascending_price_sort_visually_verified=false`, `descending_price_sort_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection is the sorting oracle.

| Implementation | Before | After first Price click | After second Price click | Clean exit |
|---|---|---|---|---|
| Slint | Canonical source order | Expected ascending marker and leading `NHP 2.39`, `MJC 4.33`, `IRQK 4.54`, `ACFN 4.56`, `HPQB 4.78` | Descending marker and monotonically decreasing visible prices | Acknowledged quit, status 0 |
| QML | Canonical source order | Expected ascending marker and rows with `$` prefixes | Descending marker and monotonically decreasing visible prices | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order | Original row order; no ascending sort observed | Identical review PNG; original order and no descending sort observed | Acknowledged quit, status 0 |

Independent RGB comparison found Bevy + egui's before/after-first and before/after-second differences confined to review rectangle `(13,64,582,276)`, above the data rows, and no pixel difference between after-first and after-second. This third unsuccessful Bevy Price process does not distinguish input-delivery failure from application behavior and does not establish an implementation defect. Slint and QML each demonstrate one ascending-to-descending sequence, not repeated-run reliability.

Independent validation checked all three records' exact three-click/seven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 9 clicks, 21 Browser 1 readbacks, and 18 PNGs in total. Before/after-first/after-second review SHA-256 values were Slint `d0070073c61174296dd8268d9705582ca57d9945ac840e6b06b2b0e3868a1ba5`, `1171393f4fccd93323877cbf98e2719074d7b87cf44af903e35aa389eb030bbb`, `5bb6cfd196f074403413936187c3e12c21a4ba8909c5ba5d2053b38af110f56b`; QML `1642aa857af4a49af6392c29c5cc772e3b7c0a5b742bd0f7a08bb79a079ab875`, `d7aca7ec5ff0eca6122014d314851ddf31e518232930dff59e3d2a2e1194351f`, `4819854419b25109d183f8018dbf9f2ab9cde78803753fe51e3a570c41f3fc89`; and Bevy + egui `06693f6a63291eebba355df558b3fad72f6553b5907f5c9f1ac656e6aa50f42d`, `2272b2d7b5616ef672d4767c7fb73165b5fa5637f810bea6e21f04d1f0f77d0c`, `2272b2d7b5616ef672d4767c7fb73165b5fa5637f810bea6e21f04d1f0f77d0c`. JSONL SHA-256 values were Slint `a428884faa247ea9c26b12982ca45fe4a5482adbb1e5516cd4a5896b420da7f7`, QML `b1cdb856aebffa77b0c4aa646c787857712ed137b8d0668fb3fdb26af163a060`, and Bevy + egui `1caaf63f5397acb7e74ce5e0d4d662ba428825c7b68c9d9d13e208f81ff8fbea`.

This establishes one real two-click ascending/descending Price interaction for Slint and QML. Bevy + egui Price sorting remains unverified after three preserved unsuccessful processes. Other headers, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Company-header page-content pointer captures (2026-11-22)

A development-only `/tmp/run_browser1_company_pointer.py` driver reused the single-click Price structure for a case-sensitive string column. First activation requests ascending sort in all three implementations; Company uses string comparison in Slint (`src/data.rs:238-256` and `src/browser1.rs:175-188`), QML (`Browser1Page.qml:40-52` and `browser1sortproxymodel.cpp:11-56`), and Bevy + egui (`src/ui/tabs/browser/browser_1_model.rs:6-24`, `src/ui/tabs/browser/browser_1.rs:505-591`, and `src/ui/state/browser_1_state.rs:157-166`). The limited common oracle is one fresh-state Company-header click producing ascending alphabetical Company order and its ascending marker.

The accepted invocation for each implementation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_company_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-company-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-company-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The Browser-primary focus points and raw/review crop conversion were unchanged from the Price runs. Company targets were:

| Implementation | Company review-crop point | Company logical point |
|---|---:|---:|
| Slint | `(200,243)` | `(1209,493.2)` |
| QML | `(200,271)` | `(1209,510)` |
| Bevy + egui | `(200,263)` | `(1209,505.2)` |

Every fresh native light/100% process attempted one focus click and one Company-header click, parked at logical `(100,100)` before each capture, and passed five Browser 1 readbacks. Every process acknowledged `quit` and exited with status 0 without programmatic route selection or keyboard input. External desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from the same `(1815,579,3415,1639)` half-open crop.

Procedural `status=passed` for Slint and Bevy + egui means only that both clicks were attempted, the route was preserved, distinct decodable capture pairs were produced, and clean exit completed. QML's before/after review PNGs were identical, so its record has `status=failed` and `captures_distinct=false` after recording clean exit. Every record deliberately retains `company_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection is the sorting oracle.

| Implementation | Subsequent visual review | Clean exit |
|---|---|---|
| Slint | Ascending Company marker and repeated `Apex Brands` leaders, replacing canonical source order | Acknowledged quit, status 0 |
| QML | Byte-identical before/after review PNGs; original order retained and no Company sort observed | Acknowledged quit, status 0 |
| Bevy + egui | Original row order retained; no ascending Company marker or sorted rows observed | Acknowledged quit, status 0 |

Independent RGB comparison found no QML review-pixel difference. Bevy + egui's difference was confined to review rectangle `(106,109,708,276)`, above the data rows, despite its procedural distinct-capture pass. Neither unsuccessful Company interaction establishes input-delivery failure or an application defect. QML's earlier Price/row successes are not treated as proof of Company behavior, and Slint's success is not generalized to other columns or runs. No failed Company attempt was retried.

Independent validation checked all three records' exact two-click/five-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 6 clicks, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `fe7a201fe76f6bcd016162ea40b0ade65f72eaefea1dab041c8c48431a410b1e` and `772a70f95da06fb8352af28d0897f8a7a55c881ac48d0c7dcb0e01a3c4497f76`; QML `3e8456b43aa6f2350c3c75e066c25ecf9bc16bb9ca831a1c02341c7a79f9c4cb` twice; and Bevy + egui `88466a61526d0f3f21c31de86a0f8599786e57457a67edf8533d6bcf64cf6b18` and `da73a3667b3f5ec2695b3b2804cb8c6fd58898cdb0308deab33b4683adb4b1c2`. JSONL SHA-256 values were Slint `2bb16679909b112c9c06a237a8410a562bafc8c88c75f833acccfdffa8ec7`, QML `b3ca1fe61140adc911284c3737d94ad664467d16f12058654a463de9477e47f7`, and Bevy + egui `c78304053cd094de26cbf20a69725039723020bdad7444d45536c9ed28ca92a0`. An initial validator incorrectly reused Bevy's earlier Price-difference rectangle; the measured Company rectangle above replaced that assumption, and the corrected independent checks passed.

This establishes one real ascending Company-sort interaction for Slint only. QML and Bevy + egui Company sorting remain unverified after one preserved unsuccessful attempt each. Other columns and directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Price then Reset View pointer captures (2026-11-22)

Source inspection rejected two initially considered reset oracles before any application launched. Slint's Reset Order restores visual column order (`src/browser1.rs:249-253`), not sorted rows, and QML exposes Reset Widths & Order rather than a common Reset All. The shared control is Reset View, but its exact sort behavior is not assumed to be identical: Slint's global callback invokes Browser 1 `reset_all`, clearing sort and restoring source rows (`src/main.rs:126-137`, `src/browser1.rs:255-266`); QML dispatches to Browser 1 `resetView`, which resets only column widths/order (`Main.qml:199-206`, `Browser1Page.qml:54-58`); Bevy + egui's shell invokes `Browser1State::reset_view`, which clears sort and restores source rows (`src/ui/tabs/browser/mod.rs:49-53`, `src/ui/state/browser_1_state.rs:571-581`). The parent contract defines Reset View as active-view transient presentation reset, while PAR-B1-012 explicitly requires column order/width restoration (`specifications/bevy-parity.md:103,224`); this evidence therefore records actual behavior without declaring QML's retained sort a defect by assumption.

A development-only `/tmp/run_browser1_reset_view_pointer.py` driver captured the fresh source state, requested one ascending Price sort, captured again, attempted the shared Reset View control, and captured a third time. The accepted invocation for each implementation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_reset_view_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-reset-view-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-reset-view-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Browser-primary focus and Price targets were unchanged from the two-click Price runs, including Bevy + egui's centered `(1413,505.2)` Price target. Reset View targets were:

| Implementation | Reset View review-crop point | Reset View logical point |
|---|---:|---:|
| Slint | `(50,80)` | `(1119,395.4)` |
| QML | `(50,80)` | `(1119,395.4)` |
| Bevy + egui | `(50,118)` | `(1119,418.2)` |

Every fresh native light/100% process attempted focus, Price, and Reset View clicks, parked at logical `(100,100)` before each capture, and passed seven Browser 1 readbacks. Every process acknowledged `quit` and exited with status 0 without programmatic route selection or keyboard input. Each external desktop PNG is 5120×2160; each review PNG is 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` requires attempted clicks, unchanged route, decodable captures, distinct before/after-sort review images, and clean exit. It deliberately does **not** require Reset View to change pixels, because a no-visible-change result is evidence to review rather than a harness malfunction. All three records passed and retain `price_sort_visually_verified=false`, `reset_view_behavior_visually_verified=false`, and `capture_pixel_content_reviewed=false` for subsequent assistant inspection.

| Implementation | Before | After Price click | After Reset View attempt | Clean exit |
|---|---|---|---|---|
| Slint | Canonical source order | Expected ascending Price marker and rows | Initial source-order review PNG restored exactly | Acknowledged quit, status 0 |
| QML | Canonical source order | Expected ascending Price marker and rows | After-sort ascending review PNG retained exactly | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order | Original rows; no ascending sort observed | Original rows; only toolbar-region differences | Acknowledged quit, status 0 |

Slint's exact initial/post-reset pixel match verifies one complete ascending-Price/Reset View cycle. QML's exact post-sort/post-reset match is consistent with its layout-only handler, but the external captures do not independently prove Reset View activated or distinguish activation from a missed/no-visible-change click. Bevy + egui's before/after-reset differences were confined to `(8,64,233,127)` and after-sort/after-reset differences to `(8,109,582,276)`, both above data rows; because its Price sort did not occur, reset-after-actual-sort behavior remains unverified.

Independent validation checked all three records' exact three-click/seven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 9 clicks, 21 Browser 1 readbacks, and 18 recorded PNGs. Before/after-sort/after-reset review SHA-256 values were Slint `3071a93e38a8687b6b184082c9c56b70c6178fefbdd32b2b9ca4b69e33279b94`, `4da17a0285f5181cd84f79063ff238366eb41726e6291f2d3beae3926ba01cf7`, `3071a93e38a8687b6b184082c9c56b70c6178fefbdd32b2b9ca4b69e33279b94`; QML `da29565fea0b20b8fcc6869b3715c6d84088251a1dbde26f04df24f647d9bfc0`, `347b259b2df6b839bc34e591db21dd86d97e9f0536ce7bf179462c3d948bc46d`, `347b259b2df6b839bc34e591db21dd86d97e9f0536ce7bf179462c3d948bc46d`; and Bevy + egui `1f2a2f338bd5f3e3d314026fe5f2082f2c8707f6e1b508170b0b3f2876bbbf70`, `83088e5d315f2b8c9ab9190e992d4a016e44ab3e878cf9dbb0787749b3ca7748`, `ab052ca6b7618836c57f00ef60c73cd35f6eaf7b01baab952378b85bda586fef`. JSONL SHA-256 values were Slint `aa0f116ba1a73e2146dd5f96f90f3b78bcad82986b27b481a9f679946e5a4914`, QML `fbf48e26c6dc91967560c02a7cb2aea81c0150a1af456a69de6330f621757ee1`, and Bevy + egui `493a7266744c1484fa8603abf884ebc1fe84aabf68bbcfe5450bb7b4150e86ff`.

This establishes one Slint sort/reset cycle and records the actual QML/Bevy + egui post-reset pixels without imposing a common sort-clearing oracle. Repeated-run reliability, QML reset activation, Bevy + egui reset after actual sorting, other controls, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 two-click first-row pointer captures (2026-11-22)

Source inspection rejected Clear Selection as a common Browser 1 oracle before any application launched: Bevy + egui exposes that control, while Slint and QML toggle row membership through repeated cell clicks. The shared action is instead two unmodified clicks on the same first row, with implementation-specific expectations. Slint and QML toggle the row off on the second click (`src/browser1.rs:146-160`, `Browser1Page.qml:31-38,215-219`); Bevy + egui's ordinary-click path clears and reinserts that row, retaining single-row selection rather than toggling it off (`src/ui/state/browser_1_state.rs:235-303`). The run therefore records actual second-click behavior without imposing common deselection semantics.

A development-only `/tmp/run_browser1_row_toggle_pointer.py` driver reused the first-row targets and captured initial, after-first-click, and after-second-click states. The accepted invocation for each implementation used its 60-second default timeout:

```bash
python3 /tmp/run_browser1_row_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-row-toggle-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-row-toggle-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The Browser-primary focus points and first-row Company targets were unchanged from the single-click run: Slint `(1209,511.2)`, QML `(1209,528.6)`, and Bevy + egui `(1209,523.8)`, corresponding to review-crop points `(200,273)`, `(200,302)`, and `(200,294)`. Every fresh native light/100% process attempted one focus click and two first-row clicks, parked at logical `(100,100)` before every capture, and passed seven Browser 1 readbacks. Every process acknowledged `quit` and exited with status 0 without keyboard input or programmatic route selection. External desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` for Slint and Bevy + egui means only that the clicks/route checks completed, decodable captures were produced, before/after-first review images differed, and clean exit completed. QML's before/after-first review PNGs were identical, so its record has `status=failed` only for that distinctness check after clean exit was recorded. All records retain `row_selection_visually_verified=false`, `row_deselection_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection is the page-content oracle.

| Implementation | Before | After first row click | After second row click | Clean exit |
|---|---|---|---|---|
| Slint | Fixed review crop contained unrelated desktop content and only a partial application slice | Terminal content obstructed the application region | Application visible with no selected `IM` row | Acknowledged quit, status 0 |
| QML | Empty selection | Byte-identical to before; empty selection | `IM` row highlighted and selected-row status identifies `IM` | Acknowledged quit, status 0 |
| Bevy + egui | `Selected: 0`, no `IM` highlight, disabled Clear Selection | Same unselected row/status state | Byte-identical to after-first; same unselected row/status state | Acknowledged quit, status 0 |

The Slint process's procedural capture pass is not valid row-interaction evidence: its first two fixed crops were obstructed or incomplete, so the clicks cannot be attributed to visible Browser 1 content and neither selection nor deselection is verified. QML shows only one visible transition, from empty selection after the first capture to selected `IM` after the second; it does not demonstrate the intended select-then-deselect cycle. Bevy + egui retained `Selected: 0` with no `IM` highlight throughout. Its after-first/after-second review PNGs were identical, and before/after-first pixel inequality is not evidence of selection. These outcomes do not establish implementation defects or distinguish input-delivery, focus, obstruction, and application causes. No attempt was retried.

Independent RGB comparison found QML's after-first/after-second and before/after-second differences confined to `(0,224,1471,316)`, while Bevy + egui's before/after-first and before/after-second differences spanned `(13,64,1556,1049)` despite unchanged selection visuals. Slint's three pairwise comparisons spanned the full review image because of the changing obstructions. Independent validation checked all three records' exact three-click/seven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 9 clicks, 21 Browser 1 readbacks, and 18 recorded PNGs. Before/after-first/after-second review SHA-256 values were Slint `f650757241942ce7f01c983488d812fa95e5fadbaee4e24853275d5a0ef249f6`, `c32cec17a094611b62d1adbdd4bdbaf4d7221412b9e044149d7352d9cbbfd449`, `3d4a59162f94a9fd5edad9a5e380964b0542b4528a4bb0ef955682ab1e7e93c3`; QML `383bbd9f98123ee0c28b960c22bcc7133b57ecb0aa7bdf281d39417962036f77`, `383bbd9f98123ee0c28b960c22bcc7133b57ecb0aa7bdf281d39417962036f77`, `53322c03300006bbf1fd47b7d301494f731d3fe0b8a12523b9aa5cddfa258411`; and Bevy + egui `67762ba0b128eeb5dd0964b27312c5ebd96709b7279245ea70f781ef55af8baf`, `f93152f980fb3d8bfe0ed3186cd95a89a3479a31fc857a23a6e976da05fd5d44`, `f93152f980fb3d8bfe0ed3186cd95a89a3479a31fc857a23a6e976da05fd5d44`. JSONL SHA-256 values were Slint `157b9620c9571853544a81e2d26ee83cd6b8b3d4bdc7dcd16dca8d6b66595594`, QML `a98a21ca387dbfc24da4f6c705b469ec1ff5a8a828184c853eff767e1f2f11c7`, and Bevy + egui `50136cf73f6368d4fc334de0b9cf255d64da83b751443d20c0a00fbbe5de1652`.

This preserves one unsuccessful two-click sequence per implementation without adding a verified second-click interaction. Slint still has only the earlier single-click selection evidence, QML now has an additional delayed single-selection observation but no deselection evidence, and Bevy + egui row selection remains unverified. Repeated-run reliability, modified/multi-selection, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Company-column resize pointer captures (2026-11-22)

A development-only `/tmp/run_browser1_column_resize_pointer.py` driver attempted one real left-button drag on Company's right header edge, the Company/Sector boundary. Slint exposes an 8 px resize handle and updates the persistent column model during motion (`ui/grid.slint:527-538`, `src/browser1.rs:75-79,190-197`); QML enables resizable columns on its horizontal header/table (`Browser1Page.qml:111-116,163-174`); Bevy + egui uses TableBuilder resizing and excludes a 6 px header-edge zone from sorting/reorder handling (`src/ui/tabs/browser/browser_1.rs:174-205,505-523,631-637`). The limited requested action was a 60-review-pixel widening, not an assumption about exact framework geometry after clipping.

The accepted invocation for each implementation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_column_resize_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-column-resize-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-column-resize-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The drag began at review x=310 and logical x=1275, then used six relative +6 logical-x motion steps before release, ending at logical x=1311 for a requested +60 review-pixel displacement. Header y targets were Slint review/logical `(310,243)` / `(1275,493.2)`, QML `(310,271)` / `(1275,510)`, and Bevy + egui `(310,263)` / `(1275,505.2)`. The Browser-primary focus points and raw/review crop conversion were unchanged. Every fresh native light/100% process attempted one focus click and one drag, parked at logical `(100,100)` before each capture, passed five Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection.

Procedural `status=failed` for Slint and QML records only identical before/after review PNGs after clean exit. Bevy + egui passed the capture-distinctness check, but this does not assert resizing. Every record retains `column_resize_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection is the interaction oracle.

| Implementation | Subsequent visual review | Clean exit |
|---|---|---|
| Slint | Byte-identical before/after review PNGs; Company/Sector boundary and rows unchanged | Acknowledged quit, status 0 |
| QML | Byte-identical before/after review PNGs; Company/Sector boundary and rows unchanged | Acknowledged quit, status 0 |
| Bevy + egui | Company/Sector boundary and rows unchanged; only toolbar-region differences | Acknowledged quit, status 0 |

Independent RGB comparison found no Slint or QML review-pixel difference. Bevy + egui's difference was confined to `(13,64,474,276)`, above the data rows, with no observed width change. These unsuccessful drag attempts do not distinguish input-delivery, hit-target, motion-processing, focus, and application causes and do not establish implementation defects. No attempt was retried.

Independent validation checked all three records' exact focus-click/drag fields, five-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 3 focus clicks, 3 drags, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `88f170a008c7c7ab034750fd7652acf9342aab755b510c47f47d48938ebf6ea5` twice; QML `7fb3b33103b6422956f51e508b401eabee2d014d9f8e769f9b78d087e2110e70` twice; and Bevy + egui `99d75234fc062d804311b5592f3f561c2f207db678a99ea8e7f052b618c2ae4e` and `0227980cff1904fea6c3932a2f2bda0546dc38c479019e61cc61489c194b1b54`. JSONL SHA-256 values were Slint `feb490333e125e467a1efea4d84a0715772ec29b0e42d6d3d80a8f2baff18208`, QML `492675adca97c0696d45adfd037b02259d333a0078c8d2f2227d817fa0e25e30`, and Bevy + egui `af1ce5aab5002f52fabbd3b0c3633cc6d337cfadb5072d5254eb63b8112202ef`.

This adds no verified column-resize interaction. Slint/QML sorting and single-click selection evidence does not generalize to drag behavior, and Bevy + egui page-content interaction remains unverified. Other resize targets/directions, reorder, scrolling, repeated-run reliability, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Slint Browser 1 two-click Company-toggle pointer captures (2026-11-22)

A Slint-only follow-up extended the previously verified ascending Company interaction to a second click. Repeated activation of the same header toggles direction (`src/browser1.rs:175-188`), and Company uses string comparison (`src/data.rs:238-256`). QML and Bevy + egui were deliberately not rerun: their first Company activation remains unverified, so this task does not retry those unsuccessful interactions or impose a second-click oracle on them.

The development-only `/tmp/run_slint_browser1_company_toggle_pointer.py` driver used one fresh native light/100% Slint process. Its accepted invocation was:

```bash
python3 /tmp/run_slint_browser1_company_toggle_pointer.py \
  --work-root "/tmp/ui-framework-slint-browser1-company-toggle-pointer-2026-11-22-01/slint" \
  --jsonl "/tmp/ui-framework-slint-browser1-company-toggle-pointer-2026-11-22-01/slint.jsonl" \
  --settle 2
```

The process attempted one Browser-primary focus click at `(1128,423.6)` and two Company-header clicks at `(1209,493.2)`, corresponding to review-crop point `(200,243)`. It parked at logical `(100,100)` before each capture, passed seven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` requires three attempted clicks, unchanged route, three pairwise-distinct decodable review captures, and clean exit. The JSONL retains `ascending_company_sort_visually_verified=false`, `descending_company_sort_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection is the sorting oracle.

| Capture | Subsequent visual review |
|---|---|
| Before | Canonical source order with no Company sort marker |
| After first Company click | Ascending Company marker and repeated `Apex` leaders |
| After second Company click | Descending Company marker and repeated `Union` leaders in descending lexical order |

Independent RGB comparison found differences in `(6,202,1425,1057)` for before/after-first and before/after-second and `(8,202,1425,1057)` for after-first/after-second, including the expected header and row changes. Independent validation checked the exact three-click/seven-route sequence, executable hash, visual-review flags, clean exit, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 3 clicks, 7 Browser 1 readbacks, and 6 recorded PNGs. Before/after-first/after-second review SHA-256 values were `68350037b7765ffc1cb09a8a5ef2eee4acb09eff0a67d37a5fa26480d312483b`, `634dffc94f239301b8bd2f8a21213b7c6e03179290a618672698eb4c38b83657`, and `7547a0a4ce0e7d8902a52b8ffdca45a9d3604c5fc1a94e947c74a392f54a6d44`; the JSONL SHA-256 was `7bd9081ed28e7ebc61316252dd6054cd2e17bb7b9ec5685d48f9cd24ea53f148`.

This establishes one real Slint ascending/descending Company sequence, adding string-column direction-toggle evidence without changing QML or Bevy + egui Company status. It is not repeated-run reliability, another string column, editing, drag, scrolling, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 sorted-first-row selection pointer captures (2026-11-22)

A Slint/QML-only follow-up tested stable row identity after sorting. Slint maps the clicked display index through its current ordering to a stable source-row identity (`src/browser1.rs:146-160`); QML delegates supply their stable `rowId` to the selection toggle (`Browser1Page.qml:21-38,176-219`). After an ascending Price sort, the displayed first row is `NHP`, not canonical source-first `IM`. Bevy + egui was deliberately excluded because its prerequisite Price sort remains unverified after three preserved unsuccessful attempts.

The development-only `/tmp/run_browser1_sorted_first_row_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_sorted_first_row_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-sorted-first-row-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-sorted-first-row-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

| Implementation | Browser-primary focus logical point | Price review/logical point | Sorted first-row Company review/logical point |
|---|---:|---:|---:|
| Slint | `(1128,423.6)` | `(500,243)` / `(1389,493.2)` | `(200,273)` / `(1209,511.2)` |
| QML | `(1128,422.4)` | `(500,271)` / `(1389,510)` | `(200,302)` / `(1209,528.6)` |

Each process attempted one focus click, one Price-header click, and one click on the newly leading row's Company cell. It parked at logical `(100,100)` before every capture, passed seven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` for both records means only that all three clicks were attempted, the route remained unchanged, three pairwise-distinct decodable review captures were produced, and clean exit completed. Both JSONL records retain `price_sort_visually_verified=false`, `sorted_row_selection_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of the labeled contact sheet is the page-content oracle.

| Implementation | Before | After Price click | After sorted-first-row click | Clean exit |
|---|---|---|---|---|
| Slint | Canonical source order with source-first `IM` | Ascending Price marker and leading `NHP 2.39` | Leading `NHP` highlighted and selection status `Rows: NHP`, not source-first `IM` | Acknowledged quit, status 0 |
| QML | Canonical source order with source-first `IM` | Ascending Price marker and leading `NHP $2.39` | Leading `NHP` highlighted and selected-row status identifies `NHP`, not source-first `IM` | Acknowledged quit, status 0 |

Independent RGB comparison measured Slint difference bounds `(1,202,1460,1057)` for before/after-sort and before/after-selection and `(1,202,1460,286)` for after-sort/after-selection. QML bounds were `(8,257,1447,1060)` for before/after-sort, `(0,224,1471,316)` for after-sort/after-selection, and `(0,224,1471,1060)` for before/after-selection. These bounds support capture review but are not the interaction oracle.

Independent validation checked both records' exact three-click/seven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 6 clicks, 14 Browser 1 readbacks, and 12 recorded PNGs. Before/after-sort/after-selection review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`, `6028c56d81e50f34d5c865ecefce79a092df35ed4a93765cd5100370d4ac68d2`, and `c3ac8a0a94960e802624cfc7f688a38e27ca0a99e38deaef441ac8822774afa3`; QML `a09da9f43afc6233a32bc872747760e0391d082ffee55041c8caa2a8c9cdd3f9`, `fb0593fc3a2060ef96e46423651c33035e2341b1efa7205cdbcadc16c290aefe`, and `2cab46a9121dea07cefc73489c1bd4cb5c9f0a77e6b2efb9170caffa9105a5d6`. JSONL SHA-256 values were Slint `31bf793d350078d92ff6f88c0382da8d4801e2590a8804048c171e252c63dc30` and QML `894e69dba4d19601189f9668113c26c69d71dd9e13c5565587edf7f5bbb6bd74`.

This establishes one sorted-view stable-identity selection sequence for each of Slint and QML: pointer sorting led with `NHP`, and clicking that displayed row selected `NHP` rather than source-first `IM`. It does not establish repeated-run reliability, repeated-row deselection, modified/multi-selection, Bevy + egui behavior, other sorted columns, editing, scrolling, drag, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 sorted-row select/deselect pointer captures (2026-11-22)

A Slint/QML-only follow-up extended the verified sorted-first-row selection into a two-click toggle cycle. Both implementations toggle stable row membership on repeated activation (`src/browser1.rs:146-160`, `Browser1Page.qml:21-38,176-219`), so the limited oracle was ascending Price, select displayed `NHP`, then deselect that same row without reverting the sort. Bevy + egui remained excluded because its prerequisite Price sort is unverified.

The development-only `/tmp/run_browser1_sorted_row_toggle_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_sorted_row_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-sorted-row-toggle-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-sorted-row-toggle-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The focus, Price, and row targets exactly reused the preceding sorted-first-row run: Slint `(1128,423.6)`, `(1389,493.2)`, and `(1209,511.2)`; QML `(1128,422.4)`, `(1389,510)`, and `(1209,528.6)`. Price review-crop points were `(500,243)` and `(500,271)`; row points were `(200,273)` and `(200,302)`, respectively. Each process attempted focus, Price, and two clicks on the newly leading row's Company cell. It parked at logical `(100,100)` before every capture, passed nine Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all four clicks were attempted, the route remained unchanged, before/after-sort, after-sort/after-selection, and after-selection/after-second-click review pairs were distinct, and clean exit completed. The driver deliberately did not require after-sort and after-second-click images to differ, because exact unselected-state restoration is valid toggle evidence. Both JSONL records retain `price_sort_visually_verified=false`, `sorted_row_selection_visually_verified=false`, `sorted_row_deselection_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of labeled contact/detail sheets is the page-content oracle.

| Implementation | After Price | After first sorted-row click | After second sorted-row click | Clean exit |
|---|---|---|---|---|
| Slint | Ascending Price with leading `NHP 2.39` | Leading `NHP` highlighted and `Rows: NHP` | Exact post-sort review PNG restored; `NHP` highlight and selection status cleared | Acknowledged quit, status 0 |
| QML | Ascending Price with leading `NHP $2.39` | Leading `NHP` highlighted and selected-row status identifies `NHP` | Exact post-sort review PNG restored; `NHP` highlight and selection status cleared | Acknowledged quit, status 0 |

Independent RGB comparison measured Slint bounds `(1,202,1460,1057)` for before/after-sort and before/after-second-click, `(1,202,1460,286)` for after-sort/after-selection and after-selection/after-second-click, and no after-sort/after-second-click difference. QML bounds were `(8,257,1447,1060)` for before/after-sort and before/after-second-click, `(0,224,1471,316)` for after-sort/after-selection and after-selection/after-second-click, and no after-sort/after-second-click difference. Before/after-selection bounds were Slint `(1,202,1460,1057)` and QML `(0,224,1471,1060)`.

Independent validation checked both records' exact four-click/nine-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, all six pairwise-distinctness fields, exact post-sort restoration, and SHA-256 values: 8 clicks, 18 Browser 1 readbacks, and 16 recorded PNGs. Before/after-sort/after-selection/after-second-click review SHA-256 values were Slint `ea6ecdab4d6c875977f728b6f7644443ecd8c0cd3622ea6de33c006b834ecc7b`, `12687587f077f0c9cdf6883e41d6b10976a7bdbf360a53337bc63f76011f4dec`, `3fdd648d7ac9a7955e5f0873534156f8ab4a3612b80909ce57c7974ef7ffcea3`, and `12687587f077f0c9cdf6883e41d6b10976a7bdbf360a53337bc63f76011f4dec`; QML `693b3bcaa2f2a0370efaead454bbb246aa0f61c35a11ccb1649138886d4433e6`, `1ea22f612cd9e235a6567c867b8dc2cfccc13b2090191fe1e35ea6db345862e4`, `53a66c4d6856f95899172b07e32a1363dce634d7b9344ccc58e579acc2204735`, and `1ea22f612cd9e235a6567c867b8dc2cfccc13b2090191fe1e35ea6db345862e4`. JSONL SHA-256 values were Slint `166d4fe865e05042a460eec143cbf59e826d2e7260b0ad5e791d65263f5038a7` and QML `fa7a1030960685581dfc2f17becf6c4428ded7d0d1f2d848af2b9b8835c35a91`. An initial validator incorrectly normalized all capture stems to hyphenated filenames; correcting it to the recorded paths passed without modifying artifacts or rerunning either application.

This establishes one complete sorted-view select/deselect cycle for each of Slint and QML, including exact post-sort pixel restoration after the second click. It does not establish a canonical-source-row repeated-click cycle, repeated-run reliability, modified/multi-selection, Bevy + egui behavior, other sorted columns, editing, scrolling, drag, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 sorted-row multi-selection pointer captures (2026-11-22)

A Slint/QML-only follow-up tested retained membership across two different sorted rows. Slint inserts each clicked source-row identity without clearing existing membership (`src/browser1.rs:146-160`); QML independently toggles each delegate's stable `rowId` (`Browser1Page.qml:21-38,176-219`). After ascending Price, the limited oracle was to select leading `NHP`, then second-row `MJC`, and retain both. Bevy + egui remained excluded because its basic row selection is unverified.

The development-only `/tmp/run_browser1_sorted_multi_selection_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_sorted_multi_selection_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-sorted-multi-selection-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-sorted-multi-selection-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Focus and Price targets were unchanged from the preceding sorted-row runs. Slint's 26 px row height (`ui/grid.slint:344-345,734-735`) puts the second-row Company target at review/logical `(200,299)` / `(1209,526.8)`, 26 review pixels below the first-row `(200,273)` / `(1209,511.2)`. QML's 28 px delegate plus 1 px row spacing (`Browser1Page.qml:170-171,176-185`) puts its second-row target at `(200,331)` / `(1209,546)`, below its first-row `(200,302)` / `(1209,528.6)`. These remain setup-specific coordinates, not resolution-independent application geometry.

Each process attempted focus, Price, first-row, and second-row clicks. It parked at logical `(100,100)` before every capture, passed nine Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all four clicks were attempted, the route remained unchanged, before/after-sort, after-sort/after-first-selection, and after-first/after-second-selection review pairs were distinct, and clean exit completed. All six review pairs were in fact distinct for both records. Both JSONL records retain `price_sort_visually_verified=false`, `sorted_first_row_selection_visually_verified=false`, `sorted_two_row_selection_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of the labeled contact sheet is the page-content oracle.

| Implementation | After Price | After first row click | After second row click | Clean exit |
|---|---|---|---|---|
| Slint | Ascending Price with leading `NHP 2.39`, then `MJC 4.33` | Only leading `NHP` highlighted | Both `NHP` and `MJC` highlighted; selection status identifies both | Acknowledged quit, status 0 |
| QML | Ascending Price with leading `NHP $2.39`, then `MJC $4.33` | Only leading `NHP` highlighted | Both `NHP` and `MJC` highlighted; selected-row status identifies both | Acknowledged quit, status 0 |

Independent RGB comparison measured Slint bounds `(1,202,1460,1057)` for before/after-sort and both before/after-selection comparisons, `(1,202,1460,286)` for after-sort/after-first-selection, and `(1,202,1460,312)` for after-sort/after-second-selection and after-first/after-second-selection. QML bounds were `(8,257,1447,1060)` for before/after-sort, `(0,224,1471,1060)` for both before/after-selection comparisons, `(0,224,1471,316)` for after-sort/after-first-selection, and `(0,224,1471,345)` for after-sort/after-second-selection and after-first/after-second-selection.

Independent validation checked both records' exact four-click/nine-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, all six pairwise-distinctness fields, and SHA-256 values: 8 clicks, 18 Browser 1 readbacks, and 16 recorded PNGs. Before/after-sort/after-first-selection/after-second-selection review SHA-256 values were Slint `61d9e6f188ebd9f3088acfabb191ab6278410e5de7b697f47c1fc10c2404e534`, `b4b97239631b1256cc27bc363a862f2b446290efe9c24d4af097f8ed1716fe79`, `7ff3d947ef920531abf2dfbb389e650f48a235163bee96fff6581bc832d56f83`, and `24ec8d2f2b172b6f3a0db75566c67d6aa30ec8823f82843a9d66c62d2ca6f82a`; QML `fb999c1308fecfde1dedacabc97b5bec43ed568de89250eac1ceec8ad872fc4c`, `0fe0892c756cc998d6a74ea261914f6cf47712d72d0cfc373954b60aeaf996ea`, `1c92aadf922b3535eded263be4a8871ab875cdf5641d3d5ee33ef5359ac9086e`, and `da46296cfaa595a6b3392ce108e7b08a86afee9752e54f39c98f5a94f9f8a80c`. JSONL SHA-256 values were Slint `8b4cf47cf566d79533f6969c0875805b97b109e22b323dac4c2d3e1efe87692c` and QML `45b9dcd84e9ec3a734a23436c3eca933452b2d0075dca9dbd5703c4c501379e9`.

This establishes one unmodified two-row sorted-view selection sequence for each of Slint and QML: clicking `MJC` added it without clearing `NHP`. It does not establish canonical-source-row multi-selection, modified/disjoint selection, repeated-run reliability, Bevy + egui behavior, other sorted columns, editing, scrolling, drag, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 sorted-row selective-deselection pointer captures (2026-11-22)

A Slint/QML-only follow-up tested independent removal from a two-row selection. The same stable-identity toggle paths (`src/browser1.rs:146-160`, `Browser1Page.qml:21-38,176-219`) imply that removing `NHP` must not clear `MJC`. The limited sequence was ascending Price, select `NHP`, add `MJC`, then click `NHP` again and retain only `MJC`. Bevy + egui remained excluded because its basic row selection is unverified.

The development-only `/tmp/run_browser1_selective_deselection_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_selective_deselection_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-selective-deselection-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-selective-deselection-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

All targets exactly reused the preceding multi-selection run. Slint first/second-row Company targets were review/logical `(200,273)` / `(1209,511.2)` and `(200,299)` / `(1209,526.8)`; QML targets were `(200,302)` / `(1209,528.6)` and `(200,331)` / `(1209,546)`. Focus and Price targets were unchanged. Each process attempted five clicks including focus and Price, parked at logical `(100,100)` before every capture, passed eleven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all five clicks were attempted, the route remained unchanged, the four sequential capture pairs were distinct, and clean exit completed. All ten review pairs were in fact distinct for both records. Both JSONL records retain `price_sort_visually_verified=false`, `sorted_two_row_selection_visually_verified=false`, `selective_deselection_visually_verified=false`, and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of the labeled contact sheet is the page-content oracle.

| Capture | Slint visual review | QML visual review |
|---|---|---|
| Before | Canonical source order, empty selection | Canonical source order, empty selection |
| After Price | Ascending `NHP 2.39`, `MJC 4.33` leaders | Ascending `NHP $2.39`, `MJC $4.33` leaders |
| After `NHP` selection | Only `NHP` highlighted | Only `NHP` highlighted |
| After `MJC` selection | Both `NHP` and `MJC` highlighted | Both `NHP` and `MJC` highlighted |
| After second `NHP` click | `NHP` unselected; only `MJC` remains highlighted and identified in selection status | `NHP` unselected; only `MJC` remains highlighted and identified in selection status |

Both processes acknowledged `quit` and exited with status 0. Independent RGB comparison measured Slint bounds `(1,202,1460,1057)` for every before/sorted-or-selected comparison, `(1,202,1460,286)` for after-sort/after-`NHP` and after-two/after-deselection, and `(1,202,1460,312)` for the other sorted/selected comparisons. QML bounds were `(8,257,1447,1060)` for before/after-sort, `(0,224,1471,1060)` for every other before/after-selection comparison, `(0,224,1471,316)` for after-sort/after-`NHP` and after-two/after-deselection, and `(0,224,1471,345)` for the other sorted/selected comparisons.

Independent validation checked both records' exact five-click/eleven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, all ten pairwise-distinctness fields, and SHA-256 values: 10 clicks, 22 Browser 1 readbacks, and 20 recorded PNGs. Before/after-sort/after-`NHP`/after-two/after-deselection review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`, `6028c56d81e50f34d5c865ecefce79a092df35ed4a93765cd5100370d4ac68d2`, `c3ac8a0a94960e802624cfc7f688a38e27ca0a99e38deaef441ac8822774afa3`, `276834f14d21e676c2980ded2d0efe7cd7a08781e5cc29a6d9f5e266b3d3138d`, and `a385071d8a965d7c9b6ecde0edb4ec2c38af4535889f08e59e901574d5003055`; QML `2691e334a5ecc4383c74d8b4a707bb81b2bcd41a8bfc94484a5cac86e5bd3e28`, `12899f3eb2bfd9730b8a0c8dc15dd83cc0a3b62b36a5fde192fe9cf62178912a`, `e20d0b2cc9094dd210cfc9f337faf9ed1d5d41ba12bf6519290ec4c98b58e282`, `c9e81c86a8d2e8ef2629a359cd3eeb216d821e36c35dc551ba6c9571086fc66f`, and `3736defdd895c6b61abd3535f62da65f4b92bfbedc454662574d1e4f243e4836`. JSONL SHA-256 values were Slint `5d795f9b1ee72ac609a6ce982c601b0040ac6d6539371824790e3d84506d91df` and QML `8d75d019499a57744f7b37f4729d2be737c48c5bae1737e200ab845bbb7bc740`.

This establishes one selective-deselection sequence for each of Slint and QML: removing `NHP` preserved `MJC` and the ascending row order. It does not establish modified/disjoint selection, canonical-source-row multi-selection, repeated-run reliability, Bevy + egui behavior, other sorted columns, editing, scrolling, drag, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Symbol-header page-content pointer captures (2026-11-22)

A new-target Browser 1 run tested one fresh-state Symbol-header click in each implementation. Symbol is a string column with typed lexical comparison (`src/data.rs:238-256`, `Browser1Page.qml:40-52`, `browser1sortproxymodel.cpp:11-56`, and Bevy + egui `src/ui/tabs/browser/browser_1_model.rs:5-24`). First activation requests ascending order (`src/browser1.rs:175-188`, `src/ui/state/browser_1_state.rs:157-166`). This was not a retry of the unsuccessful QML Company or Bevy + egui Price/Company targets.

The development-only `/tmp/run_browser1_symbol_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_symbol_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-symbol-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-symbol-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The shared 90 px Symbol width and following 220 px Company width place their centers at review x=45 and x=200 (`src/data.rs:42-54`, `Browser1Page.qml:24-25`, and `fixtures/manifests/browser1.json:49-53`). Symbol targets were therefore Slint review/logical `(45,243)` / `(1116,493.2)`, QML `(45,271)` / `(1116,510)`, and Bevy + egui `(45,263)` / `(1116,505.2)`. Browser-primary focus targets were unchanged from the Company runs. Every process attempted one focus click and one Symbol-header click, parked at logical `(100,100)` before each capture, passed five Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` for all three records means only that both clicks were attempted, the route remained unchanged, distinct decodable before/after review captures were produced, and clean exit completed. Every JSONL retains `symbol_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of labeled contact/detail sheets is the sorting oracle.

| Implementation | Before | After Symbol click | Clean exit |
|---|---|---|---|
| Slint | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending Symbol marker and lexical leaders `AAR`, `AARR`, `AB`, `ABH`, `ABKH` | Acknowledged quit, status 0 |
| QML | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending Symbol marker and the same lexical leaders | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Original order retained; no ascending marker or sorted rows observed | Acknowledged quit, status 0 |

Independent RGB comparison measured difference bounds Slint `(1,202,1425,1057)` and QML `(0,257,1447,1060)`, including their headers and row changes. Bevy + egui's differences were confined to `(8,64,233,276)`, above the data rows, despite its procedural distinct-capture pass. This unsuccessful new-target interaction does not distinguish input delivery, hit targeting, focus, and application causes and does not establish a defect. No attempt was retried.

Independent validation checked all three records' exact two-click/five-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 6 clicks, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd` and `d468edc58a96725f7630f801ad816e8aaf6890470ce6badc06709f93261a48fb`; QML `7074e9fc7ec33abf117a788fed369e763623f8d1495ee5cab5d2f626411473cd` and `ec272e12411bcaa1a3390a3b74cd20614114f02faa69dec1e86669e2f1e752d6`; and Bevy + egui `d21591e9744a59edbb7a46f835f8ef488a098745c47f6f1762acfa86ca790650` and `be7bbb36379eeebbdced188bbe1b915677e346d0ff4b82d434323814921837b1`. JSONL SHA-256 values were Slint `142109b5f60dba89d60df5976890a2c1fcb53b3df418f52bdf6b28e6e41b9c91`, QML `dc2f3ac254fa46137966a3687f68b204c12b4fe2d42b6e67e7ef7880da9bfbd8`, and Bevy + egui `6f21aab2ea335fe80d0fddcaf8dcb1314bac1c6845a8cb28b7b3ddbbaa42faee`.

This establishes one real ascending Symbol-sort interaction for Slint and QML. QML's earlier Company result is unchanged, and Bevy + egui Symbol sorting remains unverified after one preserved unsuccessful new-target attempt. Other headers and directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Symbol-toggle pointer captures (2026-11-22)

A Slint/QML-only follow-up tested a second fresh-state Symbol-header activation. The existing repeated-header paths toggle ascending/descending direction (`src/browser1.rs:175-188` and `Browser1Page.qml:40-52`), with typed lexical comparison in `src/data.rs:238-256` and `browser1sortproxymodel.cpp:11-56`. The limited sequence requested ascending then descending Symbol order. Bevy + egui remained excluded because its first Symbol activation is unverified.

The development-only `/tmp/run_browser1_symbol_toggle_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_symbol_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-symbol-toggle-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-symbol-toggle-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Symbol targets exactly reused the preceding fresh-state run: Slint review/logical `(45,243)` / `(1116,493.2)` and QML `(45,271)` / `(1116,510)`. Browser-primary focus targets were unchanged. Each process attempted one focus click and two Symbol-header clicks, parked at logical `(100,100)` before every capture, passed seven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all three clicks were attempted, the route remained unchanged, all three review-capture pairs were distinct, and clean exit completed. Both JSONL records retain `ascending_symbol_sort_visually_verified=false`, `descending_symbol_sort_visually_verified=false`, `capture_pixel_content_reviewed=false`, `rendered_frame_verified=false`, and `equivalence_established=false`; subsequent assistant inspection of labeled detail sheets is the page-content oracle.

| Capture | Slint visual review | QML visual review |
|---|---|---|
| Before | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` |
| After first Symbol click | Ascending marker and lexical leaders `AAR`, `AARR`, `AB`, `ABH`, `ABKH` | Ascending marker and the same lexical leaders |
| After second Symbol click | Descending marker and lexical leaders `ZZIW`, `ZZE`, `ZYQJ`, `ZX`, `ZX` | Descending marker and the same lexical leaders |

Independent RGB comparison measured Slint difference bounds `(1,202,1425,1057)` for before/after-first and before/after-second, and `(8,202,1425,1057)` for after-first/after-second. QML bounds were `(0,257,1447,1060)` for before/after-first and before/after-second, and `(8,267,1447,1060)` for after-first/after-second. Capture inequality alone was not treated as sorting evidence.

Independent validation checked both records' exact three-click/seven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 6 clicks, 14 Browser 1 readbacks, and 12 recorded PNGs. Before/after-first/after-second review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`, `d468edc58a96725f7630f801ad816e8aaf6890470ce6badc06709f93261a48fb`, and `590fc8fd834ee47ff1b8f12ea5cc8fb9a80618a5eea290ca8dae284cddf46cb1`; QML `f5fc39aff20dc4c6b119dfb71520be951f23a6c553f80aa366e3d37184a15935`, `0094b954318691b5ba51f116e1b58cf4605af0bd8fce16955e3ad41d3fdb358f`, and `31943fa05560ab796c3a6c146fa6d6e1838a10243c81ccf7b21decdfe0aa5e81`. JSONL SHA-256 values were Slint `530e0af7a73d89c300552bf203073e790ac1ef072642b80fae1cdb4cfbbb6409` and QML `a487c2007c2b85a440b4f82c597e3ae8a2b917cd3e394220bae9122defbb28c4`.

This establishes one real ascending-then-descending Symbol-sort sequence for each of Slint and QML. It does not establish Bevy + egui Symbol sorting, QML Company sorting, other headers/directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 selection-resort pointer captures (2026-11-22)

A Slint/QML-only follow-up tested stable row selection across Symbol direction changes. Slint resolves the displayed row through its current ordering and stores selected source-row identities (`src/browser1.rs:146-187`); QML keys selection by stable source `rowId`, independently of proxy display position (`Browser1Page.qml:21-52,176-219`). The limited sequence was ascending Symbol, select displayed leader `AAR`, descending Symbol, then restored ascending Symbol. Bevy + egui remained excluded because both Symbol sorting and row selection are unverified.

The development-only `/tmp/run_browser1_selection_resort_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_selection_resort_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-selection-resort-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-selection-resort-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Symbol targets exactly reused the preceding toggle runs. First-row Company targets were Slint review/logical `(200,273)` / `(1209,511.2)` and QML `(200,302)` / `(1209,528.6)`; Browser-primary focus targets were unchanged. Each process attempted five clicks including focus, three Symbol-header activations, and one row activation, parked at logical `(100,100)` before every capture, passed eleven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all five clicks were attempted, the route remained unchanged, all four sequential review-capture pairs were distinct, and clean exit completed. Both JSONL records retain all sorting, selection, capture-review, rendered-frame, and equivalence flags as false; subsequent assistant inspection of labeled detail/status sheets is the page-content oracle. Exact after-selection/after-restored equality was recorded independently and intentionally accepted rather than treated as a failed all-pairs-distinctness check.

| Capture | Slint visual review | QML visual review |
|---|---|---|
| Before | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI`; empty selection | Canonical source leaders and empty selection |
| After first Symbol click | Ascending `AAR`, `AARR`, `AB`, `ABH`, `ABKH`; empty selection | Same ascending leaders and empty selection |
| After `AAR` row click | `AAR` highlighted; status `Rows: AAR` | `AAR` highlighted; status `Selected rows: AAR` |
| After second Symbol click | Descending `ZZIW`, `ZZE`, `ZYQJ`, `ZX`, `ZX`; `AAR` offscreen and status remains `Rows: AAR` | Same descending leaders; `AAR` offscreen and status remains `Selected rows: AAR` |
| After third Symbol click | Ascending order and highlighted `AAR` restored; exact after-selection review PNG | Ascending order and highlighted `AAR` restored; exact after-selection review PNG |

Independent RGB comparison measured Slint bounds `(1,202,1425,1057)` for before/after-sort and before/after-descending, `(1,202,1460,1057)` for the other before/later comparisons, `(1,202,1460,286)` for after-sort/after-selection and after-sort/after-restored, `(8,202,1425,1057)` for after-sort/after-descending, and `(1,202,1460,1057)` for after-selection-or-restored/after-descending. QML bounds were `(0,257,1447,1060)` for before/after-sort, `(0,224,1447,1060)` for before/after-descending, `(0,224,1471,1060)` for the other before/later comparisons, `(0,224,1471,316)` for after-sort/after-selection and after-sort/after-restored, `(8,224,1447,1060)` for after-sort/after-descending, and `(0,267,1471,1060)` for after-selection-or-restored/after-descending. After-selection/after-restored RGB difference bounds were null in both implementations.

Independent validation checked both records' exact five-click/eleven-route sequences, executable hashes, visual-review flags, clean exits, capture modes/dimensions/byte counts, all ten pairwise-distinctness fields, exact-restoration fields, and SHA-256 values: 10 clicks, 22 Browser 1 readbacks, and 20 recorded PNGs. Before/after-sort/after-selection/after-descending/after-restored review SHA-256 values were Slint `f06fcdc4f4ef7e2e2c21cae58d827cf7f01ced90f599227291227984e328d902`, `6d4452fd92e584919af866ba100878d296a9a141d8a1a057f4f0af512d008f22`, `50c82d4779b18bb91a123e11e975575f3e96551fc3ac6f1c95fdf54d5341430e`, `286b7089ba773f442e64b7b7d49f42bbc6087b08ff6b8b3bc70493450bc9bee4`, and `50c82d4779b18bb91a123e11e975575f3e96551fc3ac6f1c95fdf54d5341430e`; QML `d71441207f2be6ddd8cc4dccb312db9fecce8acbd2741925161da228b92dedba`, `5ab56f197267360012548aa67184becc38475238ef19accbba0131878c1b95a7`, `15c07962870bb0802db6f499e87d598e82e387260e304843804bb0f51a28b35e`, `00c4e394939e75f89d7d2ef56840823b1942950df494f2bfb3b55f3321baa712`, and `15c07962870bb0802db6f499e87d598e82e387260e304843804bb0f51a28b35e`. JSONL SHA-256 values were Slint `7a1222cef1e28dc57ef18bd6ead30ce3e728c7bbf21ff7ad8161ab2987350842` and QML `3fc42248024dbd106ca9dea6c5bfa1ae3ebd3206272a9331d20b0bfc23201e36`.

This establishes one stable-selection-through-resorting sequence for each of Slint and QML: `AAR` remained selected while descending order moved it offscreen, and the third Symbol click restored the exact selected ascending capture. It does not establish canonical-source-row repeated-click behavior, modified/disjoint selection, repeated-run reliability, Bevy + egui behavior, other sorted columns, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Change %-header page-content pointer captures (2026-11-22)

A new-target Browser 1 run tested one fresh-state Change % header click in each implementation. Change % is a non-null signed numeric column with typed comparison (`src/data.rs:238-274`, `Browser1Page.qml:40-52`, `browser1sortproxymodel.cpp:11-56`, and Bevy + egui `src/ui/tabs/browser/browser_1_model.rs:5-24`). First activation requests ascending order. Sorting the executable parent generator's `browser1_rows()` by raw `change_pct` gives expected leaders `GUO -5.999998936`, `MSRU -5.999034552`, `TJH -5.997427117`, `IZN -5.997093220`, and `OQNH -5.982578783`. This was a new target, not a retry of QML Company or Bevy + egui Price/Company/Symbol.

The development-only `/tmp/run_browser1_change_percent_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_change_percent_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-change-percent-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-change-percent-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The shared widths before Change % are 90+220+140+100 px and its own width is 100 px, placing its center at review x=600 (`src/data.rs:42-54`, `Browser1Page.qml:24-25`, and `fixtures/manifests/browser1.json:49-53`). Change % targets were therefore Slint review/logical `(600,243)` / `(1449,493.2)`, QML `(600,271)` / `(1449,510)`, and Bevy + egui `(600,263)` / `(1449,505.2)`. Browser-primary focus targets were unchanged. Every process attempted one focus click and one Change %-header click, parked at logical `(100,100)` before each capture, passed five Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` for all three records means only that both clicks were attempted, the route remained unchanged, distinct decodable before/after review captures were produced, and clean exit completed. Every JSONL retains `change_percent_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of labeled detail sheets is the sorting oracle.

| Implementation | Before | After Change % click | Clean exit |
|---|---|---|---|
| Slint | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending marker/status and numeric leaders `GUO`, `MSRU`, `TJH`, `IZN`, `OQNH`, displayed as `-6.00%`, `-6.00%`, `-6.00%`, `-6.00%`, `-5.98%` | Acknowledged quit, status 0 |
| QML | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending marker and the same numeric leaders and displayed values | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Original order retained; no ascending marker or sorted rows observed | Acknowledged quit, status 0 |

Independent RGB comparison measured difference bounds Slint `(6,202,1425,1057)` and QML `(8,257,1447,1060)`, including their headers and row changes. Bevy + egui's differences were confined to `(13,64,690,276)`, above the data rows, despite its procedural distinct-capture pass. This unsuccessful new-target interaction does not distinguish input delivery, hit targeting, focus, and application causes and does not establish a defect. No attempt was retried.

Independent validation checked all three records' exact two-click/five-route sequences, target x-coordinates, executable hashes, expected leaders, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 6 clicks, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd` and `15f13a16c88a5c82af772e0dfc7fa8c02840685aa444a08bb733750323dac5d4`; QML `f81d156a79d013f75f6e4cc2bcc4b2a0dad8e6966232b1f029a95ec0ca8811d9` and `283793b9d9879a5dc5db5dcccdac49343ace6b5867c07d5471fa1c332c54cb51`; and Bevy + egui `d21591e9744a59edbb7a46f835f8ef488a098745c47f6f1762acfa86ca790650` and `b3af73f36c81e61b75051a686c447196fa042cb456b84502c1360d5f2330b842`. JSONL SHA-256 values were Slint `ca5ea2c296028643d42cc9e00098e7ec1fa46ea06d247bfc3f250a3ec1127a71`, QML `2ac98ab8798215c8696bf449d283e771a66b2c3d7f4e4e31e117ea90379a2e25`, and Bevy + egui `ddd9e0801b4644c0f49fff6dd452277fbed87724365b1a712ff67baab9eb5317`.

This establishes one real ascending signed-numeric Change %-sort interaction for Slint and QML. Bevy + egui Change % sorting remains unverified after one preserved unsuccessful new-target attempt. Other headers and directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Change %-toggle pointer captures (2026-11-22)

A Slint/QML-only follow-up tested a second fresh-state Change % header activation. The existing repeated-header paths toggle ascending/descending direction (`src/browser1.rs:175-188` and `Browser1Page.qml:40-52`), with signed numeric comparison in `src/data.rs:238-274` and `browser1sortproxymodel.cpp:11-56`. The executable parent generator's raw-value oracle expects ascending `GUO`, `MSRU`, `TJH`, `IZN`, `OQNH` and descending `TTZ`, `QTR`, `UJQ`, `PSQY`, `OFDC`. Bevy + egui remained excluded because its first Change % activation is unverified.

The development-only `/tmp/run_browser1_change_percent_toggle_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_change_percent_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-change-percent-toggle-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-change-percent-toggle-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Change % targets exactly reused the preceding fresh-state run: Slint review/logical `(600,243)` / `(1449,493.2)` and QML `(600,271)` / `(1449,510)`. Browser-primary focus targets were unchanged. Each process attempted one focus click and two Change %-header clicks, parked at logical `(100,100)` before every capture, passed seven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all three clicks were attempted, the route remained unchanged, all three review-capture pairs were distinct, and clean exit completed. Both JSONL records retain `ascending_change_percent_sort_visually_verified=false`, `descending_change_percent_sort_visually_verified=false`, `capture_pixel_content_reviewed=false`, `rendered_frame_verified=false`, and `equivalence_established=false`; subsequent assistant inspection of labeled detail sheets and the Slint descending review capture is the page-content oracle.

| Capture | Slint visual review | QML visual review |
|---|---|---|
| Before | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` |
| After first Change % click | Ascending marker/status and numeric leaders `GUO`, `MSRU`, `TJH`, `IZN`, `OQNH` | Ascending marker and the same numeric leaders |
| After second Change % click | Descending marker/status and numeric leaders `TTZ`, `QTR`, `UJQ`, `PSQY`, `OFDC` | Descending marker and the same numeric leaders |

Independent RGB comparison measured Slint difference bounds `(6,202,1425,1057)` for all three capture pairs. QML bounds were `(8,257,1447,1060)` for before/after-first and before/after-second, and `(8,267,1447,1060)` for after-first/after-second. Capture inequality alone was not treated as sorting evidence.

Independent validation checked both records' exact three-click/seven-route sequences, target x-coordinates, executable hashes, expected leaders, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 6 clicks, 14 Browser 1 readbacks, and 12 recorded PNGs. Before/after-first/after-second review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`, `15f13a16c88a5c82af772e0dfc7fa8c02840685aa444a08bb733750323dac5d4`, and `905834aabc2c53d7b9c48cd0d37c326480e8ac7912340c3fdc8ede44f6d349e9`; QML `8de5ff3df53172ac5ee3549a4c3779d8c8aec1ad629a69d3f1ceddf75ae1d0fc`, `862268db7ebe9b51786c7ec5a19b3cf8a24c0c78d850a93d2975f1c1d8aa1ca5`, and `5b79a283798f3e2cf22069c6583351b07081448d6880c36e70108a7a976b6bf3`. JSONL SHA-256 values were Slint `b647ec1c4937b564310d1b3b27027b08fed38cadfdc6a63a8e410c42400be023` and QML `9d892b9dd60681630fd795227222f627737d800fddfdefcdfd234253f3ce86d5`.

This establishes one real ascending-then-descending signed-numeric Change %-sort sequence for each of Slint and QML. It does not establish Bevy + egui Change % sorting, other headers/directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Volume-header page-content pointer captures (2026-11-22)

A new-target Browser 1 run tested one fresh-state Volume header click in each implementation. Volume is a non-null integer column with typed comparison (`src/data.rs:238-274`, `Browser1Page.qml:40-52`, `browser1sortproxymodel.cpp:11-56`, and Bevy + egui `src/ui/tabs/browser/browser_1_model.rs:5-24`). First activation requests ascending order. Sorting the executable parent generator's `browser1_rows()` by raw integer `volume` gives expected leaders `CMXC 12007`, `XU 118794`, `FZ 126771`, `TTF 173752`, and `FQ 174734`. No tie occurs among those leaders, so this run does not claim tie-oracle coverage. This was a new target, not a retry of earlier unsuccessful headers.

The development-only `/tmp/run_browser1_volume_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_volume_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-volume-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-volume-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The shared widths before Volume are 90+220+140+100+100 px and its own width is 120 px, placing its center at review x=710 (`src/data.rs:42-54`, `Browser1Page.qml:24-25`, and `fixtures/manifests/browser1.json:49-53`). Volume targets were therefore Slint review/logical `(710,243)` / `(1515,493.2)`, QML `(710,271)` / `(1515,510)`, and Bevy + egui `(710,263)` / `(1515,505.2)`. Browser-primary focus targets were unchanged. Every process attempted one focus click and one Volume-header click, parked at logical `(100,100)` before each capture, passed five Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` for all three records means only that both clicks were attempted, the route remained unchanged, distinct decodable before/after review captures were produced, and clean exit completed. Every JSONL retains `volume_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of labeled detail sheets is the sorting oracle.

| Implementation | Before | After Volume click | Clean exit |
|---|---|---|---|
| Slint | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending marker/status and integer leaders `CMXC 12,007`, `XU 118,794`, `FZ 126,771`, `TTF 173,752`, `FQ 174,734` | Acknowledged quit, status 0 |
| QML | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending marker and the same integer leaders and values | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Original order retained; no ascending marker or sorted rows observed | Acknowledged quit, status 0 |

Independent RGB comparison measured difference bounds Slint `(6,202,1425,1057)` and QML `(8,257,1447,1060)`, including their headers and row changes. Bevy + egui's differences were confined to `(13,64,818,276)`, above the data rows, despite its procedural distinct-capture pass. This unsuccessful new-target interaction does not distinguish input delivery, hit targeting, focus, and application causes and does not establish a defect. No attempt was retried.

Independent validation checked all three records' exact two-click/five-route sequences, target x-coordinates, executable hashes, expected leaders and values, visual-review flags, clean exits, capture modes/dimensions/byte counts, and SHA-256 values: 6 clicks, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd` and `0bd4c4e4a8e6fcb76914b07cf5039b0ba1c5ee1b910494596eb4be5c6d7cb827`; QML `e0a95de7cf94079fbb3480ad5d99b64b2dc3ba66b59b2a3c8c39fa7ec61e50d6` and `9baa91f3a7585393d29b82e0e5e464c75201f69cdf20617e27ebdbd57b9b353a`; and Bevy + egui `d21591e9744a59edbb7a46f835f8ef488a098745c47f6f1762acfa86ca790650` and `bf2d49caa134879b34aeab1f411f575b89f5c71abc6f17688299d57805cf2430`. JSONL SHA-256 values were Slint `b3cd6cfdc67fb2063be55e6597ae7f1457ec6ebfa07d10f8af3929164a94fd02`, QML `de8942672b56247bacd48e3569cdbf72d75e53e1373b6abb88171777e7d364ff`, and Bevy + egui `8e2739ca9a1add4d085b572b7b4d1adc646ced85099a5fd43e9d36548959d12c`.

This establishes one real ascending integer Volume-sort interaction for Slint and QML. Bevy + egui Volume sorting remains unverified after one preserved unsuccessful new-target attempt. Other headers and directions, sort ties, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Volume-toggle pointer captures (2026-11-22)

A Slint/QML-only follow-up tested a second fresh-state Volume header activation. The existing repeated-header paths toggle ascending/descending direction (`src/browser1.rs:175-188` and `Browser1Page.qml:40-52`), with integer comparison in `src/data.rs:238-274` and `browser1sortproxymodel.cpp:11-56`. The executable parent generator's raw-value oracle expects ascending `CMXC 12007`, `XU 118794`, `FZ 126771`, `TTF 173752`, `FQ 174734` and descending `UZTJ 49976165`, `LQM 49962066`, `FA 49905359`, `SI 49900780`, `HIK 49898942`. No tie occurs among those leaders, so this run does not claim tie-oracle coverage. Bevy + egui remained excluded because its first Volume activation is unverified.

The development-only `/tmp/run_browser1_volume_toggle_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_volume_toggle_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-volume-toggle-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-volume-toggle-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

Volume targets exactly reused the preceding fresh-state run: Slint review/logical `(710,243)` / `(1515,493.2)` and QML `(710,271)` / `(1515,510)`. Browser-primary focus targets were unchanged. Each process attempted one focus click and two Volume-header clicks, parked at logical `(100,100)` before every capture, passed seven Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

Procedural `status=passed` means only that all three clicks were attempted, the route remained unchanged, all three review-capture pairs were distinct, and clean exit completed. Both JSONL records retain `ascending_volume_sort_visually_verified=false`, `descending_volume_sort_visually_verified=false`, `capture_pixel_content_reviewed=false`, `rendered_frame_verified=false`, and `equivalence_established=false`; subsequent assistant inspection of labeled detail sheets is the page-content oracle.

| Capture | Slint visual review | QML visual review |
|---|---|---|
| Before | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Canonical source leaders `IM`, `BEDD`, `AZFF`, `MTM`, `UI` |
| After first Volume click | Ascending marker/status and integer leaders `CMXC 12,007`, `XU 118,794`, `FZ 126,771`, `TTF 173,752`, `FQ 174,734` | Ascending marker and the same integer leaders and values |
| After second Volume click | Descending marker/status and integer leaders `UZTJ 49,976,165`, `LQM 49,962,066`, `FA 49,905,359`, `SI 49,900,780`, `HIK 49,898,942` | Descending marker and the same integer leaders and values |

Independent RGB comparison measured Slint difference bounds `(6,202,1425,1057)` for all three capture pairs. QML bounds were `(8,257,1447,1060)` for before/after-first and before/after-second, and `(8,267,1447,1060)` for after-first/after-second. Capture inequality alone was not treated as sorting evidence.

Independent validation checked both records' exact three-click/seven-route sequences, target x-coordinates, executable hashes, expected leaders and values, visual-review flags, clean exits, capture modes/dimensions/byte counts, pairwise-distinctness fields, and SHA-256 values: 6 clicks, 14 Browser 1 readbacks, and 12 recorded PNGs. Before/after-first/after-second review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`, `0bd4c4e4a8e6fcb76914b07cf5039b0ba1c5ee1b910494596eb4be5c6d7cb827`, and `609d1b683ad3f0a4852cec3c86b2986327a0bfe82b01473f02f38ff01e8d615a`; QML `32f37bc343f7ff2aa8013a39d7cc1cd588782335438556264793eef32c8f7813`, `1888a0ebefbe009ce69a78621e4f0a9909cd59599ed1f347f72f79e13042692e`, and `a09913f6c68b6d959d49d8e6df68966c61881ff5bd2d188f0b2eeac604d75ab4`. JSONL SHA-256 values were Slint `c296dddf0b9136e3c9cd1c7c61e6863f9ca3c28e5cc5aa919b9afa975991e429` and QML `7832bfeedddc6741a4604bf5b652fd79e60a000691c1606b74c97829ef7b3a55`.

This establishes one real ascending-then-descending integer Volume-sort sequence for each of Slint and QML. It does not establish Bevy + egui Volume sorting, sort ties, other headers/directions, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, or scenario acceptance. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Browser 1 Market Cap-header page-content pointer captures (2026-11-22)

A new-target Browser 1 run tested one fresh-state Market Cap header click in each implementation. Market Cap is a non-null numeric column with typed comparison (`src/data.rs:238-274`, `Browser1Page.qml:40-52`, `browser1sortproxymodel.cpp:11-56`, and Bevy + egui `src/ui/tabs/browser/browser_1_model.rs:5-24`). First activation requests ascending order. Sorting the executable parent generator's `browser1_rows()` by raw `market_cap` gives expected leaders `FLVP 679777313.4407552`, `AN 711349241.0462298`, `ITH 921043887.6278162`, `EI 968828828.4036916`, and `XLC 1052061392.8930393`. No tie occurs among those leaders, so this run does not claim tie-oracle coverage. This was a new target, not a retry of earlier unsuccessful headers.

The development-only `/tmp/run_browser1_market_cap_pointer.py` driver used one fresh native light/100% process per implementation. Its accepted invocation used the driver's 60-second default timeout:

```bash
python3 /tmp/run_browser1_market_cap_pointer.py \
  --implementation "$IMPLEMENTATION" \
  --work-root "/tmp/ui-framework-browser1-market-cap-pointer-2026-11-22-01/$IMPLEMENTATION" \
  --jsonl "/tmp/ui-framework-browser1-market-cap-pointer-2026-11-22-01/$IMPLEMENTATION.jsonl" \
  --settle 2
```

The shared widths before Market Cap are 90+220+140+100+100+120 px and its own width is 130 px, placing its center at review x=835 (`src/data.rs:42-54`, `Browser1Page.qml:24-25`, and `fixtures/manifests/browser1.json:49-53`). Market Cap targets were therefore Slint review/logical `(835,243)` / `(1590,493.2)`, QML `(835,271)` / `(1590,510)`, and Bevy + egui `(835,263)` / `(1590,505.2)`. Browser-primary focus targets were unchanged. Every process attempted one focus click and one Market Cap-header click, parked at logical `(100,100)` before each capture, passed five Browser 1 readbacks, acknowledged `quit`, and exited with status 0 without keyboard input or programmatic route selection. Desktop PNGs are 5120×2160 and review PNGs are 1600×1060 from `(1815,579,3415,1639)`.

QML and Bevy + egui procedural `status=passed` means only that both clicks were attempted, the route remained unchanged, distinct decodable before/after review captures were produced, and clean exit completed. Slint's `status=failed` records only its byte-identical before/after review captures; its clicks, route checks, and clean exit also completed. Every JSONL retains `market_cap_sort_visually_verified=false` and `capture_pixel_content_reviewed=false`; subsequent assistant inspection of labeled detail sheets is the sorting oracle.

| Implementation | Before | After Market Cap click | Clean exit |
|---|---|---|---|
| Slint | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Original order retained with no ascending marker; before/after review PNGs byte-identical | Acknowledged quit, status 0 |
| QML | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Ascending marker and numeric leaders `FLVP 679,777,313`, `AN 711,349,241`, `ITH 921,043,888`, `EI 968,828,828`, `XLC 1,052,061,393` | Acknowledged quit, status 0 |
| Bevy + egui | Canonical source order beginning `IM`, `BEDD`, `AZFF`, `MTM`, `UI` | Original order retained; no ascending marker or sorted rows observed | Acknowledged quit, status 0 |

Independent RGB comparison measured null Slint difference bounds because its review images were identical. QML bounds were `(8,257,1447,1060)`, including its header and row changes. Bevy + egui's differences were confined to `(13,64,956,276)`, above the data rows, despite its procedural distinct-capture pass. These unsuccessful new-target interactions do not distinguish input delivery, hit targeting, focus, and application causes and do not establish defects. No attempt was retried.

Independent validation checked all three records' exact two-click/five-route sequences, target x-coordinates, executable hashes, expected leaders and values, visual-review flags, clean exits, capture modes/dimensions/byte counts, distinctness fields, and SHA-256 values, including Slint's expected failed status: 6 clicks, 15 Browser 1 readbacks, and 12 recorded PNGs. Before/after review SHA-256 values were Slint `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd` and `4c5bad6dd14baf6fc675aba7a9dac8504ee692455d335337fddee864c988e0fd`; QML `4c96966e42f8a52739ce35e3c647cd874fd356fb4c2aeb5f66f7d2bf7f563296` and `d38e952876225bdf66c420ebb2a0d843001a51892ce23d2cb177884b7cffc829`; and Bevy + egui `11abc028e348cd1fa043c3fa622a916f97017296d85f6b7d66ab1cdd50a28dc3` and `4e2f56904523ea87304170d0cffa2c099c7e26c0498ac84d97833d18e22404ea`. JSONL SHA-256 values were Slint `a3ba490e220ce428a8b241b2618b75bc73dc03368b757726328a4bfd6564a434`, QML `c7ae8d2f3615a58a73be3ae3893bead699a271f6aaabb981170942381bf2e1b0`, and Bevy + egui `aef1c7c7531ef06311c46e2112190dea5015a133c0fc00eb83453c946bce8d9f`.

This establishes one real ascending numeric Market Cap-sort interaction for QML. Slint and Bevy + egui Market Cap sorting remain unverified after one preserved unsuccessful new-target attempt each. Other headers and directions, sort ties, repeated-run reliability, editing, scrolling, drag, touch, rendered-frame timing, human-reviewed equivalence, durable artifact attachment, controlled results, and scenario acceptance remain unestablished. All 82 parent discovery tests, repository validation, and `git diff --check` passed after documentation. No application source, scenario, controlled result, fixture, or large/on-demand variant changed or was constructed.

### Bevy + egui Export View pointer and application capture (2026-11-22)

A development-only `/tmp/run_bevy_export_view_pointer.py` driver launched the unchanged Bevy + egui Release executable at native light/100% with a fresh `/tmp` working directory. It used the existing stable-ID adapter only for initial/final route readback and acknowledged quit, never route selection. Two same-route Browser-primary clicks established focus, followed by one real Export View toolbar click. The accepted invocation was:

```bash
python3 /tmp/run_bevy_export_view_pointer.py \
  --work-root /tmp/ui-framework-bevy-export-view-2026-11-22-01 \
  --jsonl /tmp/ui-framework-bevy-export-view-2026-11-22-01.jsonl \
  --settle 2
```

The compositor-logical Browser-primary focus target was `(1161,396.6)` and the Export View target was `(1242,418.8)`. The latter is the native review-crop toolbar center `(255,119)`, converted with the same `(1815,579)` raw crop origin and `1.6666666269302368` host scale as the preceding native tab run. These coordinates remain specific to the audited desktop and window placement.

Every focus/export state check retained `browser.browser1`; no programmatic route selection or keyboard input occurred. Export View produced `/tmp/ui-framework-bevy-export-view-2026-11-22-01/captures/browser-browser1-1795382821961-1.png`. The file decoded as a 1600×1000 RGB PNG, was 430,837 bytes, and had SHA-256 `3dd62de6324b9a9d5bddde054325d41107662875cea7e9e441f76705e0a3c21e`. Bevy then acknowledged `quit` and exited with status 0. The executable SHA-256 remained `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`.

Subsequent assistant inspection of that exact PNG found the Bevy shell, toolbar, Browser tabs, and populated Browser 1 table rather than a blank image or stale route; the application-owned capture excludes native window decorations. The JSONL retains `capture_pixel_content_reviewed=false` because that review occurred after the driver completed. The accepted development record is `/tmp/ui-framework-bevy-export-view-2026-11-22-01.jsonl`.

The same temporary driver then gained an optional `--route quant.vol-surface` while preserving the Browser 1 default. A second fresh native light/100% process used two real same-route Browser-primary focus clicks, one real Quantitative-primary click at `(1428,396.6)` that selected retained Volatility Surface, and one real Export View click at `(1242,418.8)`. Semantic readback produced `browser.browser1 → quant.vol-surface`; Export View preserved that route. No programmatic route selection or keyboard input occurred. The accepted native-scene invocation was:

```bash
python3 /tmp/run_bevy_export_view_pointer.py \
  --route quant.vol-surface \
  --work-root /tmp/ui-framework-bevy-export-view-native-scene-2026-11-22-01 \
  --jsonl /tmp/ui-framework-bevy-export-view-native-scene-2026-11-22-01.jsonl \
  --settle 2
```

That run produced `/tmp/ui-framework-bevy-export-view-native-scene-2026-11-22-01/captures/quant-vol-surface-1795383095238-1.png`, a 269,635-byte 1600×1000 RGB PNG with SHA-256 `9e5785f7b97c6724a34467189aec681fe92105887ed610a438d4a25109b50453`. Bevy acknowledged `quit` and exited with status 0; its executable hash was unchanged. Subsequent assistant inspection found the Quantitative shell and controls together with the populated composited 3D volatility surface, without native window decorations. The accepted development record is `/tmp/ui-framework-bevy-export-view-native-scene-2026-11-22-01.jsonl`; its `capture_pixel_content_reviewed=false` again predates the external assistant review.

These runs close the earlier Bevy Export View toolbar-click/output gap for one native Browser 1 run and one native Volatility Surface run, including one demonstrated native-scene composition. They do not establish repeated-run reliability, Export View on other routes, page-content interaction, human-reviewed visual equivalence, durable artifact attachment, presented-frame timing, controlled results, or scenario acceptance. No application source, parent test code, fixture, scenario, or large/on-demand variant changed or was constructed.

No scenario activation or implementation hash attestation is part of this parent-only BP-01 fixture deliverable.
