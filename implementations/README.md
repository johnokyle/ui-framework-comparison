# Implementation baselines

This directory contains three Git submodules pinned by the parent repository's gitlinks:

| Path | Repository | Pinned commit |
|---|---|---|
| `implementations/slint` | [Slint](https://github.com/johnokyle/slint-ui-test) | `7c1b4151b9b4d7e716683a8681a548d3220318a2` |
| `implementations/qml` | [QML](https://github.com/johnokyle/qml-ui-test) | `3561683acde306bdb65233c337d2bec3eba455c5` |
| `implementations/bevy-egui` | [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) | `4f1c89556206c8f1efd61d420062eb4039c454b6` |

The implementation repositories are currently private. Each remote publishes the annotated `comparison-baseline-2026-11-21` tag at the pinned commit listed above. Parent gitlinks, rather than branch or tag names, remain authoritative for exact source revisions.

Initialize or update the working copies with:

```bash
git submodule update --init --recursive
```

Update implementation pointers through explicit pull requests. Every scenario result must record the full commit actually used, including when it differs from the parent repository's submodule pointer.

Original Slint and Bevy + egui code uses MIT OR Apache-2.0; original QML code uses GPL-3.0-or-later. Third-party dependencies and assets retain their own licenses.
