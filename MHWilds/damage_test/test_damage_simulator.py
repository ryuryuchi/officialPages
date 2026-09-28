"""UI contract tests for catalog completeness and motion-driven input."""

from __future__ import annotations

import sys
import tkinter as tk
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from damage_data import load_demo_catalog
from damage_simulator import DamageSimulatorApp


def _create_root_or_skip(test_case: unittest.TestCase) -> tk.Tk:
    try:
        return tk.Tk()
    except tk.TclError as error:
        test_case.skipTest(f"Tkinter表示環境がありません: {error}")
        raise AssertionError("unreachable")


class DamageSimulatorUiTests(unittest.TestCase):
    def test_demo_catalog_exposes_weapons_monsters_statuses_and_motions(self):
        catalog = load_demo_catalog()
        self.assertGreaterEqual(len(catalog["weapons"]), 2)
        self.assertGreaterEqual(len(catalog["monsters"]), 1)
        self.assertTrue(catalog["motions"])
        self.assertTrue(catalog["metadata"]["complete"])

    def test_motion_choices_follow_weapon_kind_and_value_is_read_only(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            self.assertTrue(hasattr(app, "motion_combo"))
            self.assertTrue(hasattr(app, "motion_value_label"))
            self.assertFalse(hasattr(app, "motion_entry"))
            self.assertTrue(app.motion_combo["values"])
            self.assertNotEqual(app.motion_value_label.cget("text"), "—")
            self.assertFalse(
                any(
                    widget.winfo_class() == "TEntry"
                    and str(widget.cget("textvariable")) == str(app.motion_var)
                    for widget in _walk_widgets(root)
                )
            )
        finally:
            root.destroy()

    def test_all_statuses_are_available_without_dropping_unverified_entries(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            monster = app._find_monster()
            expected = ["なし"] + [
                status["name"] for status in monster["statuses"]
            ]
            self.assertEqual(list(app.status_combo["values"]), expected)
        finally:
            root.destroy()

    def test_all_monsters_are_available_and_parts_follow_selected_monster(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            self.assertEqual(
                list(app.monster_combo["values"]),
                [monster["name"] for monster in app.catalog["monsters"]],
            )
            app.monster_var.set(app.catalog["monsters"][1]["name"])
            app._update_monster_choices()
            self.assertEqual(
                list(app.part_combo["values"]),
                [part["name"] for part in app.catalog["monsters"][1]["parts"]],
            )
        finally:
            root.destroy()

    def test_weapon_and_monster_search_narrows_large_catalog_without_losing_selection(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            app.weapon_search_var.set("ボウ")
            app._weapon_search_changed(None)
            self.assertEqual(list(app.weapon_combo["values"]), ["ハンターボウ"])
            app.monster_search_var.set("チャタ")
            app._monster_search_changed(None)
            self.assertEqual(list(app.monster_combo["values"]), ["チャタカブラ"])
        finally:
            root.destroy()

    def test_incomplete_catalog_disables_calculation_with_actionable_message(self):
        catalog = load_demo_catalog()
        catalog["metadata"]["complete"] = False
        catalog["metadata"]["missing_ids"] = ["weapon-missing"]
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root, catalog=catalog)
            self.assertTrue(
                "全件" in app.input_status.cget("text")
                or app.calculate_button.instate(["disabled"])
            )
        finally:
            root.destroy()

    def test_live_load_failure_does_not_restore_demo_catalog(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            app._remote_load_failed("通信失敗")
            self.assertEqual(list(app.weapon_combo["values"]), [])
            self.assertEqual(list(app.monster_combo["values"]), [])
            self.assertIn("通信失敗", app.input_status.cget("text"))
        finally:
            root.destroy()

    def test_live_catalog_without_motions_is_visible_and_calculation_stays_disabled(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            app._remote_load_succeeded(
                {
                    "weapons": [{"id": "w", "name": "API武器", "weapon_kind": "bow"}],
                    "monsters": [],
                    "motions": [],
                    "metadata": {
                        "available": True,
                        "complete": False,
                        "missing": ["motion_catalog"],
                        "weapon_count": 1,
                        "monster_count": 0,
                        "motion_count": 0,
                    },
                }
            )
            self.assertEqual(list(app.weapon_combo["values"]), ["API武器"])
            self.assertIn("モーションデータ", app.input_status.cget("text"))
            self.assertTrue(app.calculate_button.instate(["disabled"]))
        finally:
            root.destroy()

    def test_debug_catalog_allows_calculation_and_shows_fixed_value_warning(self):
        root = _create_root_or_skip(self)
        try:
            app = DamageSimulatorApp(root)
            app._remote_load_succeeded(
                {
                    "weapons": [
                        {
                            "id": "w",
                            "name": "API武器",
                            "weapon_kind": "bow",
                            "attack": 200,
                            "element": None,
                        }
                    ],
                    "monsters": [],
                    "motions": [
                        {
                            "id": "debug-bow-fixed-50",
                            "name": "デバッグ固定モーション（50）",
                            "weapon_kind": "bow",
                            "motion_value": 50,
                        }
                    ],
                    "metadata": {
                        "available": True,
                        "complete": True,
                        "debug_motion": True,
                        "debug_motion_value": 50,
                        "weapon_count": 1,
                        "monster_count": 0,
                        "motion_count": 1,
                    },
                }
            )
            self.assertFalse(app.calculate_button.instate(["disabled"]))
            self.assertIn("デバッグモード", app.input_status.cget("text"))
            self.assertIn("50", app.motion_value_label.cget("text"))
        finally:
            root.destroy()


def _walk_widgets(widget: tk.Misc):
    for child in widget.winfo_children():
        yield child
        yield from _walk_widgets(child)


if __name__ == "__main__":
    unittest.main()
