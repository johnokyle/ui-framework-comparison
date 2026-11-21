# Bevy + egui pre-parity baseline — 2026-11-20

## Scope

This records the BP-00 verification of the current local Bevy + egui worktree before parity implementation. It is a source/build baseline, not a controlled runtime benchmark and not a comparison with Slint or QML.

## Source identity

- Repository: `/run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test`
- Branch: `master`
- HEAD: `354f7ea`
- Declared stack: Bevy 0.19.0 (0.19.1 resolved), bevy_egui 0.42.0, egui_plot 0.37, egui_extras 0.36.2

HEAD alone does **not** identify the verified application. The worktree contains tracked modifications, a deletion, and substantive untracked source trees including `src/app/`, `src/data/`, `src/numeric/`, `src/renderer/`, and `src/ui/`. No commit was created because commits were not authorized. A complete immutable source revision remains a publication blocker.

## Verification results

Commands were run with an explicit Bevy manifest path and the locked dependency graph:

```bash
cargo fmt --all --manifest-path "/run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test/Cargo.toml" -- --check
cargo test --manifest-path "/run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test/Cargo.toml" --locked
cargo build --release --manifest-path "/run/media/john/data/Experimental/UITests/Bevy+egui/bevy_egui_test/Cargo.toml" --locked
```

| Check | Result |
|---|---|
| Formatting | Passed; no diffs reported |
| Unit tests | 315 passed; 0 failed; 0 ignored |
| Test execution time | 0.14 s after compilation |
| Release build | Passed |
| Release build elapsed time | 2 min 27 s |

The release elapsed time is an observational build result for this local invocation. It is not a normalized or reproducible performance measurement.

## Existing diagnostics

The build retains existing unused-import and unused-variable warnings. BP-00 did not perform general warning cleanup. The GUI was not launched, so window behavior, rendering, accessibility, and interactions were not verified by this baseline.

## BP-00 disposition

The current source is buildable and its existing automated tests pass. Parity work can proceed incrementally against this verified worktree, while every future result must disclose that the pre-parity application is not recoverable from HEAD alone. Clean committed baselines and pinned implementation submodules remain deferred until explicitly authorized.
