"""Monster Hunter Wilds equipment simulator using the public Wilds API."""

from __future__ import annotations

import itertools
import json
import threading
import tkinter as tk
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any


API_BASE_URL = "https://wilds.mhdb.io/ja"
REQUEST_TIMEOUT_SECONDS = 30
ARMOR_KINDS = ("head", "chest", "arms", "waist", "legs")
ARMOR_LABELS = {"head": "頭", "chest": "胴", "arms": "腕", "waist": "腰", "legs": "脚"}
RESISTANCE_LABELS = {"fire": "火", "water": "水", "thunder": "雷", "ice": "氷", "dragon": "龍"}
MAX_TARGET_SKILLS = 20
MAX_ARMOR_PER_PART = 24
MAX_PARTIAL_BUILDS = 450
MAX_CHARM_CANDIDATES = 320
MAX_RANDOM_GROUP_CHOICES = 12
MAX_RESULTS = 20
CHARM_TABLE_PATH = Path(__file__).parent / "data" / "random-charm-table.json"


@dataclass(frozen=True)
class SkillTarget:
    """A skill level requested by the player."""

    id: int
    name: str
    level: int


@dataclass(frozen=True)
class CharmCandidate:
    """A fixed or theoretical charm usable by the search engine."""

    name: str
    source: str
    skills: dict[int, int]
    slots: tuple[tuple[str, int], ...]


@dataclass
class PartialBuild:
    """An incremental armor combination maintained by bounded search."""

    armor: list[dict[str, Any]]
    totals: dict[int, int]
    defense: int
    resistances: dict[str, int]
    slots: list[tuple[str, int]]


@dataclass
class BuildResult:
    """A complete build result rendered in the UI."""

    armor: list[dict[str, Any]]
    charm: CharmCandidate
    weapon: dict[str, Any] | None
    totals: dict[int, int]
    defense: int
    resistances: dict[str, int]
    decorations: list[dict[str, Any]]
    empty_slots: list[tuple[str, int]]
    fulfilled: int


def request_json(url: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Retrieve a JSON object or list and validate its top-level shape."""
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "WildsTkSimulator/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Wilds API がエラーを返しました（HTTP {error.code}）。") from error
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("Wilds API に接続できませんでした。通信状態を確認してください。") from error
    if not isinstance(payload, (list, dict)):
        raise RuntimeError("Wilds API から予想外の形式のデータが返されました。")
    return payload


def load_data() -> dict[str, Any]:
    """Load the local charm table and the API resources needed for searches."""
    try:
        charm_table = json.loads(CHARM_TABLE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"ローカル護石テーブルを読み込めません: {error}") from error
    if not isinstance(charm_table, dict):
        raise RuntimeError("ローカル護石テーブルの形式が不正です。")

    data: dict[str, Any] = {"charmTable": charm_table}
    for key in ("armor", "charms", "decorations", "skills", "weapons"):
        payload = request_json(f"{API_BASE_URL}/{key}")
        if not isinstance(payload, list):
            raise RuntimeError(f"{key} のAPIデータが配列ではありません。")
        data[key] = payload
    return data


def skill_totals(skills: list[dict[str, Any]]) -> dict[int, int]:
    """Aggregate the skill IDs and levels stored by Wilds API objects."""
    totals: dict[int, int] = {}
    for entry in skills:
        skill = entry.get("skill")
        level = entry.get("level")
        if isinstance(skill, dict) and isinstance(skill.get("id"), int) and isinstance(level, int):
            skill_id = skill["id"]
            totals[skill_id] = totals.get(skill_id, 0) + level
    return totals


def add_totals(target: dict[int, int], addition: dict[int, int]) -> dict[int, int]:
    """Add skill levels to a mutable total and return it for composition."""
    for skill_id, level in addition.items():
        target[skill_id] = target.get(skill_id, 0) + level
    return target


class BuildEngine:
    """Finds strong equipment candidates through bounded, target-driven search."""

    def __init__(self, data: dict[str, Any], targets: list[SkillTarget]) -> None:
        self.armor: list[dict[str, Any]] = data["armor"]
        self.charms: list[dict[str, Any]] = data["charms"]
        self.decorations: list[dict[str, Any]] = data["decorations"]
        self.targets = targets
        self.target_levels = {target.id: target.level for target in targets}
        self.target_decorations = [
            (decoration, decoration_skills)
            for decoration in self.decorations
            for decoration_skills in [skill_totals(decoration.get("skills", []))]
            if any(skill_id in self.target_levels for skill_id in decoration_skills)
        ]
        table: dict[str, Any] = data["charmTable"]
        self.skill_groups = {
            group["id"]: group["entries"] for group in table["skillGroups"]
        }
        self.roll_patterns: list[dict[str, Any]] = table["rollPatterns"]

    def target_score(self, totals: dict[int, int]) -> int:
        return sum(
            min(totals.get(target.id, 0), target.level) * 100 for target in self.targets
        )

    def targets_met(self, totals: dict[int, int]) -> bool:
        return all(totals.get(target.id, 0) >= target.level for target in self.targets)

    def armor_score(self, armor: dict[str, Any]) -> float:
        defense = armor.get("defense", {})
        slots = armor.get("slots", [])
        return (
            self.target_score(skill_totals(armor.get("skills", [])))
            + sum(slot * 3 for slot in slots if isinstance(slot, int))
            + int(defense.get("max", 0)) / 20
        )

    def fixed_charm_candidates(self) -> list[CharmCandidate]:
        candidates: list[CharmCandidate] = []
        for charm in self.charms:
            for rank in charm.get("ranks", []):
                candidates.append(
                    CharmCandidate(
                        name=str(rank.get("name", "名称不明の護石")),
                        source="固定護石",
                        skills=skill_totals(rank.get("skills", [])),
                        slots=(),
                    )
                )
        return candidates

    def random_charm_candidates(self) -> list[CharmCandidate]:
        candidates: dict[tuple[Any, ...], CharmCandidate] = {}
        for pattern in self.roll_patterns:
            choices: list[list[dict[str, Any] | None]] = []
            for group_id in pattern["skillGroupIds"]:
                matching = [
                    entry for entry in self.skill_groups[group_id]
                    if entry["id"] in self.target_levels
                ]
                matching.sort(
                    key=lambda entry: (
                        self.target_levels[entry["id"]] * 100 + entry["level"]
                    ),
                    reverse=True,
                )
                choices.append([None, *matching[:MAX_RANDOM_GROUP_CHOICES]])

            for selected in itertools.product(*choices):
                entries = [entry for entry in selected if entry is not None]
                if not entries or len({entry["id"] for entry in entries}) != len(entries):
                    continue
                skills = {entry["id"]: entry["level"] for entry in entries}
                for slot_pattern in pattern["slotPatterns"]:
                    slots = tuple((slot["kind"], slot["level"]) for slot in slot_pattern)
                    key = (pattern["rarity"], tuple(sorted(skills.items())), slots)
                    candidates[key] = CharmCandidate(
                        name=f"レア{pattern['rarity']} 理論護石",
                        source="理論護石",
                        skills=skills,
                        slots=slots,
                    )
        return list(candidates.values())

    def choose_decorations(
        self, totals: dict[int, int], slots: list[tuple[str, int]]
    ) -> tuple[list[dict[str, Any]], list[tuple[str, int]]]:
        available_slots = list(slots)
        selected: list[dict[str, Any]] = []
        while not self.targets_met(totals):
            best: tuple[dict[str, Any], dict[int, int], int, int] | None = None
            for decoration, decoration_skills in self.target_decorations:
                slot_level = decoration.get("slot")
                slot_kind = decoration.get("kind")
                if not isinstance(slot_level, int) or not isinstance(slot_kind, str):
                    continue
                slot_index = next(
                    (
                        index
                        for index, (kind, level) in enumerate(available_slots)
                        if kind == slot_kind and level >= slot_level
                    ),
                    None,
                )
                if slot_index is None:
                    continue
                gain = sum(
                    min(
                        max(0, self.target_levels[skill_id] - totals.get(skill_id, 0)),
                        level,
                    )
                    for skill_id, level in decoration_skills.items()
                    if skill_id in self.target_levels
                )
                if gain and (
                    best is None
                    or gain > best[3]
                    or (gain == best[3] and slot_level < best[0]["slot"])
                ):
                    best = (decoration, decoration_skills, slot_index, gain)
            if best is None:
                break
            decoration, decoration_skills, slot_index, _ = best
            add_totals(totals, decoration_skills)
            available_slots.pop(slot_index)
            selected.append(decoration)
        return selected, available_slots

    def search(
        self,
        rank: str,
        weapon: dict[str, Any] | None,
        include_fixed_charms: bool,
        include_random_charms: bool,
    ) -> list[BuildResult]:
        candidates_by_kind: dict[str, list[dict[str, Any]]] = {}
        for kind in ARMOR_KINDS:
            candidates = [
                armor
                for armor in self.armor
                if armor.get("kind") == kind and (rank == "all" or armor.get("rank") == rank)
            ]
            candidates_by_kind[kind] = sorted(
                candidates, key=self.armor_score, reverse=True
            )[:MAX_ARMOR_PER_PART]
        if any(not candidates for candidates in candidates_by_kind.values()):
            raise ValueError("指定した防具ランクには全5部位のデータがありません。")

        partial_limit = 160 if len(self.targets) > 8 else MAX_PARTIAL_BUILDS
        partials = [
            PartialBuild(
                armor=[],
                totals={},
                defense=0,
                resistances={key: 0 for key in RESISTANCE_LABELS},
                slots=[],
            )
        ]
        for kind in ARMOR_KINDS:
            next_partials: list[PartialBuild] = []
            for partial in partials:
                for armor in candidates_by_kind[kind]:
                    resistances = armor.get("resistances", {})
                    defense = armor.get("defense", {})
                    next_partials.append(
                        PartialBuild(
                            armor=[*partial.armor, armor],
                            totals=add_totals(
                                dict(partial.totals), skill_totals(armor.get("skills", []))
                            ),
                            defense=partial.defense + int(defense.get("max", 0)),
                            resistances={
                                key: partial.resistances[key] + int(resistances.get(key, 0))
                                for key in RESISTANCE_LABELS
                            },
                            slots=[
                                *partial.slots,
                                *[("armor", level) for level in armor.get("slots", [])],
                            ],
                        )
                    )
            partials = sorted(
                next_partials,
                key=lambda item: self.target_score(item.totals) + item.defense / 20,
                reverse=True,
            )[:partial_limit]

        charms: list[CharmCandidate] = []
        if include_fixed_charms:
            charms.extend(self.fixed_charm_candidates())
        if include_random_charms:
            charms.extend(self.random_charm_candidates())
        if not charms:
            charms = [CharmCandidate("護石なし", "なし", {}, ())]

        charm_limit = 72 if len(self.targets) > 8 else MAX_CHARM_CANDIDATES
        charms = sorted(
            charms, key=lambda charm: self.target_score(charm.skills), reverse=True
        )[:charm_limit]
        weapon_skills = skill_totals(weapon.get("skills", [])) if weapon else {}
        weapon_slots = [
            ("weapon", level) for level in weapon.get("slots", [])
        ] if weapon else []

        results: list[BuildResult] = []
        for partial in partials:
            for charm in charms:
                totals = add_totals(add_totals(dict(partial.totals), weapon_skills), charm.skills)
                decorations, empty_slots = self.choose_decorations(
                    totals, [*partial.slots, *weapon_slots, *charm.slots]
                )
                fulfilled = sum(
                    totals.get(target.id, 0) >= target.level for target in self.targets
                )
                results.append(
                    BuildResult(
                        armor=partial.armor,
                        charm=charm,
                        weapon=weapon,
                        totals=totals,
                        defense=partial.defense,
                        resistances=partial.resistances,
                        decorations=decorations,
                        empty_slots=empty_slots,
                        fulfilled=fulfilled,
                    )
                )
        return sorted(
            results,
            key=lambda result: (
                result.fulfilled,
                self.target_score(result.totals),
                result.defense,
            ),
            reverse=True,
        )[:MAX_RESULTS]


class WildsSimulatorApp(ttk.Frame):
    """Tkinter UI for configuring a search and inspecting matching builds."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.data: dict[str, Any] | None = None
        self.targets: list[SkillTarget] = []
        self.results: list[BuildResult] = []
        self.rank_var = tk.StringVar(value="high")
        self.weapon_kind_var = tk.StringVar()
        self.weapon_var = tk.StringVar()
        self.skill_var = tk.StringVar()
        self.level_var = tk.StringVar(value="1")
        self.fixed_charms_var = tk.BooleanVar(value=True)
        self.random_charms_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="データを読み込み中…")
        self._build_ui()
        self.pack(fill="both", expand=True)
        threading.Thread(target=self._load_data, daemon=True).start()

    def _build_ui(self) -> None:
        self.master.title("Wilds Build Finder")
        self.master.minsize(920, 650)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        conditions = ttk.LabelFrame(self, text="検索条件", padding=10)
        conditions.grid(row=0, column=0, sticky="ew")
        for column in range(5):
            conditions.columnconfigure(column, weight=1)
        ttk.Label(conditions, text="防具ランク").grid(row=0, column=0, sticky="w")
        self.rank_box = ttk.Combobox(
            conditions, textvariable=self.rank_var, values=("high", "low", "all"), state="readonly"
        )
        self.rank_box.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        ttk.Label(conditions, text="武器種").grid(row=0, column=1, sticky="w")
        self.weapon_kind_box = ttk.Combobox(
            conditions, textvariable=self.weapon_kind_var, state="disabled"
        )
        self.weapon_kind_box.grid(row=1, column=1, padx=8, sticky="ew")
        self.weapon_kind_box.bind("<<ComboboxSelected>>", self._update_weapon_options)
        ttk.Label(conditions, text="武器（任意）").grid(row=0, column=2, columnspan=2, sticky="w")
        self.weapon_box = ttk.Combobox(conditions, textvariable=self.weapon_var, state="disabled")
        self.weapon_box.grid(row=1, column=2, columnspan=2, padx=8, sticky="ew")
        ttk.Checkbutton(conditions, text="固定護石を含める", variable=self.fixed_charms_var).grid(row=1, column=4, sticky="w")
        ttk.Checkbutton(conditions, text="理論護石を含める", variable=self.random_charms_var).grid(row=2, column=4, sticky="w")

        target_frame = ttk.LabelFrame(self, text="目標スキル（最大20件）", padding=10)
        target_frame.grid(row=1, column=0, pady=10, sticky="ew")
        target_frame.columnconfigure(0, weight=1)
        self.skill_box = ttk.Combobox(target_frame, textvariable=self.skill_var, state="disabled")
        self.skill_box.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.level_box = ttk.Spinbox(target_frame, from_=1, to=10, textvariable=self.level_var, state="disabled", width=5)
        self.level_box.grid(row=0, column=1, padx=8)
        self.add_button = ttk.Button(target_frame, text="追加 / 更新", command=self._add_target, state="disabled")
        self.add_button.grid(row=0, column=2, padx=8)
        ttk.Button(target_frame, text="選択を削除", command=self._remove_target).grid(row=0, column=3, padx=(8, 0))
        self.target_list = tk.Listbox(target_frame, height=5, exportselection=False)
        self.target_list.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="ew")

        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        ttk.Label(actions, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        self.search_button = ttk.Button(actions, text="装備を検索", command=self._start_search, state="disabled")
        self.search_button.grid(row=0, column=1, sticky="e")

        result_frame = ttk.LabelFrame(self, text="候補装備（最大20件）", padding=10)
        result_frame.grid(row=3, column=0, pady=(10, 0), sticky="nsew")
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        columns = ("charm", "source", "fulfilled", "defense", "resistances")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=10)
        headings = {"charm": "護石", "source": "種別", "fulfilled": "達成", "defense": "防御力", "resistances": "耐性"}
        widths = {"charm": 210, "source": 80, "fulfilled": 70, "defense": 80, "resistances": 240}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self._show_result_details)
        self.details = tk.Text(result_frame, height=10, wrap="word", state="disabled")
        self.details.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _load_data(self) -> None:
        try:
            data = load_data()
        except RuntimeError as error:
            self.after(0, lambda: self._show_load_error(str(error)))
            return
        self.after(0, lambda: self._finish_loading(data))

    def _show_load_error(self, message: str) -> None:
        self.status_var.set(message)
        messagebox.showerror("データ取得エラー", message, parent=self.master)

    def _finish_loading(self, data: dict[str, Any]) -> None:
        self.data = data
        skills = sorted(data["skills"], key=lambda skill: skill["name"])
        self.skill_box.configure(values=[skill["name"] for skill in skills], state="readonly")
        self.skill_var.set(skills[0]["name"])
        self.level_box.configure(state="normal")
        self.add_button.configure(state="normal")
        self.search_button.configure(state="normal")
        kinds = sorted({weapon["kind"] for weapon in data["weapons"]})
        self.weapon_kind_box.configure(values=["指定なし", *kinds], state="readonly")
        self.weapon_kind_var.set("指定なし")
        self._update_weapon_options()
        self.status_var.set("データを読み込みました。目標スキルを追加して検索してください。")

    def _update_weapon_options(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        if self.data is None:
            return
        kind = self.weapon_kind_var.get()
        weapons = [
            weapon for weapon in self.data["weapons"]
            if kind == "指定なし" or weapon["kind"] == kind
        ]
        weapons.sort(key=lambda weapon: weapon["name"])
        self.weapon_box.configure(values=["武器なし", *[weapon["name"] for weapon in weapons]], state="readonly")
        self.weapon_var.set("武器なし")

    def _add_target(self) -> None:
        if self.data is None:
            return
        try:
            level = int(self.level_var.get())
        except ValueError:
            self.status_var.set("必要Lvは1以上の整数で指定してください。")
            return
        if level < 1:
            self.status_var.set("必要Lvは1以上で指定してください。")
            return
        skill = next((item for item in self.data["skills"] if item["name"] == self.skill_var.get()), None)
        if skill is None:
            self.status_var.set("目標スキルを選択してください。")
            return
        target = SkillTarget(id=skill["id"], name=skill["name"], level=level)
        for index, existing in enumerate(self.targets):
            if existing.id == target.id:
                self.targets[index] = target
                self._render_targets()
                return
        if len(self.targets) == MAX_TARGET_SKILLS:
            self.status_var.set(f"目標スキルは{MAX_TARGET_SKILLS}件までです。")
            return
        self.targets.append(target)
        self._render_targets()

    def _remove_target(self) -> None:
        selection = self.target_list.curselection()
        if not selection:
            self.status_var.set("削除する目標スキルを選択してください。")
            return
        self.targets.pop(selection[0])
        self._render_targets()

    def _render_targets(self) -> None:
        self.target_list.delete(0, tk.END)
        for target in self.targets:
            self.target_list.insert(tk.END, f"{target.name} Lv{target.level}")
        self.status_var.set(f"目標スキル {len(self.targets)} / {MAX_TARGET_SKILLS} 件")

    def _start_search(self) -> None:
        if not self.targets:
            self.status_var.set("少なくとも1つの目標スキルを追加してください。")
            return
        if self.data is None:
            self.status_var.set("データを読み込み中です。")
            return
        self.search_button.configure(state="disabled")
        self.status_var.set("候補を探索中…")
        weapon_name = self.weapon_var.get()
        weapon = next(
            (item for item in self.data["weapons"] if item["name"] == weapon_name), None
        )
        arguments = (
            self.rank_var.get(),
            weapon,
            self.fixed_charms_var.get(),
            self.random_charms_var.get(),
        )
        threading.Thread(target=self._search_worker, args=arguments, daemon=True).start()

    def _search_worker(
        self,
        rank: str,
        weapon: dict[str, Any] | None,
        fixed_charms: bool,
        random_charms: bool,
    ) -> None:
        try:
            results = BuildEngine(self.data, list(self.targets)).search(
                rank, weapon, fixed_charms, random_charms
            )
        except ValueError as error:
            self.after(0, lambda: self._finish_search([], str(error)))
            return
        self.after(0, lambda: self._finish_search(results, ""))

    def _finish_search(self, results: list[BuildResult], error: str) -> None:
        self.search_button.configure(state="normal")
        self.results = results
        self.tree.delete(*self.tree.get_children())
        if error:
            self.status_var.set(error)
            return
        for index, result in enumerate(results):
            resistances = " / ".join(
                f"{RESISTANCE_LABELS[key]} {value:+d}"
                for key, value in result.resistances.items()
            )
            self.tree.insert(
                "", "end", iid=str(index),
                values=(
                    result.charm.name, result.charm.source,
                    f"{result.fulfilled}/{len(self.targets)}",
                    result.defense, resistances,
                ),
            )
        complete = sum(result.fulfilled == len(self.targets) for result in results)
        self.status_var.set(
            f"{len(results)}件を表示。条件達成候補: {complete}件"
            if complete else "条件をすべて満たす候補は見つかりませんでした。上位候補を表示しています。"
        )
        if results:
            self.tree.selection_set("0")
            self._show_result_details()

    def _show_result_details(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        result = self.results[int(selection[0])]
        target_lines = "\n".join(
            f"  {target.name}: Lv{result.totals.get(target.id, 0)} / Lv{target.level}"
            for target in self.targets
        )
        equipment = "\n".join(
            f"  {ARMOR_LABELS[armor['kind']]}: {armor['name']}" for armor in result.armor
        )
        decorations = " / ".join(item["name"] for item in result.decorations) or "なし"
        slots = " ".join(
            f"{'武' if kind == 'weapon' else '防'}{level}"
            for kind, level in result.empty_slots
        ) or "なし"
        text = (
            f"目標スキル\n{target_lines}\n\n装備\n{equipment}\n"
            f"  護石: {result.charm.name}（{result.charm.source}）\n"
            f"  武器: {result.weapon['name'] if result.weapon else '指定なし'}\n\n"
            f"装飾品: {decorations}\n空きスロット: {slots}"
        )
        self.details.configure(state="normal")
        self.details.delete("1.0", tk.END)
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    WildsSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
