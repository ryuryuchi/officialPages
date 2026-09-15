const API_BASE = "https://wilds.mhdb.io/ja";
const ARMOR_KINDS = ["head", "chest", "arms", "waist", "legs"];
const ARMOR_LABELS = { head: "頭", chest: "胴", arms: "腕", waist: "腰", legs: "脚" };
const MAX_ARMOR_PER_PART = 24;
const MAX_PARTIAL_BUILDS = 450;
const MAX_CHARM_CANDIDATES = 320;
const MAX_TARGET_SKILLS = 20;
const MAX_RANDOM_GROUP_CHOICES = 12;
const MAX_RESULTS = 20;

const state = { armor: [], charms: [], decorations: [], skills: [], weapons: [], charmTable: null, targets: [] };
const elements = {
  status: document.querySelector("#status"),
  rank: document.querySelector("#rank-filter"),
  weaponKind: document.querySelector("#weapon-kind"),
  weapon: document.querySelector("#weapon-select"),
  fixedCharms: document.querySelector("#fixed-charms"),
  randomCharms: document.querySelector("#random-charms"),
  skill: document.querySelector("#skill-select"),
  skillLevel: document.querySelector("#skill-level"),
  addSkill: document.querySelector("#add-skill-button"),
  targets: document.querySelector("#target-skills"),
  search: document.querySelector("#search-button"),
  results: document.querySelector("#results"),
  resultSummary: document.querySelector("#result-summary"),
};

function fetchJson(url) {
  return fetch(url).then((response) => {
    if (!response.ok) throw new Error(`Request failed (${response.status})`);
    return response.json();
  });
}

function setStatus(message, error = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("error", error);
}

function skillMap(skills = []) {
  return skills.reduce((totals, entry) => {
    totals.set(entry.skill.id, (totals.get(entry.skill.id) || 0) + entry.level);
    return totals;
  }, new Map());
}

function addSkillTotals(target, addition) {
  for (const [id, level] of addition) target.set(id, (target.get(id) || 0) + level);
  return target;
}

function targetScore(totals) {
  return state.targets.reduce((score, target) => score + Math.min(totals.get(target.id) || 0, target.level) * 100, 0);
}

function armorScore(armor) {
  const totals = skillMap(armor.skills);
  return targetScore(totals) + armor.slots.reduce((sum, slot) => sum + slot * 3, 0) + armor.defense.max / 20;
}

function selectedWeapon() {
  return state.weapons.find((weapon) => String(weapon.id) === elements.weapon.value) || null;
}

function currentTargetsMet(totals) {
  return state.targets.every((target) => (totals.get(target.id) || 0) >= target.level);
}

function populateControls() {
  const skillOptions = [...state.skills].sort((a, b) => a.name.localeCompare(b.name, "ja"));
  elements.skill.replaceChildren(...skillOptions.map((skill) => new Option(skill.name, skill.id)));

  const kinds = [...new Set(state.weapons.map((weapon) => weapon.kind))].sort();
  elements.weaponKind.replaceChildren(new Option("指定なし", ""), ...kinds.map((kind) => new Option(kind, kind)));
  ["skill", "skillLevel", "addSkill", "search"].forEach((name) => { elements[name].disabled = false; });
  updateWeaponOptions();
}

function updateWeaponOptions() {
  const kind = elements.weaponKind.value;
  const weapons = state.weapons.filter((weapon) => !kind || weapon.kind === kind)
    .sort((a, b) => a.name.localeCompare(b.name, "ja"));
  elements.weapon.replaceChildren(new Option("武器なし", ""), ...weapons.map((weapon) => new Option(`${weapon.name} (${weapon.kind})`, weapon.id)));
  elements.weapon.disabled = false;
}

function renderTargets() {
  elements.targets.replaceChildren(...state.targets.map((target) => {
    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.textContent = `${target.name} Lv${target.level}`;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.ariaLabel = `${target.name}を削除`;
    remove.textContent = "×";
    remove.addEventListener("click", () => {
      state.targets = state.targets.filter((item) => item.id !== target.id);
      renderTargets();
    });
    chip.append(remove);
    return chip;
  }));
}

function addTarget() {
  const skill = state.skills.find((entry) => String(entry.id) === elements.skill.value);
  const level = Number(elements.skillLevel.value);
  if (!skill || !Number.isInteger(level) || level < 1) return;
  const existing = state.targets.find((target) => target.id === skill.id);
  if (existing) existing.level = level;
  else if (state.targets.length < MAX_TARGET_SKILLS) state.targets.push({ id: skill.id, name: skill.name, level });
  else { setStatus(`目標スキルは${MAX_TARGET_SKILLS}件までです。`, true); return; }
  renderTargets();
  setStatus("");
}

function fixedCharmCandidates() {
  return state.charms.flatMap((charm) => charm.ranks.map((rank) => ({
    name: rank.name,
    source: "固定護石",
    skills: skillMap(rank.skills),
    slots: [],
  })));
}

function randomCharmCandidates() {
  const groups = new Map(state.charmTable.skillGroups.map((group) => [group.id, group.entries]));
  const targetLevels = new Map(state.targets.map((target) => [target.id, target.level]));
  const candidates = new Map();
  for (const pattern of state.charmTable.rollPatterns) {
    const choices = pattern.skillGroupIds.map((groupId) => {
      const matching = groups.get(groupId)
        .filter((entry) => targetLevels.has(entry.id))
        .sort((left, right) => (
          targetLevels.get(right.id) * 100 + right.level
          - targetLevels.get(left.id) * 100 - left.level
        ))
        .slice(0, MAX_RANDOM_GROUP_CHOICES);
      return [null, ...matching];
    });
    const expand = (index, selected) => {
      if (index === choices.length) {
        if (!selected.some(Boolean)) return;
        for (const slots of pattern.slotPatterns) {
          const skills = new Map();
          selected.filter(Boolean).forEach((entry) => skills.set(entry.id, entry.level));
          const key = `${pattern.rarity}|${[...skills].join(",")}|${JSON.stringify(slots)}`;
          candidates.set(key, { name: `レア${pattern.rarity} 理論護石`, source: "理論護石", skills, slots });
        }
        return;
      }
      choices[index].forEach((choice) => {
        if (choice && selected.some((entry) => entry?.id === choice.id)) return;
        expand(index + 1, [...selected, choice]);
      });
    };
    expand(0, []);
  }
  return [...candidates.values()];
}

function chooseDecorations(totals, slots, targetDecorations, targetRequirements) {
  const selected = [];
  const availableSlots = slots.map((slot) => ({ ...slot }));
  while (!currentTargetsMet(totals)) {
    let best = null;
    for (const candidateDecoration of targetDecorations) {
      const { decoration, skills } = candidateDecoration;
      const usableSlotIndex = availableSlots.findIndex((slot) => slot.kind === decoration.kind && slot.level >= decoration.slot);
      if (usableSlotIndex < 0) continue;
      let gain = 0;
      for (const [skillId, level] of skills) {
        const requiredLevel = targetRequirements.get(skillId);
        if (requiredLevel) {
          gain += Math.min(
            Math.max(0, requiredLevel - (totals.get(skillId) || 0)),
            level,
          );
        }
      }
      if (!gain) continue;
      const candidate = { decoration, skills, usableSlotIndex, gain };
      if (!best || candidate.gain > best.gain || (candidate.gain === best.gain && decoration.slot < best.decoration.slot)) best = candidate;
    }
    if (!best) break;
    addSkillTotals(totals, best.skills);
    availableSlots.splice(best.usableSlotIndex, 1);
    selected.push(best.decoration);
  }
  return { selected, remainingSlots: availableSlots };
}

function findBuilds() {
  if (!state.targets.length) {
    setStatus("少なくとも1つの目標スキルを追加してください。", true);
    return;
  }
  setStatus("候補を探索中…");
  const rank = elements.rank.value;
  const candidatesByKind = new Map(ARMOR_KINDS.map((kind) => [
    kind,
    state.armor.filter((armor) => armor.kind === kind && (rank === "all" || armor.rank === rank))
      .sort((a, b) => armorScore(b) - armorScore(a)).slice(0, MAX_ARMOR_PER_PART),
  ]));
  if ([...candidatesByKind.values()].some((candidates) => !candidates.length)) {
    setStatus("指定した防具ランクには全5部位のデータがありません。", true);
    return;
  }

  const partialLimit = state.targets.length > 8 ? 160 : MAX_PARTIAL_BUILDS;
  let partials = [{ armor: [], totals: new Map(), defense: 0, resistances: { fire: 0, water: 0, thunder: 0, ice: 0, dragon: 0 }, slots: [] }];
  for (const kind of ARMOR_KINDS) {
    partials = partials.flatMap((partial) => candidatesByKind.get(kind).map((armor) => {
      const totals = addSkillTotals(new Map(partial.totals), skillMap(armor.skills));
      return {
        armor: [...partial.armor, armor],
        totals,
        defense: partial.defense + armor.defense.max,
        resistances: Object.fromEntries(Object.keys(partial.resistances).map((key) => [key, partial.resistances[key] + armor.resistances[key]])),
        slots: [...partial.slots, ...armor.slots.map((level) => ({ kind: "armor", level }))],
      };
    })).sort((a, b) => (targetScore(b.totals) + b.defense / 20) - (targetScore(a.totals) + a.defense / 20)).slice(0, partialLimit);
  }

  const weapon = selectedWeapon();
  const weaponSkills = weapon ? skillMap(weapon.skills) : new Map();
  const weaponSlots = weapon ? weapon.slots.map((level) => ({ kind: "weapon", level })) : [];
  const targetRequirements = new Map(state.targets.map((target) => [target.id, target.level]));
  const targetDecorations = state.decorations
    .map((decoration) => ({ decoration, skills: skillMap(decoration.skills) }))
    .filter(({ skills }) => [...skills.keys()].some((skillId) => targetRequirements.has(skillId)));
  const charmLimit = state.targets.length > 8 ? 72 : MAX_CHARM_CANDIDATES;
  let charms = [];
  if (elements.fixedCharms.checked) charms.push(...fixedCharmCandidates());
  if (elements.randomCharms.checked) charms.push(...randomCharmCandidates());
  if (!charms.length) charms = [{ name: "護石なし", source: "なし", skills: new Map(), slots: [] }];
  charms = charms.sort((a, b) => targetScore(b.skills) - targetScore(a.skills)).slice(0, charmLimit);

  const builds = [];
  for (const partial of partials) {
    for (const charm of charms) {
      const totals = addSkillTotals(addSkillTotals(new Map(partial.totals), weaponSkills), charm.skills);
      const decorationResult = chooseDecorations(
        totals,
        [...partial.slots, ...weaponSlots, ...charm.slots],
        targetDecorations,
        targetRequirements,
      );
      const fulfilled = state.targets.filter((target) => (totals.get(target.id) || 0) >= target.level).length;
      builds.push({ ...partial, charm, weapon, totals, decorations: decorationResult.selected, emptySlots: decorationResult.remainingSlots, fulfilled });
    }
  }
  builds.sort((a, b) => b.fulfilled - a.fulfilled || targetScore(b.totals) - targetScore(a.totals) || b.defense - a.defense);
  renderBuilds(builds.slice(0, MAX_RESULTS));
  const complete = builds.filter((build) => build.fulfilled === state.targets.length).length;
  elements.resultSummary.textContent = `${builds.length.toLocaleString()} 通りを評価 / 条件達成 ${complete.toLocaleString()} 通り`;
  setStatus(complete ? "" : "すべての目標スキルを同時に満たす候補は見つかりませんでした。", !complete);
}

function slotsText(slots) {
  return slots.length ? slots.map((slot) => `${slot.kind === "weapon" ? "武" : "防"}${slot.level}`).join(" ") : "なし";
}

function renderBuilds(builds) {
  elements.results.replaceChildren();
  if (!builds.length) {
    elements.results.innerHTML = '<p class="empty">候補がありません。</p>';
    return;
  }
  for (const build of builds) {
    const card = document.createElement("article");
    card.className = "build-card";
    const targetSkills = state.targets.map((target) => {
      const level = build.totals.get(target.id) || 0;
      return `<span class="skill ${level >= target.level ? "met" : ""}">${target.name} Lv${level}/${target.level}</span>`;
    }).join("");
    const equipment = build.armor.map((armor) => `<div><dt>${ARMOR_LABELS[armor.kind]}</dt><dd>${armor.name}</dd></div>`).join("");
    const decorations = build.decorations.length ? build.decorations.map((item) => item.name).join(" / ") : "なし";
    const resistances = Object.entries(build.resistances).map(([key, value]) => `${({ fire: "火", water: "水", thunder: "雷", ice: "氷", dragon: "龍" })[key]} ${value >= 0 ? "+" : ""}${value}`).join(" / ");
    card.innerHTML = `
      <div class="build-heading"><div><h3>${build.charm.name}</h3><span class="build-source">${build.charm.source}</span></div>
      <div class="score">達成スキル ${build.fulfilled}/${state.targets.length}<br>防御力 ${build.defense}</div></div>
      <div class="skills">${targetSkills}</div>
      <dl class="equipment">${equipment}<div><dt>護石</dt><dd>${build.charm.name}</dd></div><div><dt>武器</dt><dd>${build.weapon?.name || "指定なし"}</dd></div></dl>
      <p class="summary"><strong>装飾品:</strong> ${decorations}<br><strong>耐性:</strong> ${resistances}<br><strong>空きスロット:</strong> ${slotsText(build.emptySlots)}</p>`;
    elements.results.append(card);
  }
}

async function initialize() {
  try {
    const [armor, charms, decorations, skills, weapons, charmTable] = await Promise.all([
      fetchJson(`${API_BASE}/armor`), fetchJson(`${API_BASE}/charms`), fetchJson(`${API_BASE}/decorations`),
      fetchJson(`${API_BASE}/skills`), fetchJson(`${API_BASE}/weapons`), fetchJson("./data/random-charm-table.json"),
    ]);
    Object.assign(state, { armor, charms, decorations, skills, weapons, charmTable });
    populateControls();
    setStatus("データを読み込みました。目標スキルを追加して検索してください。");
  } catch (error) {
    console.error(error);
    setStatus("データの取得に失敗しました。HTTPサーバー経由で開き、ネットワーク接続を確認してください。", true);
  }
}

elements.weaponKind.addEventListener("change", updateWeaponOptions);
elements.addSkill.addEventListener("click", addTarget);
elements.search.addEventListener("click", findBuilds);
initialize();
