# Scenario catalog

Scenarios are divided by actual comparability. A framework does not fail a comparison merely because a framework-specific scenario is inapplicable.

## Tier A — core three-framework scenarios

These are candidates for controlled comparison after shared fixtures and executable action definitions are available.

| Area | Candidate scenarios | Important normalization |
|---|---|---|
| Shell | Cold/warm startup, first interactive, idle memory, navigation | Same viewport, initial page, build profile, and eager/lazy initialization disclosure |
| Grid | Large-table scroll, selection, sorting, editing where supported | Same rows, columns, cell types, and visible viewport |
| Charts | Pan/zoom, crosshair, source-to-rendered counts | Same source data, LOD policy disclosure, and canvas size |
| Volatility surface | Orbit, pan, zoom, reset, animation, 500×500 stress grid | Same camera and surface values; separate GPU and software rendering observations |
| Factor structure | 1K, 10K, and 100K points; selection and camera actions | Same point positions, selection IDs, and point-size policy |
| Correlation surface | 2-D/3-D switch, pair inspection | Same matrix and clustering behavior |
| Efficient frontier | Cloud display, selection, live regeneration | Disclose exact QP versus sampled-envelope algorithms |
| PCA manifold | 2-D/3-D display, trajectory, selection | Disclose computed PCA versus synthetic fixture layouts |
| Regime map | History filtering, transitions, selection | Same observations and regime assignments |
| Projection | Rectangle/group selection, pan/zoom | Do not label fixed layouts as executions of t-SNE or UMAP |
| Network graph | 100/300 and 1,000/5,000 node/edge workloads | Same graph, layout iteration policy, and visible-label budget |
| Knowledge graph | Search, expand/collapse, drag, selection | Same entities, relations, and expansion sequence |
| Monte Carlo | Paths, bands, histogram, path inspection | Same paths and confidence-band definition |
| Order book | 1,000×200 playback and inspection | Same book events and achieved update-rate measurement |

## Tier B — Slint/QML parity scenarios

The bounded path for adding Bevy + egui to this close-twin workload is defined by the [Bevy parity specification](../specifications/bevy-parity.md) and [implementation plan](bevy-parity-implementation-plan.md). Until that work is verified, Tier B remains Slint/QML-only for scenarios Bevy has not implemented.

These follow the closer Slint/QML twin workload:

- Browser 1: 2,000-row financial grid, sorting, resizing, reordering, selection, and keyboard behavior.
- Browser 2: 1,000/100,000-row editable grid with the actual 19-column workload, filtering, selection, clipboard, undo/redo, and live updates.
- Browser 3: 8×8 correlation heat map, clustering, pair statistics, and live rolling returns.
- Analytical chart: nine analytical frames, LOD, pan/zoom, crosshair, annotations, and live optimization.
- Financial chart: synchronized panels, indicators, renderer modes, events, and drawing tools.
- Pivot chart: resampling, pivots, periods, custom ranges, and navigator interaction.
- Shell: theme switching, stable-ID navigation, disabled-tab fallback, diagnostics, and keyboard focus.

Differences such as QML's missing frozen columns and Slint's high-DPI raster limitation remain explicit deviations, not silently removed requirements.

## Tier C — framework-specific scenarios

Examples include:

- Bevy GPU 3-D scenes and custom WGSL point-cloud rendering.
- Bevy numerical-analysis and full-population statistics behavior.
- QML Qt Graphs integration.
- Slint custom software raster/vector composition and reusable application-owned components.

These scenarios document strengths and engineering costs. They are not scored as missing capabilities in unrelated architectures.

## Scenario lifecycle

1. **Draft:** workload and mappings are under review; implementation-specific fixtures may remain.
2. **Active:** fixture hashes, actions, environment, and success criteria are complete enough for controlled runs.
3. **Retired:** retained for historical reproduction but no longer used for new baselines.

Machine-readable drafts live in `scenarios/`. The schema is defined in `schemas/scenario.schema.json`.
