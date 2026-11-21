# Machine-readable scenarios

The initial documents are **drafts**. They establish IDs, workload dimensions, and implementation mappings, but they do not yet define shared fixture hashes or executable automation inputs.

- `core/`: intended for all three implementations.
- `slint-qml/`: closer two-implementation parity scenarios.
- `framework-specific/`: demonstrations that are not scored against unrelated architectures.

See `docs/scenario-catalog.md` for the candidate catalog and `specifications/comparison-contract.md` for lifecycle and evidence rules.

Validate with:

```bash
python tools/validate_repository.py
```
