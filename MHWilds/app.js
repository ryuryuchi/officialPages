const DATA_BASE = "./data";
const ARMOR_KINDS = ["head", "chest", "arms", "waist", "legs"];
const ARMOR_LABELS = { head: "頭", chest: "胴", arms: "腕", waist: "腰", legs: "脚" };
const WEAPON_KIND_LABELS = {
  bow: "弓",
  "charge-blade": "チャージアックス",
  "dual-blades": "双剣",
  "great-sword": "大剣",
  gunlance: "ガンランス",
  hammer: "ハンマー",
  "heavy-bowgun": "ヘビィボウガン",
  "hunting-horn": "狩猟笛",
  "insect-glaive": "操虫棍",
  lance: "ランス",
  "light-bowgun": "ライトボウガン",
  "long-sword": "太刀",
  "switch-axe": "スラッシュアックス",
  "sword-shield": "片手剣",
};
const MAX_ARMOR_PER_PART = 24;
const MAX_PARTIAL_BUILDS = 450;
const MAX_CHARM_CANDIDATES = 320;
const MAX_TARGET_SKILLS = 20;
const MAX_RANDOM_GROUP_CHOICES = 12;
const MAX_RESULTS = 20;

const SAVED_BUILDS_KEY = "mhwilds-saved-builds-v1";
const RESISTANCE_KEYS = ["fire", "water", "thunder", "ice", "dragon"];
const RESISTANCE_LABELS = { fire: "火", water: "水", thunder: "雷", ice: "氷", dragon: "龍" };
const state = {
  armor: [], charms: [], decorations: [], skills: [], weapons: [], charmTable: null, targets: [],
  savedBuilds: [], skillKind: "all",
};
const elements = {
  status: document.querySelector("#status"),
  rank: document.querySelector("#rank-filter"),
  weaponKind: document.querySelector("#weapon-kind"),
  weapon: document.querySelector("#weapon-select"),
  skillSearch: document.querySelector("#skill-search"),
  fixedCharms: document.querySelector("#fixed-charms"),
  randomCharms: document.querySelector("#random-charms"),
  skill: document.querySelector("#skill-select"),
  skillLevel: document.querySelector("#skill-level"),
  addSkill: document.querySelector("#add-skill-button"),
  targets: document.querySelector("#target-skills"),
  search: document.querySelector("#search-button"),
  results: document.querySelector("#results"),
  resultSummary: document.querySelector("#result-summary"),
  maxRarity: document.querySelector("#max-rarity"),
  minDefense: document.querySelector("#min-defense"),
  resistanceInputs: Object.fromEntries(RESISTANCE_KEYS.map((key) => [key, document.querySelector(`#res-${key}`)])),
  simulatorView: document.querySelector("#simulator-view"),
  setsView: document.querySelector("#sets-view"),
  savedBuilds: document.querySelector("#saved-builds"),
  savedCount: document.querySelector("#saved-count"),
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

function filterPreferenceScore(defense, resistances) {
  let score = 0;
  const minimumDefense = elements.minDefense.value === "" ? 0 : Number(elements.minDefense.value);
  if (minimumDefense) score += Math.min(defense, minimumDefense) * 0.25;
  for (const key of RESISTANCE_KEYS) {
    const input = elements.resistanceInputs[key];
    if (input.value !== "") score += Math.min(resistances[key], Number(input.value)) * 12;
  }
  return score;
}

function armorScore(armor) {
  const totals = skillMap(armor.skills);
  return targetScore(totals)
    + armor.slots.reduce((sum, slot) => sum + slot * 3, 0)
    + armor.defense.max / 20
    + filterPreferenceScore(armor.defense.max, armor.resistances);
}

function partialScore(partial) {
  return targetScore(partial.totals)
    + partial.defense / 20
    + filterPreferenceScore(partial.defense, partial.resistances);
}

function selectedWeapon() {
  return state.weapons.find((weapon) => String(weapon.id) === elements.weapon.value) || null;
}

function weaponKindLabel(kind) {
  return WEAPON_KIND_LABELS[kind] || kind;
}

function currentTargetsMet(totals) {
  return state.targets.every((target) => (totals.get(target.id) || 0) >= target.level);
}

function populateControls() {
  const kinds = [...new Set(state.weapons.map((weapon) => weapon.kind))].sort();
  elements.weaponKind.replaceChildren(new Option("指定なし", ""), ...kinds.map((kind) => new Option(weaponKindLabel(kind), kind)));
  ["skill", "skillLevel", "addSkill", "search"].forEach((name) => { elements[name].disabled = false; });
  updateSkillOptions();
  updateWeaponOptions();
}

function updateSkillOptions() {
  const currentId = elements.skill.value;
  const query = elements.skillSearch.value.trim().toLocaleLowerCase("ja");
  const skillOptions = [...state.skills]
    .filter((skill) => state.skillKind === "all" || skill.kind === state.skillKind)
    .filter((skill) => !query || skill.name.toLocaleLowerCase("ja").includes(query))
    .sort((a, b) => a.name.localeCompare(b.name, "ja"));
  elements.skill.replaceChildren(...skillOptions.map((skill) => new Option(skill.name, skill.id)));
  if (skillOptions.some((skill) => String(skill.id) === currentId)) elements.skill.value = currentId;
  updateSkillLevelLimit();
}

function selectedSkill() {
  return state.skills.find((skill) => String(skill.id) === elements.skill.value) || null;
}

function maxSkillLevel(skill) {
  return Math.max(1, ...skill.ranks.map((rank) => rank.level));
}

function updateSkillLevelLimit() {
  const skill = selectedSkill();
  const maximum = skill ? maxSkillLevel(skill) : 1;
  elements.skillLevel.max = String(maximum);
  if (Number(elements.skillLevel.value) > maximum) elements.skillLevel.value = String(maximum);
  elements.skill.disabled = !skill;
  elements.skillLevel.disabled = !skill;
  elements.addSkill.disabled = !skill;
}

function updateWeaponOptions() {
  const kind = elements.weaponKind.value;
  const weapons = state.weapons.filter((weapon) => !kind || weapon.kind === kind)
    .sort((a, b) => a.name.localeCompare(b.name, "ja"));
  elements.weapon.replaceChildren(new Option("武器なし", ""), ...weapons.map((weapon) => new Option(`${weapon.name}（${weaponKindLabel(weapon.kind)}）`, weapon.id)));
  elements.weapon.disabled = false;
}

function renderTargets() {
  if (!state.targets.length) {
    const empty = document.createElement("p");
    empty.className = "target-empty";
    empty.textContent = "目標スキルを追加してください。";
    elements.targets.replaceChildren(empty);
    return;
  }
  elements.targets.replaceChildren(...state.targets.map((target) => {
    const row = document.createElement("div");
    row.className = "target-skill";
    const name = document.createElement("span");
    name.className = "target-name";
    name.textContent = target.name;
    const actions = document.createElement("div");
    actions.className = "target-actions";
    const levelLabel = document.createElement("label");
    levelLabel.className = "target-level-label";
    levelLabel.append("必要Lv");
    const level = document.createElement("select");
    level.setAttribute("aria-label", `${target.name}の必要レベル`);
    for (let value = 1; value <= target.maxLevel; value += 1) {
      level.add(new Option(`Lv ${value}`, String(value)));
    }
    level.value = String(target.level);
    level.addEventListener("change", () => {
      target.level = Number(level.value);
    });
    levelLabel.append(level);
    const remove = document.createElement("button");
    remove.className = "remove-target";
    remove.type = "button";
    remove.ariaLabel = `${target.name}を削除`;
    remove.textContent = "×";
    remove.addEventListener("click", () => {
      state.targets = state.targets.filter((item) => item.id !== target.id);
      renderTargets();
    });
    actions.append(levelLabel, remove);
    row.append(name, actions);
    return row;
  }));
}

function addTarget() {
  const skill = selectedSkill();
  const level = Number(elements.skillLevel.value);
  if (!skill || !Number.isInteger(level) || level < 1 || level > maxSkillLevel(skill)) return;
  const existing = state.targets.find((target) => target.id === skill.id);
  if (existing) {
    existing.level = level;
    existing.maxLevel = maxSkillLevel(skill);
  } else if (state.targets.length < MAX_TARGET_SKILLS) {
    state.targets.push({ id: skill.id, name: skill.name, level, maxLevel: maxSkillLevel(skill) });
  }
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

function passesBuildFilters(build) {
  const minimumDefense = elements.minDefense.value === "" ? 0 : Number(elements.minDefense.value);
  if (build.defense < minimumDefense) return false;
  return RESISTANCE_KEYS.every((key) => {
    const input = elements.resistanceInputs[key];
    return input.value === "" || build.resistances[key] >= Number(input.value);
  });
}

function findBuilds() {
  if (!state.targets.length) {
    elements.results.replaceChildren();
    elements.resultSummary.textContent = "";
    setStatus("少なくとも1つの目標スキルを追加してください。", true);
    return;
  }
  const numericFilters = [elements.minDefense, ...Object.values(elements.resistanceInputs)];
  if (numericFilters.some((input) => input.value !== "" && !input.checkValidity())) {
    setStatus("防御力・耐性の条件には有効な数値を入力してください。", true);
    return;
  }
  setStatus("候補を探索中…");
  const rank = elements.rank.value;
  const maxRarity = elements.maxRarity.value === "" ? Infinity : Number(elements.maxRarity.value);
  const candidatesByKind = new Map(ARMOR_KINDS.map((kind) => [
    kind,
    state.armor.filter((armor) => (
      armor.kind === kind
      && (rank === "all" || armor.rank === rank)
      && armor.rarity <= maxRarity
    ))
      .sort((a, b) => armorScore(b) - armorScore(a)).slice(0, MAX_ARMOR_PER_PART),
  ]));
  if ([...candidatesByKind.values()].some((candidates) => !candidates.length)) {
    setStatus("指定条件に合う防具が全5部位で見つかりません。レア度やランクを見直してください。", true);
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
    })).sort((a, b) => partialScore(b) - partialScore(a)).slice(0, partialLimit);
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
      const build = { ...partial, charm, weapon, totals, decorations: decorationResult.selected, emptySlots: decorationResult.remainingSlots, fulfilled };
      if (passesBuildFilters(build)) builds.push(build);
    }
  }
  builds.sort((a, b) => b.fulfilled - a.fulfilled || targetScore(b.totals) - targetScore(a.totals) || b.defense - a.defense);
  renderBuilds(builds.slice(0, MAX_RESULTS));
  const complete = builds.filter((build) => build.fulfilled === state.targets.length).length;
  elements.resultSummary.textContent = `条件に合う候補 ${builds.length.toLocaleString()} 通り / スキル達成 ${complete.toLocaleString()} 通り`;
  setStatus(
    complete
      ? ""
      : builds.length
        ? "条件を満たす装備はありますが、目標スキルが揃う候補はありません。"
        : "条件に合う候補がありません。詳細条件を見直してください。",
    !complete,
  );
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function slotsText(slots) {
  return slots.length ? slots.map((slot) => `${slot.kind === "weapon" ? "武" : "防"}${slot.level}`).join(" ") : "なし";
}

function charmSkillsText(skills) {
  if (!skills.size) return "スキルなし";
  return [...skills].map(([skillId, level]) => {
    const skill = state.skills.find((entry) => String(entry.id) === String(skillId));
    return `${skill?.name || `スキル${skillId}`} Lv${level}`;
  }).join(" / ");
}

function charmSlotsText(slots) {
  return slots.length
    ? slots.map((slot) => `${slot.kind === "weapon" ? "武" : "防"}${slot.level}`).join(" ")
    : "スロットなし";
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
      return `<span class="skill ${level >= target.level ? "met" : ""}">${escapeHtml(target.name)} Lv${level}/${target.level}</span>`;
    }).join("");
    const equipment = build.armor.map((armor) => `<div><dt>${ARMOR_LABELS[armor.kind]}</dt><dd>${escapeHtml(armor.name)}</dd></div>`).join("");
    const decorations = build.decorations.length ? build.decorations.map((item) => escapeHtml(item.name)).join(" / ") : "なし";
    const resistances = Object.entries(build.resistances).map(([key, value]) => `${RESISTANCE_LABELS[key]} ${value >= 0 ? "+" : ""}${value}`).join(" / ");
    card.innerHTML = `
      <div class="build-heading"><div><h3>${escapeHtml(build.charm.name)}</h3><span class="build-source">${escapeHtml(build.charm.source)}</span></div>
      <div class="score">達成スキル ${build.fulfilled}/${state.targets.length}<br>防御力 ${build.defense}</div></div>
      <div class="charm-details"><span>${escapeHtml(charmSkillsText(build.charm.skills))}</span><span>${escapeHtml(charmSlotsText(build.charm.slots))}</span></div>
      <div class="skills">${targetSkills}</div>
      <dl class="equipment">${equipment}<div><dt>護石</dt><dd>${escapeHtml(build.charm.name)}</dd></div><div><dt>武器</dt><dd>${escapeHtml(build.weapon?.name || "指定なし")}</dd></div></dl>
      <p class="summary"><strong>装飾品:</strong> ${decorations}<br><strong>耐性:</strong> ${resistances}<br><strong>空きスロット:</strong> ${slotsText(build.emptySlots)}</p>
      <div class="build-actions"><button class="save-build" type="button">マイセットに保存</button></div>`;
    card.querySelector(".save-build").addEventListener("click", () => saveBuild(build));
    elements.results.append(card);
  }
}

function createSavedBuild(build) {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    savedAt: new Date().toISOString(),
    targets: state.targets.map(({ name, level }) => ({ name, level })),
    armor: build.armor.map((armor) => ({ kind: ARMOR_LABELS[armor.kind], name: armor.name })),
    charm: build.charm.name,
    charmSkills: [...build.charm.skills].map(([skillId, level]) => {
      const skill = state.skills.find((entry) => String(entry.id) === String(skillId));
      return { name: skill?.name || `スキル${skillId}`, level };
    }),
    charmSlots: build.charm.slots.map((slot) => ({ ...slot })),
    weapon: build.weapon?.name || "指定なし",
    decorations: build.decorations.map((decoration) => decoration.name),
    defense: build.defense,
    resistances: { ...build.resistances },
  };
}

function saveBuild(build) {
  const savedBuild = createSavedBuild(build);
  state.savedBuilds.unshift(savedBuild);
  try {
    localStorage.setItem(SAVED_BUILDS_KEY, JSON.stringify(state.savedBuilds));
    renderSavedBuilds();
    setStatus("マイセットに保存しました。");
  } catch (error) {
    state.savedBuilds.shift();
    console.error("Failed to save build to local storage.", error);
    setStatus("マイセットを保存できませんでした。ブラウザーの保存領域を確認してください。", true);
  }
}

function removeSavedBuild(id) {
  const previous = state.savedBuilds;
  state.savedBuilds = previous.filter((build) => build.id !== id);
  try {
    localStorage.setItem(SAVED_BUILDS_KEY, JSON.stringify(state.savedBuilds));
    renderSavedBuilds();
  } catch (error) {
    state.savedBuilds = previous;
    console.error("Failed to remove saved build from local storage.", error);
    setStatus("マイセットを削除できませんでした。ブラウザーの保存領域を確認してください。", true);
  }
}

function renderSavedBuilds() {
  elements.savedCount.textContent = String(state.savedBuilds.length);
  if (!state.savedBuilds.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "保存したマイセットはありません。";
    elements.savedBuilds.replaceChildren(empty);
    return;
  }
  elements.savedBuilds.replaceChildren(...state.savedBuilds.map((savedBuild) => {
    const card = document.createElement("article");
    card.className = "build-card";
    const title = document.createElement("h3");
    title.textContent = `${savedBuild.armor.map((item) => item.name).join(" / ")} 装備`;
    const meta = document.createElement("p");
    meta.className = "saved-meta";
    meta.textContent = `保存日時: ${new Date(savedBuild.savedAt).toLocaleString("ja-JP")}`;
    const targets = document.createElement("p");
    targets.className = "summary";
    targets.textContent = `目標スキル: ${savedBuild.targets.map((target) => `${target.name} Lv${target.level}`).join(" / ") || "なし"}`;
    const equipment = document.createElement("p");
    equipment.className = "summary";
    equipment.textContent = `護石: ${savedBuild.charm} / 武器: ${savedBuild.weapon} / 防御力: ${savedBuild.defense}`;
    const charmDetails = document.createElement("p");
    charmDetails.className = "charm-details";
    const charmSkills = (savedBuild.charmSkills || [])
      .map((skill) => `${skill.name} Lv${skill.level}`)
      .join(" / ") || "スキルなし";
    const charmSlots = (savedBuild.charmSlots || [])
      .map((slot) => `${slot.kind === "weapon" ? "武" : "防"}${slot.level}`)
      .join(" ") || "スロットなし";
    charmDetails.textContent = `${charmSkills}　${charmSlots}`;
    const resistances = RESISTANCE_KEYS.map((key) => `${RESISTANCE_LABELS[key]} ${savedBuild.resistances[key] >= 0 ? "+" : ""}${savedBuild.resistances[key]}`).join(" / ");
    const details = document.createElement("p");
    details.className = "summary";
    details.textContent = `装飾品: ${savedBuild.decorations.join(" / ") || "なし"} / 耐性: ${resistances}`;
    const actions = document.createElement("div");
    actions.className = "build-actions";
    const remove = document.createElement("button");
    remove.className = "delete-build";
    remove.type = "button";
    remove.textContent = "削除";
    remove.addEventListener("click", () => removeSavedBuild(savedBuild.id));
    actions.append(remove);
    card.append(title, meta, targets, equipment, charmDetails, details, actions);
    return card;
  }));
}

function switchView(viewId) {
  const showingSets = viewId === "sets-view";
  elements.simulatorView.hidden = showingSets;
  elements.setsView.hidden = !showingSets;
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    const active = tab.dataset.view === viewId;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-pressed", String(active));
  });
  if (showingSets) renderSavedBuilds();
}

async function initialize() {
  try {
    const [armor, charms, decorations, skills, weapons, charmTable] = await Promise.all([
      fetchJson(`${DATA_BASE}/armor.json`), fetchJson(`${DATA_BASE}/charms.json`),
      fetchJson(`${DATA_BASE}/decorations.json`), fetchJson(`${DATA_BASE}/skills.json`),
      fetchJson(`${DATA_BASE}/weapons.json`), fetchJson(`${DATA_BASE}/random-charm-table.json`),
    ]);
    Object.assign(state, { armor, charms, decorations, skills, weapons, charmTable });
    loadSavedBuilds();
    populateControls();
    renderSavedBuilds();
    setStatus(savedBuildLoadError
      ? "シミュレーターのデータを読み込みましたが、マイセットの読み込みに失敗しました。"
      : "データを読み込みました。スキルを選択して検索してください。",
    savedBuildLoadError);
  } catch (error) {
    console.error(error);
    setStatus("データの取得に失敗しました。HTTPサーバー経由で開き、ネットワーク接続を確認してください。", true);
  }
}

let savedBuildLoadError = false;

function isSavedBuild(value) {
  return Boolean(value
    && typeof value.id === "string"
    && typeof value.savedAt === "string"
    && Number.isFinite(Date.parse(value.savedAt))
    && typeof value.charm === "string"
    && typeof value.weapon === "string"
    && Array.isArray(value.targets)
    && value.targets.every((target) => target && typeof target.name === "string" && Number.isInteger(target.level))
    && Array.isArray(value.armor)
    && value.armor.every((armor) => armor && typeof armor.kind === "string" && typeof armor.name === "string")
    && Array.isArray(value.decorations)
    && value.decorations.every((decoration) => typeof decoration === "string")
    && value.resistances
    && RESISTANCE_KEYS.every((key) => Number.isFinite(value.resistances[key]))
    && Number.isFinite(value.defense));
}

function loadSavedBuilds() {
  try {
    const serialized = localStorage.getItem(SAVED_BUILDS_KEY);
    if (!serialized) return;
    const parsed = JSON.parse(serialized);
    if (!Array.isArray(parsed)) throw new Error("Saved builds must be an array.");
    state.savedBuilds = parsed.filter(isSavedBuild);
    if (state.savedBuilds.length !== parsed.length) {
      throw new Error("One or more saved builds have an invalid format.");
    }
  } catch (error) {
    savedBuildLoadError = true;
    state.savedBuilds = [];
    console.error("Failed to load saved builds from local storage.", error);
  }
}

elements.weaponKind.addEventListener("change", updateWeaponOptions);
elements.skillSearch.addEventListener("input", updateSkillOptions);
elements.skill.addEventListener("change", updateSkillLevelLimit);
elements.addSkill.addEventListener("click", addTarget);
elements.search.addEventListener("click", findBuilds);
document.querySelectorAll(".skill-kind-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    state.skillKind = tab.dataset.kind;
    document.querySelectorAll(".skill-kind-tab").forEach((item) => {
      const active = item === tab;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    updateSkillOptions();
  });
});
document.querySelectorAll(".mode-tab").forEach((tab) => {
  tab.addEventListener("click", () => switchView(tab.dataset.view));
});
initialize();
