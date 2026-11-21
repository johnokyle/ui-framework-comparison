# Implementation baselines

This directory will contain three Git submodules:

```text
implementations/slint
implementations/qml
implementations/bevy-egui
```

No submodules are attached yet. Attaching the current source trees would produce misleading baselines because QML has no Git metadata in the audited location and the complete Bevy + egui implementation is not contained in its current HEAD.

## Prerequisites for attachment

Each implementation must first have:

1. An explicit license and third-party notices where needed.
2. A complete committed source tree with generated files and secrets excluded.
3. A README with prerequisites and build/run/test commands.
4. A dependency lockfile or equivalent reproducible version record.
5. A successful clean build and available tests.
6. An immutable tag identifying the comparison baseline.

After those requirements are met, attach each repository at its tagged commit:

```bash
git submodule add <slint-repository-url> implementations/slint
git submodule add <qml-repository-url> implementations/qml
git submodule add <bevy-egui-repository-url> implementations/bevy-egui
git submodule update --init --recursive
```

Update implementation pointers through explicit pull requests. Every scenario result must record the full commit actually used, including when it differs from the parent repository's submodule pointer.
