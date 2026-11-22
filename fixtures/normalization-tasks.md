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

The default-disabled `quant.order-book` was deliberately excluded. This batch does not capture its disabled fallback as an Order Book result or change its existing capability status. Exact artifacts are under `/tmp/ui-framework-screenshots-2026-11-22-quant-<route>-01` for `vol-surface`, `factor-structure`, `correlation`, `frontier`, `pca`, `regime`, `projection`, `network`, `knowledge`, and `monte-carlo`.

The tested executable hashes remained Slint `49022ade231309e7f34e794832de390b4a2582cc4fbf9cb5d29fe9e946737557`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `7e2f2c281bfbd3b3cc9b975b98bee489bee3986002e45efa684105cd1cc81931`. Exact capture/review hashes, route metadata, crop boxes, clean exits, and assistant observations are in each directory's `manifest.jsonl` and `assistant-review.jsonl`. No source or test code changed. All 61 parent Python tests and repository validation passed. Raw desktop images are not publication artifacts; durable attachment, other variants, active accessibility, human equivalence acceptance, controlled results, and scenario activation remain unestablished.

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

Executable hashes were Slint `34fc038090dc7f14d5a08d9e529d347f18de20bb747c196f4e333e905776ce33`, QML `4b1bf027fb5587b580b227a64f15f60ae0f72b81c6d8cb121971131523fe759e`, and Bevy + egui `f60ebe4eb6f90e56529838ac7a1b5a104b06d7019a6e98743bf569ed3e345fa1`. Slint's locked suite passed 95 tests with four explicit large cases ignored, Bevy + egui's locked suite passed 571 tests with one ignored, and both locked Release builds passed. All 15 focused parent accessibility tests, all 67 parent discovery tests, and repository validation passed. Host AT-SPI remained disabled and the Slint/Bevy process-scoped gaps remained unchanged. Quantitative secondary keyboard behavior, pointer/touch and scrolling, active-screen-reader behavior, rendered-frame correctness, human equivalence, durable attachment, controlled results, and scenario acceptance remain unestablished.

No scenario activation or implementation hash attestation is part of this parent-only BP-01 fixture deliverable.
