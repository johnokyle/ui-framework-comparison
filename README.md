# UI Framework Comparison

A versioned comparison of three data-intensive desktop UI implementations:

| Implementation | Language and UI stack | Audited framework versions |
|---|---|---|
| [Slint](https://github.com/johnokyle/slint-ui-test) (private) | Rust, Slint | Slint 1.17.1; Rust edition 2024 |
| [QML](https://github.com/johnokyle/qml-ui-test) (private) | C++, Qt Quick/QML | Qt 6.10+ declared; Qt 6.11.1 in the audited build cache |
| [Bevy + egui](https://github.com/johnokyle/bevy-egui-test) (private) | Rust, Bevy ECS, egui | Bevy 0.19.1; bevy_egui 0.42.0; egui_plot 0.37.0 |

The project compares functional coverage, native versus application-owned capabilities, implementation effort, rendering quality, maintainability, and runtime behavior. It does not reduce the comparison to a single framework ranking.

## Current status

This repository is an **initial local scaffold**. The source audit and historical metrics are recorded, but no controlled three-framework benchmark has been run.

The implementation repositories are not attached as submodules yet:

- QML has no Git baseline in the audited location.
- The complete audited Bevy + egui implementation is not contained in its current HEAD.
- Licenses have not been selected for the implementations or this parent repository.

See [Publication blockers and limitations](docs/limitations.md) before publishing or attaching implementations.

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

## Repository layout

```text
implementations/       Pinned implementation submodules, once baselines are ready
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

1. Select licenses and complete publication reviews.
2. Establish clean, complete implementation Git baselines.
3. Implement the bounded [Bevy + egui parity plan](docs/bevy-parity-implementation-plan.md).
4. Attach the three implementations as pinned submodules.
5. Replace draft scenarios with verified fixtures and executable smoke tests.
6. Collect a controlled baseline on documented hardware.
7. Publish the first versioned comparison report.

## License

No license has been selected yet. Until one is added, this repository should not be treated as licensed for redistribution or reuse.
