"""Deterministic, side-effect-free damage calculation rules.

The input is intentionally a mapping so it can be serialized by the UI or a
future API.  Every numeric result is rounded down only at the documented
component boundary:

    physical = floor(attack * motion% * affinity * physical hitzone%)
    element  = floor(element * attribute multiplier * element hitzone%)

Percentages are represented as whole numbers (70 means 70%).  A correction is
only applied when it is explicitly verified and has a supported scope.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping


SUPPORTED_CORRECTION_SCOPES = {"physical", "element", "total", "status"}


@dataclass(frozen=True)
class CalculationInput:
    """Typed representation of the calculator input boundary."""

    weapon: Mapping[str, Any] | None
    part: Mapping[str, Any] | None
    attack: Mapping[str, Any] | None
    status: Mapping[str, Any] | None = None
    quest: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class DamageResult:
    """Stable result model used by the UI and comparison layer."""

    calculable: bool
    damages: dict[str, int]
    errors: list[str]
    missing: list[str]
    invalid: list[str]
    not_applied: list[str]
    applied_corrections: list[str]
    breakdown: list[dict[str, Any]]
    status: dict[str, Any] | None
    quest: dict[str, Any] | None
    metadata: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        result = {
            "calculable": self.calculable,
            "damages": dict(self.damages),
            "errors": list(self.errors),
            "missing": list(self.missing),
            "invalid": list(self.invalid),
            "not_applied": list(self.not_applied),
            "applied_corrections": list(self.applied_corrections),
            "breakdown": list(self.breakdown),
            "status": self.status,
            "quest": self.quest,
            "metadata": list(self.metadata),
        }
        result.update(
            {
                "physical": self.damages.get("physical"),
                "element": self.damages.get("element"),
                "total": self.damages.get("total"),
            }
        )
        return result


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(
        float(value)
    )


def _read_number(
    record: Mapping[str, Any],
    key: str,
    label: str,
    errors: list[str],
    invalid: list[str],
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    default: float | None = None,
) -> float | None:
    if key not in record or record[key] is None:
        if default is not None:
            return default
        errors.append(f"{label}を入力してください。")
        return None
    value = record[key]
    if not _is_number(value):
        invalid.append(key)
        errors.append(f"{label}は数値で入力してください。")
        return None
    if minimum is not None and value < minimum:
        invalid.append(key)
        errors.append(f"{label}は{minimum:g}以上で入力してください。")
        return None
    if maximum is not None and value > maximum:
        invalid.append(key)
        errors.append(f"{label}は{maximum:g}以下で入力してください。")
        return None
    return float(value)


def _corrections(
    attack: Mapping[str, Any],
    quest: Mapping[str, Any] | None,
    *,
    not_applied: list[str],
    applied: list[str],
    errors: list[str],
    breakdown: list[dict[str, Any]],
) -> dict[str, float]:
    """Collect verified scoped multipliers without silently applying unknown data."""
    multipliers = {"physical": 1.0, "element": 1.0, "total": 1.0}
    candidates: list[Mapping[str, Any]] = []
    for key in ("corrections",):
        raw = attack.get(key, [])
        if raw is None:
            continue
        if not isinstance(raw, list):
            errors.append("攻撃補正は配列で指定してください。")
            continue
        for item in raw:
            if not isinstance(item, Mapping):
                errors.append("攻撃補正の各項目はオブジェクトで指定してください。")
                continue
            candidates.append(item)
    if quest is not None:
        raw_quest = quest.get("corrections", [])
        if not isinstance(raw_quest, list):
            errors.append("クエスト補正は配列で指定してください。")
        else:
            for item in raw_quest:
                if not isinstance(item, Mapping):
                    errors.append("クエスト補正の各項目はオブジェクトで指定してください。")
                    continue
                candidates.append(item)

    for correction in candidates:
        correction_id = correction.get("id")
        value = correction.get("value")
        if not isinstance(correction_id, str) or not correction_id.strip():
            errors.append("補正の識別子が不足しています。")
            continue
        if not _is_number(value) or value < 0:
            errors.append(f"補正 {correction_id} の値が不正です。")
            continue
        if correction.get("verified") is not True:
            not_applied.append(correction_id)
            continue
        scope = correction.get("scope")
        if scope is None and correction_id.startswith("status-"):
            scope = "status"
        if scope not in SUPPORTED_CORRECTION_SCOPES:
            not_applied.append(correction_id)
            continue
        applied.append(correction_id)
        if scope == "status":
            breakdown.append(
                {
                    "label": f"検証済み補正: {correction_id}",
                    "value": float(value),
                    "scope": scope,
                    "rounding": "状態異常式未検証のため条件のみ記録し、ダメージへは適用しない",
                }
            )
            continue
        multipliers[scope] *= float(value)
        breakdown.append(
            {
                "label": f"検証済み補正: {correction_id}",
                "value": float(value),
                "scope": scope,
                "rounding": "補正適用後に各ダメージを切り捨て",
            }
        )
    return multipliers


def calculate_damage(input_data: Mapping[str, Any] | CalculationInput) -> dict[str, Any]:
    """Calculate one attack and return a complete, inspection-friendly result."""
    if isinstance(input_data, CalculationInput):
        weapon = input_data.weapon
        part = input_data.part
        attack = input_data.attack
        status = input_data.status
        quest = input_data.quest
    else:
        weapon = input_data.get("weapon") if isinstance(input_data, Mapping) else None
        part = input_data.get("part") if isinstance(input_data, Mapping) else None
        attack = input_data.get("attack") if isinstance(input_data, Mapping) else None
        status = input_data.get("status") if isinstance(input_data, Mapping) else None
        quest = input_data.get("quest") if isinstance(input_data, Mapping) else None

    errors: list[str] = []
    missing: list[str] = []
    invalid: list[str] = []
    not_applied: list[str] = []
    applied: list[str] = []
    breakdown: list[dict[str, Any]] = []
    metadata_records: list[dict[str, Any]] = []

    for record, label, key in (
        (weapon, "武器", "weapon"),
        (part, "部位", "part"),
        (attack, "攻撃条件", "attack"),
    ):
        if not isinstance(record, Mapping):
            missing.append(key)
            errors.append(f"{label}を選択してください。")

    if not isinstance(weapon, Mapping) or not isinstance(part, Mapping) or not isinstance(
        attack, Mapping
    ):
        return DamageResult(
            False,
            {},
            errors,
            missing,
            invalid,
            not_applied,
            applied,
            breakdown,
            dict(status) if isinstance(status, Mapping) else None,
            dict(quest) if isinstance(quest, Mapping) else None,
            metadata_records,
        ).as_dict()

    for record in (weapon, part):
        record_metadata = record.get("metadata")
        if isinstance(record_metadata, Mapping):
            metadata_records.append(dict(record_metadata))

    attack_value = _read_number(
        weapon, "attack", "武器攻撃力", errors, invalid, minimum=0
    )
    element_record = weapon.get("element")
    element_value = 0.0
    element_type: str | None = None
    if element_record is None or (
        _is_number(element_record) and float(element_record) == 0
    ):
        element_value = 0.0
    elif _is_number(element_record):
        # Keep the compact fixture contract usable for element-type-neutral
        # calculations. Normalized source data should use {type, value}.
        element_value = float(element_record)
        element_type = ""
    elif not isinstance(element_record, Mapping):
        invalid.append("element")
        errors.append("武器属性の形式が不正です。")
    else:
        element_type = element_record.get("type")
        if not isinstance(element_type, str) or not element_type.strip():
            invalid.append("element.type")
            errors.append("武器属性の種類が不正です。")
        element_read = _read_number(
            element_record,
            "value",
            "武器属性値",
            errors,
            invalid,
            minimum=0,
        )
        if element_read is not None:
            element_value = element_read

    physical_hitzone = _read_number(
        part,
        "physical_hitzone",
        "物理肉質",
        errors,
        invalid,
        minimum=0,
        maximum=100,
    )
    raw_element_hitzone = part.get("element_hitzone")
    if _is_number(raw_element_hitzone) and element_type in (None, ""):
        element_hitzone = _read_number(
            {"hitzone": raw_element_hitzone},
            "hitzone",
            "属性肉質",
            errors,
            invalid,
            minimum=0,
            maximum=100,
        )
    elif not isinstance(raw_element_hitzone, Mapping):
        missing.append("element_hitzone")
        errors.append("属性肉質が不足しているため計算できません。")
        element_hitzone = None
    elif element_type is None or element_type == "":
        element_hitzone = 0.0
    elif element_type not in raw_element_hitzone:
        missing.append(f"element_hitzone.{element_type}")
        errors.append(f"{element_type}属性の属性肉質が不足しているため計算できません。")
        element_hitzone = None
    else:
        element_hitzone = _read_number(
            raw_element_hitzone,
            element_type,
            f"{element_type}属性肉質",
            errors,
            invalid,
            minimum=0,
            maximum=100,
        )

    weapon_kind = weapon.get("weapon_kind")
    motion = attack.get("motion")
    motion_value: float | None = None
    motion_id: str | None = None
    motion_name: str | None = None
    if not isinstance(motion, Mapping):
        missing.append("motion")
        errors.append("攻撃モーションを選択してください。モーション値の直接入力はできません。")
    else:
        motion_metadata = motion.get("metadata")
        if isinstance(motion_metadata, Mapping):
            metadata_records.append(dict(motion_metadata))
        motion_id = motion.get("id")
        motion_name = motion.get("name")
        motion_kind = motion.get("weapon_kind")
        if not isinstance(motion_id, str) or not motion_id.strip():
            invalid.append("motion.id")
            errors.append("攻撃モーションの識別子が不正です。")
        if not isinstance(motion_name, str) or not motion_name.strip():
            invalid.append("motion.name")
            errors.append("攻撃モーション名が不正です。")
        if not isinstance(weapon_kind, str) or not weapon_kind.strip():
            invalid.append("weapon.weapon_kind")
            errors.append("武器種が不明なためモーションを対応付けできません。")
        elif motion_kind != weapon_kind:
            invalid.append("motion.weapon_kind")
            errors.append("武器種と攻撃モーションが一致しません。")
        motion_value = _read_number(
            motion,
            "motion_value",
            "モーション値",
            errors,
            invalid,
            minimum=0,
            maximum=1000,
        )
    affinity_multiplier = _read_number(
        attack,
        "affinity_multiplier",
        "会心補正",
        errors,
        invalid,
        minimum=0,
        maximum=3,
        default=1.0,
    )
    attribute_multiplier = _read_number(
        attack,
        "attribute_multiplier",
        "属性補正",
        errors,
        invalid,
        minimum=0,
        maximum=3,
        default=1.0,
    )

    multipliers = _corrections(
        attack,
        quest if isinstance(quest, Mapping) else None,
        not_applied=not_applied,
        applied=applied,
        errors=errors,
        breakdown=breakdown,
    )
    if status is not None:
        if not isinstance(status, Mapping):
            errors.append("状態異常の形式が不正です。")
        else:
            status_id = status.get("id")
            if not isinstance(status_id, str) or not status_id.strip():
                errors.append("状態異常の識別子が不正です。")
            elif status.get("verified") is not True:
                not_applied.append(status_id)
                breakdown.append(
                    {
                        "label": f"状態異常: {status_id}",
                        "value": "未適用",
                        "rounding": "状態異常式が未検証のためダメージへ適用しない",
                    }
                )
            else:
                breakdown.append(
                    {
                        "label": f"状態異常: {status_id}",
                        "value": "記録のみ",
                        "rounding": "検証済みの蓄積式が入力されるまでダメージへ適用しない",
                    }
                )
    normalized_quest: dict[str, Any] | None = None
    if quest is not None:
        if not isinstance(quest, Mapping):
            errors.append("クエスト条件の形式が不正です。")
        else:
            players = quest.get("players")
            if not _is_number(players) or not 1 <= players <= 4:
                invalid.append("players")
                errors.append("参加人数は1〜4人で指定してください。")
            else:
                normalized_quest = dict(quest)
                normalized_quest["players"] = int(players)
                breakdown.append(
                    {
                        "label": "クエスト参加人数",
                        "value": int(players),
                        "rounding": "人数情報を記録。検証済みの対象補正だけを適用",
                    }
                )

    if (
        errors
        or missing
        or invalid
        or attack_value is None
        or physical_hitzone is None
        or motion_value is None
        or affinity_multiplier is None
        or attribute_multiplier is None
        or element_hitzone is None
    ):
        return DamageResult(
            False,
            {},
            errors,
            missing,
            invalid,
            not_applied,
            applied,
            breakdown,
            dict(status) if isinstance(status, Mapping) else None,
            normalized_quest,
            metadata_records,
        ).as_dict()

    physical_raw = attack_value * motion_value / 100.0
    physical_before_correction = physical_raw * affinity_multiplier
    physical_after_hitzone = physical_before_correction * physical_hitzone / 100.0
    physical = math.floor(physical_after_hitzone * multipliers["physical"])
    element_before_hitzone = element_value * attribute_multiplier
    element_after_hitzone = element_before_hitzone * float(element_hitzone) / 100.0
    element = math.floor(element_after_hitzone * multipliers["element"])
    total = math.floor((physical + element) * multipliers["total"])

    breakdown.extend(
        [
            {
                "label": "物理計算",
                "value": physical,
                "inputs": {
                    "攻撃力": attack_value,
                    "モーション値(%)": motion_value,
                    "会心補正": affinity_multiplier,
                    "物理肉質(%)": physical_hitzone,
                },
                "intermediate": physical_after_hitzone,
                "motion": {
                    "id": motion_id,
                    "name": motion_name,
                    "value": motion_value,
                },
                "rounding": "最終物理値を小数点以下切り捨て",
            },
            {
                "label": "属性計算",
                "value": element,
                "inputs": {
                    "属性値": element_value,
                    "属性補正": attribute_multiplier,
                    "属性肉質(%)": element_hitzone,
                },
                "intermediate": element_after_hitzone,
                "rounding": "最終属性値を小数点以下切り捨て",
            },
            {
                "label": "合計",
                "value": total,
                "intermediate": physical + element,
                "rounding": "物理+属性の後、合計補正を適用して小数点以下切り捨て",
            },
        ]
    )
    damages = {"physical": physical, "element": element, "total": total}
    return DamageResult(
        True,
        damages,
        [],
        missing,
        invalid,
        not_applied,
        applied,
        breakdown,
        dict(status) if isinstance(status, Mapping) else None,
        normalized_quest,
        metadata_records,
    ).as_dict()
