# UI Framework Comparison

A versioned comparison of three data-intensive desktop UI implementations:

| Implementation | Language and UI stack | Audited framework versions |
|---|---|---|
| [Slint](https://github.com/johnokyle/slint-ui-test) (private) | Rust, Slint | Slint 1.17.1; Rust edition 2024 |
| [QML](https://github.com/johnokyle/qml-ui-test) (private) | C++, Qt Quick/QML | Qt 6.10+ declared; Qt 6.11.1 in the audited build cache |
| [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) (private) | Rust, Bevy ECS, egui | Bevy 0.19.1; bevy_egui 0.42.0; egui_plot 0.37.0 |

The project compares functional coverage, native versus application-owned capabilities, implementation effort, rendering quality, maintainability, and runtime behavior. It does not reduce the comparison to a single framework ranking.

## Current status

This repository now contains versioned specifications, canonical fixture manifests, schemas, validation tooling, and a common stable-ID runtime smoke harness. The three implementation repositories have clean Git baselines and are linked above; they are currently private and are attached as pinned submodules under `implementations/`. Each implementation publishes the licensed baseline as the annotated `comparison-baseline-2026-11-21` tag.

Normalized headless/model fixture evidence covers all 73 parent artifacts across Slint, QML, and Bevy + egui. A development runtime smoke run also passed semantic navigation, unknown-ID non-mutation, and clean-shutdown checks in all three Release applications. These checks do not establish equivalent rendering, OS-level interaction, accessibility, or performance.

No controlled three-framework benchmark has been run. License texts, a third-party source inventory, and a reachable-history review have been added. Remaining publication work includes confirming undocumented Slint icon authorship and preparing target-specific binary-release notices.

See [Publication blockers and limitations](docs/limitations.md) for the evidence boundaries and remaining verification work.

## Comparison summary

**Preliminary comparisons are complete; controlled empirical comparisons are forthcoming.**

### Completed

- Source-level and architectural comparisons, with capability classification.
- Normalized headless/model checks covering all 73 canonical fixture artifacts across the three implementations.
- A development runtime smoke test verifying semantic navigation, retained selections, unknown-ID handling, and clean shutdown in all three applications.
- Historical measurements and implementation observations recorded with their limitations.

### Forthcoming

- Controlled three-framework performance benchmarks with raw samples and distributions.
- Defensible performance rankings.
- Equivalent screenshot and rendering-quality comparisons.
- OS-level pointer/keyboard and touch interaction testing.
- Accessibility, theme, DPI, and responsive-layout verification.
- Runtime acceptance of the controlled performance scenarios.
- The first versioned controlled comparison report.

The current evidence supports source-level, functional, fixture/model, and limited semantic-runtime comparisons. It does not yet support a controlled conclusion that one framework is faster, smoother, or generally better.

## Start here

- [Initial findings and implementation plan](docs/reports/2026-11-20-initial-findings.md)
- [Bevy + egui pre-parity baseline](docs/reports/2026-11-20-bevy-pre-parity-baseline.md)
- [Draft capability matrix](docs/capability-matrix.md)
- [Scenario catalog](docs/scenario-catalog.md)
- [Measurement methodology](docs/methodology.md)
- [Comparison contract](specifications/comparison-contract.md)
- [Bevy + egui parity specification](specifications/bevy-parity.md)
- [Bevy + egui parity implementation plan](docs/bevy-parity-implementation-plan.md)
- [Known limitations and publication blockers](docs/limitations.md)
- [Third-party notices](THIRD_PARTY.md)

## Repository layout

```text
implementations/       Pinned implementation submodules
docs/                  Methodology, matrices, limitations, and versioned reports
specifications/        Common comparison rules and workload contracts
scenarios/             Machine-readable core, Slint/QML, and specific scenarios
schemas/               JSON Schemas for scenarios and benchmark results
fixtures/              Shared-fixture policy and fixture manifests
tools/                 Repository validation and future measurement adapters
results/               Immutable raw measurements and generated summaries
.github/               Validation workflow and contribution templates
```

## Validation

The scaffold uses JSON for machine-readable scenarios so repository validation has only one Python dependency:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r tools/requirements.txt
python tools/validate_repository.py
```

Validation checks JSON syntax, scenario and result documents against their schemas, and selected cross-document invariants. It does not build or benchmark the implementations.

## Comparison principles

1. Pin implementation revisions for every result.
2. Separate NATIVE, COMPOSED, CUSTOM, EXTERNAL, and EXPERIMENTAL capabilities.
3. Keep completion status separate from implementation classification.
4. Use identical fixtures, workloads, environments, and success criteria for controlled comparisons.
5. Preserve raw samples and report distributions rather than only best-case values.
6. Label unsupported, substituted, partial, and unverified scenarios explicitly.
7. Treat screenshots, accessibility, rendering quality, and maintainability as separate evidence categories.
8. Keep historical measurements distinct from controlled benchmark results.

## Next milestones

1. Confirm undocumented Slint asset provenance and prepare release-specific notice bundles before distributing binaries.
2. Collect OS-level interaction, screenshot, theme/DPI, and accessibility evidence still required by the scenarios.
3. Activate the applicable performance scenarios and collect controlled baselines with raw samples on documented hardware.
4. Publish the first versioned controlled comparison report.

## License

Original source code, JSON schemas, scenarios, and fixture manifests are licensed under the [Apache License 2.0](LICENSE-APACHE). Original documentation, reports, and other Markdown prose are licensed under the [Creative Commons Attribution 4.0 International License](LICENSE-CC-BY-4.0). See [LICENSE](LICENSE) for the content-type mapping.

Implementation submodules are covered by their own repository licenses. Third-party dependencies, frameworks, fonts, icons, and other assets retain their respective licenses and notice requirements. See [Third-party notices](THIRD_PARTY.md) for the source and binary-release inventory.
