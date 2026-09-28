"""固定データによるダメージ計算の回帰テスト。

期待値は計算実装から取得せず、テスト仕様書の TD-009 として固定する。
計算式または出典が確定したケースだけ ``EXPECTED_CASES`` に追加する。
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from damage_calculator import calculate_damage


def _case(
    name,
    attack,
    motion,
    physical_hitzone,
    element,
    element_hitzone,
    affinity_multiplier,
    expected_physical,
    expected_element,
    expected_total,
):
    return {
        "name": name,
        "input": {
            "weapon": {
                "attack": attack,
                "weapon_kind": "long-sword",
                "element": (
                    None
                    if element == 0
                    else {"type": "fire", "value": element}
                ),
            },
            "part": {
                "physical_hitzone": physical_hitzone,
                "element_hitzone": {"fire": element_hitzone},
            },
            "attack": {
                "motion": {
                    "id": f"fixture-motion-{name}",
                    "name": name,
                    "weapon_kind": "long-sword",
                    "motion_value": motion,
                },
                "affinity_multiplier": affinity_multiplier,
            },
        },
        "expected": {
            "physical": expected_physical,
            "element": expected_element,
            "total": expected_total,
        },
    }


# TD-009: 仕様書の固定規則
#   physical = floor(attack * motion% * affinity * physical hitzone%)
#   element  = floor(element * element hitzone%)
# から、実装とは独立に算出した回帰値。
EXPECTED_CASES = [
    _case("物理01", 100, 10, 10, 0, 10, 1.0, 1, 0, 1),
    _case("物理02", 120, 25, 20, 0, 10, 1.0, 6, 0, 6),
    _case("物理03", 150, 40, 30, 0, 10, 1.0, 18, 0, 18),
    _case("物理04", 180, 55, 40, 0, 10, 1.0, 39, 0, 39),
    _case("物理05", 210, 70, 45, 0, 10, 1.0, 66, 0, 66),
    _case("物理06", 240, 85, 50, 0, 10, 1.0, 102, 0, 102),
    _case("物理07", 275, 100, 55, 0, 10, 1.0, 151, 0, 151),
    _case("物理08", 310, 125, 60, 0, 10, 1.0, 232, 0, 232),
    _case("物理09", 350, 150, 65, 0, 10, 1.0, 341, 0, 341),
    _case("物理10", 400, 200, 70, 0, 10, 1.0, 560, 0, 560),
    _case("属性01", 100, 10, 10, 50, 10, 1.0, 1, 5, 6),
    _case("属性02", 120, 25, 20, 75, 15, 1.0, 6, 11, 17),
    _case("属性03", 150, 40, 30, 100, 20, 1.0, 18, 20, 38),
    _case("属性04", 180, 55, 40, 125, 25, 1.0, 39, 31, 70),
    _case("属性05", 210, 70, 45, 150, 30, 1.0, 66, 45, 111),
    _case("会心01", 240, 85, 50, 50, 20, 1.25, 127, 10, 137),
    _case("会心02", 275, 100, 55, 75, 25, 1.25, 189, 18, 207),
    _case("会心03", 310, 125, 60, 100, 30, 0.75, 174, 30, 204),
    _case("会心04", 350, 150, 65, 125, 35, 1.0, 341, 43, 384),
    _case("会心05", 400, 200, 70, 150, 40, 1.25, 700, 60, 760),
]


class DamageCalculatorTests(unittest.TestCase):
    def test_fixed_cases_match_independently_derived_values(self):
        self.assertGreaterEqual(len(EXPECTED_CASES), 20)
        for case in EXPECTED_CASES:
            with self.subTest(case=case["name"]):
                result = calculate_damage(case["input"])
                self.assertEqual(result["physical"], case["expected"]["physical"])
                self.assertEqual(result["element"], case["expected"]["element"])
                self.assertEqual(result["total"], case["expected"]["total"])

    def test_missing_element_hitzone_is_not_treated_as_zero(self):
        result = calculate_damage(
            {
                "weapon": {
                    "attack": 200,
                    "weapon_kind": "long-sword",
                    "element": {"type": "fire", "value": 80},
                },
                "part": {"physical_hitzone": 50},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "テスト攻撃",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                },
            }
        )
        self.assertFalse(result["calculable"])
        self.assertIn("element_hitzone", result["missing"])
        self.assertEqual(result["damages"], {})

    def test_missing_required_input_is_reported_in_japanese(self):
        result = calculate_damage(
            {
                "weapon": None,
                "part": None,
                "attack": {"motion": None},
            }
        )
        self.assertFalse(result["calculable"])
        self.assertTrue(result["errors"])
        self.assertTrue(any(message for message in result["errors"]))
        self.assertEqual(result["damages"], {})

    def test_invalid_input_range_is_rejected_before_calculation(self):
        result = calculate_damage(
            {
                "weapon": {"attack": 200, "element": None, "weapon_kind": "long-sword"},
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "不正",
                        "weapon_kind": "long-sword",
                        "motion_value": -1,
                    },
                    "affinity_multiplier": 1.0,
                },
            }
        )
        self.assertFalse(result["calculable"])
        self.assertIn("motion_value", result["invalid"])
        self.assertEqual(result["damages"], {})

    def test_unsupported_correction_is_reported_without_application(self):
        result = calculate_damage(
            {
                "weapon": {"attack": 200, "element": None, "weapon_kind": "long-sword"},
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "テスト攻撃",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                    "corrections": [{"id": "unknown", "value": 2.0}],
                },
            }
        )
        self.assertIn("unknown", result["not_applied"])
        self.assertNotIn("unknown", result["applied_corrections"])

    def test_verified_quest_correction_and_status_are_in_breakdown(self):
        result = calculate_damage(
            {
                "weapon": {"attack": 200, "element": None, "weapon_kind": "long-sword"},
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "テスト攻撃",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                },
                "status": {"id": "poison", "verified": True},
                "quest": {
                    "players": 4,
                    "corrections": [
                        {"id": "status-4p", "value": 1.2, "verified": True}
                    ],
                },
            }
        )
        self.assertTrue(result["calculable"])
        self.assertEqual(result["status"]["id"], "poison")
        self.assertEqual(result["quest"]["players"], 4)
        self.assertIn("status-4p", result["applied_corrections"])
        self.assertTrue(result["breakdown"])

    def test_unverified_status_formula_is_not_applied(self):
        result = calculate_damage(
            {
                "weapon": {
                    "attack": 200,
                    "element": None,
                    "weapon_kind": "long-sword",
                },
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "テスト攻撃",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                },
                "status": {"id": "paralysis", "verified": False},
            }
        )
        self.assertTrue(result["calculable"])
        self.assertIn("paralysis", result["not_applied"])
        self.assertNotIn("paralysis", result["applied_corrections"])

    def test_same_input_is_deterministic(self):
        input_data = EXPECTED_CASES[0]["input"]
        first = calculate_damage(input_data)
        for _ in range(9):
            self.assertEqual(calculate_damage(input_data), first)

    def test_direct_motion_value_is_rejected(self):
        result = calculate_damage(
            {
                "weapon": {
                    "attack": 200,
                    "weapon_kind": "long-sword",
                    "element": None,
                },
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion_value": 30,
                    "affinity_multiplier": 1.0,
                },
            }
        )
        self.assertFalse(result["calculable"])
        self.assertIn("motion", result["missing"])
        self.assertTrue(any("モーション" in message for message in result["errors"]))

    def test_motion_is_carried_into_breakdown_and_must_match_weapon_kind(self):
        result = calculate_damage(
            {
                "weapon": {
                    "attack": 200,
                    "weapon_kind": "long-sword",
                    "element": None,
                },
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "気刃斬り",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                },
            }
        )
        self.assertTrue(result["calculable"])
        self.assertTrue(any(item.get("motion") for item in result["breakdown"]))

        mismatched = calculate_damage(
            {
                "weapon": {
                    "attack": 200,
                    "weapon_kind": "bow",
                    "element": None,
                },
                "part": {"physical_hitzone": 50, "element_hitzone": {}},
                "attack": {
                    "motion": {
                        "id": "motion-001",
                        "name": "気刃斬り",
                        "weapon_kind": "long-sword",
                        "motion_value": 30,
                    },
                    "affinity_multiplier": 1.0,
                },
            }
        )
        self.assertFalse(mismatched["calculable"])
        self.assertIn("motion.weapon_kind", mismatched["invalid"])


if __name__ == "__main__":
    unittest.main()
