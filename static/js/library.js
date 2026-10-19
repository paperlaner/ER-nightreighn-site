document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-validate-search]");
  if (form) {
    const input = form.querySelector('input[name="q"]');
    const hint = form.querySelector(".form-hint");

    form.addEventListener("submit", (event) => {
      const value = input.value.trim();
      if (value.length > 0 && value.length < 2) {
        event.preventDefault();
        hint.textContent = "Введите минимум 2 символа для поиска.";
        hint.style.color = "#d46a6a";
        input.focus();
      }
    });

    input.addEventListener("input", () => {
      if (input.value.trim().length >= 2 || input.value.trim().length === 0) {
        hint.textContent = "JS проверяет, чтобы запрос содержал минимум 2 символа.";
        hint.style.color = "";
      }
    });
  }

  const grid = document.getElementById("grid");
  const searchInput = document.getElementById("search");
  const sortSelect = document.getElementById("sort");
  const descToggle = document.getElementById("desc");

  if (!grid || !searchInput || !sortSelect || !descToggle) {
    return;
  }

  const cards = Array.from(grid.querySelectorAll(".card"));

  const readValue = (card, key) => {
    if (key === "name") {
      return card.dataset.name;
    }
    return Number(card.dataset[key]);
  };

  const renderCards = () => {
    const term = searchInput.value.trim().toLowerCase();
    const sortKey = sortSelect.value;
    const desc = descToggle.checked;

    const filtered = cards.filter((card) => card.dataset.name.includes(term));

    filtered.sort((a, b) => {
      const av = readValue(a, sortKey);
      const bv = readValue(b, sortKey);
      if (sortKey === "name") {
        return desc ? String(bv).localeCompare(String(av)) : String(av).localeCompare(String(bv));
      }
      return desc ? bv - av : av - bv;
    });

    cards.forEach((card) => {
      card.style.display = "none";
    });

    filtered.forEach((card, index) => {
      card.style.display = "";
      card.style.animationDelay = `${index * 0.05}s`;
      grid.appendChild(card);
    });
  };

  searchInput.addEventListener("input", renderCards);
  sortSelect.addEventListener("change", renderCards);
  descToggle.addEventListener("change", renderCards);
  renderCards();
});
