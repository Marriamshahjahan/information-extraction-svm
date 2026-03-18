async function extractEntities() {

  const text = document.getElementById("articleInput").value.trim();
  const box  = document.getElementById("outputBox");
  const btn  = document.getElementById("extractBtn");

  if (!text) {
    box.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <p>Please paste an article first.</p>
      </div>`;
    return;
  }

  btn.disabled = true;
  box.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Analysing article…</p>
    </div>`;

  try {

    const response = await fetch("http://localhost:8000/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();
    renderEntities(data.result);

  } catch (error) {

    box.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon" style="border-color:#c95c2e44;color:#c95c2e;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <p style="color:#c95c2e;">Extraction failed. Is the server running?</p>
      </div>`;
    console.error(error);

  }

  btn.disabled = false;
}


function renderEntities(result) {

  const box = document.getElementById("outputBox");

  if (!result || result.trim() === "" || result === "No entities found.") {
    box.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
        </div>
        <p>No entities detected in this article.</p>
      </div>`;
    return;
  }

  // ── Parse into a map: { "PERSONS": ["Tim Cook", ...], ... }
  const map = {};
  const lines = result.split("\n");

  lines.forEach(line => {
    line = line.trim();
    if (!line) return;

    // Format 1: "Persons:" header then "- Tim Cook" lines
    if (line.endsWith(":") && !line.includes(" ")) {
      const key = line.replace(":", "").trim();
      if (!map[key]) map[key] = [];
      return;
    }

    // Format 2: "PERSON: Tim Cook" or "ORG: Apple" (spaCy inline)
    const inlineMatch = line.match(/^([A-Z_]+)\s*:\s*(.+)$/);
    if (inlineMatch) {
      const rawType = inlineMatch[1].trim();
      const entity  = inlineMatch[2].trim();
      const label   = normalizeLabel(rawType);
      if (!map[label]) map[label] = [];
      map[label].push(entity);
      return;
    }

    // Format 3: "- Tim Cook" (belongs to last key)
    if (line.startsWith("- ") || line.startsWith("• ")) {
      const entity = line.replace(/^[-•]\s*/, "").trim();
      const keys   = Object.keys(map);
      if (keys.length > 0) {
        map[keys[keys.length - 1]].push(entity);
      }
      return;
    }

    // Format 4: "Persons: Tim Cook, Sam Altman" (comma separated)
    const colonComma = line.match(/^(.+?)\s*:\s*(.+)$/);
    if (colonComma) {
      const label    = normalizeLabel(colonComma[1].trim());
      const entities = colonComma[2].split(",").map(e => e.trim()).filter(Boolean);
      if (!map[label]) map[label] = [];
      map[label].push(...entities);
    }
  });

  const sections = Object.entries(map).filter(([, arr]) => arr.length > 0);

  if (!sections.length) {
    box.innerHTML = `<div class="empty-state"><p>No entities detected.</p></div>`;
    return;
  }

  // ── Render
  let html = `<div class="result-header">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
    Extracted Entities
  </div>`;

  sections.forEach(([type, entities], si) => {

    const delay = si * 0.08;

    html += `
    <div class="entity-section" style="animation-delay:${delay}s">
      <div class="entity-type">
        <span class="entity-icon">${getIcon(type)}</span>
        ${type}
        <span class="entity-count">${entities.length}</span>
      </div>
      <div class="tag-list">`;

    entities.forEach((entity, ei) => {
      html += `<div class="tag" style="animation-delay:${delay + ei * 0.05}s">${entity}</div>`;
    });

    html += `</div></div>`;

    if (si < sections.length - 1) {
      html += `<div class="divider"></div>`;
    }
  });

  box.innerHTML = html;
}


// Normalize spaCy labels → readable names
function normalizeLabel(raw) {
  const map = {
    "PERSON":"Persons","PER":"Persons","PERSONS":"Persons",
    "ORG":"Organizations","ORGANIZATION":"Organizations","ORGANISATIONS":"Organizations",
    "GPE":"Locations","LOC":"Locations","LOCATION":"Locations","LOCATIONS":"Locations",
    "DATE":"Dates","TIME":"Dates","DATES":"Dates",
    "MISC":"Miscellaneous","MISCELLANEOUS":"Miscellaneous",
    "MONEY":"Money","CARDINAL":"Numbers","ORDINAL":"Numbers",
    "EVENT":"Events","PRODUCT":"Products","WORK_OF_ART":"Works",
    "LAW":"Laws","LANGUAGE":"Languages","FAC":"Facilities","NORP":"Groups",
  };
  return map[raw.toUpperCase()] || raw.charAt(0).toUpperCase() + raw.slice(1).toLowerCase();
}


function getIcon(type) {
  const t = type.toLowerCase();
  if (t.includes("person"))       return "👤";
  if (t.includes("org"))          return "🏢";
  if (t.includes("location") || t.includes("place")) return "📍";
  if (t.includes("date") || t.includes("time"))      return "📅";
  return "🔖";
}


// Ctrl/Cmd + Enter shortcut
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("articleInput").addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") extractEntities();
  });
});
