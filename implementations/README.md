# Implementation baselines

This directory contains three Git submodules pinned by the parent repository's gitlinks:

| Path | Repository | Pinned commit |
|---|---|---|
| `implementations/slint` | [Slint](https://github.com/johnokyle/slint-ui-test) | `10da5581ec16992beb6adf71cd7abf09e9c20362` |
| `implementations/qml` | [QML](https://github.com/johnokyle/qml-ui-test) | `df83bdf6704f0c33b43eda56bae9ba9db28c8cc5` |
| `implementations/bevy-egui` | [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) | `adf0d678609d99f6fd836fc1cfce520f8aba0344` |

The implementation repositories are currently private. Each remote retains the annotated `comparison-baseline-2026-11-21` tag at its original licensed baseline. The current pins above include the subsequent README, third-party-notice, and publication-cleanup revisions. Parent gitlinks, rather than branch or tag names, remain authoritative for exact source revisions.

Initialize or update the working copies with:

```bash
git submodule update --init --recursive
```

Update implementation pointers through explicit pull requests. Every scenario result must record the full commit actually used, including when it differs from the parent repository's submodule pointer.

Original Slint and Bevy + egui code uses MIT OR Apache-2.0; original QML code uses GPL-3.0-or-later. Third-party dependencies and assets retain their own licenses.
