# Shared fixtures

The manifests in this directory are the authoritative BP-01 fixture contract. Existing Slint, QML, and Bevy generators remain implementation-specific until their normalized output matches these manifests. Equal seed numbers alone do not establish equal data.

## Layout and ownership

- `manifests/*.json` contains versioned family contracts, typed columns, dimensions, stable-identity rules, RNG draw order, formulas, golden rows, and SHA-256 content hashes.
- `../schemas/fixture-manifest.schema.json` validates the manifest metadata.
- `../tools/generate_fixtures.py` is the reference generator and hash oracle. It uses only the Python standard library.
- `../tools/validate_repository.py` performs cheap schema and metadata validation with the repository's existing `jsonschema` dependency; it does not generate fixture content.
- `normalization-tasks.md` records the Slint/QML work required before a controlled three-framework comparison.

The current contract is schema/generator revision 1: **17 families, 29 variants, and 73 artifacts**. `correlation` deliberately publishes no duplicate payload artifacts; it references the Browser 3 source and matrix instead.

## Commands

Run these commands from the repository root.

```bash
# Cheap schema, ID, reference, golden-width, and result/scenario validation.
python3 tools/validate_repository.py

# Regenerate every artifact in memory and verify row count, golden rows, and hash.
python3 tools/generate_fixtures.py check

# Faster focused checks while developing an adapter.
python3 tools/generate_fixtures.py check --family browser1
python3 tools/generate_fixtures.py check --family analytical --variant days-500

# Repeat --family or --variant to select several entries.
python3 tools/generate_fixtures.py check --family browser2 --family browser3

# Recompute and rewrite manifests after an intentional generator-contract change.
python3 tools/generate_fixtures.py update-hashes
python3 tools/generate_fixtures.py update-hashes --family browser1

# Focused standard-library tests; no large artifact generation.
python3 tools/test_generate_fixtures.py
```

`check` is read-only. `--variant` is check-only so a partial update cannot mix artifact revisions within a family. `update-hashes` rewrites every selected family manifest; use it only with a reviewed generator change, and bump the applicable family/generator revision when semantics change. Do not hand-edit generated golden samples or hashes.

A full check streams all variants, including on-demand sizes, and takes about 67 seconds on the recorded development host. The analytical 1M core artifact is the largest single cost (about 28.5 seconds). Network node and edge artifacts currently rebuild the same layout independently (about 6.1–6.3 seconds each at 1,000 nodes). Ordinary repository validation avoids these costs.

## Canonical artifact bytes

Each artifact hash is SHA-256 over one conceptual compact JSON document:

```text
{"artifact_id":"...","columns":["column_id",...],"rows":[[...],...]}
```

There is exactly one LF after the closing brace. Payload documents are streamed directly into the hasher; they are not written to disk.

Adapters must apply all of these rules before comparing hashes:

1. **Encoding and layout:** UTF-8 without BOM, no insignificant whitespace, separators `,` and `:`, no carriage returns, and exactly one trailing LF. Object keys are sorted by Unicode code point. The three top-level keys therefore appear as `artifact_id`, `columns`, `rows`.
2. **Rows and columns:** `columns` contains IDs only, in manifest order. Every row is an array in that same order. Source order is authoritative; sorting, filtering, clustering, display mapping, and LOD do not reorder source identity or change hashed content.
3. **Numbers:** calculations use IEEE 754 binary64 without intermediate nine-decimal rounding, except Browser 2 trend operations explicitly use binary32. Serialization uses fixed base-10 notation with exactly nine digits after the decimal point, round-to-nearest ties-to-even, and no exponent. JSON integers remain integers.
4. **Zero and nonfinite values:** negative zero and any nonzero value rounding to zero at nine decimals serialize as `0.000000000`. NaN and either infinity are rejected, not serialized.
5. **Other values:** missing/warm-up values are JSON `null`; booleans are JSON `true`/`false`; strings use RFC 8259 escaping and direct UTF-8 for non-ASCII text, with no locale conversion or Unicode normalization.
6. **Dates and calendars:** dates are `YYYY-MM-DD`; datetimes are UTC `YYYY-MM-DDTHH:MM:SSZ`. Business calendars skip Saturday/Sunday but claim no holiday calendar. Synthetic intraday sessions contain 390 one-minute bars from 09:30 through 15:59 inclusive (16:00 exclusive).
7. **Golden samples:** selectors such as `row[123]` address the canonical artifact row array, not a sorted or filtered view. Formula comparisons may use absolute and relative tolerance `1e-9`; content hashes still require exact canonical bytes.

The manifest's pretty-printed JSON and its numeric golden values are metadata, not the payload byte stream. Do not hash the manifest file itself.

## Random-number contract

Generated families use SplitMix64 with wrapping unsigned 64-bit arithmetic:

- Initialize state to the specified seed modulo 2^64.
- `next_u64` first adds `0x9E3779B97F4A7C15`, then applies the two published xor/shift/multiply mixing stages modulo 2^64.
- `uniform()` is `(next_u64() >> 11) * 2^-53`.
- `below(n)` is `next_u64() modulo n`; there is no rejection sampling.
- `normal()` consumes exactly two uniforms, clamps the first to at least `1e-12`, and returns only the Box–Muller cosine component. The sine component is discarded and normals are never cached.

The per-family manifest fixes seeds, independent-stream rules, and exact consumption order. Skipping, adding, or reordering a draw invalidates all later content. In particular, Browser 1/2 source row 123 still consumes the symbol-length draw but consumes no symbol-letter draws before emitting `WA`.

## Inventory and selection policy

`default` is the canonical small startup selection. `on-demand` artifacts are included in full `check`/`update-hashes`, but must be constructed only after explicit selection.

| Family manifest | Default variant | On-demand variants | Artifact IDs |
|---|---|---|---|
| `browser1.json` | `2000x12` | — | `browser1.rows.2000` |
| `browser2.json` | `1000x19` | `100000x19` | `browser2.rows.1000`, `browser2.rows.100000` |
| `browser3.json` | `8x250` | — | `browser3.returns.250`, `browser3.correlation.8x8`, `browser3.covariance.8x8`, `browser3.annualized-volatility.8`, `browser3.beta.8x8`, `browser3.cluster-order.8`, `browser3.live.16` |
| `analytical.json` | `days-500` | `days-2500`, `days-20000`, `days-100000`, `days-1000000` | `analytical.returns.{n}`, `analytical.core.{n}`, and `analytical.risk-oracles.{n}` for each `n` in `500,2500,20000,100000,1000000`; plus `analytical.features.10`, `analytical.optimization.240`, `analytical.optimization-live.48`, `analytical.accuracy.12`, `analytical.confusion.3x3`, `analytical.attribution.12x5`, `analytical.correlation-results.250` |
| `stock.json` | `daily` | `intraday` | For `daily.1260` and `intraday.20000`: `stock.bars.{variant}`, `stock.indicators.{variant}`, `stock.markers.{variant}`; plus `stock.live.daily.16`, `stock.live.intraday.16` |
| `pivot.json` | `9x1500` | — | `pivot.daily.9x1500`, `pivot.weekly.9x300`, `pivot.monthly.9-calendar`, `pivot.strict-oracles.9x1500`, `pivot.zigzag.9` |
| `volatility.json` | `100x100` | `250x250`, `500x500` | `volatility.surface.100x100`, `volatility.surface.250x250`, `volatility.surface.500x500` |
| `factor.json` | `points-240` | `points-1000`, `points-10000`, `points-100000` | `factor.points.240`, `factor.points.1000`, `factor.points.10000`, `factor.points.100000` |
| `correlation.json` | `8x250-shared` | — | No payload artifacts; references `browser3.returns.250`, `browser3.correlation.8x8`, `browser3.cluster-order.8` |
| `frontier.json` | `12x2500x40` | — | `frontier.assets.12`, `frontier.portfolios.2500`, `frontier.envelope.40`, `frontier.special.3` |
| `pca.json` | `synthetic-500` | — | `pca.synthetic.500` |
| `regime.json` | `observations-400` | — | `regime.observations.400` |
| `projection.json` | `5000x5x3` | — | `projection.pca-like.5000`, `projection.tsne-like.5000`, `projection.umap-like.5000` |
| `network.json` | `100x300` | `1000x5000` | `network.nodes.100`, `network.edges.300`, `network.nodes.1000`, `network.edges.5000` |
| `knowledge.json` | `24x22` | — | `knowledge.entities.24`, `knowledge.relations.22` |
| `monte-carlo.json` | `600x120` | — | `monte-carlo.paths.600x120`, `monte-carlo.bands.120`, `monte-carlo.histogram.40` |
| `order-book.json` | `1000x200` | — | `order-book.snapshots.1000x200`, `order-book.levels.1000x200`, `order-book.events.1032` |

**Startup rule:** default construction must not create `browser2.rows.100000`, `analytical.*.100000`, or `analytical.*.1000000`. Other nondefault variants are also on-demand. Keep full-resolution source data authoritative and separate from extrema-preserving rendering LOD, presentation caches, and display mappings.

## Identity and numerical/rendering separation

Browser 1 and Browser 2 derive stable IDs respectively as `b1-{source_ordinal:06d}` and `b2-{source_ordinal:06d}`; these are not additional displayed columns. Browser 1's WA row is `b1-000123`. Other families use their explicit first-column IDs or the identity rule in `entity_identity`. Selection, filtering, clustering, resizing, and live updates must not silently renumber source entities.

`classification` is intentional:

- `numerical` families define exact formulas and derived-series oracles, including sample denominators, warm-up nulls, aggregation, and pivot confirmation timing.
- `rendering` families define deterministic inputs for visual parity, not claims about a more advanced algorithm. The sampled frontier is not exact QP; synthetic PCA coordinates are not a decomposition; `*-like` projection layouts do not run PCA/t-SNE/UMAP; and Monte Carlo rendering paths are not a numerical GBM benchmark.
- Existing exact/advanced implementation features may remain extensions, but must not silently replace common rendering inputs in a controlled scenario.

Pivot behavior deliberately canonicalizes strict high/low ties and applies derived steps at confirmation index `candidate+period`, not retroactively at the candidate. This is a shared normalization decision, not a requirement for Bevy to reproduce an existing Slint/QML discrepancy.

## Payload and activation policy

1. Do not commit large generated payload files. Generate them on demand or stream them in memory using the versioned contract.
2. Preserve authoritative full-resolution data separately from presentation caches and LOD samples.
3. Verify all required normalized content hashes before a controlled benchmark run and record the verified family/artifact revisions.
4. Record intentional algorithmic differences rather than masking them with a common output fixture.
5. A draft scenario may use implementation-specific generated data. It must not become active for controlled cross-framework comparison until fixture contracts and hashes are verified in every participating implementation.

Publishing these parent-owned contracts does not itself activate a scenario or establish a three-framework comparison.
