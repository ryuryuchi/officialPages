"""Tkinter UI for the MHWilds one-hit damage calculator."""

from __future__ import annotations

import argparse
import tkinter as tk
import threading
from dataclasses import dataclass
from tkinter import ttk
from typing import Any

from damage_calculator import calculate_damage
from damage_data import (
    DEFAULT_MHDB_MONSTERS_URL,
    DEFAULT_MHDB_WEAPONS_URL,
    DataError,
    fetch_live_catalog,
    load_demo_catalog,
)


MAX_COMPARISONS = 5


@dataclass
class ComparisonEntry:
    """A calculable result and the labels needed to identify it in the table."""

    label: str
    conditions: str
    result: dict[str, Any]


class DamageSimulatorApp:
    """Small presentation layer around the pure calculation/data modules."""

    def __init__(
        self,
        root: tk.Tk,
        *,
        catalog: dict[str, Any] | None = None,
        load_remote: bool = False,
        debug_motion: bool = False,
    ) -> None:
        self.root = root
        self.root.title("MHWilds ダメージ計算")
        self.root.minsize(920, 680)
        self.catalog = catalog or load_demo_catalog()
        self.load_remote = load_remote and catalog is None
        self.debug_motion = debug_motion
        if self.load_remote:
            self.catalog = {
                "weapons": [],
                "monsters": [],
                "motions": [],
                "metadata": {
                    "available": False,
                    "complete": False,
                    "missing": ["MHDB APIデータを読み込み中"],
                    "source_count": 0,
                    "imported_count": 0,
                },
            }
        self.comparisons: list[ComparisonEntry] = []
        self.current_result: dict[str, Any] | None = None
        self._parts_by_label: dict[str, dict[str, Any]] = {}
        self._statuses_by_label: dict[str, dict[str, Any] | None] = {}

        self.weapon_var = tk.StringVar()
        self.weapon_search_var = tk.StringVar()
        self.motion_var = tk.StringVar()
        self.monster_var = tk.StringVar()
        self.monster_search_var = tk.StringVar()
        self.part_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.players_var = tk.StringVar(value="1")
        self.affinity_var = tk.StringVar(value="1.0")
        self.attribute_var = tk.StringVar(value="1.0")
        self.status_var.trace_add("write", self._status_changed)

        self._build_styles()
        self._build_layout()
        self._load_choices()
        if self.load_remote:
            self._start_remote_load()

    def _build_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Yu Gothic UI", 16, "bold"))
        style.configure("Heading.TLabel", font=("Yu Gothic UI", 11, "bold"))
        style.configure("Metric.TLabel", font=("Yu Gothic UI", 18, "bold"))
        style.configure("Error.TLabel", foreground="#a32626")
        style.configure("Hint.TLabel", foreground="#5c5c5c")

    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, padding=16)
        outer.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)

        ttk.Label(
            outer,
            text="MHWilds ダメージ計算",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            outer,
            text="1回の攻撃を対象に、計算式とデータの根拠を追跡できます。",
            style="Hint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        body = ttk.Panedwindow(outer, orient="horizontal")
        body.grid(row=2, column=0, sticky="nsew")
        input_frame = ttk.Frame(body, padding=(0, 0, 10, 0))
        result_frame = ttk.Frame(body, padding=(10, 0, 0, 0))
        body.add(input_frame, weight=1)
        body.add(result_frame, weight=2)
        input_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        result_frame.rowconfigure(2, weight=1)

        self._build_input_panel(input_frame)
        self._build_result_panel(result_frame)

    def _build_input_panel(self, parent: ttk.Frame) -> None:
        data_box = ttk.LabelFrame(parent, text="対象データ", padding=10)
        data_box.grid(row=0, column=0, sticky="ew")
        data_box.columnconfigure(1, weight=1)
        self._entry(data_box, 0, "武器を検索", self.weapon_search_var).bind(
            "<KeyRelease>", self._weapon_search_changed
        )
        self.weapon_combo = self._combo(
            data_box, 1, "武器", self.weapon_var, self._weapon_names()
        )
        self.weapon_combo.bind("<<ComboboxSelected>>", self._weapon_changed)
        self.motion_combo = self._combo(data_box, 2, "攻撃モーション", self.motion_var, [])
        self.motion_combo.bind("<<ComboboxSelected>>", self._motion_changed)
        self.motion_value_label = ttk.Label(data_box, text="—", style="Hint.TLabel")
        self.motion_value_label.grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 3)
        )
        self._entry(data_box, 4, "モンスターを検索", self.monster_search_var).bind(
            "<KeyRelease>", self._monster_search_changed
        )
        self.monster_combo = self._combo(
            data_box, 5, "モンスター", self.monster_var, self._monster_names()
        )
        self.part_combo = self._combo(data_box, 6, "対象部位", self.part_var, [])
        self.part_hint = ttk.Label(data_box, style="Hint.TLabel", wraplength=320)
        self.part_hint.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 3))
        self.status_combo = self._combo(data_box, 8, "状態異常", self.status_var, [])
        self.monster_combo.bind("<<ComboboxSelected>>", self._monster_changed)
        self.part_combo.bind("<<ComboboxSelected>>", self._part_changed)
        self.status_combo.bind("<<ComboboxSelected>>", self._status_changed)
        self.data_hint = ttk.Label(data_box, style="Hint.TLabel", wraplength=320)
        self.data_hint.grid(row=9, column=0, columnspan=2, sticky="w", pady=(8, 0))

        attack_box = ttk.LabelFrame(parent, text="攻撃条件", padding=10)
        attack_box.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        attack_box.columnconfigure(1, weight=1)
        self._entry(attack_box, 0, "会心補正", self.affinity_var)
        self._entry(attack_box, 1, "属性補正", self.attribute_var)
        ttk.Label(
            attack_box,
            text="例: 会心補正 1.25、属性補正 1.0。未対応スキルは適用しません。",
            style="Hint.TLabel",
            wraplength=320,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        quest_box = ttk.LabelFrame(parent, text="クエスト条件", padding=10)
        quest_box.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        quest_box.columnconfigure(1, weight=1)
        self._entry(quest_box, 0, "参加人数 (1〜4)", self.players_var)
        self.quest_hint = ttk.Label(quest_box, style="Hint.TLabel", wraplength=320)
        self.quest_hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        action_box = ttk.Frame(parent)
        action_box.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        action_box.columnconfigure(0, weight=1)
        self.calculate_button = ttk.Button(
            action_box, text="計算する", command=self.calculate
        )
        self.calculate_button.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            action_box, text="入力を初期化", command=self.reset_inputs
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.input_status = ttk.Label(
            parent, text="", style="Error.TLabel", wraplength=350
        )
        self.input_status.grid(row=4, column=0, sticky="w", pady=(8, 0))

    def _build_result_panel(self, parent: ttk.Frame) -> None:
        summary_box = ttk.LabelFrame(parent, text="計算結果", padding=10)
        summary_box.grid(row=0, column=0, sticky="ew")
        summary_box.columnconfigure(0, weight=1)
        self.result_status = ttk.Label(summary_box, text="条件を入力して計算してください。")
        self.result_status.grid(row=0, column=0, sticky="w")
        self.metric_labels: dict[str, ttk.Label] = {}
        metric_frame = ttk.Frame(summary_box)
        metric_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        for column, (key, label) in enumerate(
            (("physical", "物理"), ("element", "属性"), ("total", "合計"))
        ):
            metric_frame.columnconfigure(column, weight=1)
            cell = ttk.Frame(metric_frame)
            cell.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 8, 0),
            )
            ttk.Label(cell, text=label).grid(row=0, column=0, sticky="w")
            value_label = ttk.Label(cell, text="—", style="Metric.TLabel")
            value_label.grid(row=1, column=0, sticky="w")
            self.metric_labels[key] = value_label
        self.add_compare_button = ttk.Button(
            summary_box, text="現在の結果を比較に追加", command=self.add_comparison
        )
        self.add_compare_button.grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.add_compare_button.state(["disabled"])

        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        breakdown_tab = ttk.Frame(notebook, padding=8)
        source_tab = ttk.Frame(notebook, padding=8)
        notebook.add(breakdown_tab, text="計算内訳")
        notebook.add(source_tab, text="データの根拠")
        breakdown_tab.rowconfigure(0, weight=1)
        breakdown_tab.columnconfigure(0, weight=1)
        source_tab.rowconfigure(0, weight=1)
        source_tab.columnconfigure(0, weight=1)
        self.breakdown_text = self._readonly_text(breakdown_tab)
        self.source_text = self._readonly_text(source_tab)

        comparison_box = ttk.LabelFrame(parent, text="比較一覧（最大5件）", padding=8)
        comparison_box.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        comparison_box.rowconfigure(0, weight=1)
        comparison_box.columnconfigure(0, weight=1)
        columns = ("label", "conditions", "physical", "element", "total", "difference")
        self.comparison_tree = ttk.Treeview(
            comparison_box, columns=columns, show="headings", height=6
        )
        headings = {
            "label": "区分",
            "conditions": "条件",
            "physical": "物理",
            "element": "属性",
            "total": "合計",
            "difference": "基準差",
        }
        widths = {
            "label": 54,
            "conditions": 220,
            "physical": 70,
            "element": 70,
            "total": 70,
            "difference": 70,
        }
        for column in columns:
            self.comparison_tree.heading(column, text=headings[column])
            self.comparison_tree.column(column, width=widths[column], anchor="w")
        self.comparison_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            comparison_box, orient="vertical", command=self.comparison_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.comparison_tree.configure(yscrollcommand=scrollbar.set)
        comparison_actions = ttk.Frame(comparison_box)
        comparison_actions.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Button(
            comparison_actions, text="選択を削除", command=self.remove_comparison
        ).grid(row=0, column=0)
        ttk.Button(
            comparison_actions, text="比較を全消去", command=self.clear_comparisons
        ).grid(row=0, column=1, padx=(6, 0))

    @staticmethod
    def _combo(
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        values: list[str],
    ) -> ttk.Combobox:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        combo = ttk.Combobox(
            parent, textvariable=variable, values=values, state="readonly"
        )
        combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=3)
        return combo

    @staticmethod
    def _entry(
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=3)
        return entry

    @staticmethod
    def _readonly_text(parent: ttk.Frame) -> tk.Text:
        text = tk.Text(parent, wrap="word", height=8, state="disabled")
        text.grid(row=0, column=0, sticky="nsew")
        return text

    def _weapon_names(self) -> list[str]:
        return [weapon["name"] for weapon in self.catalog.get("weapons", [])]

    def _monster_names(self) -> list[str]:
        return [monster["name"] for monster in self.catalog.get("monsters", [])]

    def _load_choices(self) -> None:
        weapons = self._weapon_names()
        monsters = self._monster_names()
        self.weapon_combo["values"] = weapons
        self.monster_combo["values"] = monsters
        if weapons:
            self.weapon_var.set(weapons[0])
            self._update_motion_choices()
        if monsters:
            self.monster_var.set(monsters[0])
            self._update_monster_choices()
        self._update_data_hint()
        if not self.catalog.get("metadata", {}).get("complete", False):
            self.calculate_button.state(["disabled"])
            self.input_status.configure(
                text=self._catalog_error_message()
            )
        else:
            self.calculate_button.state(["!disabled"])

    def _catalog_error_message(self) -> str:
        metadata = self.catalog.get("metadata", {})
        details: list[str] = []
        for key in ("missing_ids", "duplicate_ids"):
            values = metadata.get(key, [])
            if values:
                details.append(f"{key}={', '.join(str(value) for value in values)}")
        suffix = f"（{'; '.join(details)}）" if details else ""
        return (
            "データ全件性を確認できないため計算できません。"
            f"{suffix} データを再取得してください。"
        )

    def _find_monster(self) -> dict[str, Any] | None:
        return next(
            (
                monster
                for monster in self.catalog.get("monsters", [])
                if monster["name"] == self.monster_var.get()
            ),
            None,
        )

    def _find_weapon(self) -> dict[str, Any] | None:
        return next(
            (
                weapon
                for weapon in self.catalog.get("weapons", [])
                if weapon["name"] == self.weapon_var.get()
            ),
            None,
        )

    def _update_motion_choices(self) -> None:
        weapon = self._find_weapon()
        weapon_kind = weapon.get("weapon_kind") if weapon else None
        motions = [
            motion
            for motion in self.catalog.get("motions", [])
            if motion.get("weapon_kind") == weapon_kind
        ]
        self._motions_by_label = {motion["name"]: motion for motion in motions}
        names = list(self._motions_by_label)
        self.motion_combo["values"] = names
        self.motion_var.set(names[0] if names else "")
        self._update_motion_value()

    def _update_motion_value(self) -> None:
        motion = getattr(self, "_motions_by_label", {}).get(self.motion_var.get())
        self.motion_value_label.configure(
            text=(
                f"モーション値: {motion['motion_value']}（自動設定・編集不可）"
                if motion
                else "モーション値: —（攻撃モーションを選択してください）"
            )
        )

    def _update_monster_choices(self) -> None:
        monster = self._find_monster()
        if monster is None:
            self.part_combo["values"] = []
            self.status_combo["values"] = []
            return
        self._parts_by_label = {
            part["name"]: part for part in monster.get("parts", [])
        }
        part_names = list(self._parts_by_label)
        self.part_combo["values"] = part_names
        self.part_var.set(part_names[0] if part_names else "")
        self._update_part_hint()
        statuses: dict[str, dict[str, Any] | None] = {"なし": None}
        statuses.update(
            {status["name"]: status for status in monster.get("statuses", [])}
        )
        self._statuses_by_label = statuses
        self.status_combo["values"] = list(statuses)
        self.status_var.set("なし")
        self._update_quest_hint(monster)
        self._update_data_hint()

    def _update_quest_hint(self, monster: dict[str, Any]) -> None:
        corrections = monster.get("quest", {}).get("corrections", [])
        if corrections:
            description = " / ".join(
                f"{item['id']}={item['value']}" for item in corrections
            )
            self.quest_hint.configure(text=f"登録済み補正: {description}")
        else:
            self.quest_hint.configure(text="登録済みの人数補正はありません。")

    def _update_data_hint(self) -> None:
        metadata = self.catalog.get("metadata", {})
        state = "利用可能" if metadata.get("available") else "読み込み中/未取得"
        if metadata.get("debug_motion"):
            state += "（デバッグ固定モーション）"
        self.data_hint.configure(
            text=(
                f"状態: {state} / "
                f"武器: {metadata.get('weapon_count', len(self.catalog.get('weapons', [])))} / "
                f"モンスター: {metadata.get('monster_count', len(self.catalog.get('monsters', [])))} / "
                f"状態異常: {metadata.get('status_count', '不明')} / "
                f"モーション: {metadata.get('motion_count', len(self.catalog.get('motions', [])))} / "
                f"全件: {'確認済み' if metadata.get('complete') else '未確認'}"
            )
        )

    def _start_remote_load(self) -> None:
        self.input_status.configure(text="MHDB APIから全武器・全モンスターを読み込み中です。")

        def worker() -> None:
            try:
                catalog = fetch_live_catalog(
                    debug_motion_value=50 if self.debug_motion else None
                )
            except DataError as error:
                self.root.after(0, lambda: self._remote_load_failed(str(error)))
                return
            self.root.after(0, lambda: self._remote_load_succeeded(catalog))

        threading.Thread(target=worker, daemon=True).start()

    def _remote_load_succeeded(self, catalog: dict[str, Any]) -> None:
        self.catalog = catalog
        self._load_choices()
        if catalog["metadata"].get("debug_motion"):
            self.input_status.configure(
                text=(
                    "デバッグモード: APIデータで計算できます。"
                    "全攻撃モーションの値を仮値50として扱っています。"
                    "実データの計算結果には使用しないでください。"
                )
            )
        elif not catalog["metadata"].get("complete", False):
            self.input_status.configure(
                text=(
                    "APIデータの取得は完了しましたが、計算に必要なモーションデータが未取得です。"
                    "モーションデータを追加するまで計算できません。"
                )
            )

    def _remote_load_failed(self, message: str) -> None:
        self.catalog = {
            "weapons": [],
            "monsters": [],
            "motions": [],
            "metadata": {
                "available": False,
                "complete": False,
                "missing": ["武器・モンスターデータ"],
                "error": message,
                "source_count": 0,
                "imported_count": 0,
            },
        }
        self._load_choices()
        self.input_status.configure(
            text=f"APIデータを取得できませんでした。{message} 再起動して再取得してください。"
        )

    def _monster_changed(self, _event: tk.Event) -> None:
        self._update_monster_choices()

    def _weapon_changed(self, _event: tk.Event) -> None:
        self._update_motion_choices()

    def _weapon_search_changed(self, _event: tk.Event) -> None:
        query = self.weapon_search_var.get().strip().casefold()
        values = [
            name for name in self._weapon_names() if not query or query in name.casefold()
        ]
        self.weapon_combo["values"] = values
        if self.weapon_var.get() not in values:
            self.weapon_var.set(values[0] if values else "")
        self._update_motion_choices()

    def _monster_search_changed(self, _event: tk.Event) -> None:
        query = self.monster_search_var.get().strip().casefold()
        values = [
            name
            for name in self._monster_names()
            if not query or query in name.casefold()
        ]
        self.monster_combo["values"] = values
        if self.monster_var.get() not in values:
            self.monster_var.set(values[0] if values else "")
        self._update_monster_choices()

    def _motion_changed(self, _event: tk.Event) -> None:
        self._update_motion_value()

    def _part_changed(self, _event: tk.Event) -> None:
        self._update_part_hint()
        self._update_data_hint()

    def _update_part_hint(self) -> None:
        part = self._parts_by_label.get(self.part_var.get())
        if part is None:
            self.part_hint.configure(text="肉質データなし")
            return
        element_hitzone = part.get("element_hitzone", {})
        element_text = ", ".join(
            f"{key}:{value}%" for key, value in element_hitzone.items()
        )
        self.part_hint.configure(
            text=(
                f"物理肉質 {part.get('physical_hitzone')}% / "
                f"属性肉質 {element_text or 'なし'}"
            )
        )

    def _status_changed(self, *_args: Any) -> None:
        status = self._statuses_by_label.get(self.status_var.get())
        if status and status.get("verified") is not True:
            self.input_status.configure(
                text="この状態異常の蓄積式は未検証です。ダメージへは適用されません。"
            )
        elif self.input_status.cget("text").startswith("この状態異常の蓄積式"):
            self.input_status.configure(text="")

    @staticmethod
    def _number_or_none(value: str) -> float | None:
        if not value.strip():
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def _build_input(self) -> dict[str, Any]:
        weapon = next(
            (
                weapon
                for weapon in self.catalog.get("weapons", [])
                if weapon["name"] == self.weapon_var.get()
            ),
            None,
        )
        monster = self._find_monster()
        part = self._parts_by_label.get(self.part_var.get())
        status = self._statuses_by_label.get(self.status_var.get())
        motion = getattr(self, "_motions_by_label", {}).get(self.motion_var.get())
        players = self._number_or_none(self.players_var.get())
        return {
            "weapon": weapon,
            "part": part,
            "attack": {
                "motion": motion,
                "affinity_multiplier": self._number_or_none(self.affinity_var.get()),
                "attribute_multiplier": self._number_or_none(
                    self.attribute_var.get()
                ),
            },
            "status": status,
            "quest": (
                {
                    "players": players,
                    "corrections": monster.get("quest", {}).get("corrections", []),
                }
                if monster is not None
                else None
            ),
        }

    def calculate(self) -> None:
        if not self.catalog.get("metadata", {}).get("complete", False):
            self.input_status.configure(
                text=self._catalog_error_message()
            )
            return
        result = calculate_damage(self._build_input())
        self.current_result = result
        self._render_result(result)

    def _render_result(self, result: dict[str, Any]) -> None:
        if result["calculable"]:
            self.result_status.configure(
                text="計算完了。各タブで内訳とデータ根拠を確認できます。"
            )
            for key, label in self.metric_labels.items():
                label.configure(text=f"{result['damages'][key]:,}")
            self.input_status.configure(text="")
            self.add_compare_button.state(["!disabled"])
        else:
            self.result_status.configure(
                text="計算できません。入力と不足データを確認してください。"
            )
            for label in self.metric_labels.values():
                label.configure(text="—")
            messages = result["errors"][:]
            if result["not_applied"]:
                messages.append("未適用: " + ", ".join(result["not_applied"]))
            self.input_status.configure(text="\n".join(messages))
            self.add_compare_button.state(["disabled"])
        self._set_text(self.breakdown_text, self._format_breakdown(result))
        self._set_text(self.source_text, self._format_sources(result))

    @staticmethod
    def _format_breakdown(result: dict[str, Any]) -> str:
        lines: list[str] = []
        for item in result.get("breakdown", []):
            lines.append(f"■ {item.get('label', '項目')}: {item.get('value', '—')}")
            if "inputs" in item:
                lines.append(
                    "  入力: "
                    + ", ".join(
                        f"{key}={value}" for key, value in item["inputs"].items()
                    )
                )
            if "intermediate" in item:
                lines.append(f"  途中値: {item['intermediate']}")
            if item.get("rounding"):
                lines.append(f"  端数処理: {item['rounding']}")
        if result.get("not_applied"):
            lines.append("\n未適用: " + ", ".join(result["not_applied"]))
        return "\n".join(lines) or "計算結果がありません。"

    @staticmethod
    def _format_sources(result: dict[str, Any]) -> str:
        sources = result.get("metadata", [])
        if not sources:
            return "この計算にはデータ根拠が登録されていません。"
        return "\n\n".join(
            "\n".join(
                (
                    f"出典: {source.get('source_url', '不明')}",
                    f"取得時刻: {source.get('retrieved_at', '不明')}",
                    f"データ版: {source.get('data_version', '不明')}",
                    f"利用可否: {'利用可能' if source.get('available') else '利用不可'}",
                    "不足項目: " + (", ".join(source.get("missing", [])) or "なし"),
                )
            )
            for source in sources
        )

    @staticmethod
    def _set_text(widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def _condition_label(self) -> str:
        motion = getattr(self, "_motions_by_label", {}).get(self.motion_var.get())
        motion_label = motion["name"] if motion else "未選択"
        return (
            f"{self.weapon_var.get()} / {self.monster_var.get()} "
            f"{self.part_var.get()} / {motion_label}"
        )

    def add_comparison(self) -> None:
        if not self.current_result or not self.current_result.get("calculable"):
            return
        if len(self.comparisons) >= MAX_COMPARISONS:
            self.input_status.configure(
                text="比較対象は最大5件までです。不要な結果を削除してください。"
            )
            return
        self.comparisons.append(
            ComparisonEntry(
                label="基準" if not self.comparisons else f"比較{len(self.comparisons)}",
                conditions=self._condition_label(),
                result=self.current_result,
            )
        )
        self._render_comparisons()

    def remove_comparison(self) -> None:
        selected = self.comparison_tree.selection()
        if not selected:
            return
        index = int(selected[0])
        self.comparisons.pop(index)
        for position, entry in enumerate(self.comparisons):
            entry.label = "基準" if position == 0 else f"比較{position}"
        self._render_comparisons()

    def clear_comparisons(self) -> None:
        self.comparisons.clear()
        self._render_comparisons()

    def _render_comparisons(self) -> None:
        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)
        base_total = (
            self.comparisons[0].result["damages"]["total"]
            if self.comparisons
            else None
        )
        for index, entry in enumerate(self.comparisons):
            damages = entry.result["damages"]
            difference = 0 if index == 0 else damages["total"] - base_total
            self.comparison_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    entry.label,
                    entry.conditions,
                    damages["physical"],
                    damages["element"],
                    damages["total"],
                    f"{difference:+d}",
                ),
            )

    def reset_inputs(self) -> None:
        self.weapon_search_var.set("")
        self.monster_search_var.set("")
        self.weapon_combo["values"] = self._weapon_names()
        self.monster_combo["values"] = self._monster_names()
        self._update_motion_choices()
        self._update_motion_value()
        self.affinity_var.set("1.0")
        self.attribute_var.set("1.0")
        self.players_var.set("1")
        if self.monster_var.get():
            self._update_monster_choices()
        self.current_result = None
        self.input_status.configure(text="")
        self.result_status.configure(text="条件を入力して計算してください。")
        for label in self.metric_labels.values():
            label.configure(text="—")
        self._set_text(self.breakdown_text, "計算結果がありません。")
        self._set_text(self.source_text, "計算結果がありません。")
        self.add_compare_button.state(["disabled"])


def create_app(
    catalog: dict[str, Any] | None = None,
    *,
    load_remote: bool = False,
    debug_motion: bool = False,
) -> DamageSimulatorApp:
    """Create the app for manual use or a small UI smoke test."""
    root = tk.Tk()
    return DamageSimulatorApp(
        root,
        catalog=catalog,
        load_remote=load_remote,
        debug_motion=debug_motion,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MHWildsダメージ計算")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="モーション値50のデバッグ固定値を明示的に有効化",
    )
    args = parser.parse_args()
    app = create_app(load_remote=True, debug_motion=args.debug)
    app.root.mainloop()
