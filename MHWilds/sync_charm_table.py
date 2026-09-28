"""Build locally managed random-charm data from the public source tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import urllib.request
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path


SPREADSHEET_ID = "1sWzcj2yZ7ZIgY8MH6CbR2pZj13bwBHlnXIkhakCsdLM"
SPREADSHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
)
API_BASE_URL = "https://wilds.mhdb.io/ja"
OUTPUT_PATH = Path(__file__).parent / "data" / "random-charm-table.json"
NAMESPACE = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SKILL_NAME_ALIASES = {
    "回避距離": "回避距離UP",
    "火属性強化": "火属性攻撃強化",
    "水属性強化": "水属性攻撃強化",
    "雷属性強化": "雷属性攻撃強化",
    "氷属性強化": "氷属性攻撃強化",
    "龍属性強化": "龍属性攻撃強化",
    "貫通弾・貫通矢強化": "貫通弾・竜の矢強化",
    "通常弾・連射矢強化": "通常弾・通常矢強化",
    "防御down耐性": "防御力DOWN耐性",
}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "APIApp/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def column_number(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    number = 0
    for character in letters:
        number = number * 26 + ord(character) - ord("A") + 1
    return number - 1


def read_worksheet_rows(workbook_path: Path, worksheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(workbook_path) as archive:
        shared_strings_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared_strings = [
            "".join(item.itertext()) for item in shared_strings_root.findall("x:si", NAMESPACE)
        ]

        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_targets = {
            relationship.attrib["Id"]: relationship.attrib["Target"]
            for relationship in relationships_root
        }
        sheet = next(
            (
                item
                for item in workbook_root.findall("x:sheets/x:sheet", NAMESPACE)
                if item.attrib["name"] == worksheet_name
            ),
            None,
        )
        if sheet is None:
            raise ValueError(f"Worksheet not found: {worksheet_name}")

        relationship_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        target = relationship_targets[relationship_id].lstrip("/")
        worksheet_path = f"xl/{target}" if not target.startswith("xl/") else target
        worksheet_root = ET.fromstring(archive.read(worksheet_path))

        rows: list[list[str]] = []
        for row in worksheet_root.findall("x:sheetData/x:row", NAMESPACE):
            values: dict[int, str] = {}
            for cell in row.findall("x:c", NAMESPACE):
                value = cell.findtext("x:v", default="", namespaces=NAMESPACE)
                if cell.attrib.get("t") == "s" and value:
                    value = shared_strings[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(cell.find("x:is", NAMESPACE).itertext())
                values[column_number(cell.attrib["r"])] = value
            rows.append(
                [values.get(index, "") for index in range(max(values, default=-1) + 1)]
            )
    return rows


def api_skills() -> tuple[dict[str, dict[str, object]], str]:
    skills = json.loads(fetch(f"{API_BASE_URL}/skills"))
    version = json.loads(fetch("https://wilds.mhdb.io/version"))["version"]
    by_name: dict[str, dict[str, object]] = {}
    duplicates: set[str] = set()
    for skill in skills:
        name = skill["name"]
        if name in by_name:
            duplicates.add(name)
        by_name[name] = {
            "id": skill["id"],
            "name": name,
            "kind": skill["kind"],
        }
    if duplicates:
        raise ValueError(f"Duplicate API skill names: {sorted(duplicates)}")
    return by_name, version


def normalized_skill_name(name: str) -> str:
    return unicodedata.normalize("NFKC", name).replace(" ", "").casefold()


def parse_groups(rows: list[list[str]], skills_by_name: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    normalized_skills_by_name = {
        normalized_skill_name(name): skill for name, skill in skills_by_name.items()
    }
    if len(normalized_skills_by_name) != len(skills_by_name):
        raise ValueError("API skill names collide after normalization")

    groups: list[dict[str, object]] = []
    for group_id, name_column in enumerate(range(1, 30, 3), start=1):
        level_column = name_column + 1
        entries: list[dict[str, object]] = []
        for row in rows[3:]:
            name = row[name_column].strip() if len(row) > name_column else ""
            level = row[level_column].strip() if len(row) > level_column else ""
            if not name:
                continue
            canonical_name = SKILL_NAME_ALIASES.get(name, name)
            skill = normalized_skills_by_name.get(normalized_skill_name(canonical_name))
            if skill is None:
                raise ValueError(
                    f"Skill group {group_id} references unknown API skill: {name}"
                )
            entry = {**skill, "level": int(float(level))}
            if canonical_name != name:
                entry["sourceName"] = name
            entries.append(entry)
        if not entries:
            raise ValueError(f"Skill group {group_id} has no entries")
        groups.append({"id": group_id, "entries": entries})
    return groups


def parse_slots(value: str) -> list[list[dict[str, object]]]:
    patterns: list[list[dict[str, object]]] = []
    for pattern in re.findall(r"\[([^\]]+)\]", value):
        slots: list[dict[str, object]] = []
        for token in pattern.split(","):
            token = token.strip()
            if token == "0":
                continue
            if token.upper().startswith("W"):
                slots.append({"kind": "weapon", "level": int(token[1:])})
            else:
                slots.append({"kind": "armor", "level": int(token)})
        patterns.append(slots)
    if not patterns:
        raise ValueError(f"Invalid slot pattern: {value}")
    return patterns


def parse_probability(value: str) -> float:
    numeric_value = float(value.removesuffix("%"))
    return numeric_value / 100 if value.endswith("%") else numeric_value


def parse_roll_patterns(rows: list[list[str]]) -> list[dict[str, object]]:
    patterns: list[dict[str, object]] = []
    for row in rows[1:]:
        rarity = row[0].strip() if row else ""
        if not re.fullmatch(r"RARE\[[5-8]\]", rarity):
            continue
        group_ids = [
            int(float(value))
            for value in row[1:4]
            if value.strip() and value.strip() != "-"
        ]
        if not group_ids:
            raise ValueError(f"Missing skill groups for {rarity}")
        patterns.append(
            {
                "rarity": int(rarity[5]),
                "skillGroupIds": group_ids,
                "slotPatterns": parse_slots(row[4]),
            }
        )
    if not patterns:
        raise ValueError("No random-charm roll patterns found")
    return patterns


def source_probabilities(rows: list[list[str]]) -> dict[str, object]:
    rarity_weights: dict[str, float] = {}
    rare_eight_slot_weights: list[dict[str, object]] = []
    for row in rows:
        left = row[6].strip() if len(row) > 6 else ""
        probability = row[7].strip() if len(row) > 7 else ""
        if re.fullmatch(r"Rare [5-8]", left) and probability:
            rarity_weights[left[-1]] = parse_probability(probability)
        if left.startswith("[W1") and probability:
            rare_eight_slot_weights.append(
                {
                    "slots": parse_slots(left)[0],
                    "probability": parse_probability(probability),
                }
            )
    return {
        "rarity": [
            {"rarity": int(rarity), "probability": probability}
            for rarity, probability in sorted(rarity_weights.items())
        ],
        "rareEightSlots": rare_eight_slot_weights,
    }


def build_data(workbook_bytes: bytes) -> dict[str, object]:
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temporary_file:
        temporary_file.write(workbook_bytes)
        workbook_path = Path(temporary_file.name)

    try:
        combination_rows = read_worksheet_rows(
            workbook_path, "護石組み合わせ"
        )
        group_rows = read_worksheet_rows(workbook_path, "スキルグループ")
    finally:
        workbook_path.unlink(missing_ok=True)

    skills_by_name, api_version = api_skills()
    return {
        "schemaVersion": 1,
        "source": {
            "spreadsheetUrl": (
                f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/htmlview"
            ),
            "spreadsheetSha256": hashlib.sha256(workbook_bytes).hexdigest(),
            "retrievedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "wildsApiVersion": api_version,
        },
        "notes": {
            "theoretical": (
                "Entries model the published random-charm table, not player-owned charms."
            ),
            "slotKinds": {
                "weapon": "Weapon decoration slot.",
                "armor": "Armor decoration slot.",
            },
        },
        "skillGroups": parse_groups(group_rows, skills_by_name),
        "rollPatterns": parse_roll_patterns(combination_rows),
        "probabilities": source_probabilities(combination_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize Monster Hunter Wilds random-charm source data."
    )
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    arguments = parser.parse_args()

    data = build_data(fetch(SPREADSHEET_URL))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {len(data['skillGroups'])} skill groups and "
        f"{len(data['rollPatterns'])} roll patterns to {arguments.output}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError, zipfile.BadZipFile) as error:
        print(f"Synchronization failed: {error}", file=sys.stderr)
        raise SystemExit(1)
