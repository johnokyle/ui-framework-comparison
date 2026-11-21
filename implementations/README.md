# Implementation baselines

This directory contains three Git submodules pinned by the parent repository's gitlinks:

| Path | Repository | Pinned commit |
|---|---|---|
| `implementations/slint` | [Slint](https://github.com/johnokyle/slint-ui-test) | `c7d5f6c725569369f2ccf08efcf269b28d39105d` |
| `implementations/qml` | [QML](https://github.com/johnokyle/qml-ui-test) | `45f35f524f3fbbcd1e55fe5de6d26acc3259af6c` |
| `implementations/bevy-egui` | [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) | `5f2697153a93132585e28fcd3e205c527d081cce` |

The implementation repositories are currently private. The parent gitlinks, rather than branch or tag names, identify the exact source revisions.

Initialize or update the working copies with:

```bash
git submodule update --init --recursive
```

Update implementation pointers through explicit pull requests. Every scenario result must record the full commit actually used, including when it differs from the parent repository's submodule pointer.

License selection and immutable baseline tags remain publication follow-up work.
