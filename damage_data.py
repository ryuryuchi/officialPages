"""Damage simulator data contracts and retrieval helpers.

The calculator deliberately consumes a small, validated contract instead of
raw API responses.  This keeps source-specific changes out of the calculation
rules and makes missing data visible rather than silently inventing values.
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping


REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_USER_AGENT = "MHWildsDamageSimulator/1.0"
DEFAULT_MHDB_WEAPONS_URL = "https://wilds.mhdb.io/ja/weapons"
DEFAULT_MHDB_MONSTERS_URL = "https://wilds.mhdb.io/ja/monsters"


class DataError(RuntimeError):
    """Base class for errors that can be shown to the user."""


class DataFetchError(DataError):
    """Raised when an external data source cannot be read."""


class DataValidationError(DataError):
    """Raised when a source payload does not satisfy the data contract."""


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DataValidationError(f"{label} はオブジェクト形式である必要があります。")
    return value


def _required_text(record: Mapping[str, Any], key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DataValidationError(f"{label} の {key} が不足しています。")
    return value.strip()


def _number(
    value: Any,
    label: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DataValidationError(f"{label} は数値である必要があります。")
    if not math.isfinite(float(value)):
        raise DataValidationError(f"{label} は有限の数値である必要があります。")
    if minimum is not None and value < minimum:
        raise DataValidationError(f"{label} は {minimum} 以上である必要があります。")
    if maximum is not None and value > maximum:
        raise DataValidationError(f"{label} は {maximum} 以下である必要があります。")
    return value


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def metadata(
    *,
    source_url: str,
    retrieved_at: str,
    data_version: str,
    available: bool = True,
    missing: list[str] | None = None,
) -> dict[str, Any]:
    """Create the common provenance object attached to every normalized record."""
    return {
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "data_version": data_version,
        "available": available,
        "missing": list(missing or []),
    }


def fetch_json(
    url: str,
    *,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
    user_agent: str = DEFAULT_USER_AGENT,
) -> Any:
    """Fetch JSON and turn transport/format failures into actionable errors."""
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": user_agent},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise DataFetchError(
            f"データ取得に失敗しました（HTTP {error.code}）。URLを確認してください。"
        ) from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise DataFetchError(
            f"データ取得に失敗しました。通信状態とURLを確認してください: {error}"
        ) from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DataFetchError(
            f"取得したデータをJSONとして読み込めませんでした: {error}"
        ) from error
    return payload


def normalize_weapon(
    raw: Any,
    *,
    source_url: str = "",
    retrieved_at: str = "",
    data_version: str = "",
) -> dict[str, Any]:
    """Normalize a weapon record while preserving only validated values."""
    record = _require_mapping(raw, "武器")
    weapon_id = _required_text(record, "id", "武器")
    name = _required_text(record, "name", "武器")
    weapon_kind = record.get("weapon_kind", record.get("kind"))
    if weapon_kind is not None:
        weapon_kind = _required_text(
            {"weapon_kind": weapon_kind}, "weapon_kind", "武器"
        )
    attack = _number(record.get("attack"), "武器の攻撃力", minimum=0)

    raw_element = record.get("element")
    element: dict[str, Any] | None
    if raw_element is None:
        element = None
    else:
        element_record = _require_mapping(raw_element, "武器の属性")
        element_type = _required_text(element_record, "type", "武器の属性")
        element_value = _number(
            element_record.get("value"), "武器の属性値", minimum=0
        )
        element = {"type": element_type, "value": element_value}

    return {
        "id": weapon_id,
        "name": name,
        "weapon_kind": weapon_kind,
        "attack": attack,
        "element": element,
        "metadata": metadata(
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        ),
    }


def normalize_mhdb_weapon(
    raw: Any,
    *,
    source_url: str,
    retrieved_at: str,
    data_version: str,
) -> dict[str, Any]:
    """Adapt the public MHDB Wilds weapon payload to the shared contract."""
    record = _require_mapping(raw, "MHDB武器")
    raw_damage = _require_mapping(record.get("damage"), "MHDB武器の攻撃力")
    raw_specials = record.get("specials", [])
    if not isinstance(raw_specials, list):
        raise DataValidationError("MHDB武器の属性データが不正です。")
    elements = [
        special
        for special in raw_specials
        if isinstance(special, Mapping) and special.get("kind") == "element"
    ]
    element = None
    if elements:
        special = elements[0]
        special_damage = _require_mapping(special.get("damage"), "MHDB武器の属性値")
        element = {
            "type": special.get("element"),
            "value": special_damage.get("raw"),
        }
    return normalize_weapon(
        {
            "id": str(record.get("id")),
            "name": record.get("name"),
            "weapon_kind": record.get("kind"),
            "attack": raw_damage.get("raw"),
            "element": element,
        },
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )


def normalize_motion(
    raw: Any,
    *,
    source_url: str = "",
    retrieved_at: str = "",
    data_version: str = "",
) -> dict[str, Any]:
    """Normalize one weapon-specific attack motion."""
    record = _require_mapping(raw, "攻撃モーション")
    motion_id = _required_text(record, "id", "攻撃モーション")
    weapon_kind = _required_text(record, "weapon_kind", "攻撃モーション")
    name = _required_text(record, "name", "攻撃モーション")
    motion_value = _number(
        record.get("motion_value"),
        "モーション値",
        minimum=0,
        maximum=1000,
    )
    return {
        "id": motion_id,
        "weapon_kind": weapon_kind,
        "name": name,
        "motion_value": motion_value,
        "metadata": metadata(
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        ),
    }


def normalize_monster_part(raw: Any) -> dict[str, Any]:
    """Normalize a monster part; an absent element hitzone is an error."""
    record = _require_mapping(raw, "モンスター部位")
    monster_id = _required_text(record, "monster_id", "モンスター部位")
    part_id = _required_text(record, "part_id", "モンスター部位")
    name = _required_text(record, "name", "モンスター部位")
    physical_hitzone = _number(
        record.get("physical_hitzone"),
        "物理肉質",
        minimum=0,
        maximum=100,
    )
    raw_element_hitzone = record.get("element_hitzone")
    if not isinstance(raw_element_hitzone, Mapping):
        raise DataValidationError(
            "モンスター部位の element_hitzone が不足しています。"
        )
    element_hitzone: dict[str, int | float] = {}
    for element_type, value in raw_element_hitzone.items():
        if not isinstance(element_type, str) or not element_type.strip():
            raise DataValidationError("属性肉質の属性識別子が不正です。")
        element_hitzone[element_type] = _number(
            value,
            f"属性肉質({element_type})",
            minimum=0,
            maximum=100,
        )
    return {
        "monster_id": monster_id,
        "part_id": part_id,
        "name": name,
        "physical_hitzone": physical_hitzone,
        "element_hitzone": element_hitzone,
    }


def normalize_mhdb_monster(
    raw: Any,
    *,
    source_url: str,
    retrieved_at: str,
    data_version: str,
) -> dict[str, Any]:
    """Adapt MHDB monster parts and hitzone multipliers to percentages."""
    record = _require_mapping(raw, "MHDBモンスター")
    monster_id = str(record.get("id"))
    raw_parts = record.get("parts")
    if not isinstance(raw_parts, list) or not raw_parts:
        raise DataValidationError(f"MHDBモンスター {monster_id} の部位が不足しています。")
    parts: list[dict[str, Any]] = []
    for raw_part in raw_parts:
        part = _require_mapping(raw_part, "MHDBモンスター部位")
        multipliers = _require_mapping(part.get("multipliers"), "MHDB部位肉質")
        physical = multipliers.get("slash")
        if not _is_finite_number(physical):
            raise DataValidationError(f"MHDBモンスター {monster_id} の物理肉質が不足しています。")
        element_hitzone = {
            str(key): float(value) * 100
            for key, value in multipliers.items()
            if key in {"fire", "water", "thunder", "ice", "dragon"}
            and _is_finite_number(value)
        }
        parts.append(
            normalize_monster_part(
                {
                    "monster_id": monster_id,
                    "part_id": str(part.get("id", part.get("part"))),
                    "name": part.get("name", part.get("part")),
                    "physical_hitzone": float(physical) * 100,
                    "element_hitzone": element_hitzone,
                }
            )
        )
    raw_statuses = record.get("weaknesses", [])
    statuses: list[dict[str, Any]] = []
    seen_statuses: set[str] = set()
    if isinstance(raw_statuses, list):
        for weakness in raw_statuses:
            if not isinstance(weakness, Mapping) or weakness.get("kind") != "status":
                continue
            status_id = weakness.get("status")
            if not isinstance(status_id, str) or status_id in seen_statuses:
                continue
            seen_statuses.add(status_id)
            statuses.append(
                {"id": status_id, "name": status_id, "verified": False}
            )
    source = metadata(
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )
    for part in parts:
        part["metadata"] = dict(source)
    return {
        "id": monster_id,
        "name": _required_text(record, "name", "MHDBモンスター"),
        "parts": parts,
        "statuses": statuses,
        "quest": {"players": 1, "corrections": []},
        "metadata": source,
    }


def normalize_status(raw: Any) -> dict[str, Any]:
    """Normalize status data without assuming an accumulation formula."""
    record = _require_mapping(raw, "状態異常")
    status_id = _required_text(record, "id", "状態異常")
    name = _required_text(record, "name", "状態異常")
    verified = record.get("verified", False)
    if not isinstance(verified, bool):
        raise DataValidationError("状態異常の verified は真偽値である必要があります。")
    result = {"id": status_id, "name": name, "verified": verified}
    if "initial" in record:
        result["initial"] = _number(record["initial"], "状態異常の初期値", minimum=0)
    if "increment" in record:
        result["increment"] = _number(record["increment"], "状態異常の増加値", minimum=0)
    return result


def normalize_quest(raw: Any) -> dict[str, Any]:
    """Normalize quest/player corrections and retain their verification flag."""
    record = _require_mapping(raw, "クエスト条件")
    players = _number(record.get("players"), "参加人数", minimum=1, maximum=4)
    raw_corrections = record.get("corrections", [])
    if not isinstance(raw_corrections, list):
        raise DataValidationError("クエスト補正は配列である必要があります。")
    corrections: list[dict[str, Any]] = []
    for index, raw_correction in enumerate(raw_corrections, start=1):
        correction = _require_mapping(raw_correction, f"クエスト補正{index}")
        correction_id = _required_text(correction, "id", f"クエスト補正{index}")
        value = _number(correction.get("value"), f"クエスト補正{index}の値", minimum=0)
        verified = correction.get("verified", False)
        if not isinstance(verified, bool):
            raise DataValidationError(f"クエスト補正{index}の verified が不正です。")
        normalized = {"id": correction_id, "value": value, "verified": verified}
        if isinstance(correction.get("scope"), str):
            normalized["scope"] = correction["scope"]
        corrections.append(normalized)
    return {"players": int(players), "corrections": corrections}


def normalize_monster(raw: Any) -> dict[str, Any]:
    """Normalize a monster and all of its parts/statuses."""
    record = _require_mapping(raw, "モンスター")
    monster_id = _required_text(record, "id", "モンスター")
    name = _required_text(record, "name", "モンスター")
    raw_parts = record.get("parts")
    if not isinstance(raw_parts, list) or not raw_parts:
        raise DataValidationError("モンスターの部位データが不足しています。")
    parts = [normalize_monster_part(part) for part in raw_parts]
    if any(part["monster_id"] != monster_id for part in parts):
        raise DataValidationError(f"モンスター部位の識別子が一致しません: {monster_id}")
    raw_statuses = record.get("statuses", [])
    if not isinstance(raw_statuses, list):
        raise DataValidationError("モンスターの状態異常データは配列である必要があります。")
    statuses = [normalize_status(status) for status in raw_statuses]
    record_metadata = record.get(
        "metadata",
        metadata(
            source_url="",
            retrieved_at="",
            data_version="",
        ),
    )
    if not isinstance(record_metadata, Mapping):
        raise DataValidationError("モンスターのメタデータ形式が不正です。")
    for part in parts:
        part["metadata"] = dict(record_metadata)
    quest = normalize_quest(record.get("quest", {"players": 1, "corrections": []}))
    return {
        "id": monster_id,
        "name": name,
        "parts": parts,
        "statuses": statuses,
        "quest": quest,
        "metadata": record_metadata,
    }


def combine_records(
    weapon: Any,
    relation: Any,
    skill: Any,
) -> dict[str, Any]:
    """Join records only when their explicit identifiers agree."""
    weapon_record = _require_mapping(weapon, "武器")
    relation_record = _require_mapping(relation, "武器関連")
    weapon_id = weapon_record.get("id")
    relation_weapon_id = relation_record.get("weapon_id")
    if weapon_id != relation_weapon_id:
        raise DataValidationError(
            f"武器識別子が一致しません: weapon={weapon_id}, relation={relation_weapon_id}"
        )

    skill_ids = relation_record.get("skill_ids", [])
    if not isinstance(skill_ids, list) or any(
        not isinstance(skill_id, str) or not skill_id.strip()
        for skill_id in skill_ids
    ):
        raise DataValidationError("スキル識別子の形式が不正です。")
    skills: list[dict[str, Any]] = []
    if skill is not None:
        skill_record = _require_mapping(skill, "スキル")
        skill_id = skill_record.get("id")
        if skill_id not in skill_ids:
            raise DataValidationError(
                f"スキル識別子が対応していません: {skill_id}"
            )
        skills.append(dict(skill_record))
    elif skill_ids:
        raise DataValidationError(
            f"スキルデータが不足しています: {', '.join(skill_ids)}"
        )
    return {
        "weapon": dict(weapon_record),
        "relation": dict(relation_record),
        "skills": skills,
    }


def _catalog_metadata(
    *,
    source_url: str,
    retrieved_at: str,
    data_version: str,
    source_count: int,
    imported_count: int,
    duplicate_ids: list[str],
    missing_ids: list[str],
) -> dict[str, Any]:
    return {
        **metadata(
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
            missing=missing_ids,
        ),
        "source_count": source_count,
        "imported_count": imported_count,
        "duplicate_ids": duplicate_ids,
        "missing_ids": missing_ids,
        "complete": not duplicate_ids and not missing_ids,
    }


def _ensure_catalog_complete(
    items: list[dict[str, Any]],
    *,
    expected_ids: set[str] | None,
    label: str,
    source_url: str,
    retrieved_at: str,
    data_version: str,
) -> dict[str, Any]:
    ids = [str(item["id"]) for item in items]
    duplicate_ids = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    missing_ids = (
        sorted(expected_ids - set(ids)) if expected_ids is not None else []
    )
    catalog_metadata = _catalog_metadata(
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
        source_count=len(ids),
        imported_count=len(set(ids)),
        duplicate_ids=duplicate_ids,
        missing_ids=missing_ids,
    )
    if not catalog_metadata["complete"]:
        problems: list[str] = []
        if duplicate_ids:
            problems.append(f"重複識別子={','.join(duplicate_ids)}")
        if missing_ids:
            problems.append(f"欠落識別子={','.join(missing_ids)}")
        raise DataValidationError(f"{label}の全件性を確認できません: {'; '.join(problems)}")
    return {"items": items, "metadata": catalog_metadata}


def normalize_weapon_catalog(
    raw_items: Any,
    *,
    expected_ids: set[str] | None = None,
    source_url: str = "",
    retrieved_at: str = "",
    data_version: str = "",
) -> dict[str, Any]:
    """Normalize every weapon record and reject an incomplete catalog."""
    if not isinstance(raw_items, list):
        raise DataValidationError("武器カタログのトップレベルは配列である必要があります。")
    items = [
        normalize_weapon(
            item,
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        for item in raw_items
    ]
    return _ensure_catalog_complete(
        items,
        expected_ids=expected_ids,
        label="武器カタログ",
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )


def normalize_monster_catalog(
    raw_items: Any,
    *,
    expected_ids: set[str] | None = None,
    source_url: str = "",
    retrieved_at: str = "",
    data_version: str = "",
) -> dict[str, Any]:
    """Normalize every monster record and reject an incomplete catalog."""
    if not isinstance(raw_items, list):
        raise DataValidationError("モンスターカタログのトップレベルは配列である必要があります。")
    items = [normalize_monster(item) for item in raw_items]
    for item in items:
        item["metadata"] = metadata(
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        for part in item["parts"]:
            part["metadata"] = dict(item["metadata"])
    return _ensure_catalog_complete(
        items,
        expected_ids=expected_ids,
        label="モンスターカタログ",
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )


def normalize_motion_catalog(
    raw_items: Any,
    *,
    expected_ids: set[str] | None = None,
    source_url: str = "",
    retrieved_at: str = "",
    data_version: str = "",
) -> dict[str, Any]:
    """Normalize all motion records and reject duplicate/missing identifiers."""
    if not isinstance(raw_items, list):
        raise DataValidationError("モーションカタログのトップレベルは配列である必要があります。")
    items = [
        normalize_motion(
            item,
            source_url=source_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        for item in raw_items
    ]
    return _ensure_catalog_complete(
        items,
        expected_ids=expected_ids,
        label="モーションカタログ",
        source_url=source_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )


def _fixture_metadata() -> dict[str, Any]:
    return metadata(
        source_url="local://mhwilds-damage-fixture",
        retrieved_at="2026-09-10T00:00:00Z",
        data_version="fixture-2026-09-10",
    )


def load_demo_catalog() -> dict[str, Any]:
    """Return deterministic, fully validated data for offline UI use and tests."""
    source = _fixture_metadata()
    source_kwargs = {
        "source_url": source["source_url"],
        "retrieved_at": source["retrieved_at"],
        "data_version": source["data_version"],
    }
    raw_weapons = [
        {
            "id": "iron-longsword",
            "name": "アイアンソード",
            "weapon_kind": "long-sword",
            "attack": 180,
            "element": None,
        },
        {
            "id": "flame-longsword",
            "name": "フレイムソード",
            "weapon_kind": "long-sword",
            "attack": 165,
            "element": {"type": "fire", "value": 80},
        },
        {
            "id": "hunter-bow",
            "name": "ハンターボウ",
            "weapon_kind": "bow",
            "attack": 150,
            "element": {"type": "water", "value": 60},
        },
    ]
    weapon_catalog = normalize_weapon_catalog(raw_weapons, **source_kwargs)
    raw_monsters = [
        {
            "id": "dosha-guma",
            "name": "ドシャグマ",
            "parts": [
                {
                    "monster_id": "dosha-guma",
                    "part_id": "head",
                    "name": "頭",
                    "physical_hitzone": 70,
                    "element_hitzone": {"fire": 25, "water": 15},
                },
                {
                    "monster_id": "dosha-guma",
                    "part_id": "body",
                    "name": "胴",
                    "physical_hitzone": 45,
                    "element_hitzone": {"fire": 15, "water": 10},
                },
            ],
            "statuses": [
                {"id": "poison", "name": "毒", "verified": True},
                {"id": "paralysis", "name": "麻痺", "verified": False},
                {"id": "sleep", "name": "睡眠", "verified": False},
                {"id": "blast", "name": "爆破", "verified": False},
            ],
            "quest": {
                "players": 1,
                "corrections": [
                    {
                        "id": "status-4p",
                        "value": 1.2,
                        "verified": True,
                        "scope": "status",
                    }
                ],
            },
        },
        {
            "id": "chatacabra",
            "name": "チャタカブラ",
            "parts": [
                {
                    "monster_id": "chatacabra",
                    "part_id": "head",
                    "name": "頭",
                    "physical_hitzone": 60,
                    "element_hitzone": {"fire": 20, "water": 10},
                }
            ],
            "statuses": [
                {"id": "poison", "name": "毒", "verified": True},
                {"id": "sleep", "name": "睡眠", "verified": False},
            ],
            "quest": {"players": 1, "corrections": []},
        },
    ]
    monster_catalog = normalize_monster_catalog(
        raw_monsters,
        expected_ids={"dosha-guma", "chatacabra"},
        **source_kwargs,
    )
    raw_motions = [
        {
            "id": "ls-spirit-roundslash",
            "weapon_kind": "long-sword",
            "name": "気刃大回転斬り",
            "motion_value": 42,
        },
        {
            "id": "ls-vertical-slash",
            "weapon_kind": "long-sword",
            "name": "縦斬り",
            "motion_value": 24,
        },
        {
            "id": "bow-rapid-shot",
            "weapon_kind": "bow",
            "name": "溜め射撃",
            "motion_value": 20,
        },
    ]
    motion_catalog = normalize_motion_catalog(raw_motions, **source_kwargs)
    aggregate_metadata = {
        **source,
        "source_count": (
            weapon_catalog["metadata"]["source_count"]
            + monster_catalog["metadata"]["source_count"]
            + motion_catalog["metadata"]["source_count"]
        ),
        "imported_count": (
            weapon_catalog["metadata"]["imported_count"]
            + monster_catalog["metadata"]["imported_count"]
            + motion_catalog["metadata"]["imported_count"]
        ),
        "duplicate_ids": [],
        "missing_ids": [],
        "weapon_count": len(weapon_catalog["items"]),
        "monster_count": len(monster_catalog["items"]),
        "status_count": len(
            {
                status["id"]
                for monster in monster_catalog["items"]
                for status in monster["statuses"]
            }
        ),
        "motion_count": len(motion_catalog["items"]),
        "complete": all(
            catalog["metadata"]["complete"]
            for catalog in (weapon_catalog, monster_catalog, motion_catalog)
        ),
    }
    return {
        "weapons": weapon_catalog["items"],
        "monsters": monster_catalog["items"],
        "motions": motion_catalog["items"],
        "metadata": aggregate_metadata,
    }


def fetch_live_catalog(
    *,
    weapon_url: str = DEFAULT_MHDB_WEAPONS_URL,
    monster_url: str = DEFAULT_MHDB_MONSTERS_URL,
    motion_items: list[dict[str, Any]] | None = None,
    debug_motion_value: int | None = None,
) -> dict[str, Any]:
    """Load all public MHDB weapons/monsters without hiding missing motion data.

    MHDB currently exposes weapon and monster records, but not a verified
    motion-value endpoint. The catalog therefore remains explicitly
    incomplete until a validated motion catalog is supplied. A caller may
    opt into a clearly marked debug catalog with one fixed value per weapon
    kind; that mode is never used implicitly by production callers.
    """
    retrieved_at = datetime.now(timezone.utc).isoformat()
    data_version = f"mhdb-live-{retrieved_at}"
    raw_weapons = fetch_json(weapon_url)
    raw_monsters = fetch_json(monster_url)
    if not isinstance(raw_weapons, list) or not isinstance(raw_monsters, list):
        raise DataValidationError(
            "MHDBの武器・モンスターデータは配列形式である必要があります。"
        )
    weapons = [
        normalize_mhdb_weapon(
            raw,
            source_url=weapon_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        for raw in raw_weapons
    ]
    monsters = [
        normalize_mhdb_monster(
            raw,
            source_url=monster_url,
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        for raw in raw_monsters
    ]
    weapon_catalog = _ensure_catalog_complete(
        weapons,
        expected_ids=None,
        label="MHDB武器カタログ",
        source_url=weapon_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )
    monster_catalog = _ensure_catalog_complete(
        monsters,
        expected_ids=None,
        label="MHDBモンスターカタログ",
        source_url=monster_url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )
    debug_motion = debug_motion_value is not None
    if debug_motion:
        if debug_motion_value < 0 or debug_motion_value > 1000:
            raise DataValidationError("デバッグ用モーション値は0〜1000で指定してください。")
        source = metadata(
            source_url="debug://fixed-motion-value",
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        weapon_kinds = sorted(
            {
                weapon["weapon_kind"]
                for weapon in weapons
                if isinstance(weapon.get("weapon_kind"), str)
            }
        )
        motions = [
            {
                "id": f"debug-{weapon_kind}-fixed-50",
                "weapon_kind": weapon_kind,
                "name": f"デバッグ固定モーション（{debug_motion_value}）",
                "motion_value": debug_motion_value,
                "metadata": dict(source),
            }
            for weapon_kind in weapon_kinds
        ]
    else:
        motions = list(motion_items or [])
    motion_metadata = _catalog_metadata(
        source_url="",
        retrieved_at=retrieved_at,
        data_version=data_version,
        source_count=len(motions),
        imported_count=len(motions),
        duplicate_ids=[],
        missing_ids=[] if motions else ["motion_catalog"],
    )
    status_ids = {
        status["id"]
        for monster in monsters
        for status in monster.get("statuses", [])
        if isinstance(status.get("id"), str)
    }
    return {
        "weapons": weapon_catalog["items"],
        "monsters": monster_catalog["items"],
        "motions": motions,
        "metadata": {
            "source_url": f"{weapon_url}, {monster_url}",
            "retrieved_at": retrieved_at,
            "data_version": data_version,
            "available": True,
            "missing": [] if motions else ["motion_catalog"],
            "notice": (
                f"デバッグモード: 全モーション値を{debug_motion_value}として計算"
                if debug_motion
                else ""
            ),
            "source_count": (
                weapon_catalog["metadata"]["source_count"]
                + monster_catalog["metadata"]["source_count"]
                + motion_metadata["source_count"]
            ),
            "imported_count": (
                weapon_catalog["metadata"]["imported_count"]
                + monster_catalog["metadata"]["imported_count"]
                + motion_metadata["imported_count"]
            ),
            "weapon_count": len(weapons),
            "monster_count": len(monsters),
            "status_count": len(status_ids),
            "motion_count": len(motions),
            "duplicate_ids": [],
            "missing_ids": [] if motions else ["motion_catalog"],
            "complete": bool(weapons and monsters and motions),
            "debug_motion": debug_motion,
            "debug_motion_value": debug_motion_value,
        },
    }


def fetch_weapons(url: str, *, data_version: str) -> list[dict[str, Any]]:
    """Fetch and normalize a weapon endpoint with one shared retrieval timestamp."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = fetch_json(url)
    if not isinstance(payload, list):
        raise DataValidationError("武器データのトップレベルは配列である必要があります。")
    return normalize_weapon_catalog(
        payload,
        source_url=url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )["items"]


def fetch_monsters(url: str, *, data_version: str) -> list[dict[str, Any]]:
    """Fetch and normalize monster/part/status/quest data from one endpoint."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = fetch_json(url)
    if not isinstance(payload, list):
        raise DataValidationError("モンスターデータのトップレベルは配列である必要があります。")
    return normalize_monster_catalog(
        payload,
        source_url=url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )["items"]


def fetch_motions(url: str, *, data_version: str) -> list[dict[str, Any]]:
    """Fetch and normalize every weapon-specific motion."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = fetch_json(url)
    if not isinstance(payload, list):
        raise DataValidationError("モーションデータのトップレベルは配列である必要があります。")
    return normalize_motion_catalog(
        payload,
        source_url=url,
        retrieved_at=retrieved_at,
        data_version=data_version,
    )["items"]


def fetch_catalog(
    *,
    weapon_url: str,
    monster_url: str,
    motion_url: str,
    data_version: str,
) -> dict[str, Any]:
    """Fetch and validate source payloads supplied by the caller.

    The function intentionally requires URLs explicitly.  It does not hide a
    network call in the UI startup path or fall back to fabricated values.
    """
    retrieved_at = datetime.now(timezone.utc).isoformat()
    weapons = fetch_weapons(weapon_url, data_version=data_version)
    monsters = fetch_monsters(monster_url, data_version=data_version)
    motions = fetch_motions(motion_url, data_version=data_version)
    counts = [len(weapons), len(monsters), len(motions)]
    return {
        "weapons": weapons,
        "monsters": monsters,
        "motions": motions,
        "metadata": metadata(
            source_url=f"{weapon_url}, {monster_url}, {motion_url}",
            retrieved_at=retrieved_at,
            data_version=data_version,
        )
        | {
            "source_count": sum(counts),
            "imported_count": sum(counts),
            "duplicate_ids": [],
            "missing_ids": [],
            "complete": bool(weapons and monsters and motions),
        },
    }
