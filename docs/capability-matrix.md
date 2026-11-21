# Draft capability matrix

## Evidence status

This is a **source-audited draft with Slint/QML fixture-normalization and Bevy BP-01–BP-09 implementation/headless-test evidence**, not a runtime acceptance matrix. “Present” means the capability was found in source; a test count applies only to the named implementation and test scope. “Different” means the implementation has a related but non-equivalent workload. All three implementations now have headless/model evidence for the same 73 canonical artifacts; this is not runtime, screenshot, accessibility, or performance acceptance.

Provision labels follow the comparison contract:

- **NATIVE:** directly provided by the framework or its standard modules.
- **COMPOSED:** assembled from ordinary framework controls.
- **CUSTOM:** substantial application-owned implementation.
- **EXTERNAL:** third-party library or renderer.
- **EXPERIMENTAL:** unstable or feature-gated integration.

## Feature coverage

| Capability | Slint | QML | Bevy + egui |
|---|---|---|---|
| Two-level desktop navigation | Present — CUSTOM/COMPOSED | Present — NATIVE/COMPOSED | Present — CUSTOM/COMPOSED |
| Light/dark theme | Present — COMPOSED | Present — NATIVE/COMPOSED | System/Light/Dark selector and theme-aware rendering; equivalent runtime screenshots pending — COMPOSED/CUSTOM |
| System theme | Present with custom-rendering caveat | Present; validation pending | System option exposed through egui; actual system resolution and screenshots pending — NATIVE/COMPOSED |
| Basic financial table | 2,000×12 — CUSTOM | 2,000×12 — COMPOSED/CUSTOM | Canonical 2,000×12 fixture, virtualization, typed sorting, stable WA identity, resize/reorder and focused keyboard navigation — EXTERNAL/CUSTOM |
| Advanced editable grid | 1K/100K×19 — CUSTOM | 1K/100K×19; no frozen columns — COMPOSED/CUSTOM | Canonical 1K/100K×19 fixture, stable source IDs, virtualization, sorting/filtering, four selection modes, validated editors, TSV, bounded undo/redo and deterministic live updates; runtime evidence pending — EXTERNAL/CUSTOM |
| Correlation browser | 8×8 — CUSTOM | 8×8 — CUSTOM | Canonical 8×8 matrix, clustering, pair statistics, hover/selection, precision controls and deterministic 500 ms updates with hidden-route clock rebasing; screenshots pending — CUSTOM |
| Nine-view analytical chart | Present — CUSTOM raster/vector | Present — CUSTOM Canvas/C++ | Nine canonical frames, 500-day default plus explicit 2,500/20,000/100,000/1,000,000 source sizes, raw-observation inspection, extrema-preserving LOD, annotations, deterministic live optimization and structured views; runtime/performance/screenshot evidence pending — EXTERNAL `egui_plot` plus CUSTOM |
| Professional financial chart | Present — CUSTOM | Present — CUSTOM | Canonical 1,260 daily/on-demand 20,000 intraday OHLCV, shared Price/Volume/Indicator viewport and crosshair, Candlestick/OHLC/Line, indicators/VWAP variants, inspectable fixed-demo markers/events, five annotation kinds, deterministic live updates and aggregation counters; runtime/performance/screenshot evidence pending — CUSTOM |
| Pivot chart | Present — CUSTOM | Present — CUSTOM | Canonical nine-symbol 1,500-day fixture, five-day Weekly/calendar Monthly OHLCV, strict pivots/buffers, zig-zag/steps, three price modes, six ranges, complete readouts, and a shared full-series navigator with five-bar minimum and 8 px edge targets; runtime evidence pending — CUSTOM |
| Line/scatter/histogram analysis | Related analytical views only | Related analytical views only | Present — EXTERNAL `egui_plot` plus CUSTOM |
| Volatility surface | Up to 500×500 — CUSTOM software 3-D | Present — Qt Graphs/CUSTOM | Explicit Common 100/250/500 fixture and Advanced modes; shared calm/stressed interpolation, nearest-sample selection and source-aware native rebuilds — COMPOSED Bevy 3-D/CUSTOM |
| Factor structure | Up to 100K points — CUSTOM | Present — Qt Graphs/CUSTOM | Explicit Common 240/1K/10K/100K fixture with stable IDs/canonical symbols and Advanced populations; source-aware WGSL billboard rendering — CUSTOM WGSL/Bevy |
| Correlation surface | 2-D/3-D — CUSTOM | 2-D/3-D — CUSTOM | Common mode synchronizes Browser 3’s current 8×8 matrix, clustering and pair selection in 2-D/3-D; larger Advanced matrices retained — COMPOSED/CUSTOM |
| Efficient frontier | Sampled envelope — CUSTOM | Present; algorithm limits recorded — CUSTOM | Common 12-asset/2,500-portfolio/40-bin sampled envelope at 2% risk-free rate; Advanced exact long-only QP/live/larger clouds remain separate — CUSTOM/EXTERNAL |
| PCA manifold | Synthetic PCA-like fixture — CUSTOM | Generated PCA-like fixture — CUSTOM | Common 500 fixed synthetic coordinates with stable selection and 2-D/3-D rendering; computed PCA, explained variance and trajectories are Advanced-only — CUSTOM/EXTERNAL |
| Regime map | Present — CUSTOM | Present — CUSTOM | Common 400-observation/five-regime fixture with stable IDs, history/filter/selection caches; larger Advanced populations retained — CUSTOM/EXTERNAL |
| High-dimensional projection | Fixed PCA/t-SNE/UMAP-like layouts — CUSTOM | Fixed projection layouts — CUSTOM | Common 5,000 points/five categories/three explicitly fixed synthetic “-like” layouts with rectangle/group selection; Advanced populations retained; lasso missing — CUSTOM |
| Network graph | Up to 1,000/5,000 — CUSTOM | Up to 1,000/5,000; fixed canonical layout — CUSTOM | Common 100/300 and 1,000/5,000 graphs with canonical fixed positions and 120/40 iteration provenance; drag/select/filter/label budgets retained — CUSTOM |
| Knowledge graph | Present — CUSTOM | Present — CUSTOM | Common 24-entity/22-relation fixture with stable IDs and authoritative parent-chain expansion; search/reveal/drag/selection and Advanced graph retained — CUSTOM |
| Monte Carlo | Paths, bands, histogram, optional 3-D — CUSTOM | Paths, bands, histogram — CUSTOM | Common 600×120 post-initial paths, zero-based IDs, nearest-rank 5/50/95 bands and 40-bin histogram with selection/LOD; Advanced GBM/type-7 statistics and benchmarks retained — CUSTOM/EXTERNAL |
| Order-book heat map | Up to 1,000×200 — CUSTOM | Up to 1,000×200 — CUSTOM C++/QML | Common 1,000×200 moving-price stream with 32 same-stream live events, stable historical selection and 50 ms source timestamps; 1/10/30 Hz retained-texture playback and Advanced fixed-price stream retained — CUSTOM raster/vector |
| Clipboard | External `arboard` plus CUSTOM integration | Qt/C++ integration | Contiguous cell/range and ordered row/column TSV copy; validated atomic rectangular paste; disjoint cell copy rejected — NATIVE egui events plus CUSTOM grid integration |
| Accessibility | Runtime verification pending | Runtime verification pending | AccessKit grid/cell roles and chart summaries verified in headless tree tests; Linux AT-SPI runtime unverified — NATIVE/EXTERNAL/CUSTOM |
| Diagnostics | Present; internal cadence/RSS | Present; internal cadence/Canvas/RSS | Frame/startup/backend/RSS, scoped CPU/LOD counters, and real PNG capture path; runtime panel/export activation unverified — COMPOSED/CUSTOM |
| Automated tests | 83 passed, 4 ignored in the locked ordinary suite; all 4 explicit large release tests passed; all 73 canonical artifacts covered | 12 ordinary and 7 explicit large CTest entries passed; 50 ordinary plus 23 large canonical artifact cases covered all 73 artifacts; production Qt Test run reported 18 passed | 563 passed, 1 ignored in the locked ordinary suite; explicit 100K/1M analytical hash test passed separately |
| Equivalent screenshots | Not collected | Not collected | Not collected; capture implementation tests are not equivalent screenshot evidence |

## Interpretation notes

### Slint

The grid, charts, reusable tabs, heat map, raster drawing, and 3-D rendering represent substantial application-owned infrastructure. Slint markup LOC alone therefore understates the implementation effort.

Key references: Slint `src/nav.rs:12-30`, `ui/grid.slint:1-867`, `src/raster.rs:21-267`, `src/render3d.rs:1-156`, and `results/metrics.md:55-92`.

### QML

Qt Quick supplies standard controls and table infrastructure, and Qt Graphs supplies 3-D building blocks. Many analytical and quantitative views still depend on custom Canvas and C++ code. QML and C++ totals must be considered together.

Key references: QML `CMakeLists.txt:20-95`, `Main.qml:45-101`, `Browser2Page.qml:21-332`, and `ChartViewport.qml:418-677`.

### Bevy + egui

Bevy + egui has the strongest distinction between native GPU 3-D, external plotting, and custom immediate-mode rendering. Browser 1, Browser 2, Browser 3, the nine-frame analytical chart, the professional stock chart, the pivot chart, and all eleven quantitative views now expose their canonical workloads with focused model/headless coverage. Quantitative Common modes are lazy and preserve Advanced computations as separately labeled extensions; shell reset scopes, Browser 3 correlation sharing and hidden-route clock rebasing, global live gating, and source/rendered diagnostics are headless-tested. Matching normalized outputs are now established in Slint, QML, and Bevy + egui at the headless/model level. Cross-framework comparison still requires runtime evidence; pointer/touch interaction, equivalent screenshots, synchronized native rendering, accessibility, and Q-P1–Q-P4 acceptance remain pending.

Key references: Bevy + egui `src/renderer/plugin.rs`, `assets/shaders/factor_point_cloud.wgsl`, `src/ui/tabs/browser/browser_1.rs:75-126`, `src/ui/tabs/browser/browser_2.rs:46-340`, `src/ui/state/browser_2_state.rs:244-1599`, `src/ui/tabs/browser/browser_3.rs:18-66`, `src/ui/state/browser_3_state.rs:31-236`, `src/data/models/analytical_fixture.rs`, `src/ui/state/charting_state.rs`, `src/plots/line/plot.rs`, `src/ui/tabs/charting/line.rs`, `src/data/models/stock_chart.rs`, `src/ui/state/stock_chart_state.rs`, `src/plots/financial/mod.rs`, `src/ui/tabs/charting/stock.rs`, `src/data/models/pivot_chart.rs`, `src/ui/state/pivot_chart_state.rs`, `src/ui/tabs/charting/pivot.rs`, `src/data/models/quantitative/common_fixtures.rs`, `src/ui/tabs/quantitative_visualization.rs`, `src/ui/main_window/diagnostics_panel.rs`, and `src/ui/input_tests.rs`.

## Next revision

Replace source-audited cells with evidence-linked statuses only after smoke tests and equivalent screenshots exist. Keep any provision classification visible even when a feature is missing or partial.
