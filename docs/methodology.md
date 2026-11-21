# Measurement methodology

## Purpose

Measure engineering trade-offs for equivalent, explicitly defined workloads. Separate framework-provided functionality, application-owned infrastructure, rendering quality, and runtime cost.

The historical Slint and QML measurements recorded on 2026-08-25 are not controlled head-to-head results. They must not be used alone to rank the frameworks.

## 1. Source and implementation effort

Use one configured version of `scc`, `tokei`, or an equivalent source counter for all implementations. Publish its version and configuration.

Report separately:

- Physical and logical UI-markup lines.
- Physical and logical backend lines.
- Test code.
- Generated code and assets, excluded from hand-written totals.
- Application-owned grid, chart, rendering, navigation, and infrastructure code.
- Direct and transitive dependencies from locked dependency graphs.

Do not compare the existing custom-code totals directly: their file scopes differ. Define ownership by a reviewed path manifest for each implementation.

Supplement subjective difficulty scores with repeatable extension tasks, such as adding a grid column, adding a chart annotation, or adding a quant view. Record files touched, lines changed, defects introduced, and validation performed.

## 2. Build measurements

Report these as separate metrics:

1. Completely clean build, including dependencies.
2. Application-only build with dependencies already cached.
3. Incremental rebuild after a specified source change.
4. Release build.

Record compiler, linker, build-system and dependency versions, parallelism, cache state, power mode, and relevant environment variables. Run builds on the same host for direct comparisons and retain every sample.

## 3. Runtime environment

For every run, record:

- Implementation source commit and scenario revision.
- OS, kernel, compositor or window system, and session type.
- CPU, RAM, GPU, driver, and rendering backend.
- Build profile and compiler.
- Window size, scale factor, and theme.
- Initial page, dataset, live-update state, and enabled overlays.
- Cold/warm filesystem-cache state and background-load controls.

Use a common viewport for controlled scenarios. Do not silently compare Slint's 1600×1000 default, QML geometry, and Bevy's 1600×900 default without normalizing them.

## 4. Startup and memory

Measure both:

- Process start to first rendered frame.
- Process start to a defined first-interactive condition.

Distinguish cold and warm starts. Existing `AfterRendering`, QML startup, and other internal signals may be retained as supplementary measurements, but their definitions must remain visible.

Measure idle memory only after a specified warm-up, then measure steady-state and peak memory for each workload. On Linux, retain RSS and, where practical, PSS and peak RSS. Record GPU memory separately when reliable tooling is available.

## 5. Interaction and rendering

Use scripted, stable-ID-based actions where possible. Measure:

- Frame-time median, p95, p99, and maximum.
- Dropped or missed frames.
- CPU and, where available, GPU time.
- Achieved live-update frequency.
- Input-to-next-present latency when instrumentation supports it.

Application render-call intervals, Canvas callback latency, and CPU stage timings are not substitutes for compositor presentation timing or input-to-photon latency.

Use physical, documented graphics hardware for authoritative graphics comparisons. Virtual-display, offscreen, and software-rendered CI runs are useful for correctness but must be labeled separately.

## 6. Quality and accessibility

Keep visual quality separate from feature completion. Capture equivalent views for:

- Light and dark themes.
- System-theme behavior where supported.
- Narrow and minimum window sizes.
- 100% and 200% scale factors.
- Dense grids, chart overlays, 3-D surfaces, and live updates.

Test keyboard-only operation, focus traversal, disabled states, editing, and selection. Inspect accessibility-tree exposure for custom controls where the platform permits. Record unsupported screen-reader or automation paths explicitly.

## 7. Sampling and reporting

Use repeated process runs and a documented warm-up for interaction scenarios. Publish raw samples, median, p95/p99 where meaningful, spread, and anomalies. Do not report only the minimum or best of three.

Randomize implementation order where practical and monitor thermal or background interference. Results are immutable: rerun the complete scenario and add a new run rather than editing an old one.

Every summary table must link to its scenario definition, source commits, machine manifest, raw data, and known deviations.
