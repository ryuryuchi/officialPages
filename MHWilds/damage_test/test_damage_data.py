"""データ取得・変換・結合の契約テスト。"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from damage_data import (
    DataFetchError,
    DataValidationError,
    combine_records,
    fetch_catalog,
    fetch_live_catalog,
    fetch_json,
    load_demo_catalog,
    normalize_monster,
    normalize_monster_catalog,
    normalize_monster_part,
    normalize_motion,
    normalize_motion_catalog,
    normalize_weapon,
    normalize_weapon_catalog,
)


class DamageDataTests(unittest.TestCase):
    def test_weapon_is_normalized_to_common_contract(self):
        weapon = normalize_weapon(
            {
                "id": "weapon-001",
                "name": "テスト武器",
                "weapon_kind": "long-sword",
                "attack": 250,
                "element": {"type": "fire", "value": 120},
            },
            source_url="https://example.test/weapons",
            retrieved_at="2026-09-10T00:00:00Z",
            data_version="fixture-001",
        )
        self.assertEqual(weapon["id"], "weapon-001")
        self.assertEqual(weapon["name"], "テスト武器")
        self.assertEqual(weapon["weapon_kind"], "long-sword")
        self.assertEqual(weapon["attack"], 250)
        self.assertEqual(weapon["element"], {"type": "fire", "value": 120})
        self.assertEqual(weapon["metadata"]["data_version"], "fixture-001")

    def test_monster_part_keeps_physical_and_element_hitzones(self):
        part = normalize_monster_part(
            {
                "monster_id": "monster-001",
                "part_id": "head",
                "name": "頭",
                "physical_hitzone": 70,
                "element_hitzone": {"fire": 25},
            }
        )
        self.assertEqual(part["monster_id"], "monster-001")
        self.assertEqual(part["part_id"], "head")
        self.assertEqual(part["physical_hitzone"], 70)
        self.assertEqual(part["element_hitzone"], {"fire": 25})

    def test_matching_identifiers_are_combined(self):
        combined = combine_records(
            {"id": "weapon-001", "name": "武器"},
            {"weapon_id": "weapon-001", "skill_ids": ["skill-001"]},
            {"id": "skill-001", "name": "スキル"},
        )
        self.assertEqual(combined["weapon"]["id"], "weapon-001")
        self.assertEqual(combined["skills"][0]["id"], "skill-001")

    def test_mismatched_identifiers_are_rejected(self):
        with self.assertRaises(DataValidationError) as context:
            combine_records(
                {"id": "weapon-001"},
                {"weapon_id": "weapon-999", "skill_ids": []},
                None,
            )
        self.assertIn("weapon", str(context.exception))
        self.assertIn("weapon-999", str(context.exception))

    def test_required_hitzone_is_not_invented_when_missing(self):
        with self.assertRaises(DataValidationError) as context:
            normalize_monster_part(
                {
                    "monster_id": "monster-001",
                    "part_id": "head",
                    "name": "頭",
                    "physical_hitzone": 70,
                }
            )
        self.assertIn("element_hitzone", str(context.exception))

    def test_invalid_numeric_value_is_rejected(self):
        with self.assertRaises(DataValidationError):
            normalize_weapon(
                {
                    "id": "weapon-001",
                    "name": "テスト武器",
                    "attack": "not-a-number",
                    "element": {"type": "fire", "value": 120},
                }
            )

    def test_metadata_contains_source_and_availability(self):
        weapon = normalize_weapon(
            {
                "id": "weapon-001",
                "name": "テスト武器",
                "attack": 250,
                "element": None,
            },
            source_url="https://example.test/weapons",
            retrieved_at="2026-09-10T00:00:00Z",
            data_version="fixture-001",
        )
        self.assertEqual(
            weapon["metadata"],
            {
                "source_url": "https://example.test/weapons",
                "retrieved_at": "2026-09-10T00:00:00Z",
                "data_version": "fixture-001",
                "available": True,
                "missing": [],
            },
        )

    def test_all_weapon_catalog_records_are_retained_with_completeness_metadata(self):
        catalog = normalize_weapon_catalog(
            [
                {
                    "id": "weapon-001",
                    "name": "武器1",
                    "weapon_kind": "long-sword",
                    "attack": 200,
                    "element": None,
                },
                {
                    "id": "weapon-002",
                    "name": "武器2",
                    "weapon_kind": "bow",
                    "attack": 180,
                    "element": {"type": "fire", "value": 50},
                },
            ],
            expected_ids={"weapon-001", "weapon-002"},
            source_url="https://example.test/weapons",
            retrieved_at="2026-09-10T00:00:00Z",
            data_version="fixture-001",
        )
        self.assertEqual([item["id"] for item in catalog["items"]], [
            "weapon-001",
            "weapon-002",
        ])
        self.assertEqual(catalog["metadata"]["source_count"], 2)
        self.assertEqual(catalog["metadata"]["imported_count"], 2)
        self.assertTrue(catalog["metadata"]["complete"])
        self.assertEqual(catalog["metadata"]["missing_ids"], [])

    def test_duplicate_or_missing_weapon_is_rejected_as_incomplete(self):
        with self.assertRaises(DataValidationError) as context:
            normalize_weapon_catalog(
                [
                    {
                        "id": "weapon-001",
                        "name": "武器1",
                        "weapon_kind": "long-sword",
                        "attack": 200,
                        "element": None,
                    },
                    {
                        "id": "weapon-001",
                        "name": "重複武器",
                        "weapon_kind": "long-sword",
                        "attack": 210,
                        "element": None,
                    },
                ],
                expected_ids={"weapon-001", "weapon-002"},
            )
        self.assertIn("weapon-001", str(context.exception))
        self.assertIn("weapon-002", str(context.exception))

    def test_all_monster_statuses_are_retained_even_when_formula_is_unverified(self):
        monster = normalize_monster(
            {
                "id": "monster-001",
                "name": "テストモンスター",
                "parts": [
                    {
                        "monster_id": "monster-001",
                        "part_id": "head",
                        "name": "頭",
                        "physical_hitzone": 70,
                        "element_hitzone": {"fire": 20},
                    }
                ],
                "statuses": [
                    {"id": "poison", "name": "毒", "verified": True},
                    {"id": "sleep", "name": "睡眠", "verified": False},
                    {"id": "blast", "name": "爆破", "verified": False},
                ],
            }
        )
        self.assertEqual(
            [status["id"] for status in monster["statuses"]],
            ["poison", "sleep", "blast"],
        )

    def test_motion_keeps_weapon_kind_and_provenance(self):
        motion = normalize_motion(
            {
                "id": "ls-spirit-roundslash",
                "weapon_kind": "long-sword",
                "name": "気刃大回転斬り",
                "motion_value": 42,
            },
            source_url="https://example.test/motions",
            retrieved_at="2026-09-10T00:00:00Z",
            data_version="motion-001",
        )
        self.assertEqual(motion["weapon_kind"], "long-sword")
        self.assertEqual(motion["motion_value"], 42)
        self.assertEqual(motion["metadata"]["data_version"], "motion-001")

    def test_monster_catalog_keeps_all_monsters_and_parts(self):
        catalog = normalize_monster_catalog(
            [
                {
                    "id": "monster-001",
                    "name": "モンスター1",
                    "parts": [
                        {
                            "monster_id": "monster-001",
                            "part_id": "head",
                            "name": "頭",
                            "physical_hitzone": 70,
                            "element_hitzone": {"fire": 20},
                        },
                        {
                            "monster_id": "monster-001",
                            "part_id": "body",
                            "name": "胴",
                            "physical_hitzone": 40,
                            "element_hitzone": {"fire": 10},
                        },
                    ],
                    "statuses": [],
                },
                {
                    "id": "monster-002",
                    "name": "モンスター2",
                    "parts": [
                        {
                            "monster_id": "monster-002",
                            "part_id": "head",
                            "name": "頭",
                            "physical_hitzone": 60,
                            "element_hitzone": {"fire": 15},
                        }
                    ],
                    "statuses": [],
                },
            ],
            expected_ids={"monster-001", "monster-002"},
        )
        self.assertEqual(len(catalog["items"]), 2)
        self.assertEqual(len(catalog["items"][0]["parts"]), 2)
        self.assertTrue(catalog["metadata"]["complete"])

    def test_motion_catalog_rejects_mismatched_missing_ids(self):
        with self.assertRaises(DataValidationError) as context:
            normalize_motion_catalog(
                [
                    {
                        "id": "motion-001",
                        "weapon_kind": "long-sword",
                        "name": "斬り",
                        "motion_value": 30,
                    }
                ],
                expected_ids={"motion-001", "motion-002"},
            )
        self.assertIn("motion-002", str(context.exception))

    @patch("damage_data.fetch_json")
    def test_fetch_catalog_does_not_return_partial_catalog(self, fetch):
        fetch.side_effect = [
            [
                {
                    "id": "weapon-001",
                    "name": "武器",
                    "weapon_kind": "long-sword",
                    "attack": 200,
                    "element": None,
                }
            ],
            DataFetchError("monster source unavailable"),
        ]
        with self.assertRaises(DataFetchError):
            fetch_catalog(
                weapon_url="https://example.test/weapons",
                monster_url="https://example.test/monsters",
                motion_url="https://example.test/motions",
                data_version="fixture-001",
            )

    @patch("damage_data.fetch_json")
    def test_live_catalog_keeps_all_api_weapons_and_monsters_and_reports_missing_motions(
        self, fetch
    ):
        fetch.side_effect = [
            [
                {
                    "id": 101,
                    "name": "API武器",
                    "kind": "long-sword",
                    "damage": {"raw": 200},
                    "specials": [],
                }
            ],
            [
                {
                    "id": 202,
                    "name": "APIモンスター",
                    "parts": [
                        {
                            "id": 303,
                            "name": "head",
                            "multipliers": {
                                "slash": 0.7,
                                "fire": 0.2,
                            },
                        }
                    ],
                    "weaknesses": [
                        {"kind": "status", "status": "poison"},
                        {"kind": "status", "status": "sleep"},
                    ],
                }
            ],
        ]
        catalog = fetch_live_catalog(
            weapon_url="https://example.test/weapons",
            monster_url="https://example.test/monsters",
        )
        self.assertEqual(len(catalog["weapons"]), 1)
        self.assertEqual(len(catalog["monsters"]), 1)
        self.assertEqual(
            [status["id"] for status in catalog["monsters"][0]["statuses"]],
            ["poison", "sleep"],
        )
        self.assertEqual(catalog["metadata"]["status_count"], 2)
        self.assertEqual(catalog["metadata"]["missing"], ["motion_catalog"])
        self.assertFalse(catalog["metadata"]["complete"])

    @patch("damage_data.fetch_json")
    def test_debug_live_catalog_supplies_selectable_fixed_motion_value(self, fetch):
        fetch.side_effect = [
            [
                {
                    "id": 101,
                    "name": "API武器",
                    "kind": "long-sword",
                    "damage": {"raw": 200},
                    "specials": [],
                }
            ],
            [
                {
                    "id": 202,
                    "name": "APIモンスター",
                    "parts": [
                        {
                            "id": 303,
                            "name": "head",
                            "multipliers": {"slash": 0.7},
                        }
                    ],
                    "weaknesses": [],
                }
            ],
        ]
        catalog = fetch_live_catalog(
            weapon_url="https://example.test/weapons",
            monster_url="https://example.test/monsters",
            debug_motion_value=50,
        )
        self.assertTrue(catalog["metadata"]["complete"])
        self.assertTrue(catalog["metadata"]["debug_motion"])
        self.assertEqual(catalog["motions"][0]["motion_value"], 50)
        self.assertEqual(catalog["motions"][0]["weapon_kind"], "long-sword")

    def test_demo_catalog_is_not_a_single_dummy_and_has_complete_catalog_metadata(self):
        catalog = load_demo_catalog()
        self.assertGreaterEqual(len(catalog["weapons"]), 2)
        self.assertGreaterEqual(len(catalog["monsters"]), 1)
        self.assertTrue(catalog["metadata"]["complete"])
        self.assertIn("source_count", catalog["metadata"])

    @patch("damage_data.urllib.request.urlopen")
    def test_fetch_failure_contains_actionable_error(self, urlopen):
        urlopen.side_effect = OSError("network is down")
        with self.assertRaises(DataFetchError) as context:
            fetch_json("https://example.test/data")
        self.assertIn("取得", str(context.exception))
        self.assertIn("network is down", str(context.exception))

if __name__ == "__main__":
    unittest.main()
