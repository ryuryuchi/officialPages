const fs = require("node:fs");
const path = require("node:path");

const API_BASE = "https://wilds.mhdb.io/ja";
const DATA_DIRECTORY = path.join(__dirname, "data");
const RESISTANCE_KEYS = ["fire", "water", "thunder", "ice", "dragon"];
const RESOURCE_NAMES = ["armor", "charms", "decorations", "skills", "weapons"];

async function fetchResource(name) {
  const response = await fetch(`${API_BASE}/${name}`, {
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) {
    throw new Error(`${name}: MHWilds DB returned HTTP ${response.status}.`);
  }
  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error(`${name}: expected an array from MHWilds DB.`);
  }
  return data;
}

function compactSkills(entries) {
  if (!Array.isArray(entries)) throw new Error("Expected a skill list.");
  return entries.map((entry) => {
    if (!Number.isInteger(entry?.skill?.id) || !Number.isInteger(entry.level)) {
      throw new Error("MHWilds DB returned an invalid skill entry.");
    }
    return { skill: { id: entry.skill.id }, level: entry.level };
  });
}

function compactResource(name, records) {
  switch (name) {
    case "armor":
      return records.map((armor) => {
        if (!armor?.defense || !armor.resistances || !Array.isArray(armor.slots)) {
          throw new Error("MHWilds DB returned an invalid armor record.");
        }
        return {
          kind: armor.kind,
          name: armor.name,
          rank: armor.rank,
          rarity: armor.rarity,
          resistances: Object.fromEntries(RESISTANCE_KEYS.map((key) => [key, armor.resistances[key]])),
          defense: { max: armor.defense.max },
          skills: compactSkills(armor.skills),
          slots: armor.slots,
        };
      });
    case "charms":
      return records.map((charm) => ({
        ranks: charm.ranks.map((rank) => ({ name: rank.name, skills: compactSkills(rank.skills) })),
      }));
    case "decorations":
      return records.map((decoration) => ({
        name: decoration.name,
        kind: decoration.kind,
        slot: decoration.slot,
        skills: compactSkills(decoration.skills),
      }));
    case "skills":
      return records.map((skill) => ({
        id: skill.id,
        name: skill.name,
        kind: skill.kind,
        ranks: skill.ranks.map((rank) => ({ level: rank.level })),
      }));
    case "weapons":
      return records.map((weapon) => ({
        id: weapon.id,
        kind: weapon.kind,
        name: weapon.name,
        skills: compactSkills(weapon.skills),
        slots: weapon.slots,
      }));
    default:
      throw new Error(`Unsupported resource: ${name}`);
  }
}

async function main() {
  const resources = await Promise.all(RESOURCE_NAMES.map(async (name) => {
    const records = await fetchResource(name);
    return [name, compactResource(name, records)];
  }));

  fs.mkdirSync(DATA_DIRECTORY, { recursive: true });
  for (const [name, records] of resources) {
    const filePath = path.join(DATA_DIRECTORY, `${name}.json`);
    fs.writeFileSync(filePath, `${JSON.stringify(records)}\n`, "utf8");
    console.log(`${name}: ${records.length} records -> ${path.relative(__dirname, filePath)}`);
  }
}

main().catch((error) => {
  console.error("Unable to refresh the bundled MHWilds data.", error);
  process.exitCode = 1;
});
