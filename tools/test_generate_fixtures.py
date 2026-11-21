#!/usr/bin/env python3
"""Focused stdlib tests for the canonical fixture contract."""

from __future__ import annotations

import hashlib
import math
import unittest

from generate_fixtures import (
    Artifact,
    SplitMix64,
    analytical_core_rows,
    build_families,
    canonical_bytes,
    hash_artifact,
    intraday_timestamp,
    pivot_oracles,
    stock_bars,
    stock_indicators,
)


class SplitMix64Tests(unittest.TestCase):
    def test_published_seed_zero_vectors(self) -> None:
        rng = SplitMix64(0)
        self.assertEqual(
            [rng.next_u64() for _ in range(4)],
            [
                0xE220A8397B1DCDAF,
                0x6E789E6AA1B965F4,
                0x06C45D188009454F,
                0xF88BB8A8724C81EC,
            ],
        )

    def test_uniform_below_and_normal_consumption(self) -> None:
        uniform_rng = SplitMix64(42)
        expected_state = (42 + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
        value = uniform_rng.uniform()
        self.assertEqual(uniform_rng.state, expected_state)
        self.assertGreaterEqual(value, 0.0)
        self.assertLess(value, 1.0)

        below_rng = SplitMix64(42)
        expected = below_rng.next_u64() % 17
        self.assertEqual(SplitMix64(42).below(17), expected)

        normal_rng = SplitMix64(42)
        first = SplitMix64(42)
        u1 = max(first.uniform(), 1e-12)
        u2 = first.uniform()
        expected_normal = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        self.assertEqual(normal_rng.normal(), expected_normal)
        self.assertEqual(normal_rng.state, first.state)


class CanonicalSerializationTests(unittest.TestCase):
    def test_scalars_containers_and_unicode(self) -> None:
        self.assertEqual(canonical_bytes(None), b"null")
        self.assertEqual(canonical_bytes(True), b"true")
        self.assertEqual(canonical_bytes(False), b"false")
        self.assertEqual(canonical_bytes(-12), b"-12")
        self.assertEqual(
            canonical_bytes({"z": 1, "a": [None, False]}),
            b'{"a":[null,false],"z":1}',
        )
        self.assertEqual(canonical_bytes("é"), '"é"'.encode("utf-8"))

    def test_fixed_nine_decimals_and_negative_zero(self) -> None:
        self.assertEqual(canonical_bytes(1.0), b"1.000000000")
        self.assertEqual(canonical_bytes(1e20), b"100000000000000000000.000000000")
        for value in (-0.0, -1e-12, 1e-12):
            self.assertEqual(canonical_bytes(value), b"0.000000000")

    def test_nonfinite_values_are_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                canonical_bytes(value)

    def test_artifact_envelope_hash_and_golden_rows(self) -> None:
        spec = Artifact(
            "test.artifact",
            "a:integer,b:number?",
            lambda: iter([[1, 2.0], [2, None]]),
            "test",
            (0, -1),
        )
        result = hash_artifact(spec)
        payload = (
            b'{"artifact_id":"test.artifact","columns":["a","b"],'
            b'"rows":[[1,2.000000000],[2,null]]}\n'
        )
        self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(
            result["golden_samples"],
            [
                {"selector": "row[0]", "row": [1, 2.0]},
                {"selector": "row[1]", "row": [2, None]},
            ],
        )


class FormulaBoundaryTests(unittest.TestCase):
    def test_analytical_sma_warmup(self) -> None:
        rows = list(analytical_core_rows(20)())
        self.assertTrue(all(row[7] is None for row in rows[:19]))
        self.assertIsNotNone(rows[19][7])

    def test_intraday_session_boundaries(self) -> None:
        self.assertEqual(
            intraday_timestamp(0),
            ("2021-01-04-session", "2021-01-04T09:30:00Z", 0),
        )
        self.assertEqual(
            intraday_timestamp(389),
            ("2021-01-04-session", "2021-01-04T15:59:00Z", 389),
        )
        self.assertEqual(
            intraday_timestamp(390),
            ("2021-01-05-session", "2021-01-05T09:30:00Z", 0),
        )
        self.assertEqual(
            intraday_timestamp(5 * 390),
            ("2021-01-11-session", "2021-01-11T09:30:00Z", 0),
        )

    def test_stock_indicator_warmups(self) -> None:
        bars, _ = stock_bars("daily", 34)
        rows = stock_indicators(bars, "daily")
        self.assertIsNotNone(rows[0][6])  # One-bar daily session VWAP.
        self.assertTrue(all(value is None for value in rows[0][1:6]))
        self.assertIsNone(rows[0][7])
        self.assertIsNone(rows[0][8])
        self.assertIsNone(rows[13][7])
        self.assertIsNotNone(rows[14][7])
        self.assertIsNotNone(rows[14][8])
        self.assertTrue(all(rows[19][i] is not None for i in range(1, 6)))
        self.assertIsNotNone(rows[25][9])
        self.assertIsNone(rows[25][10])
        self.assertIsNotNone(rows[33][10])
        self.assertIsNotNone(rows[33][11])

    @staticmethod
    def synthetic_bars(highs: list[float]) -> list[list[object]]:
        return [
            [f"T-{i:04d}", f"2021-01-{i + 1:02d}", 5.0, high, 1.0, 5.0, 100.0]
            for i, high in enumerate(highs)
        ]

    def test_pivot_strict_ties_and_confirmation(self) -> None:
        rows, _ = pivot_oracles(self.synthetic_bars([8.0, 9.0, 10.0, 9.0, 8.0]), period=1)
        self.assertEqual(rows[2][3], 10.0)
        self.assertEqual(rows[2][7], 3)
        self.assertIsNone(rows[2][9])
        self.assertEqual(rows[3][9], 10.0)

        tied_rows, _ = pivot_oracles(self.synthetic_bars([8.0, 9.0, 10.0, 10.0, 8.0]), period=1)
        self.assertIsNone(tied_rows[2][3])
        self.assertIsNone(tied_rows[3][3])


class InventoryPolicyTests(unittest.TestCase):
    def test_inventory_and_large_default_policy(self) -> None:
        families = build_families()
        variants = [variant for family in families for variant in family.variants]
        artifacts = [artifact for variant in variants for artifact in variant.artifacts]
        self.assertEqual(len(families), 17)
        self.assertEqual(len(variants), 29)
        self.assertEqual(len(artifacts), 73)
        self.assertEqual(len({family.id for family in families}), 17)
        self.assertEqual(len({variant.id for variant in variants}), 29)
        self.assertEqual(len({artifact.id for artifact in artifacts}), 73)
        self.assertTrue(all(sum(v.selection == "default" for v in family.variants) == 1 for family in families))

        by_id = {artifact.id: variant for variant in variants for artifact in variant.artifacts}
        self.assertEqual(by_id["browser2.rows.100000"].selection, "on-demand")
        for size in (100000, 1000000):
            for kind in ("returns", "core", "risk-oracles"):
                self.assertEqual(by_id[f"analytical.{kind}.{size}"].selection, "on-demand")
        self.assertEqual(by_id["analytical.core.500"].selection, "default")


if __name__ == "__main__":
    unittest.main()
