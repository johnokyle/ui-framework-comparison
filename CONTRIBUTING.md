# Contributing

## Change scope

Use this parent repository for cross-framework specifications, scenarios, fixtures, measurement tooling, and reports. Keep implementation defects and framework-specific changes in the relevant implementation repository once those repositories are published.

## Add or revise a scenario

1. Read `specifications/comparison-contract.md` and `docs/scenario-catalog.md`.
2. Add a JSON document under the appropriate `scenarios/` tier.
3. Give the scenario a stable ID and increment its revision when its meaning changes.
4. Map each implementation to its actual stable page ID.
5. Record the exact workload, environment, actions, and expected evidence.
6. Mark unsupported or substituted behavior explicitly.
7. Run `python tools/validate_repository.py`.

Do not silently change an existing scenario to make results comparable. Create a new scenario revision and retain prior measurements with their original scenario revision.

## Add benchmark results

Each result must identify:

- Scenario ID and revision.
- Implementation and full source commit.
- Build profile and relevant compiler/framework versions.
- Hardware, OS, compositor, GPU, driver, and rendering backend.
- Window size, scale factor, theme, and initial page.
- Cold/warm cache state and warm-up procedure.
- Raw samples and summary statistics.
- Related artifacts and known deviations.

Never replace an immutable run because a newer result is more favorable. Add a new run with a unique run ID.

## Performance claims

A performance claim requires raw evidence collected under `docs/methodology.md`. Historical application diagnostics may be discussed as observations, but must not be presented as controlled cross-framework rankings.

## Generated and local files

Do not commit build directories, dependency caches, virtual environments, credentials, `.env` files, editor-local configuration, or machine-specific CMake caches. Store large benchmark artifacts as release or CI artifacts rather than adding them directly to Git.
