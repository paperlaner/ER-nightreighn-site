const characters = [
  {
    name: "Wylder",
    role: "Боец‑универсал",
    stats: { hp: 240, fp: 65, stamina: 54 },
    scaling: { strength: "A", dexterity: "B", intelligence: "C", faith: "C", arcane: "C" },
  },
  {
    name: "Guardian",
    role: "Танк‑защитник",
    stats: { hp: 280, fp: 55, stamina: 60 },
    scaling: { strength: "B", dexterity: "C", intelligence: "D", faith: "C", arcane: "C" },
  },
  {
    name: "Duchess",
    role: "Ловкий дуэлянт",
    stats: { hp: 220, fp: 75, stamina: 54 },
    scaling: { strength: "D", dexterity: "B", intelligence: "A", faith: "B", arcane: "C" },
  },
  {
    name: "Recluse",
    role: "Маг поддержки",
    stats: { hp: 200, fp: 80, stamina: 54 },
    scaling: { strength: "D", dexterity: "C", intelligence: "S", faith: "S", arcane: "C" },
  },
  {
    name: "Ironeye",
    role: "Дальний урон",
    stats: { hp: 200, fp: 55, stamina: 56 },
    scaling: { strength: "C", dexterity: "A", intelligence: "D", faith: "D", arcane: "B" },
  },
  {
    name: "Raider",
    role: "Силовой боец",
    stats: { hp: 260, fp: 55, stamina: 60 },
    scaling: { strength: "S", dexterity: "C", intelligence: "D", faith: "D", arcane: "C" },
  },
  {
    name: "Executor",
    role: "Крит‑дуэлянт",
    stats: { hp: 220, fp: 55, stamina: 54 },
    scaling: { strength: "C", dexterity: "S", intelligence: "D", faith: "D", arcane: "S" },
  },
  {
    name: "Revenant",
    role: "Колдун‑призыватель",
    stats: { hp: 200, fp: 80, stamina: 54 },
    scaling: { strength: "C", dexterity: "C", intelligence: "B", faith: "S", arcane: "B" },
  },
];

const grid = document.getElementById("grid");
const searchInput = document.getElementById("search");
const sortSelect = document.getElementById("sort");
const descToggle = document.getElementById("desc");

const scalingOrder = { S: 6, A: 5, B: 4, C: 3, D: 2, E: 1 };

function render() {
  const term = searchInput.value.trim().toLowerCase();
  const sortKey = sortSelect.value;
  const desc = descToggle.checked;

  let list = characters.filter((c) => c.name.toLowerCase().includes(term));

  list = list.sort((a, b) => {
    if (sortKey === "name") {
      return a.name.localeCompare(b.name);
    }

    if (sortKey === "strength" || sortKey === "dexterity") {
      const av = scalingOrder[a.scaling[sortKey]];
      const bv = scalingOrder[b.scaling[sortKey]];
      return desc ? bv - av : av - bv;
    }

    const av = a.stats[sortKey];
    const bv = b.stats[sortKey];
    return desc ? bv - av : av - bv;
  });

  grid.innerHTML = "";

  list.forEach((character, index) => {
    const card = document.createElement("article");
    card.className = "card";
    card.style.animationDelay = `${index * 0.05}s`;
    card.innerHTML = `
      <div class="card__header">
        <h2 class="card__title">${character.name}</h2>
        <span class="role">${character.role}</span>
      </div>
      <div class="stats">
        <div class="stat"><strong>${character.stats.hp}</strong><span>HP</span></div>
        <div class="stat"><strong>${character.stats.fp}</strong><span>FP</span></div>
        <div class="stat"><strong>${character.stats.stamina}</strong><span>Stamina</span></div>
      </div>
      <div class="scaling">
        <div><span>Сила</span><b>${character.scaling.strength}</b></div>
        <div><span>Ловкость</span><b>${character.scaling.dexterity}</b></div>
        <div><span>Интеллект</span><b>${character.scaling.intelligence}</b></div>
        <div><span>Вера</span><b>${character.scaling.faith}</b></div>
        <div><span>Тайна</span><b>${character.scaling.arcane}</b></div>
      </div>
    `;
    grid.appendChild(card);
  });
}

searchInput.addEventListener("input", render);
sortSelect.addEventListener("change", render);
descToggle.addEventListener("change", render);

render();
