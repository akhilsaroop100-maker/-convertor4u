(() => {
  for (const suffix of ["recent", "favorites", "theme"]) {
    const oldKey = `convert26-${suffix}`, newKey = `convertor4u-${suffix}`;
    if (localStorage.getItem(newKey) === null && localStorage.getItem(oldKey) !== null) localStorage.setItem(newKey, localStorage.getItem(oldKey));
  }
  const box = document.querySelector("#converter");
  const commandForm = document.querySelector("#command-form");
  const commandInput = document.querySelector("#command-input");
  const commandResult = document.querySelector("#command-result");
  if (!box) return;

  const value = document.querySelector("#from-value");
  const from = document.querySelector("#from-unit");
  const to = document.querySelector("#to-unit");
  const result = document.querySelector("#result");
  const rate = document.querySelector("#rate");
  const formatMode = document.querySelector("#format-mode");
  const precision = document.querySelector("#precision");
  const multiPanel = document.querySelector("#multi-results");
  const providerStatus = document.querySelector("#provider-status");
  const searchResults = document.querySelector("#unit-search-results");
  let timer;
  let requestNumber = 0;
  let lastRawResult = "0";
  let lastRawRate = "0";

  const selected = select => select.options[select.selectedIndex];
  const unitSymbol = select => selected(select)?.dataset.symbol || "";
  const fraction = (number, denominator) => {
    const sign = number < 0 ? "−" : "";
    const absolute = Math.abs(number);
    let whole = Math.floor(absolute);
    let numerator = Math.round((absolute - whole) * denominator);
    if (numerator === denominator) { whole += 1; numerator = 0; }
    const gcd = (a, b) => b ? gcd(b, a % b) : a;
    if (!numerator) return `${sign}${whole}`;
    const divisor = gcd(numerator, denominator);
    return `${sign}${whole ? whole + " " : ""}${numerator / divisor}/${denominator / divisor}`;
  };
  const formatNumber = (number, targetSymbol = "", exactText = "") => {
    if (!Number.isFinite(number)) return "—";
    if (number === 0) return "0";
    const digits = Number(precision?.value || 4);
    const mode = formatMode?.value || "auto";
    if (mode === "auto" && exactText) return exactText;
    if (mode === "fixed") return number.toFixed(digits);
    if (mode === "significant") return Number(number.toPrecision(digits)).toString();
    if (mode === "scientific") return number.toExponential(digits).replace("e+", "e");
    if (mode === "fraction" && targetSymbol === "in") return fraction(number, 2 ** digits);
    if (Math.abs(number) >= 1e12 || Math.abs(number) < 1e-8) return number.toExponential(8).replace("e+", "e");
    return Number(number.toPrecision(12)).toString();
  };
  const convertLocal = (amount, source, target) => {
    const sourceScale = Number(source.dataset.scale), sourceOffset = Number(source.dataset.offset);
    const targetScale = Number(target.dataset.scale), targetOffset = Number(target.dataset.offset);
    if (![amount, sourceScale, sourceOffset, targetScale, targetOffset].every(Number.isFinite)) throw new Error("Conversion definition unavailable.");
    let base;
    if (source.dataset.mode === "reciprocal") {
      if (amount === 0) throw new Error("A reciprocal unit cannot convert zero.");
      base = sourceScale / amount;
    } else base = amount * sourceScale + sourceOffset;
    if (target.dataset.mode === "reciprocal") {
      if (base === 0) throw new Error("A reciprocal result is undefined at zero.");
      return targetScale / base;
    }
    return (base - targetOffset) / targetScale;
  };

  const setProviderStatus = status => {
    if (!providerStatus) return;
    const labels = {live: "LIVE RATES_", cached: "CACHED RATES_", unavailable: "PROVIDER OFFLINE_", exact: "EXACT ENGINE_"};
    providerStatus.classList.toggle("unavailable", status === "unavailable");
    providerStatus.innerHTML = `<i></i> ${labels[status] || "READY_"}`;
  };

  async function renderMulti() {
    if (!multiPanel || multiPanel.hidden) return;
    const list = multiPanel.querySelector("ul");
    list.textContent = "Loading comparisons…";
    try {
      const query = new URLSearchParams({category: box.dataset.category, from: from.value, value: value.value || "0"});
      const response = await fetch("/api/multi-convert/?" + query);
      const data = await response.json();
      if (!response.ok || data.error) throw new Error(data.error || "Multi-convert is unavailable.");
      list.replaceChildren(...data.items.map(item => {
        const row = document.createElement("li"), strong = document.createElement("strong"), label = document.createElement("span");
        strong.textContent = item.result; label.textContent = `${item.symbol} · ${item.name}`;
        row.append(strong, label); return row;
      }));
      setProviderStatus(data.provider_status);
    } catch (error) { list.textContent = error.message; setProviderStatus("unavailable"); }
  }

  async function calculate() {
    if (!from.value || !to.value) return;
    clearTimeout(timer);
    timer = setTimeout(async () => {
      const activeRequest = ++requestNumber;
      try {
        const amount = (value.value || "0").trim();
        if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(amount)) throw new Error("Enter a valid number.");
        const query = new URLSearchParams({category: box.dataset.category, from: from.value, to: to.value, value: amount});
        const response = await fetch("/api/convert/?" + query);
        const data = await response.json();
        if (activeRequest !== requestNumber) return;
        if (!response.ok || data.error) throw new Error(data.error || "Conversion is temporarily unavailable.");
        lastRawResult = data.result; lastRawRate = data.rate;
        const shown = formatNumber(Number(lastRawResult), unitSymbol(to), lastRawResult);
        result.textContent = shown;
        const rateDate = data.rate_date ? ` · RATE ${data.rate_date}` : "";
        rate.textContent = `1 ${unitSymbol(from)} = ${formatNumber(Number(lastRawRate), unitSymbol(to), lastRawRate)} ${unitSymbol(to)}${rateDate}${data.rate_stale ? " · LAST KNOWN RATE" : ""}`;
        setProviderStatus(data.provider_status);
        saveRecent(`/${box.dataset.category}/${from.value}-to-${to.value}/`, shown);
        await renderMulti();
      } catch (error) { result.textContent = "—"; rate.textContent = error.message; if (box.dataset.category === "currency") setProviderStatus("unavailable"); }
    }, 80);
  }

  function saveRecent(url, converted) {
    const key = "convertor4u-recent";
    let items = JSON.parse(localStorage.getItem(key) || "[]");
    const row = {url, text: `${value.value} ${from.value} → ${converted} ${to.value}`};
    items = [row, ...items.filter(item => item.url !== url)].slice(0, 5);
    localStorage.setItem(key, JSON.stringify(items)); renderLocal();
  }
  function renderLocal() {
    for (const [key, id] of [["convertor4u-recent", "recent-list"], ["convertor4u-favorites", "favorite-list"]]) {
      const element = document.getElementById(id); if (!element) continue;
      const items = JSON.parse(localStorage.getItem(key) || "[]");
      element.replaceChildren();
      if (!items.length) { element.textContent = key.includes("recent") ? "Your recent conversions stay on this device." : "Star a conversion for quick access."; continue; }
      for (const item of items) {
        const row = document.createElement("p"), link = document.createElement("a"), remove = document.createElement("button");
        link.href = item.url; link.textContent = item.text;
        remove.type = "button"; remove.textContent = "REMOVE"; remove.dataset.removeLocal = key; remove.dataset.url = item.url; remove.setAttribute("aria-label", `Remove ${item.text}`);
        row.append(link, remove); element.append(row);
      }
    }
  }

  async function loadCategory(slug, activeButton = null) {
    const response = await fetch(`/api/categories/${slug}/units/`);
    const data = await response.json();
    if (data.error) throw new Error(data.error);
    box.dataset.category = slug;
    document.querySelectorAll(".category-tabs [data-category]").forEach(item => item.classList.toggle("active", item === activeButton || item.dataset.category === slug));
    const buildOptions = () => data.units.map(unit => {
      const option = document.createElement("option");
      option.value = unit.slug; option.textContent = `${unit.name} · ${unit.symbol}`;
      option.dataset.scale = unit.scale; option.dataset.offset = unit.offset; option.dataset.symbol = unit.symbol; option.dataset.mode = unit.mode;
      option.dataset.search = [unit.name, unit.plural, unit.symbol, unit.slug, unit.aliases].join(" ");
      return option;
    });
    from.replaceChildren(...buildOptions()); to.replaceChildren(...buildOptions()); to.selectedIndex = Math.min(1, to.length - 1);
    document.querySelector("#unit-search")?.dispatchEvent(new Event("input"));
  }

  value.addEventListener("input", calculate); from.addEventListener("change", calculate); to.addEventListener("change", calculate);
  formatMode?.addEventListener("change", calculate); precision?.addEventListener("change", calculate);
  document.querySelector(".swap")?.addEventListener("click", () => { const current = from.value; from.value = to.value; to.value = current; calculate(); });
  document.querySelector("#copy")?.addEventListener("click", async event => {
    await navigator.clipboard.writeText(`${value.value} ${unitSymbol(from)} = ${result.textContent} ${unitSymbol(to)}\n${rate.textContent}`);
    event.currentTarget.textContent = "COPIED ✓"; setTimeout(() => event.currentTarget.textContent = "COPY CALCULATION", 1200);
  });
  document.querySelector("#favorite")?.addEventListener("click", event => {
    const key = "convertor4u-favorites", url = `/${box.dataset.category}/${from.value}-to-${to.value}/`;
    let items = JSON.parse(localStorage.getItem(key) || "[]");
    items = [{url, text: `${from.value} → ${to.value}`}, ...items.filter(item => item.url !== url)].slice(0, 8);
    localStorage.setItem(key, JSON.stringify(items)); event.currentTarget.textContent = "★ FAVORITED"; renderLocal();
  });
  document.addEventListener("click", event => {
    const remove = event.target.closest("[data-remove-local]");
    if (remove) {
      const key = remove.dataset.removeLocal;
      const items = JSON.parse(localStorage.getItem(key) || "[]").filter(item => item.url !== remove.dataset.url);
      localStorage.setItem(key, JSON.stringify(items)); renderLocal();
    }
    const clear = event.target.closest("[data-clear-local]");
    if (clear) { localStorage.removeItem(clear.dataset.clearLocal); renderLocal(); }
    const choose = event.target.closest("[data-unit-choice]");
    if (choose) { const select = choose.dataset.unitChoice === "from" ? from : to; select.value = choose.dataset.unitSlug; select.dispatchEvent(new Event("change")); }
  });
  document.querySelector("#share-conversion")?.addEventListener("click", async event => {
    const query = new URLSearchParams({category: box.dataset.category, value: value.value, from: from.value, to: to.value});
    const url = `${location.origin}${location.pathname}?${query}`;
    await navigator.clipboard.writeText(url); event.currentTarget.textContent = "LINK COPIED ✓";
    setTimeout(() => event.currentTarget.textContent = "SHARE LINK", 1200);
  });
  document.querySelector("#toggle-multi")?.addEventListener("click", event => { multiPanel.hidden = false; event.currentTarget.setAttribute("aria-expanded", "true"); renderMulti(); });
  document.querySelector("#close-multi")?.addEventListener("click", () => { multiPanel.hidden = true; document.querySelector("#toggle-multi")?.setAttribute("aria-expanded", "false"); });
  document.querySelectorAll(".category-tabs [data-category]").forEach(button => button.addEventListener("click", async () => { try { await loadCategory(button.dataset.category, button); calculate(); } catch (error) { rate.textContent = error.message; } }));
  const normalizeSearch = text => text.toLowerCase().normalize("NFKD").replace(/[^a-z0-9°/]+/g, " ").trim();
  const distance = (a, b) => { const row = [...Array(b.length + 1).keys()]; for (let i = 1; i <= a.length; i++) { let previous = row[0]; row[0] = i; for (let j = 1; j <= b.length; j++) { const saved = row[j]; row[j] = Math.min(row[j] + 1, row[j - 1] + 1, previous + (a[i - 1] === b[j - 1] ? 0 : 1)); previous = saved; } } return row[b.length]; };
  const searchScore = (haystack, needle) => {
    if (!needle) return 0; if (haystack === needle) return 100; if (haystack.includes(needle)) return 80 - haystack.indexOf(needle);
    const words = haystack.split(" "); const closest = Math.min(...words.map(word => distance(word, needle)));
    return closest <= Math.max(1, Math.floor(needle.length / 3)) ? 50 - closest : -1;
  };
  document.querySelector("#unit-search")?.addEventListener("input", event => {
    const query = normalizeSearch(event.target.value);
    const options = [...from.options];
    for (const select of [from, to]) for (const option of select.options) option.hidden = Boolean(query) && searchScore(normalizeSearch(option.dataset.search || option.text), query) < 0;
    if (!searchResults) return;
    searchResults.replaceChildren(); searchResults.hidden = !query;
    if (!query) return;
    const matches = options.map(option => ({option, score: searchScore(normalizeSearch(option.dataset.search || option.text), query)})).filter(item => item.score >= 0).sort((a, b) => b.score - a.score).slice(0, 6);
    if (!matches.length) { searchResults.textContent = "No close unit matches."; return; }
    for (const {option} of matches) {
      const row = document.createElement("div"), name = document.createElement("strong"), fromButton = document.createElement("button"), toButton = document.createElement("button");
      name.textContent = option.text; fromButton.textContent = "USE FROM"; toButton.textContent = "USE TO";
      fromButton.type = toButton.type = "button"; fromButton.dataset.unitChoice = "from"; toButton.dataset.unitChoice = "to"; fromButton.dataset.unitSlug = toButton.dataset.unitSlug = option.value;
      row.append(name, fromButton, toButton); searchResults.append(row);
    }
  });
  document.querySelector(".theme")?.addEventListener("click", () => { document.body.classList.toggle("dark"); localStorage.setItem("convertor4u-theme", document.body.classList.contains("dark") ? "dark" : "light"); });

  commandForm?.addEventListener("submit", async event => {
    event.preventDefault(); commandResult.textContent = "CALCULATING_";
    try {
      const response = await fetch(`/api/query/?q=${encodeURIComponent(commandInput.value)}`); const data = await response.json();
      if (data.error) throw new Error(data.error);
      commandResult.innerHTML = `<a href="${data.url}"><strong>${data.input} = ${data.result} ${data.to_symbol}</strong><span>${data.from_name} → ${data.to_name} · OPEN DETAILS ↗</span></a>`;
      await loadCategory(data.category); value.value = data.amount; from.value = data.from; to.value = data.to; calculate();
    } catch (error) { commandResult.textContent = error.message; }
  });
  document.addEventListener("keydown", event => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); commandInput?.focus(); } });

  async function hydrate() {
    const params = new URLSearchParams(location.search);
    const category = params.get("category"), fromUnit = params.get("from"), toUnit = params.get("to"), amount = params.get("value");
    try { if (category && category !== box.dataset.category) await loadCategory(category); } catch (_) {}
    if (amount !== null) value.value = amount; if (fromUnit) from.value = fromUnit; if (toUnit) to.value = toUnit;
    calculate();
  }
  if (localStorage.getItem("convertor4u-theme") === "dark") document.body.classList.add("dark");
  renderLocal(); hydrate();

  const chart = document.querySelector("[data-currency-chart]");
  if (chart) (async () => {
    const canvas = chart.querySelector("canvas"), summary = chart.querySelector(".chart-summary");
    try {
      const response = await fetch(`/api/currency/history/?from=${encodeURIComponent(chart.dataset.from)}&to=${encodeURIComponent(chart.dataset.to)}&days=30`);
      const data = await response.json(); if (!response.ok || data.error) throw new Error(data.error || "History unavailable.");
      const values = data.points.map(point => Number(point.rate)), context = canvas.getContext("2d"), ratio = window.devicePixelRatio || 1;
      const width = canvas.clientWidth || 760, height = canvas.clientHeight || 260; canvas.width = width * ratio; canvas.height = height * ratio; context.scale(ratio, ratio);
      const min = Math.min(...values), max = Math.max(...values), range = max - min || 1, pad = 24;
      context.clearRect(0, 0, width, height); context.strokeStyle = getComputedStyle(document.body).getPropertyValue("--line"); context.lineWidth = 1;
      for (let i = 0; i < 4; i++) { const y = pad + (height - pad * 2) * i / 3; context.beginPath(); context.moveTo(pad, y); context.lineTo(width - pad, y); context.stroke(); }
      context.strokeStyle = getComputedStyle(document.body).getPropertyValue("--orange"); context.lineWidth = 3; context.beginPath();
      values.forEach((point, index) => { const x = pad + (width - pad * 2) * index / Math.max(values.length - 1, 1), y = height - pad - ((point - min) / range) * (height - pad * 2); index ? context.lineTo(x, y) : context.moveTo(x, y); }); context.stroke();
      const change = ((values.at(-1) / values[0] - 1) * 100).toFixed(2); summary.textContent = `${data.points[0].date} to ${data.points.at(-1).date} · ${values[0]} to ${values.at(-1)} · ${Number(change) >= 0 ? "+" : ""}${change}%`;
    } catch (error) { summary.textContent = `${error.message} Current conversion remains available when a cached rate exists.`; }
  })();
})();
