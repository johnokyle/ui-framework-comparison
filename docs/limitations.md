# Known limitations and publication blockers

This register records limitations from the initial static audit, subsequent Bevy BP-01–BP-09 implementation checks, and Slint/QML canonical fixture normalization. Evidence limits are stated explicitly; implementation and headless tests do not imply cross-framework runtime acceptance.

## Repository and submodule state

- As of 2026-11-21, the [parent comparison repository](https://github.com/johnokyle/ui-framework-comparison) is public. The audited Slint, QML, and Bevy + egui source trees have clean committed baselines synchronized to private GitHub remotes.
- The parent repository attaches all three implementations as pinned submodules:
  - `implementations/slint` uses [Slint](https://github.com/johnokyle/slint-ui-test) at `d1fc847ac5956d501a8204b6cfc4206c0bd6464e`.
  - `implementations/qml` uses [QML](https://github.com/johnokyle/qml-ui-test) at `df0dd1baeaa263dea5523d6d7172ea47060b065c`.
  - `implementations/bevy-egui` uses [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) at `8eaf9ba44569c3f3c78a550516c4a1b841c63cf6`.
- Each implementation remote retains the annotated `comparison-baseline-2026-11-21` tag at its original licensed baseline. The current pins above include the subsequent README, third-party-notice, and publication-cleanup revisions; parent gitlinks remain authoritative even if implementation branches advance. Because the implementation repositories are private, public parent clones cannot initialize the submodules without the corresponding GitHub access.

## Licensing

- Original parent source code, JSON schemas, scenarios, and fixture manifests use Apache-2.0; original parent documentation, reports, and other Markdown prose use CC BY 4.0.
- Original Slint and Bevy + egui implementation code uses MIT OR Apache-2.0. Original QML implementation code uses GPL-3.0-or-later.
- These licenses cover only original repository content. Third-party dependencies, frameworks, fonts, icons, and other assets retain their respective licenses and notice requirements. The parent and each implementation now provide a `THIRD_PARTY.md` inventory; the parent inventory links to the implementation records.

## Cross-project publication blockers

- The 2026-11-21 reachable-history review examined 35 commits and 547 unique historical blobs across all local heads, remote-tracking refs, and tags. It found no confirmed committed credentials, private keys, tokens, credential-bearing URLs, compiled build output, caches, or large binaries. Pattern-based scanning cannot prove the absence of every secret; unreachable objects and non-Git GitHub content were not reviewed.
- Populated local credential files remain ignored and were not found in tracked history. Their values were not displayed or validated. Repository-local ignore rules now cover local environment variants and agent/editor settings, including QML's previously global-only `.claude/settings.local.json` rule.
- Current documentation replaces machine-specific checkout paths with variables, the QML metrics script no longer defaults to a user-specific Qt prefix, and irrelevant tracked Bevy clangd settings were removed. Existing commits and baseline tags still contain their original content; no history or tag rewrite was performed. No secret-driven history rewrite is presently indicated.
- Optional provider scripts are documented as development-agent helpers unrelated to application workloads. Bevy's project-relative agent configuration is retained and documented; its 204 newline-only Rust placeholder modules remain intentional-inclusion review items rather than confirmed generated artifacts.
- Source notices identify the modified Feather and Lucide icons in Slint and the source-versus-binary obligations for all implementations. The maintainer confirmed on 2026-11-21 that Claude Code created the other 15 Slint SVGs for the project; no third-party derivation was reported.
- Slint binary distribution requires an explicit Slint licensing-route and attribution decision. Bevy binaries require the embedded default-font notices, and QML binaries require an exact shipped-Qt-module inventory and licensing/source-compliance review. Linux x86-64 development inventories now record 484 Slint and 449 Bevy Cargo target-resolution packages plus the audited QML Qt linkage/SBOM inputs. These are not complete release notice bundles: 42 Slint and 25 Bevy packages lack package-root license/notice files in the local package copies, and actual shipped artifacts still require verification.
- No controlled three-framework benchmark or equivalent screenshot set exists.

## Slint

- Canonical fixture/model evidence now covers all 73 parent artifacts: 83 ordinary tests passed with four large cases isolated, and all four explicitly invoked large release tests passed. Default-construction tests cover Browser 2 1K, analytical 500 days, stock daily-only, pivot SPY-only, and quantitative Common defaults. These results do not establish runtime or scenario acceptance.
- Export View is a logging stub; reset commands have limited scope.
- Fixed-resolution raster canvases stretch under high DPI, while vector overlays remain sharp.
- Custom System-theme rendering does not fully follow actual system lightness.
- Browser 2 implements 19 columns rather than the specification's 25-column performance wording.
- Global live updates use a fixed 500 ms cadence rather than a general 1/10/30 Hz selector.
- Efficient-frontier and projection/PCA-related views use documented synthetic or sampled approximations.
- Existing startup is best of three; raw benchmark distributions and clean Release build timing are absent.
- Screenshot capture remains incomplete because of the audited Wayland tooling limitation.

Primary records: Slint `results/deviations.md`, `results/metrics.md`, and `results/metrics-auto.md`.

## QML

- Canonical fixture/model evidence now covers all 73 parent artifacts: all 12 ordinary CTest entries and all 7 explicit large entries passed. The 50 ordinary plus 23 large canonical cases verify exact parent hashes, golden rows, row counts, and columns; the complete production-model Qt Test invocation reported 18 passed, 0 failed. Default-construction tests cover Browser 2 1K, analytical 500 days, stock daily-only, pivot SPY-only, and quantitative Common defaults. These results do not establish runtime or scenario acceptance.
- Browser #4 and Chart Layout are placeholders; Reset Demo Data is a logging stub.
- Browser 2 lacks frozen columns and has 19 rather than 25 columns.
- Some filter visuals, disjoint-selection copying, live behavior, and stale status labels require correction or disclosure.
- Pivot Weekly aggregation uses five source days and Monthly uses calendar months; pattern regions remain fixed labels.
- PCA and projection views use generated fixtures rather than full numerical algorithms.
- Network uses canonical fixed layouts; runtime drag, hover, and 1,000-node interaction remain unmeasured.
- Theme, narrow-window, DPI, and accessibility behavior need runtime verification.
- Existing startup is best of three; clean Release timing and raw distributions are absent.

Primary records: QML `CMakeLists.txt`, `fixtures/`, `tests/`, `Main.qml`, `Browser2Page.qml`, model sources, and `results/metrics-auto.md`.

## Bevy + egui

- Headless/model normalized fixture equality is now established for all 73 parent artifacts in Slint, QML, and Bevy + egui against the unchanged manifests. This does not establish equivalent runtime behavior, rendering, interaction, accessibility, or performance.
- All eleven Bevy quantitative views now expose lazy Common/Advanced source modes with canonical model or focused state/headless tests, stable selection/reset coverage, and source/rendered diagnostics. These tests do not establish real pointer/touch interaction, native GPU output, equivalent screenshots, theme/DPI behavior, or Q-P1–Q-P4 runtime acceptance. No schema-valid Q-P1–Q-P4 dry-run evidence has been recorded, so those performance scenarios remain inactive.
- No saved controlled benchmark-results document or standalone controlled benchmark runner was found.
- The toolbar exposes System/Light/Dark theme choices and Browser 1/Browser 2/Browser 3 resolve theme-aware colors. Actual System-theme resolution and equivalent light/dark screenshots remain unverified.
- Ingestion, provider, realtime, and storage modules are empty or unrelated to the implemented local-data workload.
- High-Dimensional Projection uses fixed synthetic layouts; lasso selection is not implemented.
- Browser 1, Browser 2, and Browser 3 now use their canonical fixtures and have focused state/headless tests. Equivalent light/dark and 100%/200% screenshots have not been collected; runtime table resizing/reordering, horizontal scrolling, Browser 2 pointer/editor/clipboard interactions, heat-map hover, and header/cell interactions remain unverified.
- The analytical chart now has nine canonical frames, structured content, raw-observation inspection, annotations, LOD, deterministic live optimization, and shell reset/live routing. Model/headless tests and explicit 100K/1M hash checks pass, but real pointer/touch interaction, equivalent screenshots, sustained crosshair behavior, pan/zoom presentation timing, and C-P1–C-P3 runtime acceptance remain unverified.
- The professional stock chart now has canonical daily/on-demand 20K intraday fixtures, shared Price/Volume/Indicator navigation and crosshair, three mandatory price modes, indicators including session/rolling/anchored VWAP, inspectable fixed-demo patterns/signals/events, five annotation kinds, focus-gated Delete, deterministic live updates, and source/visible/rendered/aggregation diagnostics. Model/headless tests cover canonical hashes, annotation/viewport preservation, shell reset/live routing, textual accessibility, and the 20K/1,000-visible render counts. Real pointer/touch drawing and selection, equivalent screenshots, sustained crosshair behavior, pan/zoom presentation timing, and C-P4 runtime performance acceptance remain unverified.
- The pivot chart now has nine canonical 1,500-business-day symbols, exact five-source-day Weekly and calendar Monthly aggregation, strict pivot/buffer/zig-zag/step oracles, three price modes, six ranges, crosshair readouts, and one state-owned viewport shared with a full-series navigator. Default initialization constructs only SPY. Model/headless tests cover canonical SHA-256 artifacts, ranges, the five-bar minimum, navigator operations and actual 8 px edge hit targets, shell reset scopes, textual accessibility, and 300-bar Weekly rendering. Real pointer/touch center/edge/outside interactions, equivalent screenshots, sustained crosshair behavior, and synchronized runtime view/navigator acceptance remain unverified.
- Live modes are local simulations; target update frequency is not measured frame rate. Browser 2, Browser 3, analytical optimization, and the stock chart consume the global 500 ms Live Simulation control. Common correlation shares Browser 3’s 500 ms stream; their hidden-route clock rebasing prevents hidden-page catch-up backlogs, while visible due-tick catch-up remains deterministic. Frontier retains its specialized Advanced rate and the order book retains 1/10/30 Hz playback, both gated by global Live without changing local preferences. Common order-book 50 ms timestamps are source time, not the playback cadence. Tick scheduling, hidden-route rebasing, and deterministic appends are headless-tested, but actual desktop cadence is unmeasured.
- Inactive native-scene updates, hidden cameras, and volatility animation are gated, but comparative startup and idle measurements have not been recorded.
- Fixed 1024×640 3-D targets and desktop-oriented controls limit responsive/high-DPI claims.
- Browser 2 copies contiguous cell/range selections and ordered row/column selections as TSV, and pastes validated rectangular blocks atomically through native egui clipboard events. Disjoint cell copy is rejected with an explanatory status message.
- Browser 2 undo/redo covers direct edits, checkbox changes, Delete, and paste with a 500-mutation undo bound. Save-baseline, demo-data reset, and manual revert clear history. System clipboard delivery has not been exercised through the running desktop application.
- `bevy_egui/accesskit` is enabled. Headless tests verify Browser 2 grid/grid-cell semantics and analytical/stock-chart textual summaries, but they do not establish screen-reader behavior or standards compliance.
- The locked dependency graph contains AccessKit's macOS and Windows `accesskit_winit` adapters but no observed Linux `accesskit_unix`/AT-SPI adapter. Linux runtime accessibility therefore remains unverified.
- Export View requests a real composited primary-window `Screenshot` and writes PNG output through an observer; the file-writing path is unit-tested. OS-level synthetic clicks did not activate the toolbar in the audited session, so no toolbar-triggered PNG was produced.
- Startup-to-first-composited-frame, first-interactive timing, live adapter/RSS text, and capture status were not directly inspected in the running GUI. The automatic startup readback adds measurement overhead and must be disclosed with any startup result.
- Plot submission and texture-enqueue durations are CPU-side measurements, not GPU execution time. Linux RSS is sampled from `/proc/self/status` at most once per second while diagnostics are visible.

## Stable-ID development runtime evidence

- On 2026-11-21, `tools/runtime_smoke.py` drove the Slint, QML, and Bevy + egui Release executables sequentially in the audited GNOME Wayland session using their explicit automation opt-ins and `BEVY_ASSET_ROOT` for Bevy. Metrics and offscreen/renderer overrides were absent. NT-12 records a checkout-independent rendering of the invocation and the route replies; the development JSONL log was kept outside the repositories.
- All three passed initial-state, canonical cross-primary selection, retained-secondary, idempotent-reselection, and unknown-ID non-mutation assertions, including a follow-up `state` check. Each restored Browser 1, acknowledged `quit`, and exited with status 0. QML local IDs were translated and canonicalized by the parent runner.
- These are semantic application-state checks after adapter-specific GUI-thread or post-draw acknowledgement. They are not OS-level pointer/keyboard tests and do not establish rendered content, presented frames, screenshots, accessibility, theme/DPI behavior, cadence, performance, disabled-route behavior, or controlled scenario acceptance. No capability status or inactive performance scenario was changed by this smoke run.

## Interpretation rules

- Source-observed behavior is not runtime-verified behavior.
- Absence of a test result is not a failed test.
- Historical metrics are observations, not controlled rankings.
- Exact numerical algorithms and synthetic visualization fixtures are not equivalent workloads.
- Application-owned components must not be described as stock framework widgets.
- Offscreen/software-rendered CI performance is not comparable with physical-GPU desktop performance.
