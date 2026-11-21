# Comparison contract

## 1. Comparison unit

The unit of comparison is a **scenario revision executed against exact implementation source commits**, not an unpinned framework version or an application page name alone.

Each comparison must identify:

- Scenario ID and revision.
- Implementation repository and full commit.
- Stable application page ID.
- Fixture or generator revision and content hash.
- Workload dimensions.
- Environment and build profile.
- Action sequence and success criteria.
- Raw evidence and known deviations.

## 2. Completion status

Completion and provision are separate attributes.

| Status | Meaning |
|---|---|
| `unverified` | Source or documentation suggests coverage, but runtime evidence is incomplete |
| `supported` | The complete scenario has passed its defined validation |
| `partial` | Some required behavior is implemented or verified, with deviations recorded |
| `not-implemented` | The implementation does not provide the required behavior |
| `not-applicable` | The scenario is intentionally specific to another architecture |
| `not-comparable` | A related demonstration exists, but its workload is not equivalent |

A page's existence is insufficient for `supported`.

## 3. Provision classification

| Class | Meaning |
|---|---|
| `NATIVE` | Directly supported by the framework or its standard modules |
| `COMPOSED` | Implemented by combining ordinary framework controls |
| `CUSTOM` | Requires substantial application-owned component, model, or renderer code |
| `EXTERNAL` | Requires a third-party renderer or library |
| `EXPERIMENTAL` | Depends on unstable or feature-gated integration |

Multiple classes may apply. For example, an `egui_plot` chart with a custom selection model can be both EXTERNAL and CUSTOM.

## 4. Scenario tiers

- `core`: intended for equivalent execution in all three implementations.
- `slint-qml`: the closer two-implementation parity workload.
- `framework-specific`: an architecture-specific demonstration that is not scored against unrelated implementations.

## 5. Scenario documents

Scenario files are JSON documents validated by `schemas/scenario.schema.json`.

A scenario starts as `draft`. To become `active`, it must have:

1. A shared fixture or shared generator with a SHA-256 content contract.
2. Exact workload dimensions and implementation page mappings.
3. A reproducible action sequence and expected evidence.
4. Defined viewport, scale factor, theme, and build profile.
5. Explicit measurement names and documented deviations.

Increment the scenario revision whenever fixture contents, workload, actions, or success criteria change. Do not rewrite history by applying a new scenario definition to old measurements.

## 6. Result documents

Controlled results are JSON documents validated by `schemas/benchmark-result.schema.json`.

A result is complete only when it includes:

- A unique run ID and collection timestamp.
- Scenario and implementation identity.
- Full 40-character source commit.
- Machine and rendering environment.
- Build information.
- Raw metric samples and summary statistics.
- Artifact references and deviations.

Internal application diagnostics may be included, but their metric names must distinguish them from external presentation, latency, or memory measurements.

## 7. Fairness rules

1. Do not compare different dataset sizes as equivalent workloads.
2. Do not compare an exact numerical algorithm with a synthetic visualization without disclosing the computational difference.
3. Do not attribute application-authored components to stock framework functionality.
4. Do not combine build timings with different cache scopes.
5. Do not compare best-case startup with median startup.
6. Do not treat internal frame callbacks as compositor presentation measurements.
7. Do not compare physical-GPU results with offscreen or software-rendered CI results.
8. Do not hide missing, partial, or substituted behavior.
9. Preserve raw runs and make summaries regenerable.
10. Keep framework-specific strengths visible without converting them into an arbitrary aggregate score.
