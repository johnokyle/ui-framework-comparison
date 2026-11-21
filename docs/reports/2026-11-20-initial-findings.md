# Initial UI Framework Comparison Findings and Implementation Plan

**Report date:** 2026-11-20
**Status:** Initial static audit and repository plan
**Implementations:** Rust/Slint, C++/Qt QML, and Rust/Bevy + egui

## Evidence statement

This report is based on source inspection and existing project records. No files were modified in the implementation projects during the audit, and no applications, builds, tests, or benchmarks were run. Historical measurements were not independently reproduced.

“Source-observed” therefore means that code or project records describe a capability. It does not mean that the capability passed an automated or manual runtime acceptance test.

## Executive summary

Create a **parent comparison repository** accompanied by a **GitHub Projects board**, with the three implementations maintained as separate repositories and included through pinned Git submodules.

This arrangement preserves each project's native build system and history while providing one location for:

- A common capability matrix.
- Shared test scenarios and deterministic fixtures.
- Reproducible benchmarks.
- Screenshots and interaction evidence.
- Versioned comparison reports.
- CI automation and public documentation.

The implementations should not initially be merged into one Cargo/CMake workspace. Their toolchains, rendering architectures, and current feature coverage differ too much for a unified build to improve the comparison.

The central finding is that this should be **a versioned comparison of implementations and engineering trade-offs**, not simply a claim about which framework is fastest. The projects contain rich comparison material, but licensing, source baselines, workload normalization, and measurement discipline must come first.

---

## 1. Current findings

### 1.1 High-level comparison

| Area | Rust / Slint | C++ / Qt QML | Rust / Bevy + egui |
|---|---|---|---|
| Functional coverage | 17 secondary views: 3 Browser, 3 Charting, 11 Quant | 19 declared tabs; 17 functional, 2 placeholders; 11 Quant | 16 leaf pages: 2 Browser, 3 Charting, 11 Quant |
| UI architecture | Declarative Slint shell with Rust controllers | QML interface backed by C++ models | Immediate-mode egui hosted in Bevy ECS |
| Rendering | Extensive custom software raster and software 3-D | Qt Quick, Qt Graphs, custom QML Canvas and C++ rendering | Bevy GPU 3-D, custom WGSL, `egui_plot`, and `egui::Painter` |
| Data | Deterministic local synthetic data | Local synthetic data | Deterministic local synthetic data |
| Automated tests | None found | None found | 315 statically discovered `#[test]` attributes; not executed |
| Existing benchmarks | Startup, memory, LOC, and build timings | Startup, memory, LOC, and build timings | Diagnostics, but no saved comparable benchmark results |
| License | None found | None found | None found |
| Publication state | Git repository, no observed remote | No Git metadata found | Most substantive implementation is uncommitted/untracked |

### 1.2 Workload compatibility

Slint and QML are close functional twins. Bevy + egui is a related quantitative-visualization application, but not a literal implementation of the same Browser and Charting workload.

Examples:

- Slint has three browser implementations, including a correlation heat map.
- QML has the corresponding three functional browsers plus a placeholder fourth browser.
- Bevy + egui has two browsers and uses Line, Scatter, and Histogram charting pages instead of the Slint/QML analytical, financial, and pivot-chart set.

The comparison therefore needs **shared core scenarios plus framework-specific scenarios**. Page existence alone must not be treated as equivalent coverage.

The Slint specification provides a useful metric and feature-classification foundation at `docs/UI_Framework_Comparison_Test_App_Specification.md:2665-2709`.

### 1.3 Audited framework versions

| Implementation | Version evidence |
|---|---|
| Slint | Rust edition 2024; locked Slint and slint-build 1.17.1; arboard 3.6.1 |
| QML | CMake 3.16+ and Qt 6.10+ declared; audited cache used Qt 6.11.1, GCC/G++ 15.2.0, CMake 4.4.2, and Ninja |
| Bevy + egui | Rust edition 2024; Bevy 0.19.1; bevy_egui 0.42.0; egui_plot 0.37.0; egui_extras/egui 0.36.2 |

The observed Rust compiler was 1.98.1 for the Rust projects, but neither Rust project had a pinned `rust-toolchain` file during the audit.

---

## 2. Implementation findings

### 2.1 Rust / Slint

#### Architecture and capabilities

The application has three primary areas and 17 secondary views. Its architecture separates deterministic data/model modules, effectful view controllers, declarative Slint UI, and application-owned raster/3-D rendering.

Key capabilities include:

- A reusable two-level tab bar with keyboard behavior and stable page IDs.
- A 2,000-row financial grid.
- A 1,000/100,000-row editable virtualized grid with 19 columns, filtering, sorting, selection, validation, clipboard, and undo/redo.
- An 8×8 correlation heat map.
- Three extensive chart implementations with LOD, pan/zoom, crosshairs, annotations, indicators, and navigators.
- Eleven quantitative-visualization pages, including software 3-D, graphs, projections, Monte Carlo, and order-book heat maps.
- Light, Dark, and System theme controls and application diagnostics.

Stable IDs are listed in `src/nav.rs:12-30`. The shared grid is implemented in `ui/grid.slint`; software rendering is supported by `src/raster.rs` and `src/render3d.rs`.

The advanced grid, charts, reusable tabs, heat map, and 3-D renderer are application-owned components. They must not be attributed to Slint as stock widgets.

#### Historical metrics

Recorded on 2026-08-25:

| Metric | Recorded value |
|---|---:|
| Slint markup | 3,868 lines |
| Rust backend | 10,906 lines |
| Total application code | 14,774 lines |
| Custom framework code | 1,835 lines |
| Direct dependencies | 2 |
| Dependency tree | 398 unique package names |
| Debug build, application crate only | 23.7 s |
| Incremental debug build | 4.5 s |
| Clean Release build | Not collected |
| Release startup, best of three | 305 ms |
| Idle RSS | 149.3 MB |

Sources: `results/metrics-auto.md:7-17` and `results/final-report.md:15-18`.

Qualifications:

- Startup is the minimum of three runs, not a distribution.
- The debug build figure has dependencies cached; it is not a full clean dependency build.
- Browser memory under the 100,000-row workload was not automatically collected.
- Markup LOC alone understates effort because substantial rendering and controller code is in Rust.

#### Limitations and deviations

- No automated tests were found.
- Export View is a logging stub; reset commands have limited scope.
- Fixed-resolution raster canvases stretch under high DPI, while vector overlays remain sharp: `results/deviations.md:16`.
- Custom System-theme rendering does not fully follow actual system lightness.
- Browser 2 has 19 columns rather than the older performance specification's 25-column wording.
- Global live updates use a fixed 500 ms cadence rather than a general 1/10/30 Hz selector.
- Efficient-frontier and projection/PCA-related views use documented synthetic or sampled approximations.
- Raw performance distributions and a clean Release build time are absent.
- Screenshot and recording evidence remains incomplete: `results/deviations.md:35-38`.

### 2.2 C++ / Qt QML

#### Architecture and capabilities

The application declares 19 secondary tabs, of which 17 are functional. It combines native Qt Quick controls, Qt Graphs, custom QML Canvas, and backend-assisted custom C++ models and rendering.

Key capabilities include:

- Light/dark/system themes, navigation, diagnostics, and PNG export.
- A 2,000-row, 12-column financial table.
- A 100,000-row, 19-column editable grid with filtering, selection, validation, clipboard, undo/redo, and live updates.
- An 8×8 correlation browser.
- Nine analytical chart frames with source sizes up to one million points.
- Professional financial and pivot charts.
- Eleven quantitative-visualization pages.

Relevant references include `Main.qml:45-101`, `Browser2Page.qml:21-332`, `ChartViewport.qml:418-677`, and `CMakeLists.txt:20-95`.

Qt Graphs must not receive credit for charts actually rendered by application Canvas code. QML and C++ totals must be considered together when evaluating implementation effort.

#### Historical metrics

Recorded on 2026-08-25:

| Metric | Recorded value |
|---|---:|
| QML markup | 9,485 lines |
| C++ backend | 5,989 lines |
| Selected custom framework code | 2,735 lines |
| Dependencies beyond Qt 6 | 0; Quick and Graphs |
| Full Debug rebuild | 8.0 s |
| Incremental Debug build | 2.4 s |
| Clean Release build | Not collected |
| Release startup, best of three | 687 ms |
| Idle RSS | 394.4 MB |

Source: QML `results/metrics-auto.md:1-15`.

Qualifications:

- The custom-code total covers a selected subset and is not directly comparable with Slint's custom-code total.
- Startup is best of three; RSS is the last valid sample.
- The measurements were not independently reproduced by this audit.
- Existing metric collection has side effects and does not constitute a durable benchmark harness.

#### Limitations and deviations

- No automated tests, CTest registrations, or Qt Test targets were found.
- Browser #4 and Chart Layout are placeholders; Reset Demo Data is a logging stub.
- Browser 2 lacks frozen columns and has 19 rather than 25 columns.
- Some filter visuals, disjoint-selection copying, live behavior, and status labels require correction or disclosure.
- Weekly/monthly pivot aggregation uses fixed 5-/21-bar windows; pattern regions are fixed labels.
- PCA and projection views use generated fixtures rather than full numerical algorithms.
- Network layout performs all-pairs O(N²) work at its configured cadence.
- Theme, narrow-window, DPI, and accessibility behavior need runtime verification.
- Internal diagnostics are not full CPU/GPU or input-to-photon measurements.

### 2.3 Rust / Bevy + egui

#### Architecture and capabilities

The application has 16 leaf pages and combines four rendering approaches:

1. Native Bevy 3-D scenes embedded into egui through offscreen textures.
2. Custom GPU point-cloud rendering with WGSL.
3. External plotting with `egui_plot`.
4. Custom immediate-mode rendering with `egui::Painter` and retained raster textures.

Key references include:

- `src/app/application.rs:10-24`
- `src/renderer/plugin.rs:28-72`
- `src/ui/state/ui_state.rs:17-58`
- `assets/shaders/factor_point_cloud.wgsl:27-57`

The application contains:

- Two data browsers with sorting, resizing, selection, editing, validation, and keyboard behavior.
- Line, Scatter, and Histogram analytical pages with substantial statistics and LOD.
- Eleven quantitative-visualization pages.
- Stable data identifiers and explicit source/eligible/visible/rendered accounting.
- More advanced numerical implementations in selected areas, including genuine PCA and an exact long-only frontier calculation.
- A substantial model/state unit-test inventory.

#### Metrics and tests

No saved cross-framework benchmark-results document or standalone controlled benchmark runner was found. Diagnostics expose CPU-stage timings, cache/LOD counts, approximate payload sizes, and related state, but these are not equivalent to frame presentation time, GPU time, RSS, VRAM, or input-to-photon latency.

Static discovery found 315 `#[test]` attributes across 52 Rust files, with no ignored tests found. The audit did not execute them, so this is an inventory rather than a passing result.

#### Limitations and deviations

- Browser and Charting coverage does not literally match Slint/QML.
- There is no application theme selector.
- Ingestion, provider, realtime, and storage modules are empty or unrelated to the implemented local-data workload.
- High-Dimensional Projection uses fixed synthetic layouts; lasso selection is not implemented.
- Browser 1 contains a temporary hard-coded row; save-baseline behavior is in memory only.
- Live modes are local simulations; target update frequency is not measured frame rate.
- Four 3-D scenes initialize globally, affecting startup and idle-cost comparisons.
- Fixed 1024×640 3-D targets and desktop-oriented controls limit responsive/high-DPI claims.
- Most importantly, the current Git HEAD does not contain the complete audited application.

---

## 3. Why the historical numbers are not a ranking

The Slint and QML measurements are useful historical observations, but not controlled head-to-head results:

- Build timings measure different cache scopes.
- Both startup values use best-of-three sampling.
- Page initialization is largely eager, but the workloads differ.
- Rendering backends and custom rendering work differ.
- Bevy + egui has no corresponding saved measurements.
- Existing collectors can clean build directories, touch source files, and overwrite result documents.

These values must be labeled **historical, not directly comparable**. A new controlled baseline is required before making performance claims.

---

## 4. Proposed GitHub project architecture

Use four repositories:

1. `slint-ui-comparison`
2. `qml-ui-comparison`
3. `bevy-egui-ui-comparison`
4. `ui-framework-comparison` — parent repository

Recommended parent layout:

```text
ui-framework-comparison/
├── README.md
├── CONTRIBUTING.md
├── implementations/
│   ├── slint/                 # submodule, pinned commit
│   ├── qml/                   # submodule, pinned commit
│   └── bevy-egui/             # submodule, pinned commit
├── docs/
│   ├── methodology.md
│   ├── capability-matrix.md
│   ├── scenario-catalog.md
│   ├── limitations.md
│   └── reports/
├── specifications/
│   └── comparison-contract.md
├── scenarios/
│   ├── core/
│   ├── slint-qml/
│   └── framework-specific/
├── schemas/
│   ├── scenario.schema.json
│   └── benchmark-result.schema.json
├── fixtures/
│   └── manifests/
├── tools/
├── results/
│   ├── raw/
│   └── summaries/
└── .github/
    ├── workflows/
    └── ISSUE_TEMPLATE/
```

Small JSON/CSV summaries can be tracked in Git. Large screenshots, traces, and videos should be stored as Actions artifacts or Release assets rather than bloating the repository.

Every result must identify the exact submodule commit, not merely a branch name.

---

## 5. Implementation plan

### Phase 0 — Licensing and publication readiness

Before making code public:

1. Choose explicit licenses for all four repositories.
2. Add third-party notices where necessary and review Qt distribution/licensing obligations separately from the application's own license.
3. Audit Git history and untracked files for credentials, `.env` files, local paths, editor settings, unrelated scripts, and generated builds.
4. Establish appropriate `.gitignore` rules.
5. Add implementation READMEs with purpose, prerequisites, exact commands, dependency versions, known deviations, and parent-project links.

**Exit condition:** every implementation has an authorized license, a clean source inventory, and no known secrets or generated artifacts queued for publication.

### Phase 1 — Create reproducible source baselines

For each implementation:

1. Commit the complete intended source.
   - Initialize Git for QML.
   - Capture the currently untracked Bevy + egui implementation.
   - Review Slint's unrelated untracked files rather than adding them automatically.
2. Build and run available tests.
3. Record compiler, framework, OS, graphics backend, and lockfile state.
4. Create an immutable tag such as `comparison-baseline-v1`.
5. Add the repository to the parent as a submodule at that tag.

Update submodule pointers through explicit parent pull requests so historical reports remain reproducible.

**Exit condition:** a fresh recursive clone can build each implementation from its recorded commit.

### Phase 2 — Define the comparison contract

Create stable capability IDs, scenario IDs, and page-ID mappings.

Use three tiers:

#### Tier A — core three-framework scenarios

Candidates include startup/idle, navigation, large-table interaction, basic chart interaction, volatility surface, factor cloud, correlation surface, efficient frontier, PCA manifold, regime map, projection, network graph, knowledge graph, Monte Carlo, and order book.

#### Tier B — Slint/QML parity scenarios

Include the closer shared Browser 1/2/3, analytical chart, professional financial chart, pivot chart, and detailed keyboard/clipboard/editing/annotation/navigator behavior.

#### Tier C — framework-specific demonstrations

Examples include Bevy GPU 3-D and numerical-analysis behavior, QML Qt Graphs integration, and Slint software raster/vector composition. These demonstrate strengths without counting them as failures in unrelated architectures.

Each scenario must specify its ID/revision, page mappings, fixture hash, workload dimensions, viewport/DPI, theme, build profile, warm-up, actions, update rate, duration, and success criteria.

Unsupported scenarios must be marked `not-implemented`, `not-applicable`, or `not-comparable`; no silent workload substitutions.

### Phase 3 — Normalize fixtures and capability accounting

The implementations currently generate their own synthetic data. Equivalent seeds alone do not establish equivalent input data.

Recommended approach:

- Store small canonical fixtures directly.
- Generate large fixtures from a versioned common generator.
- Verify generated data with SHA-256 hashes.
- Separate computational results from rendering results.

Exact PCA/QP and synthetic visualization fixtures must not be presented as equivalent computational work.

Use two independent capability axes:

1. **Completion:** verified, partial, missing, not applicable, or unverified.
2. **Provision:** NATIVE, COMPOSED, CUSTOM, EXTERNAL, or EXPERIMENTAL.

This prevents application-authored components from being credited as built-in framework features.

### Phase 4 — Add functional evidence

Implement a common smoke-test layer for launch/exit, stable-ID navigation, representative workloads, basic input, state verification, and screenshots.

Also cover:

- Light/dark and system-theme behavior where supported.
- Minimum/narrow window sizes.
- 100% and 200% scaling.
- Keyboard-only navigation and focus traversal.
- Accessibility-tree exposure where available.
- Long-running live-update stability.

Functional CI can use virtual displays where appropriate. Performance from software-rendered or offscreen CI must remain separate from physical-GPU desktop results.

### Phase 5 — Build the benchmark harness

Use implementation-specific adapters with one shared result schema.

#### Static metrics

Measure physical/logical LOC, markup/backend code, test code, application-owned infrastructure, direct/transitive dependencies, and files/lines changed for standardized extension tasks.

#### Build metrics

Report completely clean, application-only cached, incremental, and Release builds separately.

#### Runtime metrics

Control and record hardware, OS, compositor, GPU/driver, backend, window size, scale factor, initial page, dataset, theme, live state, and cache state.

Measure:

- First rendered frame and first interactive state.
- Idle, steady-state, and peak memory.
- CPU utilization.
- Frame-time median, p95, and p99.
- Dropped frames.
- Achieved live-update frequency.
- Input-to-next-present latency where instrumentation permits.

Use repeated runs and retain raw samples. Framework diagnostics remain supplementary; they are not automatically compositor or input-to-photon measurements.

### Phase 6 — Publish the comparison

The first public report should contain:

1. Scope and tested versions.
2. Side-by-side screenshots.
3. Capability matrix.
4. Architecture comparison.
5. Implementation-effort analysis.
6. Benchmark environment and methodology.
7. Results with raw-data links.
8. Deviations and unsupported scenarios.
9. Use-case-oriented conclusions.

Avoid a single aggregate winner. Prefer conclusions about conventional desktop controls, GPU/3-D visualization, custom infrastructure required, runtime cost for a specific workload, and maintainability observations from repeatable tasks.

---

## 6. GitHub configuration

### Projects board

Create one parent Projects board with fields such as Status, Framework, Workstream, Scenario, Priority, Milestone, and Evidence Required.

Useful views:

- Publication blockers.
- Capability parity.
- Benchmark readiness.
- Current milestone.
- Framework-specific work.

Keep implementation defects in child repositories and cross-framework methodology/reporting issues in the parent. Link both through the board.

### GitHub Actions

Recommended workflows:

#### Pull-request validation

- Validate submodule revisions.
- Validate scenario and result schemas.
- Verify fixture hashes.
- Build implementations once attached.
- Run available unit tests and functional smoke tests.
- Check generated reports and documentation links.

#### Benchmark workflow

- Trigger manually or on a controlled self-hosted runner.
- Record the machine manifest.
- Execute approved scenario sets.
- Upload raw results, screenshots, and traces.
- Generate summaries without overwriting historical runs.

Shared GitHub-hosted runners are suitable for correctness checks but should not be the authoritative source of graphics performance numbers.

### Documentation site

After the first validated baseline, publish Markdown reports through GitHub Pages. Organize the site around the capability matrix, scenario definitions, architecture notes, implementation revisions, and hardware-specific results.

---

## 7. Milestones and definition of done

| Milestone | Required outcome |
|---|---|
| M0: Publication-ready sources | Licenses, clean histories, READMEs, complete committed implementations |
| M1: Reproducible parent baseline | Three pinned submodules, fresh-clone build instructions, initial CI |
| M2: Capability baseline | Scenario catalog, capability matrix, explicit deviations, screenshots |
| M3: Functional baseline | Smoke tests, fixture verification, keyboard/theme/resize evidence |
| M4: Performance baseline | Controlled environment, raw samples, statistical summaries |
| M5: Public report v1 | Versioned report, documentation site, limitations, reproduction instructions |

An initial public version may contain `unverified` or `not measured` entries. It should not wait for artificial feature parity, but it must not hide gaps.

---

## 8. Initial scaffold delivered with this report

The local parent repository now contains:

- Root orientation and contribution guidance.
- This versioned findings report.
- Draft capability matrix, methodology, scenario catalog, and limitations register.
- A formal comparison contract.
- Scenario and benchmark-result JSON Schemas.
- Four draft scenario documents covering startup, volatility stress, Browser 2, and a Bevy-specific GPU workload.
- A Python repository validator and an initial GitHub Actions metadata-validation workflow.
- GitHub issue and pull-request templates.
- Fixture, implementation, and result storage policies.

The implementation directories remain unattached by design. Licensing, source baselines, and submodule attachment are the next gated actions.

## Immediate next steps

1. Select licenses and repository visibility.
2. Establish complete clean Git baselines, especially for QML and Bevy + egui.
3. Attach three tagged implementation repositories as pinned submodules.
4. Replace draft scenario inputs with verified shared fixtures and executable actions.
5. Add functional smoke tests and equivalent screenshots.
6. Collect the first controlled performance baseline.
