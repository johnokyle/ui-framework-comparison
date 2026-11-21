#!/usr/bin/env python3
"""Generate and verify the canonical, normalized comparison fixture hashes.

No payload files are written. ``update-hashes`` is the only command that changes
manifests; ``check`` is read-only. Artifact rows are streamed into SHA-256 so
large variants do not require a serialized payload in memory or on disk.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, Sequence

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "fixtures" / "manifests"
GENERATOR_NAME = "common-fixture-generator"
GENERATOR_REVISION = 1
SCHEMA_VERSION = "1.0.0"
MASK64 = (1 << 64) - 1

NORMALIZATION = {
    "encoding": "UTF-8 without BOM",
    "document": "One compact JSON object with keys artifact_id, columns, rows; columns contains column IDs and rows contains arrays in manifest column order.",
    "object_keys": "JSON object keys sorted by Unicode code point; no insignificant whitespace; separators are ',' and ':'.",
    "array_order": "Arrays and rows retain manifest/generator order; no sorting unless a formula explicitly requires it.",
    "numbers": "IEEE 754 binary64 results are formatted as base-10 fixed-point with exactly 9 digits after the decimal point, round-to-nearest ties-to-even; no exponent notation.",
    "integers": "JSON integers use base-10 without leading zeroes and are not converted to floating point.",
    "negative_zero": "IEEE -0.0 and any nonzero value rounding to zero at 9 decimals serialize as 0.000000000.",
    "nonfinite": "NaN, +Infinity, and -Infinity are rejected before serialization; null is the only missing/warm-up representation.",
    "nulls": "Missing values serialize as JSON null, never NaN, an empty string, or a sentinel number.",
    "booleans": "JSON true and false only.",
    "strings": "JSON string escaping per RFC 8259; non-ASCII characters are emitted directly as UTF-8; no locale conversion or Unicode normalization.",
    "dates": "ISO 8601 YYYY-MM-DD strings. Business calendars skip Saturday/Sunday and make no holiday claim.",
    "datetimes": "ISO 8601 UTC strings YYYY-MM-DDTHH:MM:SSZ; synthetic intraday sessions are 09:30 through 16:00 exclusive, 390 one-minute bars, weekdays only.",
    "line_endings": "No carriage returns; exactly one LF (0x0A) follows the closing JSON brace; no other trailing bytes.",
}
NUMERIC_ORACLE = {
    "calculation": "Compute with IEEE 754 binary64 (and explicit binary32 only for Browser 2 trend) without intermediate 9-decimal rounding. Normalize only for content serialization.",
    "absolute_tolerance": 1e-9,
    "relative_tolerance": 1e-9,
    "display_formatting": "Display precision, currency symbols, grouping, and locale are separate. Formula tests may use these tolerances; content hashes require exact normalized bytes.",
}
RNG_COMMON = {
    "algorithm": "SplitMix64",
    "state": "Unsigned 64-bit state initialized to seed modulo 2^64. next_u64 first adds 0x9E3779B97F4A7C15 modulo 2^64.",
    "output": "z=state; z=(z xor (z>>30))*0xBF58476D1CE4E5B9 mod 2^64; z=(z xor (z>>27))*0x94D049BB133111EB mod 2^64; return z xor (z>>31).",
    "uniform": "(next_u64() >> 11) * 2^-53, producing IEEE binary64 in [0,1).",
    "below": "below(n)=next_u64() modulo n for integer n>=1; no rejection sampling.",
    "normal": "u1=max(uniform(),1e-12); u2=uniform(); return sqrt(-2*ln(u1))*cos(2*pi*u2). Consume exactly two outputs, discard the sine component, and do not cache normals.",
}


class SplitMix64:
    def __init__(self, seed: int):
        self.state = seed & MASK64

    def next_u64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def uniform(self) -> float:
        return (self.next_u64() >> 11) / float(1 << 53)

    def below(self, n: int) -> int:
        if n < 1:
            raise ValueError("below requires n >= 1")
        return self.next_u64() % n

    def normal(self) -> float:
        u1 = max(self.uniform(), 1e-12)
        u2 = self.uniform()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def f32(value: float) -> float:
    return struct.unpack("!f", struct.pack("!f", value))[0]


def canonical_bytes(value: object) -> bytes:
    """Encode one value using the manifest's canonical JSON rules."""
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int):
        return str(value).encode("ascii")
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite value in canonical fixture")
        text = format(value, ".9f")
        if float(text) == 0.0:
            text = "0.000000000"
        return text.encode("ascii")
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if isinstance(value, (list, tuple)):
        return b"[" + b",".join(canonical_bytes(item) for item in value) + b"]"
    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            if not isinstance(key, str):
                raise TypeError("canonical object keys must be strings")
            parts.append(canonical_bytes(key) + b":" + canonical_bytes(value[key]))
        return b"{" + b",".join(parts) + b"}"
    raise TypeError(f"unsupported canonical type: {type(value).__name__}")


def normalized_json_value(value: object) -> object:
    """Convert a generated value to the numeric value represented by canonical bytes."""
    if isinstance(value, float):
        text = canonical_bytes(value).decode("ascii")
        return float(text)
    if isinstance(value, list):
        return [normalized_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [normalized_json_value(item) for item in value]
    return value


def business_date(index: int, start: dt.date = dt.date(2021, 1, 4)) -> str:
    return (start + dt.timedelta(days=(index // 5) * 7 + index % 5)).isoformat()


def intraday_timestamp(index: int) -> tuple[str, str, int]:
    session = index // 390
    minute = index % 390
    date = business_date(session)
    stamp = dt.datetime.fromisoformat(date + "T09:30:00+00:00") + dt.timedelta(minutes=minute)
    return f"{date}-session", stamp.strftime("%Y-%m-%dT%H:%M:%SZ"), minute


def cols(spec: str) -> list[dict[str, object]]:
    result = []
    for item in spec.split(","):
        name, kind = item.strip().split(":", 1)
        nullable = kind.endswith("?")
        if nullable:
            kind = kind[:-1]
        result.append({"id": name, "type": kind, "nullable": nullable})
    return result


Rows = Callable[[], Iterable[list[object]]]


@dataclass
class Artifact:
    id: str
    column_spec: str
    rows: Rows
    description: str
    samples: tuple[int, ...] = (0, -1)


@dataclass
class Variant:
    id: str
    selection: str
    dimensions: dict[str, object]
    artifacts: list[Artifact]


@dataclass
class Family:
    id: str
    title: str
    classification: str
    seed: str | None
    draw_order: list[str]
    formulas: dict[str, str]
    variants: list[Variant]
    identity: str = "The first column is the stable entity/record ID unless entity_identity states otherwise."
    ordering: str = "Source ordinal order is canonical; display sorting, clustering, filtering, and LOD never change source identity."
    extensions: list[str] = field(default_factory=list)
    separation_notes: list[str] = field(default_factory=list)
    references: list[dict[str, object]] = field(default_factory=list)


SECTORS = [
    "Technology", "Health Care", "Financials", "Consumer Discretionary",
    "Communication Services", "Industrials", "Consumer Staples", "Energy",
    "Utilities", "Real Estate", "Materials",
]
SIGNALS = ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"]
ADJ = [
    "Apex", "Blue", "Cedar", "Delta", "Ever", "First", "Grand", "Harbor", "Iron",
    "Keystone", "Lakes", "Meridian", "North", "Omega", "Pinnacle", "Quantum",
    "River", "Summit", "Titan", "Union",
]
NOUN = [
    "Dynamics", "Systems", "Holdings", "Industries", "Labs", "Capital", "Foods",
    "Energy", "Pharma", "Networks", "Motors", "Software", "Materials",
    "Logistics", "Brands", "Ventures",
]


def browser1_rows() -> Iterator[list[object]]:
    rng = SplitMix64(20260819)
    for i in range(2000):
        slen = 2 + rng.below(3)
        symbol = "WA" if i == 123 else "".join(chr(65 + rng.below(26)) for _ in range(slen))
        company = f"{ADJ[rng.below(len(ADJ))]} {NOUN[rng.below(len(NOUN))]}"
        price = 2.0 + rng.uniform() * 998.0
        shares_out = 1_000_000.0 + rng.uniform() * 5_000_000_000.0
        sector = SECTORS[rng.below(len(SECTORS))]
        change = (rng.uniform() - 0.5) * 12.0
        volume = 10_000 + rng.below(50_000_000)
        market_cap = price * shares_out
        rsi = None if rng.below(37) == 0 else 15.0 + rng.uniform() * 70.0
        volatility = 5.0 + rng.uniform() * 75.0
        signal = SIGNALS[rng.below(len(SIGNALS))]
        score = rng.below(101)
        stamp = "2026-08-{:02}T{:02}:{:02}:{:02}Z".format(
            1 + rng.below(19), 9 + rng.below(8), rng.below(60), rng.below(60)
        )
        yield [symbol, company, sector, price, change, volume, market_cap, rsi,
               volatility, signal, score, stamp]


def browser2_rows(count: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        rng = SplitMix64(20260819)
        strategies = ["Momentum", "Mean Reversion", "Breakout", "Value", "Growth", "Income", "Pairs"]
        notes = [
            "Watch closely", "Earnings next week", "Upgrade pending", "Core holding",
            "Reduce on strength", "Add on weakness", "Under review", "High conviction",
            "Tactical position", "Hedge overlay", "Monitor liquidity", "Rebalance soon",
        ]
        for i in range(count):
            slen = 2 + rng.below(3)
            symbol = "WA" if i == 123 else "".join(chr(65 + rng.below(26)) for _ in range(slen))
            company = f"{ADJ[rng.below(len(ADJ))]} {NOUN[rng.below(len(NOUN))]}"
            price = 2.0 + rng.uniform() * 998.0
            entry = price * (0.6 + rng.uniform() * 0.7)
            age = rng.below(14)
            value = f32(rng.uniform())
            trend = []
            for _ in range(7):
                # Explicit binary32 at every Rust-f32 operation boundary.
                delta = f32(f32(f32(rng.uniform()) - f32(0.5)) * f32(0.3))
                value = min(f32(1.0), max(f32(0.0), f32(value + delta)))
                trend.append(value)
            sector = SECTORS[rng.below(len(SECTORS))]
            change = (rng.uniform() - 0.5) * 12.0
            volume = 10_000 + rng.below(50_000_000)
            rsi = None if rng.below(37) == 0 else 15.0 + rng.uniform() * 70.0
            signal = SIGNALS[rng.below(5)]
            score = rng.uniform()
            shares = rng.below(2_000_000)
            target = rng.uniform() * 20.0
            pl = (price - entry) / entry * 100.0
            enabled = rng.below(10) > 1
            strategy = strategies[rng.below(7)]
            listed = "20{:02}-{:02}-{:02}".format(10 + rng.below(16), 1 + rng.below(12), 1 + rng.below(28))
            stamp = "2026-08-{:02}T{:02}:{:02}:00Z".format(19 - age, 9 + rng.below(8), rng.below(60))
            note = notes[rng.below(len(notes))]
            yield [symbol, company, sector, price, change, volume, rsi, signal, score,
                   shares, entry, target, pl, enabled, strategy, listed, stamp, note, trend]
    return generate


B3_SYMBOLS = ["SPY", "QQQ", "IWM", "DIA", "AAPL", "MSFT", "NVDA", "XLE"]
B3_PARAMS = [
    (1.00, 0.004, False), (1.20, 0.007, True), (1.10, 0.008, False),
    (0.90, 0.005, False), (1.10, 0.010, True), (1.00, 0.008, True),
    (1.40, 0.014, True), (0.80, 0.011, False),
]


def browser3_data() -> tuple[list[list[float]], SplitMix64]:
    rng = SplitMix64(20260819)
    market = [0.0003 + 0.010 * rng.normal() for _ in range(250)]
    tech = [0.0002 + 0.008 * rng.normal() for _ in range(250)]
    returns = []
    for beta, idio, in_tech in B3_PARAMS:
        returns.append([
            beta * market[d] + (0.8 * tech[d] if in_tech else 0.0) + idio * rng.normal()
            for d in range(250)
        ])
    return returns, rng


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def covariance(a: Sequence[float], b: Sequence[float]) -> float:
    ma, mb = mean(a), mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (len(a) - 1)


def correlation(a: Sequence[float], b: Sequence[float]) -> float:
    value = covariance(a, b) / (math.sqrt(covariance(a, a)) * math.sqrt(covariance(b, b)))
    return max(-1.0, min(1.0, value))


def symmetric_matrix(returns: list[list[float]], function: Callable[[Sequence[float], Sequence[float]], float]) -> list[list[float]]:
    matrix = [[0.0] * 8 for _ in range(8)]
    for i in range(8):
        for j in range(i, 8):
            matrix[i][j] = matrix[j][i] = function(returns[i], returns[j])
    return matrix


def cluster_order(matrix: list[list[float]]) -> list[int]:
    children: list[tuple[int, int]] = []
    active = list(range(8))

    def members(node: int) -> list[int]:
        stack, out = [node], []
        while stack:
            current = stack.pop()
            if current < 8:
                out.append(current)
            else:
                left, right = children[current - 8]
                stack.extend([left, right])
        return out

    def distance(a: int, b: int) -> float:
        ma, mb = members(a), members(b)
        return sum(1.0 - matrix[i][j] for i in ma for j in mb) / (len(ma) * len(mb))

    while len(active) > 1:
        best = None
        for x in range(len(active)):
            for y in range(x + 1, len(active)):
                candidate = (distance(active[x], active[y]), x, y)
                if best is None or candidate[0] < best[0]:
                    best = candidate
        assert best is not None
        _, x, y = best
        children.append((active[x], active[y]))
        new_node = 8 + len(children) - 1
        active.pop(y)
        active.pop(x)
        active.append(new_node)
    return members(active[0])


def b3_artifact_rows(kind: str) -> Rows:
    def generate() -> Iterator[list[object]]:
        returns, rng = browser3_data()
        if kind == "returns":
            for day in range(250):
                yield [f"b3-{day:03d}", business_date(day)] + [returns[s][day] for s in range(8)]
        elif kind == "live":
            for event in range(16):
                market = 0.0003 + 0.010 * rng.normal()
                tech = 0.0002 + 0.008 * rng.normal()
                values = [beta * market + (0.8 * tech if in_tech else 0.0) + idio * rng.normal()
                          for beta, idio, in_tech in B3_PARAMS]
                yield [f"b3-live-{event:03d}", event, business_date(250 + event)] + values
        elif kind in ("correlation", "covariance", "beta"):
            if kind == "correlation":
                matrix = [[1.0 if i == j else 0.0 for j in range(8)] for i in range(8)]
                for i in range(8):
                    for j in range(i + 1, 8):
                        matrix[i][j] = matrix[j][i] = correlation(returns[i], returns[j])
            elif kind == "covariance":
                matrix = symmetric_matrix(returns, covariance)
            else:
                matrix = symmetric_matrix(returns, lambda a, b: covariance(a, b) / covariance(b, b))
            for i, symbol in enumerate(B3_SYMBOLS):
                yield [symbol] + matrix[i]
        elif kind == "volatility":
            for symbol, values in zip(B3_SYMBOLS, returns):
                yield [symbol, math.sqrt(covariance(values, values)) * math.sqrt(252.0)]
        elif kind == "clustering":
            matrix = [[1.0 if i == j else correlation(returns[i], returns[j]) for j in range(8)] for i in range(8)]
            for order, source in enumerate(cluster_order(matrix)):
                yield [order, B3_SYMBOLS[source], source]
        else:
            raise AssertionError(kind)
    return generate


def analytical_returns_data(days: int) -> tuple[list[float], list[float]]:
    rng = SplitMix64(20260819)
    benchmark = [0.0004 + 0.011 * rng.normal() for _ in range(days)]
    strategy = [0.85 * value + 0.0002 + 0.007 * rng.normal() for value in benchmark]
    return strategy, benchmark


def rolling_mean_value(values: Sequence[float], index: int, window: int) -> float | None:
    if index + 1 < window:
        return None
    return sum(values[index + 1 - window:index + 1]) / window


def analytical_core_rows(days: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        strategy, benchmark = analytical_returns_data(days)
        eq_s, eq_b, high_water = 100000.0, 100000.0, -math.inf
        rolling_sum = 0.0
        returns_pct = []
        for i, (s, b) in enumerate(zip(strategy, benchmark)):
            eq_s *= 1.0 + s
            eq_b *= 1.0 + b
            high_water = max(high_water, eq_s)
            pct = s * 100.0
            returns_pct.append(pct)
            rolling_sum += pct
            if i >= 20:
                rolling_sum -= returns_pct[i - 20]
            sma20 = rolling_sum / 20.0 if i >= 19 else None
            yield [i, business_date(i), eq_s, eq_b, high_water, (eq_s / high_water - 1.0) * 100.0, pct, sma20]
    return generate


def analytical_risk_at(strategy: list[float], benchmark: list[float], i: int) -> list[object]:
    if i < 59:
        return [i, business_date(i), None, None, None, None, None]
    a = strategy[i - 59:i + 1]
    b = benchmark[i - 59:i + 1]
    ma, mb = mean(a), mean(b)
    variance = sum((x - ma) ** 2 for x in a) / 59.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    bench_var = sum((y - mb) ** 2 for y in b)
    ordered = sorted(a)
    var95 = ordered[int(59 * 0.05)] * 100.0
    es95 = sum(ordered[:math.ceil(60 * 0.05)]) / math.ceil(60 * 0.05) * 100.0
    differences = [x - y for x, y in zip(a, b)]
    md = mean(differences)
    te = math.sqrt(sum((x - md) ** 2 for x in differences) / 59.0) * math.sqrt(252.0) * 100.0
    beta = cov / bench_var if bench_var > 0.0 else None
    return [i, business_date(i), math.sqrt(variance) * math.sqrt(252.0) * 100.0,
            var95, es95, beta, te]


def analytical_risk_rows(days: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        strategy, benchmark = analytical_returns_data(days)
        indices = sorted(set([0, 18, 19, 58, 59, 60, days // 2, days - 1]))
        for i in indices:
            yield analytical_risk_at(strategy, benchmark, i)
    return generate


def analytical_source_rows(days: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        strategy, benchmark = analytical_returns_data(days)
        for i in range(days):
            yield [i, business_date(i), benchmark[i], strategy[i]]
    return generate


def analytical_static_rows(kind: str) -> Rows:
    def generate() -> Iterator[list[object]]:
        if kind == "features":
            values = [
                ("Momentum 12-1", 0.42), ("Value (B/P)", 0.31), ("Quality (ROE)", 0.27),
                ("Low Volatility", 0.19), ("Size", -0.08), ("Short-term Reversal", 0.15),
                ("Dividend Yield", 0.09), ("Growth (SGR)", -0.14), ("Liquidity", 0.05),
                ("Sentiment", -0.03),
            ]
            for rank, (name, value) in enumerate(sorted(values, key=lambda item: -item[1])):
                yield [rank, name, value]
        elif kind in ("optimization", "optimization-live"):
            rng = SplitMix64(20260819 ^ 0xBEEF)
            objective = []
            count = 240 if kind == "optimization" else 288
            for i in range(count):
                value = 1.83 + 1.4 * math.exp(-i / 45.0) + 0.09 * rng.normal()
                objective.append(value)
                if kind == "optimization" or i >= 240:
                    yield [i, value, max(objective)]
        elif kind == "accuracy":
            rng = SplitMix64(20260819 ^ 0xACC)
            metrics = []
            for base, drift in [(0.68, 0.008), (0.65, 0.009), (0.61, 0.011), (0.63, 0.010)]:
                metrics.append([max(0.5, min(0.99, base + drift * i + 0.02 * rng.normal())) * 100.0
                                for i in range(12)])
            for i in range(12):
                yield [i + 1] + [metric[i] for metric in metrics]
            # The confusion matrix is a separate artifact to keep this table rectangular.
        elif kind == "confusion":
            # Advance through all four metric streams exactly as the Slint reference does.
            rng = SplitMix64(20260819 ^ 0xACC)
            for base, drift in [(0.68, 0.008), (0.65, 0.009), (0.61, 0.011), (0.63, 0.010)]:
                for i in range(12):
                    max(0.5, min(0.99, base + drift * i + 0.02 * rng.normal()))
            for actual in range(3):
                row = []
                for predicted in range(3):
                    row.append(800 + rng.below(400) if actual == predicted else rng.below(160))
                yield [actual] + row
        elif kind == "attribution":
            rng = SplitMix64(20260819 ^ 0xA7718)
            for month in range(12):
                yield [month + 1] + [((rng.uniform() - 0.42) * 3.0) / (group + 1.5) for group in range(5)]
        elif kind == "correlation":
            returns, _ = browser3_data()
            a, b = returns[0], returns[1]
            for i in range(250):
                value = correlation(a[i - 59:i + 1], b[i - 59:i + 1]) if i >= 59 else None
                yield [i, business_date(i), value]
        else:
            raise AssertionError(kind)
    return generate


def stock_bars(kind: str, count: int) -> tuple[list[list[object]], SplitMix64]:
    seed = 20260820 if kind == "daily" else 20260821
    rng = SplitMix64(seed)
    price = 100.0
    bars: list[list[object]] = []
    for i in range(count):
        if kind == "daily":
            regime = math.sin(i / 250.0) * 0.0009
            drift = 0.00015 + regime
            vol = 0.008 + 0.005 * abs(math.cos(i / 97.0))
            volume_scale = 8.0e6
        else:
            regime = math.sin(i / (250.0 * 390.0)) * 0.0009
            drift = 0.00015 / 390.0 + regime / 390.0
            vol = (0.008 + 0.005 * abs(math.cos(i / (97.0 * 390.0)))) / math.sqrt(390.0)
            volume_scale = 8.0e6 / 390.0
        r = drift + vol * rng.normal()
        open_ = price
        close = max(1.0, open_ * (1.0 + r))
        spread = vol * open_ * (0.3 + 0.7 * rng.uniform())
        high = max(open_, close) + spread * rng.uniform()
        low = max(0.5, min(open_, close) - spread * rng.uniform())
        volume = volume_scale * (1.0 + 2.5 * abs(r) / max(vol, 1e-9)) * (0.6 + 0.8 * rng.uniform())
        price = close
        identity = f"ACME-{kind}-{i:06d}"
        if kind == "daily":
            bars.append([identity, business_date(i), open_, high, low, close, volume])
        else:
            session, timestamp, minute = intraday_timestamp(i)
            bars.append([identity, session, timestamp, minute, open_, high, low, close, volume])
    return bars, rng


def stock_next_bar(previous: list[object], rng: SplitMix64, kind: str) -> list[float]:
    close_index = 5 if kind == "daily" else 7
    open_ = max(1.0, float(previous[close_index]))
    scale = 1.0 if kind == "daily" else 1.0 / math.sqrt(390.0)
    drift = 0.0002 if kind == "daily" else 0.0002 / 390.0
    r = drift + 0.009 * scale * rng.normal()
    close = max(1.0, open_ * (1.0 + r))
    spread = 0.009 * scale * open_ * (0.3 + 0.7 * rng.uniform())
    high = max(open_, close) + spread * rng.uniform()
    low = max(0.5, min(open_, close) - spread * rng.uniform())
    volume = (8.0e6 if kind == "daily" else 8.0e6 / 390.0) * (0.6 + 0.8 * rng.uniform())
    return [open_, high, low, close, volume]


def ema(values: Sequence[float], window: int) -> list[float | None]:
    k = 2.0 / (window + 1.0)
    state = None
    seed = 0.0
    out = []
    for i, value in enumerate(values):
        if state is None:
            seed += value
            if i + 1 == window:
                state = seed / window
        else:
            state = value * k + state * (1.0 - k)
        out.append(state)
    return out


def stock_indicators(bars: list[list[object]], kind: str) -> list[list[object]]:
    offset = 2 if kind == "daily" else 4
    close = [float(row[offset + 3]) for row in bars]
    high = [float(row[offset + 1]) for row in bars]
    low = [float(row[offset + 2]) for row in bars]
    volume = [float(row[offset + 4]) for row in bars]
    n = len(bars)
    sma20: list[float | None] = [None] * n
    boll_u: list[float | None] = [None] * n
    boll_l: list[float | None] = [None] * n
    running = 0.0
    for i, value in enumerate(close):
        running += value
        if i >= 20:
            running -= close[i - 20]
        if i >= 19:
            mid = running / 20.0
            window = close[i - 19:i + 1]
            variance = sum((x - mid) ** 2 for x in window) / 20.0
            deviation = math.sqrt(max(0.0, variance))
            sma20[i], boll_u[i], boll_l[i] = mid, mid + 2.0 * deviation, mid - 2.0 * deviation
    ema20 = ema(close, 20)
    e12, e26 = ema(close, 12), ema(close, 26)
    macd_line = [None if e12[i] is None or e26[i] is None else e12[i] - e26[i] for i in range(n)]
    valid_line = [value for value in macd_line if value is not None]
    valid_signal = ema(valid_line, 9)
    macd_signal: list[float | None] = [None] * n
    for i in range(25, n):
        macd_signal[i] = valid_signal[i - 25]
    rsi: list[float | None] = [None] * n
    avg_gain = avg_loss = 0.0
    for i in range(1, n):
        change = close[i] - close[i - 1]
        gain, loss = max(0.0, change), max(0.0, -change)
        if i <= 14:
            avg_gain += gain
            avg_loss += loss
            if i == 14:
                avg_gain /= 14.0
                avg_loss /= 14.0
            else:
                continue
        else:
            avg_gain = (avg_gain * 13.0 + gain) / 14.0
            avg_loss = (avg_loss * 13.0 + loss) / 14.0
        if avg_loss == 0.0:
            rsi[i] = 50.0 if avg_gain == 0.0 else 100.0
        else:
            rsi[i] = 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
    atr: list[float | None] = [None] * n
    atr_state = None
    tr_sum = 0.0
    for i in range(1, n):
        tr = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        if atr_state is None:
            tr_sum += tr
            if i == 14:
                atr_state = tr_sum / 14.0
        else:
            atr_state = (atr_state * 13.0 + tr) / 14.0
        atr[i] = atr_state
    out = []
    pv = vv = 0.0
    current_session = None
    for i, bar in enumerate(bars):
        session = bar[1]
        if session != current_session:
            current_session = session
            pv = vv = 0.0
        typical = (high[i] + low[i] + close[i]) / 3.0
        pv += typical * volume[i]
        vv += volume[i]
        signal = macd_signal[i]
        histogram = None if macd_line[i] is None or signal is None else macd_line[i] - signal
        out.append([bar[0], sma20[i], ema20[i], sma20[i], boll_u[i], boll_l[i],
                    pv / vv if vv > 0.0 else None, rsi[i], atr[i], macd_line[i], signal, histogram])
    return out


def stock_indicator_rows(kind: str, count: int) -> Rows:
    return lambda: iter(stock_indicators(stock_bars(kind, count)[0], kind))


def stock_live_rows(kind: str, count: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        bars, rng = stock_bars(kind, count)
        previous = bars[-1]
        for event in range(16):
            values = stock_next_bar(previous, rng, kind)
            index = count + event
            identity = f"ACME-{kind}-live-{event:03d}"
            if kind == "daily":
                row: list[object] = [identity, event, business_date(index)] + values
            else:
                session, timestamp, minute = intraday_timestamp(index)
                row = [identity, event, session, timestamp, minute] + values
            yield row
            # Only the close position is consumed by stock_next_bar; set it explicitly.
            if kind == "daily":
                previous = [identity, business_date(index), *values]
            else:
                previous = [identity, session, timestamp, minute, *values]
    return generate


def stock_event_rows(kind: str, count: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        bars, _ = stock_bars(kind, count)
        close_index = 5 if kind == "daily" else 7
        close = [float(row[close_index]) for row in bars]
        fast = [rolling_mean_value(close, i, 20) for i in range(count)]
        slow = [rolling_mean_value(close, i, 50) for i in range(count)]
        records = []
        for i in range(1, count):
            if None not in (fast[i - 1], fast[i], slow[i - 1], slow[i]):
                buy = fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]
                sell = fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]
                if buy or sell:
                    strength = max(0.25, min(1.0, abs(fast[i] - slow[i]) / slow[i] * 40.0))
                    records.append([i, "signal", "buy" if buy else "sell", "SMA20/SMA50 crossover", strength])
        for name, a, b, confidence in [
            ("Ascending triangle", 0.10, 0.20, 0.72), ("Bull flag", 0.34, 0.40, 0.64),
            ("Head & shoulders", 0.55, 0.70, 0.58), ("Double bottom", 0.82, 0.92, 0.77),
        ]:
            records.append([int(count * a), "pattern-start", name, "Fixed demonstration region", confidence])
            records.append([min(count - 1, int(count * b)), "pattern-end", name, "Fixed demonstration region", confidence])
        i = 40
        while i < count:
            records.append([i, "event", "earnings", f"Earnings: EPS beat +{2.0 + i % 7:.1f}%", None])
            i += 63
        i = 20
        while i < count:
            records.append([i, "event", "dividend", f"Dividend ${0.35 + i % 5 * 0.05:.2f}/share", None])
            i += 63
        records.append([count * 3 // 5, "event", "split", "2-for-1 stock split", None])
        rng = SplitMix64((20260820 if kind == "daily" else 20260821) ^ 0xE7E7)
        for _ in range(max(2, count // 200)):
            index = int(rng.uniform() * count)
            records.append([index, "event", "news", f"Macro: CPI print moves market (bar {index})", None])
        records.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
        for sequence, record in enumerate(records):
            yield [f"ACME-{kind}-marker-{sequence:05d}", *record]
    return generate


PIVOT_SYMBOLS = ["SPY", "SPX", "QQQ", "MINT", "IEF", "TLT", "AAPL", "MSFT", "NVDA"]


def pivot_series(symbol: int) -> list[list[object]]:
    rng = SplitMix64(20260821 + symbol * 7919)
    price = 40.0 + 30.0 * (symbol % 5)
    drift = 0.0001 + 0.00006 * (symbol % 4)
    base_vol = 0.006 + 0.002 * (symbol % 3)
    bars = []
    for i in range(1500):
        regime = math.sin(i / 220.0 + symbol) * 0.0008
        vol = base_vol + 0.004 * abs(math.cos(i / 83.0))
        r = drift + regime + vol * rng.normal()
        open_ = price
        close = price * (1.0 + r)
        high = max(open_, close) * (1.0 + vol * rng.uniform() * 0.6)
        low = min(open_, close) * (1.0 - vol * rng.uniform() * 0.6)
        volume = (2.0 + 30.0 * abs(r) / vol) * (0.6 + 0.8 * rng.uniform()) * 1e6
        price = close
        bars.append([f"{PIVOT_SYMBOLS[symbol]}-{i:04d}", business_date(i), open_, high, low, close, volume])
    return bars


def pivot_aggregate(bars: list[list[object]], interval: str) -> list[list[object]]:
    groups: list[list[tuple[int, list[object]]]] = []
    last_key = None
    for i, bar in enumerate(bars):
        date = dt.date.fromisoformat(str(bar[1]))
        key = i // 5 if interval == "weekly" else (date.year, date.month) if interval == "monthly" else i
        if key != last_key:
            groups.append([])
            last_key = key
        groups[-1].append((i, bar))
    out = []
    for group in groups:
        first_index, first = group[0]
        last_index, last = group[-1]
        key = first_index // 5 if interval == "weekly" else str(first[1])[:7]
        out.append([str(key), first[1], last[1], first_index, last_index, first[2],
                    max(float(bar[3]) for _, bar in group), min(float(bar[4]) for _, bar in group),
                    last[5], sum(float(bar[6]) for _, bar in group)])
    return out


def pivot_oracles(bars: list[list[object]], period: int = 3) -> tuple[list[list[object]], list[list[object]]]:
    n = len(bars)
    candidate_hi: list[float | None] = [None] * n
    candidate_lo: list[float | None] = [None] * n
    accepted_hi: list[float | None] = [None] * n
    accepted_lo: list[float | None] = [None] * n
    for i in range(n):
        if i + period >= n:
            continue
        indices = [j for j in range(max(0, i - period), i + period + 1) if j != i]
        if all(float(bars[i][3]) > float(bars[j][3]) for j in indices):
            candidate_hi[i] = float(bars[i][3])
        if all(float(bars[i][4]) < float(bars[j][4]) for j in indices):
            candidate_lo[i] = float(bars[i][4])
    last_hi = last_lo = None
    swings = []
    for i in range(n):
        if candidate_hi[i] is not None and (last_hi is None or abs(candidate_hi[i] - last_hi) >= 0.0):
            accepted_hi[i] = candidate_hi[i]
            last_hi = candidate_hi[i]
            swings.append([i, i + period, candidate_hi[i], True])
        if candidate_lo[i] is not None and (last_lo is None or abs(candidate_lo[i] - last_lo) >= 0.0):
            accepted_lo[i] = candidate_lo[i]
            last_lo = candidate_lo[i]
            swings.append([i, i + period, candidate_lo[i], False])
    upper: list[float | None] = [None] * n
    lower: list[float | None] = [None] * n
    for target, accepted in [(upper, accepted_hi), (lower, accepted_lo)]:
        value = None
        confirmation_for = {i + period: accepted[i] for i in range(n) if accepted[i] is not None}
        for i in range(n):
            if i in confirmation_for:
                value = confirmation_for[i]
            target[i] = value
    zigzag = []
    for swing in swings:
        if zigzag and zigzag[-1][3] == swing[3]:
            better = swing[2] > zigzag[-1][2] if swing[3] else swing[2] < zigzag[-1][2]
            if better:
                zigzag[-1] = swing
        else:
            zigzag.append(swing)
    rows = []
    for i, bar in enumerate(bars):
        rows.append([bar[0], i, bar[1], candidate_hi[i], candidate_lo[i], accepted_hi[i], accepted_lo[i],
                     i + period if accepted_hi[i] is not None else None,
                     i + period if accepted_lo[i] is not None else None, upper[i], lower[i]])
    zig_rows = [[sequence, *swing] for sequence, swing in enumerate(zigzag)]
    return rows, zig_rows


def pivot_rows(kind: str) -> Rows:
    def generate() -> Iterator[list[object]]:
        for source, symbol in enumerate(PIVOT_SYMBOLS):
            bars = pivot_series(source)
            if kind == "daily":
                for bar in bars:
                    yield [symbol, *bar]
            elif kind in ("weekly", "monthly"):
                for aggregate in pivot_aggregate(bars, kind):
                    yield [symbol, *aggregate]
            else:
                oracle, zigzag = pivot_oracles(bars)
                selected = oracle if kind == "pivots" else zigzag
                for row in selected:
                    yield [symbol, *row]
    return generate


def volatility_rows(n: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        moneyness = [0.7 + 0.6 * i / max(1, n - 1) for i in range(n)]
        maturity = [0.05 + 1.95 * (i / max(1, n - 1)) ** 2 for i in range(n)]
        for t in range(n):
            for k in range(n):
                m, tau = moneyness[k], maturity[t]
                values = []
                for stress in (0.0, 1.0):
                    base = 0.18 + stress * 0.16
                    skew = (0.10 + stress * 0.12) * (1.0 - m)
                    smile = 0.35 * (m - 1.0) ** 2
                    term = 0.03 * (tau - 0.6) + 0.02 * math.sin(tau * 8.0) * 0.2
                    wobble = 0.004 * math.sin(k * 1.7 + t * 2.3)
                    values.append(max(0.02, base + skew / max(0.3, math.sqrt(tau)) + smile + term + wobble))
                yield [t, k, m, tau, values[0], values[1]]
    return generate


FACTOR_SECTORS = ["Technology", "Health", "Financials", "Energy", "Consumer", "Industrials"]


def factor_rows(n: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        rng = SplitMix64(20260822)
        for i in range(n):
            sector = i % 6
            tilt = sector - 2.5
            beta = max(0.05, 1.0 + 0.12 * tilt * 0.3 + 0.35 * rng.normal())
            value = 0.15 * tilt + 0.6 * rng.normal()
            momentum = -0.08 * tilt + 0.7 * rng.normal()
            cap = 20.0 * math.exp(rng.uniform() * 6.0)
            yield [f"S{i + 1:03d}", sector, FACTOR_SECTORS[sector], beta, value, momentum, cap]
    return generate


def frontier_data() -> tuple[list[list[float]], list[list[object]], list[list[object]], list[list[object]]]:
    rng = SplitMix64(20260825)
    mu = [0.03 + 0.012 * i + 0.01 * rng.uniform() for i in range(12)]
    vol = [0.09 + 0.013 * i + 0.02 * rng.uniform() for i in range(12)]
    assets = [[f"A{i:02d}", mu[i], vol[i]] for i in range(12)]
    portfolios = []
    cloud = []
    for p in range(2500):
        weights = [-math.log(max(1e-9, rng.uniform())) for _ in range(12)]
        total = sum(weights)
        expected = sum(w * m for w, m in zip(weights, mu)) / total
        risk = math.sqrt(sum(w * w * v * v for w, v in zip(weights, vol))) / total
        portfolios.append([f"portfolio-{p:04d}", risk, expected, weights])
        cloud.append((risk, expected))
    vlo = min(p[0] for p in cloud)
    vhi = max(p[0] for p in cloud)
    envelope = []
    for b in range(40):
        lo = vlo + (vhi - vlo) * b / 40.0
        hi = vlo + (vhi - vlo) * (b + 1) / 40.0
        candidates = [(i, p) for i, p in enumerate(cloud) if p[0] >= lo and p[0] < hi]
        if candidates:
            index, point = max(candidates, key=lambda item: item[1][1])
            envelope.append([b, lo, hi, f"portfolio-{index:04d}", point[0], point[1]])
        else:
            envelope.append([b, lo, hi, None, None, None])
    min_index = min(range(2500), key=lambda i: cloud[i][0])
    sharpe_index = max(range(2500), key=lambda i: (cloud[i][1] - 0.02) / cloud[i][0])
    special = [
        ["minimum-variance", f"portfolio-{min_index:04d}", cloud[min_index][0], cloud[min_index][1], (cloud[min_index][1] - 0.02) / cloud[min_index][0]],
        ["maximum-sharpe", f"portfolio-{sharpe_index:04d}", cloud[sharpe_index][0], cloud[sharpe_index][1], (cloud[sharpe_index][1] - 0.02) / cloud[sharpe_index][0]],
        ["current", None, 0.14, 0.065, (0.065 - 0.02) / 0.14],
    ]
    return assets, portfolios, envelope, special


def frontier_rows(kind: str) -> Rows:
    return lambda: iter(frontier_data()[{"assets": 0, "portfolios": 1, "envelope": 2, "special": 3}[kind]])


def pca_rows() -> Iterator[list[object]]:
    rng = SplitMix64(20260829)
    for i in range(500):
        sector = i % 6
        t = float(sector)
        yield [f"P{i + 1:03d}", sector, FACTOR_SECTORS[sector],
               0.9 * rng.normal() + 0.5 * (t - 2.5),
               0.7 * rng.normal() + 0.4 * math.sin(t * 2.1),
               0.5 * rng.normal() + 0.3 * math.cos(t * 1.3)]


REGIME_NAMES = ["Bull / Low Vol", "Bull / High Vol", "Bear / Low Vol", "Bear / High Vol", "Transitional"]


def regime_rows() -> Iterator[list[object]]:
    rng = SplitMix64(20260835)
    trend, vol = 0.4, 0.35
    for i in range(400):
        trend = max(-1.0, min(1.0, trend * 0.985 + 0.05 * rng.normal()))
        vol = max(0.05, min(1.0, vol * 0.99 + 0.01 * 0.35 + 0.03 * abs(rng.normal())))
        if abs(trend) < 0.25:
            regime = 4
        elif trend > 0.0:
            regime = 0 if vol < 0.5 else 1
        else:
            regime = 2 if vol < 0.5 else 3
        yield [f"regime-{i:03d}", i, trend, vol, regime, REGIME_NAMES[regime]]


def projection_rows(method: int) -> Rows:
    def generate() -> Iterator[list[object]]:
        rng = SplitMix64(20260851)
        centers = [(math.cos(i * 2.0 * math.pi / 5), math.sin(i * 2.0 * math.pi / 5)) for i in range(5)]
        for i in range(5000):
            category = rng.below(5)
            cx, cy = centers[category]
            sx, sy = 0.22 * rng.normal(), 0.22 * rng.normal()
            if method == 0:
                x, y = 0.55 * cx + 1.1 * sx + 0.5 * sy, 0.55 * cy + 0.4 * sx + 0.7 * sy
                name = "PCA-like"
            elif method == 1:
                x, y = 0.85 * cx + 0.16 * sx, 0.85 * cy + 0.16 * sy
                name = "t-SNE-like"
            else:
                bend = 0.3 * math.sin(cx * 2.0)
                x, y = 0.75 * cx + 0.2 * sx, 0.75 * cy + bend + 0.2 * sy
                name = "UMAP-like"
            yield [f"projection-{i:04d}", name, x, y, category]
    return generate


def network_data(n_nodes: int, n_edges: int) -> tuple[list[list[object]], list[list[object]]]:
    rng = SplitMix64(20260859)
    n_sym = max(1, n_nodes - 8)
    nodes = []
    initial = []
    for i in range(n_nodes):
        if i < n_sym:
            label, kind = f"S{i + 1:02d}", 0
        elif i < n_sym + 6:
            label, kind = FACTOR_SECTORS[i - n_sym], 1
        else:
            label, kind = ["Beta", "Momentum"][i - n_sym - 6], 2
        x, y = 1.6 * (rng.uniform() - 0.5), 1.6 * (rng.uniform() - 0.5)
        nodes.append([f"node-{i:04d}", label, kind, x, y])
        initial.append([x, y])
    edges = []
    for i in range(n_sym):
        edges.append([i, n_sym + i % 6, 0.5 + 0.5 * rng.uniform()])
        edges.append([i, n_sym + 6 + i % 2, 0.3 + 0.6 * rng.uniform()])
        if i % 2 == 0:
            edges.append([i, (i + 5) % n_sym, 0.2 + 0.7 * rng.uniform()])
    while len(edges) < n_edges:
        a, b = rng.below(n_sym), rng.below(n_sym)
        if a != b:
            edges.append([a, b, 0.2 + 0.7 * rng.uniform()])
    edges = edges[:max(n_edges, 2 * n_sym)]
    iterations = 40 if n_nodes > 200 else 120
    k = math.sqrt(2.4 / n_nodes)
    for iteration in range(iterations):
        temp = 0.06 * (1.0 - iteration / iterations)
        disp = [[0.0, 0.0] for _ in range(n_nodes)]
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                dx, dy = float(nodes[i][3]) - float(nodes[j][3]), float(nodes[i][4]) - float(nodes[j][4])
                distance = max(0.01, math.sqrt(dx * dx + dy * dy))
                force = k * k / distance
                dx, dy = dx * force / distance, dy * force / distance
                disp[i][0] += dx
                disp[i][1] += dy
                disp[j][0] -= dx
                disp[j][1] -= dy
        for a, b, weight in edges:
            dx, dy = float(nodes[a][3]) - float(nodes[b][3]), float(nodes[a][4]) - float(nodes[b][4])
            distance = max(0.01, math.sqrt(dx * dx + dy * dy))
            force = distance * distance / k * (0.4 + 0.6 * weight)
            disp[a][0] -= dx / distance * force * 0.02
            disp[a][1] -= dy / distance * force * 0.02
            disp[b][0] += dx / distance * force * 0.02
            disp[b][1] += dy / distance * force * 0.02
        for i, node in enumerate(nodes):
            length = max(1e-9, math.sqrt(disp[i][0] ** 2 + disp[i][1] ** 2))
            node[3] = max(-1.0, min(1.0, float(node[3]) + disp[i][0] / length * min(temp, length)))
            node[4] = max(-1.0, min(1.0, float(node[4]) + disp[i][1] / length * min(temp, length)))
    node_rows = [[*node, initial[i][0], initial[i][1], iterations] for i, node in enumerate(nodes)]
    edge_rows = [[f"edge-{i:04d}", f"node-{a:04d}", f"node-{b:04d}", weight]
                 for i, (a, b, weight) in enumerate(edges)]
    return node_rows, edge_rows


def network_rows(n: int, edges: int, kind: str) -> Rows:
    return lambda: iter(network_data(n, edges)[0 if kind == "nodes" else 1])


def knowledge_data() -> tuple[list[list[object]], list[list[object]]]:
    nodes = []
    edges = []
    rng = SplitMix64(20260873)

    def add(label: str, kind: str, parent: int | None) -> int:
        index = len(nodes)
        nodes.append([f"kg-{index:02d}", label, kind, f"kg-{parent:02d}" if parent is not None else None,
                      parent is None, 0.0, 0.0])
        return index

    for company_index in range(3):
        company = add(["Acme Corp", "Globex", "Initech"][company_index], "Company", None)
        sector = add(["Technology", "Energy", "Finance"][company_index], "Sector", company)
        executive = add(["CEO A. Doe", "CEO B. Smith", "CEO C. Ray"][company_index], "Executive", company)
        edges.append([company, sector, "BELONGS_TO"])
        edges.append([executive, company, "ISSUED_BY"])
        for security_index in range(2):
            security = add(f"{['ACM', 'GLX', 'INT'][company_index]}{security_index + 1} Equity", "Security", company)
            edges.append([security, company, "ISSUED_BY"])
            indicator = add(f"Vol{security_index + 1}", "Indicator", security)
            edges.append([security, indicator, "DERIVED_FROM"])
        event = add(f"Earnings Q{company_index + 1}", "Event", company)
        edges.append([company, event, "AFFECTED_BY"])
    edges.append([0, 8, "CORRELATED_WITH"])
    for i, node in enumerate(nodes):
        parent = nodes[i][3]
        depth = 0 if parent is None else 1
        if parent is not None:
            parent_index = int(parent.split("-")[1])
            if nodes[parent_index][3] is not None:
                depth = 2
        angle = i * 2.399 + rng.uniform() * 0.2
        radius = 0.25 + 0.3 * depth
        node[5], node[6] = radius * math.cos(angle), radius * math.sin(angle)
    edge_rows = [[f"kg-edge-{i:02d}", f"kg-{a:02d}", f"kg-{b:02d}", relation]
                 for i, (a, b, relation) in enumerate(edges)]
    return nodes, edge_rows


def knowledge_rows(kind: str) -> Rows:
    return lambda: iter(knowledge_data()[0 if kind == "nodes" else 1])


def monte_carlo_paths() -> list[list[float]]:
    rng = SplitMix64(20260913)
    paths = []
    for _ in range(600):
        value = 1.0
        path = []
        for _ in range(120):
            value *= 1.0 + 0.001 + 0.02 * rng.normal()
            path.append(value)
        paths.append(path)
    return paths


def monte_carlo_rows(kind: str) -> Rows:
    def generate() -> Iterator[list[object]]:
        paths = monte_carlo_paths()
        if kind == "paths":
            for i, path in enumerate(paths):
                for step, value in enumerate(path):
                    yield [f"path-{i:03d}", i, step, value]
        elif kind == "bands":
            for step in range(120):
                ordered = sorted(path[step] for path in paths)
                yield [step] + [ordered[p * (len(ordered) - 1) // 100] for p in (5, 50, 95)]
        else:
            terminal = [path[-1] for path in paths]
            low, high = min(terminal), max(terminal)
            counts = [0] * 40
            for value in terminal:
                bucket = int((value - low) / max(1e-9, high - low) * 40)
                counts[min(39, bucket)] += 1
            for bucket, count in enumerate(counts):
                lo = low + (high - low) * bucket / 40.0
                hi = low + (high - low) * (bucket + 1) / 40.0
                yield [bucket, lo, hi, count]
    return generate


def order_book_events(count: int = 1032) -> list[list[object]]:
    rng = SplitMix64(20260899)
    mid = 100.0
    events = []
    for tick in range(count):
        mid *= 1.0 + 0.0012 * rng.normal()
        base = mid - 200 / 2.0 * 0.05
        sizes = []
        for level in range(200):
            price = base + level * 0.05
            distance = abs(price - mid) / 0.05
            depth = 60.0 / (1.0 + distance * distance * 0.02) * (0.4 + rng.uniform())
            size = depth if price < mid else -depth
            sizes.append(0.0 if rng.uniform() < 0.06 else size)
        touch = int((mid - base) / 0.05)
        trades = []
        for _ in range(2):
            level = max(0, min(199, touch + rng.below(7) - 3))
            trades.append(level)
        events.append([f"order-event-{tick:04d}", tick, base, mid, mid - 0.025, mid + 0.025, sizes, trades])
    return events


def order_book_rows(kind: str) -> Rows:
    def generate() -> Iterator[list[object]]:
        events = order_book_events()
        if kind == "book":
            for event in events[:1000]:
                yield [event[0], event[1], event[2], event[3], event[6]]
        elif kind == "events":
            for event in events:
                yield [event[0], event[1], event[3], event[4], event[5], event[7]]
        else:
            # Long-form level rows are convenient for adapters that cannot consume nested arrays.
            for event in events[:1000]:
                for level, size in enumerate(event[6]):
                    yield [event[0], event[1], level, float(event[2]) + level * 0.05, size]
    return generate


def artifact(id_: str, spec: str, rows: Rows, description: str, samples: tuple[int, ...] = (0, -1)) -> Artifact:
    return Artifact(id_, spec, rows, description, samples)


def family_manifest(family: Family, computed: dict[tuple[str, str], dict[str, object]]) -> dict[str, object]:
    rng = None
    if family.seed is not None:
        rng = dict(RNG_COMMON)
        rng["seed"] = family.seed
        rng["draw_order"] = family.draw_order
    variants = []
    for variant in family.variants:
        artifacts = []
        for spec in variant.artifacts:
            result = computed[(variant.id, spec.id)]
            artifacts.append({
                "id": spec.id,
                "description": spec.description,
                "row_count": result["row_count"],
                "columns": cols(spec.column_spec),
                "golden_samples": result["golden_samples"],
                "sha256": result["sha256"],
            })
        variants.append({"id": variant.id, "selection": variant.selection,
                         "dimensions": variant.dimensions, "artifacts": artifacts})
    return {
        "schema_version": SCHEMA_VERSION,
        "id": family.id,
        "revision": 1,
        "title": family.title,
        "classification": family.classification,
        "generator": {"name": GENERATOR_NAME, "revision": GENERATOR_REVISION},
        "entity_identity": {"rule": family.identity, "ordering": family.ordering},
        "rng": rng,
        "normalization": NORMALIZATION,
        "numeric_oracle": NUMERIC_ORACLE,
        "formulas": family.formulas,
        "variants": variants,
        "extensions": family.extensions,
        "separation_notes": family.separation_notes,
        "references": family.references,
    }


def build_families() -> list[Family]:
    b1_columns = "symbol:string,company:string,sector:string,price:number,change_pct:number,volume:integer,market_cap:number,rsi:number?,volatility:number,signal:string,score:integer,last_update:datetime"
    b2_columns = "symbol:string,company:string,sector:string,price:number,change_pct:number,volume:integer,rsi:number?,signal:string,score:number,shares:integer,entry_price:number,target_weight_pct:number,pl_pct:number,enabled:boolean,strategy:string,listed:date,last_update:datetime,notes:string,trend:number[]"
    b3_values = ",".join(symbol.lower() + ":number" for symbol in B3_SYMBOLS)
    b3_matrix = "symbol:string," + b3_values
    families = [
        Family("browser1", "Browser 1 standard financial grid", "rendering", "20260819", [
            "Per source row: symbol-length below(3); symbol letters (none for WA at 123); adjective; noun; price uniform; shares-out uniform; sector; change uniform; volume below; RSI missing below(37) then value uniform when present; volatility; signal; score; day/hour/minute/second below draws in that order."
        ], {
            "generation": "price=2+998*u; shares_out=1e6+5e9*u; change_pct=12*(u-0.5); volume=10000+below(50000000); market_cap=price*shares_out; RSI=null when below(37)=0 else 15+70*u; volatility=5+75*u; score=below(101).",
            "display_columns": "symbol,company,sector,price,change_pct,volume,market_cap,rsi,volatility,signal,score,last_update (labels and widths 90,220,140,100,100,120,130,80,110,110,90,170).",
            "identity_sort": "Stable ID is b1-{source_ordinal:06d}; WA is b1-000123. Typed sort ties use ascending source ordinal. Null RSI sorts last in both directions; apply direction only to present values.",
            "special": "The symbol at zero-based source ordinal 123 is WA; the symbol-length draw still occurs and symbol-letter draws are skipped.",
        }, [Variant("2000x12", "default", {"rows": 2000, "columns": 12, "wa_source_ordinal": 123},
                    [artifact("browser1.rows.2000", b1_columns, browser1_rows, "Two thousand rows in source order; stable ID derives from row selector.", (0, 123, -1))])],
            identity="Stable ID b1-{source_ordinal:06d} is derived from the zero-based row selector and is not an extra displayed column."),
        Family("browser2", "Browser 2 advanced editable grid", "rendering", "20260819", [
            "Per source row: symbol length/letters; adjective/noun; price; entry-price uniform; age below; initial trend uniform then seven (uniform, binary32 update) pairs; sector; change; volume; nullable RSI; signal; score; shares; target weight; enabled; strategy; listed year/month/day; update hour/minute; notes."
        ], {
            "generation": "Matches the Slint field formulas and order. entry=price*(0.6+0.7*u); target_weight_pct=20*u; pl_pct=100*(price-entry)/entry; enabled=below(10)>1; score is [0,1).",
            "trend": "Seven values use explicit IEEE binary32 after each conversion/add/multiply/clamp: v=clamp(v+(f32(u)-0.5)*0.3,0,1), then serialize as binary64 fixed9.",
            "identity_edit": "Stable ID b2-{source_ordinal:06d} is the zero-based source row. Target Weight is editable only when enabled=true. Variants share prefixes and IDs.",
            "activation": "100000 rows are on-demand only and MUST NOT be constructed by default/startup. Switching size drops incompatible display mappings and preserves only valid common source IDs.",
        }, [Variant(f"{n}x19", "default" if n == 1000 else "on-demand", {"rows": n, "columns": 19},
                    [artifact(f"browser2.rows.{n}", b2_columns, browser2_rows(n), "Editable 19-column rows; nested trend has exactly seven binary32 values.", (0, 123, -1))]) for n in (1000, 100000)],
            identity="Stable ID b2-{source_ordinal:06d} is derived from source row position and is not a twentieth displayed column."),
        Family("browser3", "Browser 3 returns and correlation oracles", "numerical", "20260819", [
            "Generate all 250 market normals, then all 250 tech normals; then for symbol SPY..XLE generate 250 idiosyncratic normals. Live continuation draws one market and one tech normal, then eight idiosyncratic normals per event."
        ], {
            "returns": "market[d]=0.0003+0.010*N; tech[d]=0.0002+0.008*N; r[i][d]=beta[i]*market[d]+(0.8*tech[d] if tech member)+idio[i]*N. Parameters in order: (1,.004,F),(1.2,.007,T),(1.1,.008,F),(.9,.005,F),(1.1,.010,T),(1,.008,T),(1.4,.014,T),(.8,.011,F).",
            "statistics": "mean uses left-to-right sum/n. covariance=sum((a-ma)*(b-mb))/(n-1). correlation=cov/sqrt(var_a*var_b), clamped [-1,1]. Diagonal correlation exactly 1. Annualized volatility=sqrt(sample variance)*sqrt(252). beta(a,b)=cov(a,b)/var(b). Matrices compute upper triangle then mirror exactly.",
            "clustering": "Average linkage over all cross pairs with distance=1-correlation. Scan active pairs lexicographically and replace best only on strict smaller distance. New node replaces removed pair by appending; leaf member traversal is stack-based pushing left then right (right leaf visited first).",
            "live": "At each 500 ms tick drop source day 0, append the event values, and recompute the 250-day statistics without changing selected symbol identities.",
        }, [Variant("8x250", "default", {"symbols": 8, "observations": 250, "matrix_rows": 8, "matrix_columns": 8, "live_events": 16}, [
            artifact("browser3.returns.250", "observation_id:string,date:date," + b3_values, b3_artifact_rows("returns"), "Observation-major factor-model returns."),
            artifact("browser3.correlation.8x8", b3_matrix, b3_artifact_rows("correlation"), "Symmetric Pearson sample correlation matrix."),
            artifact("browser3.covariance.8x8", b3_matrix, b3_artifact_rows("covariance"), "Symmetric sample covariance matrix using denominator 249."),
            artifact("browser3.annualized-volatility.8", "symbol:string,annualized_volatility:number", b3_artifact_rows("volatility"), "Per-symbol annualized sample volatility."),
            artifact("browser3.beta.8x8", b3_matrix, b3_artifact_rows("beta"), "Beta of row symbol versus column symbol."),
            artifact("browser3.cluster-order.8", "display_order:integer,symbol:string,source_index:integer", b3_artifact_rows("clustering"), "Canonical average-linkage display order."),
            artifact("browser3.live.16", "event_id:string,tick:integer,date:date," + b3_values, b3_artifact_rows("live"), "Sixteen continuation events from the post-generation RNG state."),
        ])], references=[]),
    ]

    analytical_sizes = (500, 2500, 20000, 100000, 1000000)
    analytical_variants = []
    for n in analytical_sizes:
        artifacts = [
            artifact(f"analytical.returns.{n}", "source_index:integer,date:date,benchmark_return:number,strategy_return:number", analytical_source_rows(n), "Authoritative source returns in business-day order."),
            artifact(f"analytical.core.{n}", "source_index:integer,date:date,strategy_equity:number,benchmark_equity:number,high_water:number,drawdown_pct:number,strategy_return_pct:number,sma20_return_pct:number?", analytical_core_rows(n), "Full-resolution equity, drawdown, returns and SMA20 derived series."),
            artifact(f"analytical.risk-oracles.{n}", "source_index:integer,date:date,annualized_volatility_pct:number?,var95_pct:number?,es95_pct:number?,beta:number?,tracking_error_pct:number?", analytical_risk_rows(n), "Selected full-window 60-day risk oracles, including warm-up nulls.", tuple(sorted(set([0, 1, 2, 3, 4, -1])))),
        ]
        if n == 500:
            artifacts += [
                artifact("analytical.features.10", "rank:integer,name:string,value:number", analytical_static_rows("features"), "Signed feature importance sorted descending."),
                artifact("analytical.optimization.240", "iteration:integer,objective:number,best_so_far:number", analytical_static_rows("optimization"), "Initial deterministic optimization sequence."),
                artifact("analytical.optimization-live.48", "iteration:integer,objective:number,best_so_far:number", analytical_static_rows("optimization-live"), "Sixteen 500 ms ticks, three appended iterations per tick."),
                artifact("analytical.accuracy.12", "fold:integer,accuracy_pct:number,precision_pct:number,recall_pct:number,f1_pct:number", analytical_static_rows("accuracy"), "Twelve-fold model metric series."),
                artifact("analytical.confusion.3x3", "actual_class:integer,predicted_0:integer,predicted_1:integer,predicted_2:integer", analytical_static_rows("confusion"), "Three-class confusion matrix; rows actual, columns predicted."),
                artifact("analytical.attribution.12x5", "month:integer,tech:number,health:number,financials:number,energy:number,other:number", analytical_static_rows("attribution"), "Twelve months of signed group attribution percentages."),
                artifact("analytical.correlation-results.250", "source_index:integer,date:date,spy_qqq_correlation_60:number?", analytical_static_rows("correlation"), "Rolling SPY/QQQ correlation referencing Browser 3 returns."),
            ]
        analytical_variants.append(Variant(f"days-{n}", "default" if n == 500 else "on-demand", {"source_points": n, "initial_equity": 100000, "base_date": "2021-01-04", "risk_window": 60}, artifacts))
    families.append(Family("analytical", "Analytical chart derived-series oracles", "numerical", "20260819", [
        "For each size independently: generate all benchmark normals, then all strategy normals. Static streams use seed XOR 0xBEEF (optimization), 0xACC (accuracy), and 0xA7718 (attribution). Correlation Results consumes Browser 3, not this stream."
    ], {
        "returns": "benchmark=0.0004+0.011*N; strategy=0.85*benchmark+0.0002+0.007*N. Dates are weekdays from 2021-01-04 with no holiday claim.",
        "equity": "equity[0] starts from 100000 then multiplies by (1+return) at each row; high_water includes the current equity and no separate initial-equity row; drawdown_pct=100*(equity/high_water-1); strategy_return_pct=100*strategy; SMA20 uses rolling left-to-right sum and null before index 19.",
        "risk": "At index>=59 use the inclusive 60-value window. Volatility and tracking error use sample denominator 59 and sqrt(252)*100. VaR95 is sorted_window[floor(59*0.05)]*100. ES95 averages the first ceil(60*0.05)=3 sorted values*100. Beta=sum cross deviations/sum benchmark squared deviations, null if denominator zero. Risk artifact stores selected oracles; adapters compute the full series from this formula.",
        "optimization": "objective[i]=1.83+1.4*exp(-i/45)+0.09*N; initial 240 values, then three values per live tick; best_so_far is running maximum.",
        "accuracy": "Four 12-value metric streams in accuracy,precision,recall,F1 order: clamp(base+drift*i+0.02*N,0.5,0.99)*100 with bases .68,.65,.61,.63 and drifts .008,.009,.011,.010. Confusion draws then proceed actual row-major, predicted column-major: diagonal 800+below(400), off-diagonal below(160).",
        "attribution": "For month then Tech,Health,Financials,Energy,Other: ((u-0.42)*3)/(zero_based_group+1.5), in percent.",
        "startup_lod": "Only days-500 is default. 100000 and 1000000 (and other nondefault sizes) construct only on explicit selection. Full source remains authoritative; rendering LOD must preserve extrema and is not included in content hashes.",
    }, analytical_variants, identity="Analytical identity is source_index plus date; static tables use their explicit rank/fold/month/class keys.", references=[{"family": "browser3", "artifact_ids": ["browser3.returns.250"], "reason": "Correlation Results is SPY/QQQ rolling correlation of the same Browser 3 source returns."}]))

    stock_variants = []
    for kind, n in [("daily", 1260), ("intraday", 20000)]:
        bar_cols = "bar_id:string,date:date,open:number,high:number,low:number,close:number,volume:number" if kind == "daily" else "bar_id:string,session_id:string,timestamp:datetime,minute_of_session:integer,open:number,high:number,low:number,close:number,volume:number"
        live_cols = "event_id:string,tick:integer,date:date,open:number,high:number,low:number,close:number,volume:number" if kind == "daily" else "event_id:string,tick:integer,session_id:string,timestamp:datetime,minute_of_session:integer,open:number,high:number,low:number,close:number,volume:number"
        stock_variants.append(Variant(kind, "default" if kind == "daily" else "on-demand", {"symbol": "ACME", "bars": n, "session_bars": 1 if kind == "daily" else 390, "timezone": "UTC", "live_events": 16}, [
            artifact(f"stock.bars.{kind}.{n}", bar_cols, lambda kind=kind, n=n: iter(stock_bars(kind, n)[0]), f"ACME {kind} OHLCV source bars.", (0, 13, 19, 389 if kind == "intraday" else 49, -1)),
            artifact(f"stock.indicators.{kind}.{n}", "bar_id:string,sma20:number?,ema20:number?,bollinger_mid:number?,bollinger_upper:number?,bollinger_lower:number?,session_vwap:number?,wilder_rsi14:number?,wilder_atr14:number?,macd_12_26:number?,macd_signal9:number?,macd_histogram:number?", stock_indicator_rows(kind, n), "Indicator series with explicit warm-up nulls.", (0, 13, 14, 19, 25, 33, 389 if kind == "intraday" else 49, -1)),
            artifact(f"stock.markers.{kind}.{n}", "marker_id:string,bar_index:integer,kind:string,label:string,detail:string,value:number?", stock_event_rows(kind, n), "Signals, fixed demonstration pattern boundaries, and deterministic events in stable order."),
            artifact(f"stock.live.{kind}.16", live_cols, stock_live_rows(kind, n), "Sixteen bars from the continuation RNG state; timestamps advance through synthetic sessions."),
        ]))
    families.append(Family("stock", "ACME stock OHLCV, sessions and indicators", "numerical", "20260820 daily; 20260821 intraday; each variant has an independent stream", [
        "Daily: one normal then spread/high/low/volume uniforms in order per bar. Intraday uses the same draw order and a separately seeded stream. Live uses next-bar normal then spread/high/low/volume uniforms after all source draws."
    ], {
        "daily_bars": "price0=100; regime=.0009*sin(i/250); drift=.00015+regime; vol=.008+.005*abs(cos(i/97)); r=drift+vol*N; open=previous close; close=max(1,open*(1+r)); spread=vol*open*(.3+.7*u); high=max(open,close)+spread*u; low=max(.5,min(open,close)-spread*u); volume=8e6*(1+2.5*abs(r)/vol)*(.6+.8*u).",
        "intraday_bars": "Daily formula with independent seed; drift and regime divided by 390, vol divided by sqrt(390), and volume scale 8e6/390. Timestamps are synthetic UTC weekdays at 09:30+minute_of_session, minute 0..389; no holiday or exchange-calendar claim.",
        "live": "open=max(1,previous close); close=max(1,open*(1+drift+vol*N)); spread=vol*open*(.3+.7*u); high/low and volume use the source helper order; daily drift=.0002 vol=.009, intraday drift=.0002/390 vol=.009/sqrt(390).",
        "sma_ema_bollinger": "SMA20 and EMA20 seed with first 20 closes at index 19; EMA k=2/21 and recurses x*k+previous*(1-k). Bollinger mid=SMA20 and bands=mid+/-2*sqrt(population variance) using two-pass squared deviations /20; all null before index 19.",
        "vwap": "At each session_id change reset cumulative sums. typical=(high+low+close)/3; session_vwap=sum(typical*volume)/sum(volume). Daily has one bar per session; intraday resets at minute_of_session 0.",
        "rsi_atr": "Wilder period 14. RSI first appears at index 14 from mean gains/losses of deltas 1..14, then (13*previous+current)/14. Zero loss gives RSI 100 unless both gain and loss are zero, which gives 50. ATR index 0 null; true range uses current high/low and previous close; first ATR at index 14 is arithmetic mean TR1..14 then Wilder recursion.",
        "macd": "EMA12/EMA26 are SMA-seeded independently. MACD line is null before index 25, then EMA12-EMA26. Signal is EMA9 over compacted nonnull MACD values, first at source index 33. Histogram=line-signal when both nonnull.",
        "markers_live": "SMA20/50 crossover signals use strict post-cross comparison and strength=clamp(abs(fast-slow)/slow*40,.25,1). Patterns are fixed demonstration ranges, not recognition. Reset Demo Data restores source and resets live stream; Reset View preserves source/annotations as scenario-defined.",
    }, stock_variants, identity="bar_id and event_id are stable source identifiers; marker_id is stable after canonical (bar_index,kind,label,detail) sorting."))

    pivot_variants = [Variant("9x1500", "default", {"symbols": 9, "business_days": 1500, "base_date": "2021-01-04", "weekly_group_days": 5, "high_low_period": 3, "buffers": 0}, [
        artifact("pivot.daily.9x1500", "symbol:string,bar_id:string,date:date,open:number,high:number,low:number,close:number,volume:number", pivot_rows("daily"), "Nine independent per-symbol daily OHLCV series.", (0, 1499, 1500, -1)),
        artifact("pivot.weekly.9x300", "symbol:string,group_id:string,first_date:date,last_date:date,first_day:integer,last_day:integer,open:number,high:number,low:number,close:number,volume:number", pivot_rows("weekly"), "Consecutive five-business-day aggregation by source index."),
        artifact("pivot.monthly.9-calendar", "symbol:string,month:string,first_date:date,last_date:date,first_day:integer,last_day:integer,open:number,high:number,low:number,close:number,volume:number", pivot_rows("monthly"), "Actual calendar year/month aggregation, not fixed 21-day bins."),
        artifact("pivot.strict-oracles.9x1500", "symbol:string,bar_id:string,candidate_index:integer,date:date,candidate_high:number?,candidate_low:number?,confirmed_high:number?,confirmed_low:number?,high_confirmed_at:integer?,low_confirmed_at:integer?,upper_step:number?,lower_step:number?", pivot_rows("pivots"), "Strict candidates, buffer acceptance, confirmation indices and no-lookahead steps."),
        artifact("pivot.zigzag.9", "symbol:string,sequence:integer,candidate_index:integer,confirmed_at:integer,price:number,is_high:boolean", pivot_rows("zigzag"), "Alternating confirmed swing sequence; same-type runs keep the more extreme point."),
    ])]
    families.append(Family("pivot", "Nine-symbol pivot chart and aggregation oracles", "numerical", "20260821 + symbol_source_index*7919 (mod 2^64)", [
        "Each symbol has an independent stream. Per day: one normal, high uniform, low uniform, volume uniform, in that order."
    ], {
        "generation": "price0=40+30*(symbol%5); drift=.0001+.00006*(symbol%4); base_vol=.006+.002*(symbol%3); regime=.0008*sin(i/220+symbol); vol=base_vol+.004*abs(cos(i/83)); r=drift+regime+vol*N; open=previous close; close=open*(1+r); high=max(open,close)*(1+vol*u*.6); low=min(open,close)*(1-vol*u*.6); volume=(2+30*abs(r)/vol)*(.6+.8*u)*1e6.",
        "aggregation": "Daily rows are source bars. Weekly groups consecutive source indices floor(i/5), including a final partial group. Monthly groups actual ISO year/month. OHLCV is first open, maximum high, minimum low, last close, sum volume; retain first/last source indices and dates.",
        "candidates": "Default high/low periods are 3. Candidate i requires i+period<n and compares against every other available bar from max(0,i-period) through i+period. High requires strict > against every neighbor; low strict <. Equal extrema are not candidates. This deliberately replaces Slint's >=/<= and QML's asymmetric tie behavior.",
        "confirmation_buffers": "A candidate is known at confirmation index i+period. Accept candidates in source order when abs(price-last_accepted_same_type)>=buffer; default buffers 0 accept all candidates. Step series change at confirmation index, not retroactively at candidate index. high/low_confirmed_at records the window oracle.",
        "zigzag": "Merge accepted highs then lows at each candidate index. Enforce alternating type; same-type runs replace only with strictly higher high or strictly lower low. The artifact applies to daily bars; apply identical formulas after aggregation for weekly/monthly.",
    }, pivot_variants, identity="bar_id is {SYMBOL}-{zero_based_day:04d}; pivot candidate identity is bar_id plus high/low type. Display/range changes never renumber source bars."))

    families.append(Family("volatility", "Volatility rendering surfaces", "rendering", None, [], {
        "axes": "For square n in {100,250,500}: moneyness[k]=.7+.6*k/(n-1); maturity[t]=.05+1.95*(t/(n-1))^2. Rows are maturity-major then strike.",
        "surface": "For stress s in {0,1}: base=.18+.16*s; skew=(.10+.12*s)*(1-m); smile=.35*(m-1)^2; term=.03*(tau-.6)+.004*sin(8*tau); wobble=.004*sin(1.7*k+2.3*t); value=max(.02,base+skew/max(.3,sqrt(tau))+smile+term+wobble). Calm uses s=0 and stressed s=1; no RNG.",
        "presentation": "Blending, surface/wireframe/color, camera and animation are rendering state. Q-P1 animation is off. Nearest-sample selection uses grid indices, never interpolated replacement values.",
    }, [Variant(f"{n}x{n}", "default" if n == 100 else "on-demand", {"maturity_points": n, "strike_points": n, "states": 2}, [artifact(f"volatility.surface.{n}x{n}", "maturity_index:integer,strike_index:integer,moneyness:number,maturity:number,calm:number,stressed:number", volatility_rows(n), "Two deterministic states on the canonical square grid.")]) for n in (100, 250, 500)], separation_notes=["This is an analytic rendering surface, not a calibrated implied-volatility model."]))

    families.append(Family("factor", "Factor structure point cloud", "rendering", "20260822 (all sizes restart and therefore share prefixes)", [
        "Per point: beta normal, value normal, momentum normal, cap uniform. Sector is source index modulo 6 and consumes no random value."
    ], {
        "points": "tilt=sector-2.5; beta=max(.05,1+.12*tilt*.3+.35*N); value=.15*tilt+.6*N; momentum=-.08*tilt+.7*N; cap=20*exp(6*u).",
        "selection": "Symbol S{source_index+1:03d} is stable (larger numbers are not truncated). Sector color and cap point size do not affect numeric identity. 100K is explicitly selected, never a startup default.",
    }, [Variant(f"points-{n}", "default" if n == 240 else "on-demand", {"points": n, "sectors": 6}, [artifact(f"factor.points.{n}", "symbol:string,sector_index:integer,sector:string,beta:number,value:number,momentum:number,cap:number", factor_rows(n), "Stable synthetic factor coordinates.")]) for n in (240, 1000, 10000, 100000)], extensions=["Custom circular-billboard rendering and additional factor controls are implementation extensions."]))

    families.append(Family("correlation", "Correlation surface shared Browser 3 input", "numerical", None, [], {
        "reuse": "No independent payload or RNG is permitted. Use browser3.returns.250, browser3.correlation.8x8, and browser3.cluster-order.8 with their recorded SHA-256 values.",
        "presentation": "2-D/3-D surface and clustering reorder only display coordinates; pair inspection keys remain source symbol IDs. Palette endpoints are #2166AC and #B35806 with a theme-appropriate neutral midpoint.",
    }, [Variant("8x250-shared", "default", {"symbols": 8, "observations": 250, "matrix_rows": 8, "matrix_columns": 8}, [])], references=[{"family": "browser3", "artifact_ids": ["browser3.returns.250", "browser3.correlation.8x8", "browser3.cluster-order.8"], "reason": "The quantitative correlation surface is another renderer of the Browser 3 fixture, not a separately generated numerical example."}]))

    families.append(Family("frontier", "Sampled efficient-frontier rendering fixture", "rendering", "20260825", [
        "Generate 12 expected-return uniforms then 12 volatility uniforms. For each of 2500 portfolios generate 12 uniforms and transform to exponential weights before normalization. No draws for envelope or special portfolios."
    ], {
        "assets": "mu[i]=.03+.012*i+.01*u; vol[i]=.09+.013*i+.02*u for i=0..11.",
        "portfolios": "w[i]=-ln(max(1e-9,u)); sum=sum(w); expected=sum(w*mu)/sum; risk=sqrt(sum(w^2*vol^2))/sum. Weights are retained unnormalized in the artifact; normalized weight is w/sum. This is a diagonal-volatility rendering model, not a covariance QP.",
        "envelope": "vlo/vhi are cloud min/max risk. Forty half-open bins [vlo+(vhi-vlo)*b/40,vlo+(vhi-vlo)*(b+1)/40). Select maximum expected return; ties retain earliest source portfolio. Empty bins have null portfolio/risk/return. The maximum-risk cloud point is intentionally eligible only through special portfolios, matching half-open bin semantics.",
        "special": "minimum-variance and maximum-Sharpe ties retain earliest source index. Sharpe=(return-.02)/risk. Current is fixed risk=.14, return=.065 and is not claimed feasible.",
        "separation": "Sampled envelope and special cloud points are rendering-only. Exact long-only QP, larger clouds, and numerical frontier benchmarks require a separate numerical fixture/revision.",
    }, [Variant("12x2500x40", "default", {"assets": 12, "portfolios": 2500, "bins": 40, "risk_free_rate": 0.02}, [
        artifact("frontier.assets.12", "asset_id:string,expected_return:number,volatility:number", frontier_rows("assets"), "Twelve synthetic asset parameters."),
        artifact("frontier.portfolios.2500", "portfolio_id:string,risk:number,expected_return:number,unnormalized_weights:number[]", frontier_rows("portfolios"), "Random long-only portfolio cloud with twelve weights per row."),
        artifact("frontier.envelope.40", "bin:integer,risk_low:number,risk_high:number,portfolio_id:string?,risk:number?,expected_return:number?", frontier_rows("envelope"), "All forty sampled-envelope bins including null empty bins."),
        artifact("frontier.special.3", "kind:string,portfolio_id:string?,risk:number,expected_return:number,sharpe:number", frontier_rows("special"), "Minimum variance, maximum Sharpe and fixed current portfolio."),
    ])], separation_notes=["Do not replace this fixture with an exact frontier in rendering parity scenarios; exact numerical demonstrations remain separate."]))

    families.append(Family("pca", "Synthetic PCA-like rendering manifold", "rendering", "20260829", [
        "Per point consume three normals in pc1,pc2,pc3 order. Sector is index modulo 6."
    ], {
        "coordinates": "t=sector_index; pc1=.9*N+.5*(t-2.5); pc2=.7*N+.4*sin(2.1*t); pc3=.5*N+.3*cos(1.3*t). IDs P001..P500 and sector names follow factor sector order.",
        "separation": "These are explicitly synthetic coordinates. They are not eigenvectors, computed PCA scores, or explained-variance evidence. Computed PCA is a separate numerical extension.",
    }, [Variant("synthetic-500", "default", {"points": 500, "dimensions": 3, "sectors": 6}, [artifact("pca.synthetic.500", "symbol:string,sector_index:integer,sector:string,pc1:number,pc2:number,pc3:number", pca_rows, "Five hundred fixed synthetic coordinates.")])], separation_notes=["Never label this rendering fixture as a computed decomposition; computed PCA requires separate inputs and numerical oracles."]))

    families.append(Family("regime", "Fixed five-class regime map", "rendering", "20260835", [
        "Per observation consume trend normal then absolute-volatility normal."
    ], {
        "path": "trend0=.4 and vol0=.35 are state before observation 0; trend=clamp(.985*trend+.05*N,-1,1); vol=clamp(.99*vol+.01*.35+.03*abs(N),.05,1).",
        "classes": "abs(trend)<.25 => Transitional; otherwise trend>0 gives Bull/Low Vol when vol<.5 and Bull/High Vol otherwise; trend<0 gives Bear/Low Vol or Bear/High Vol by same threshold. Five assignments are fixed, not inferred by a classifier.",
    }, [Variant("observations-400", "default", {"observations": 400, "classes": 5}, [artifact("regime.observations.400", "observation_id:string,source_index:integer,trend:number,volatility:number,regime_index:integer,regime:string", regime_rows, "Historical path with fixed current/hover selection identities.")])]))

    families.append(Family("projection", "Fixed high-dimensional projection-like layouts", "rendering", "20260851 independently restarted for each layout", [
        "Per point consume category below(5), x normal, y normal. Each layout restarts at the same seed so category and base noise correspond across layouts."
    ], {
        "centers": "For category c: cx=cos(2*pi*c/5), cy=sin(2*pi*c/5); sx=sy=.22*N using successive independent normals.",
        "layouts": "PCA-like: x=.55*cx+1.1*sx+.5*sy,y=.55*cy+.4*sx+.7*sy. t-SNE-like: x=.85*cx+.16*sx,y=.85*cy+.16*sy. UMAP-like: bend=.3*sin(2*cx),x=.75*cx+.2*sx,y=.75*cy+bend+.2*sy.",
        "separation": "Names intentionally end in '-like' (including PCA-like). No layout runs PCA, t-SNE, or UMAP. Categories and point IDs are shared for rectangle/group selection oracles.",
    }, [Variant("5000x5x3", "default", {"points": 5000, "categories": 5, "layouts": 3}, [artifact(f"projection.{name}.5000", "point_id:string,layout:string,x:number,y:number,category:integer", projection_rows(i), f"Fixed {name} layout; no iterative embedding claim.") for i, name in enumerate(("pca-like", "tsne-like", "umap-like"))])], separation_notes=["Actual projection algorithms and lasso interactions are separately scoped extensions."]))

    families.append(Family("network", "Deterministic network graphs and initial layouts", "rendering", "20260859", [
        "Generate x/y uniforms for every node first. For each symbol add sector weight, factor weight, and every even symbol's symbol-symbol weight. Top up edges with a,b below draws and a weight uniform only when a!=b. Layout consumes no RNG.",
        "Run 120 iterations for 100 nodes and 40 for 1000 nodes; iterate repulsion pairs i<j, edges in source order, then node updates in source order."
    ], {
        "nodes_edges": "Reserve six sectors and Beta/Momentum after n-8 symbols. Every symbol links to sector i%6 and factor i%2. Weights: sector .5+.5*u, factor .3+.6*u, symbol .2+.7*u. Duplicate undirected pairs are allowed and remain distinct edge IDs. Edges truncate to max(requested,2*n_symbols), which equals requested canonical sizes.",
        "layout": "k=sqrt(2.4/n); temp=.06*(1-iteration/iterations); repulsion distance=max(.01,Euclidean), force=k^2/d; attraction force=d^2/k*(.4+.6*w)*.02; update clamp(position+displacement/len*min(temp,len),-1,1). Initial x/y are retained beside final positions.",
        "budgets": "Initial position and iteration counts are fixture inputs. Interactive drag/select/neighbor highlighting uses stable node IDs. Further layout/filter/statistics controls are extensions.",
    }, [Variant(f"{n}x{e}", "default" if n == 100 else "on-demand", {"nodes": n, "edges": e, "layout_iterations": 120 if n == 100 else 40}, [
        artifact(f"network.nodes.{n}", "node_id:string,label:string,kind:integer,x:number,y:number,initial_x:number,initial_y:number,layout_iterations:integer", network_rows(n, e, "nodes"), "Node identity, final position, initial position and fixed budget."),
        artifact(f"network.edges.{e}", "edge_id:string,source_node_id:string,target_node_id:string,weight:number", network_rows(n, e, "edges"), "Ordered weighted edges with stable IDs."),
    ]) for n, e in ((100, 300), (1000, 5000))]))

    families.append(Family("knowledge", "Versioned knowledge graph and expansion oracle", "rendering", "20260873", [
        "Construct all 24 nodes and 22 relations in company order, then consume one position uniform per node in stable node order."
    ], {
        "structure": "Three companies each have Sector, Executive, two Securities, two Indicators and one Event. Relations retain construction order plus one company-0/company-1 CORRELATED_WITH link. IDs kg-00..kg-23 and kg-edge-00..kg-edge-21 are stable, not display indices.",
        "visibility": "Only root Company nodes initially visible=true; every nonroot starts collapsed/hidden until ancestors expand. Expanding a company reveals its direct Sector, Executive, Securities and Event; expanding a Security reveals its Indicator. Collapse hides descendants without deleting entities or relations.",
        "positions": "depth=0 root, depth=1 when parent is root, else depth=2; angle=2.399*source_index+.2*u; radius=.25+.3*depth; x=radius*cos(angle), y=radius*sin(angle). Drag overrides presentation position only.",
    }, [Variant("24x22", "default", {"entities": 24, "relations": 22, "initial_visible": 3}, [
        artifact("knowledge.entities.24", "entity_id:string,label:string,type:string,parent_id:string?,initial_visible:boolean,x:number,y:number", knowledge_rows("nodes"), "Typed entities, parent hierarchy, initial visibility and fixed positions."),
        artifact("knowledge.relations.22", "relation_id:string,source_entity_id:string,target_entity_id:string,type:string", knowledge_rows("edges"), "Stable typed relation list and expansion input."),
    ])]))

    families.append(Family("monte-carlo", "Monte Carlo rendering paths and summaries", "rendering", "20260913", [
        "Paths are outer loop 0..599 and steps inner loop 0..119, consuming one normal per step. Summary calculations consume no RNG."
    ], {
        "paths": "Initial value before step 0 is exactly 1.0 and is not an emitted step. At each step value*=1+.001+.02*N; artifact stores 120 post-update values per path. These are rendering paths, not a validated GBM log-return benchmark.",
        "percentiles": "At each step sort 600 values ascending. 5/50/95 percentile uses zero-based index floor(p*(600-1)/100): 29,299,569. No interpolation.",
        "histogram": "Terminal values use 40 equal-width bins from min to max; bucket=floor((value-min)/max(1e-9,max-min)*40), clamped to 39. Artifact stores bin lower/upper and exact counts.",
        "lod": "Path selection uses path-000..path-599. Display decimation is presentation-only and must not alter bands or terminal histogram.",
    }, [Variant("600x120", "default", {"paths": 600, "steps": 120, "initial_value": 1.0, "histogram_bins": 40}, [
        artifact("monte-carlo.paths.600x120", "path_id:string,path_index:integer,step:integer,value:number", monte_carlo_rows("paths"), "Long-form path/step values in generation order."),
        artifact("monte-carlo.bands.120", "step:integer,p05:number,p50:number,p95:number", monte_carlo_rows("bands"), "Fixed nearest-index percentile bands."),
        artifact("monte-carlo.histogram.40", "bin:integer,lower:number,upper:number,count:integer", monte_carlo_rows("histogram"), "Terminal-value histogram with forty bins."),
    ])], separation_notes=["Larger GBM populations and numerical distribution benchmarks are separate from this rendering fixture."]))

    families.append(Family("order-book", "Order-book event stream and heat-map snapshots", "rendering", "20260899", [
        "Per event: one mid normal; then for level 0..199 one depth uniform and one zero-out uniform; then two trade-level below(7) draws. All 1000 initial events precede 32 live continuation events."
    ], {
        "book": "mid0=100 before event 0; mid*=1+.0012*N; base=mid-100*.05; level price=base+level*.05. depth=60/(1+distance^2*.02)*(.4+u), distance=abs(price-mid)/.05; signed size=depth below mid else -depth, replaced by 0 when second u<.06.",
        "events": "touch=int((mid-base)/.05); two trade levels clamp(touch+below(7)-3,0,199). best_bid=mid-.025, best_ask=mid+.025; these are synthetic touch oracles, not inferred from nonzero liquidity.",
        "history": "book snapshots 0..999 form the initial chronological 1000x200 history. Events 1000..1031 are the continuation live stream; on each event shift/drop the oldest column and append, retaining stable event IDs for historical inspection. Positive size is bid, negative ask, zero empty.",
        "cadence": "1/10/30 Hz controls remain specialized. Pause/resume and price zoom do not consume extra events. Long-form levels artifact is an equivalent expansion of the nested snapshot sizes.",
    }, [Variant("1000x200", "default", {"time_columns": 1000, "price_levels": 200, "tick_size": 0.05, "initial_events": 1000, "live_events": 32}, [
        artifact("order-book.snapshots.1000x200", "event_id:string,tick:integer,base_price:number,mid_price:number,signed_sizes:number[]", order_book_rows("book"), "Chronological snapshots with exactly 200 signed sizes per row."),
        artifact("order-book.levels.1000x200", "event_id:string,tick:integer,level:integer,price:number,signed_size:number", order_book_rows("levels"), "Equivalent long-form snapshot expansion for simple adapters.", (0, 199, 200, -1)),
        artifact("order-book.events.1032", "event_id:string,tick:integer,mid_price:number,best_bid:number,best_ask:number,trade_levels:number[]", order_book_rows("events"), "Initial and live event oracles including touch and two trade levels."),
    ])]))
    return families


def hash_artifact(spec: Artifact) -> dict[str, object]:
    digest = hashlib.sha256()
    column_ids = [column["id"] for column in cols(spec.column_spec)]
    digest.update(b'{"artifact_id":')
    digest.update(canonical_bytes(spec.id))
    digest.update(b',"columns":')
    digest.update(canonical_bytes(column_ids))
    digest.update(b',"rows":[')
    wanted = {index for index in spec.samples if index >= 0}
    captured: dict[int, object] = {}
    previous: object = None
    count = 0
    for count, row in enumerate(spec.rows(), start=1):
        if not isinstance(row, (list, tuple)) or len(row) != len(column_ids):
            raise ValueError(f"{spec.id}: row {count - 1} does not match {len(column_ids)} columns")
        index = count - 1
        encoded = canonical_bytes(row)
        if index:
            digest.update(b",")
        digest.update(encoded)
        if index in wanted:
            captured[index] = normalized_json_value(row)
        previous = normalized_json_value(row)
    digest.update(b"]}\n")
    if count == 0:
        raise ValueError(f"{spec.id}: empty artifacts are not publishable")
    if -1 in spec.samples:
        captured[count - 1] = previous
    missing = wanted - captured.keys()
    if missing:
        raise ValueError(f"{spec.id}: golden selectors out of range: {sorted(missing)}")
    golden = [{"selector": f"row[{index}]", "row": captured[index]} for index in sorted(captured)]
    return {"sha256": digest.hexdigest(), "row_count": count, "golden_samples": golden}


def select_families(families: list[Family], selected: list[str]) -> list[Family]:
    if not selected:
        return families
    known = {family.id for family in families}
    unknown = set(selected) - known
    if unknown:
        raise ValueError(f"unknown families: {', '.join(sorted(unknown))}")
    return [family for family in families if family.id in selected]


def select_variants(family: Family, selected: list[str]) -> list[Variant]:
    if not selected:
        return family.variants
    known = {variant.id for variant in family.variants}
    unknown = set(selected) - known
    if unknown:
        raise ValueError(f"{family.id}: unknown variants: {', '.join(sorted(unknown))}")
    return [variant for variant in family.variants if variant.id in selected]


def run_update(families: list[Family], family_ids: list[str]) -> int:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    artifact_count = 0
    for family in select_families(families, family_ids):
        computed = {}
        for variant in family.variants:
            for spec in variant.artifacts:
                before = time.monotonic()
                computed[(variant.id, spec.id)] = hash_artifact(spec)
                artifact_count += 1
                print(f"hash {spec.id}: {computed[(variant.id, spec.id)]['row_count']} rows, "
                      f"{time.monotonic() - before:.2f}s", flush=True)
        document = family_manifest(family, computed)
        path = MANIFEST_DIR / f"{family.id}.json"
        path.write_text(json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(ROOT)}", flush=True)
    print(f"Updated {len(select_families(families, family_ids))} manifests and {artifact_count} artifacts in {time.monotonic() - started:.2f}s.")
    return 0


def run_check(families: list[Family], family_ids: list[str], variant_ids: list[str]) -> int:
    started = time.monotonic()
    errors = []
    artifact_count = 0
    checked_variants = 0
    for family in select_families(families, family_ids):
        path = MANIFEST_DIR / f"{family.id}.json"
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        published_variants = {item["id"]: item for item in document.get("variants", [])}
        for variant in select_variants(family, variant_ids):
            checked_variants += 1
            published = published_variants.get(variant.id)
            if published is None:
                errors.append(f"{family.id}/{variant.id}: missing published variant")
                continue
            published_artifacts = {item["id"]: item for item in published.get("artifacts", [])}
            for spec in variant.artifacts:
                expected = published_artifacts.get(spec.id)
                if expected is None:
                    errors.append(f"{family.id}/{variant.id}: missing artifact {spec.id}")
                    continue
                before = time.monotonic()
                actual = hash_artifact(spec)
                artifact_count += 1
                for key in ("sha256", "row_count", "golden_samples"):
                    if actual[key] != expected.get(key):
                        errors.append(f"{spec.id}: {key} mismatch")
                print(f"check {spec.id}: {time.monotonic() - before:.2f}s", flush=True)
            if set(published_artifacts) != {spec.id for spec in variant.artifacts}:
                errors.append(f"{family.id}/{variant.id}: published artifact set differs from generator")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Verified {artifact_count} artifacts in {checked_variants} variants in {time.monotonic() - started:.2f}s; no payload files written.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("update-hashes", "check"))
    parser.add_argument("--family", action="append", default=[], help="family ID; repeat to select several (default: all)")
    parser.add_argument("--variant", action="append", default=[], help="variant ID for check only; repeat to select several")
    args = parser.parse_args()
    families = build_families()
    try:
        if args.command == "update-hashes":
            if args.variant:
                parser.error("--variant is check-only; update an entire family so manifests never mix revisions")
            return run_update(families, args.family)
        return run_check(families, args.family, args.variant)
    except (OSError, ValueError, TypeError) as error:
        print(f"Fixture {args.command} failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
