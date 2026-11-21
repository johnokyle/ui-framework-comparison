# Results

No controlled benchmark results have been collected yet.

## Storage policy

- `raw/` contains immutable, small JSON result documents and associated machine manifests.
- `summaries/` contains generated Markdown or CSV summaries derived from raw results.
- Large screenshots, videos, profiler captures, and traces should be attached to CI runs or releases and referenced by checksum.
- Historical application measurements belong in versioned reports and must be labeled as historical, not controlled comparison results.

Use a unique run directory or run ID for each collection. Never overwrite a previous run in place.

Each result document must validate against `schemas/benchmark-result.schema.json`. A result without an exact source commit, scenario revision, and machine manifest is incomplete.
