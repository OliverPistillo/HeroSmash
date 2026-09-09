const DATA_BASE_PATH = "data";

export let RUNTIME = {
  version: "1.11.0",
  label: "v1.11",
  title: "Hero Smash",
  subtitle: "Market Actions Polish",
  homeTagline: "Hero Draft · Arena Market · Clear Actions",
  buildNote: "Build integrata: runtime JSON, league fix, hero draft, arena market, recap round, inspect carta e azioni market più leggibili.",
  footer: "v1.11 Market Actions"
};

export let BRANCHES = [];
export let HEROES = [];
export let ENEMIES = [];
export let CARDS = [];
export let ECONOMY = {};

// Registry JSON completo per AssetManager.loadFromRegistry().
export let ASSET_REGISTRY = { version: "", images: {} };

// Fallback semplice usato se il registry asset fallisce.
export let ASSET_MANIFEST = { heroes: {}, cards: {} };

export let FINAL_ART_MANIFEST = {};
export let CARD_FRAMES_MANIFEST = {};
export let BRANCH_ICONS_MANIFEST = {};
export let MARKET_UI_MANIFEST = {};

let loaded = false;

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json();
}

function flattenPathManifest(records = {}) {
  return Object.fromEntries(
    Object.entries(records)
      .map(([key, value]) => [key, typeof value === "string" ? value : value?.path])
      .filter(([, path]) => typeof path === "string" && path.length)
  );
}

function buildSimpleAssetManifest(assetIndex = {}) {
  const heroes = Object.fromEntries(
    Object.entries(assetIndex.heroes || {})
      .map(([id, rec]) => [id, rec?.path])
      .filter(([, path]) => typeof path === "string" && path.length)
  );
  const cards = Object.fromEntries(
    Object.entries(assetIndex.cards || {})
      .map(([id, rec]) => [id, rec?.path])
      .filter(([, path]) => typeof path === "string" && path.length)
  );

  // Ultimo paracadute: usa i path dichiarati direttamente nei dati gameplay.
  for (const h of HEROES) if (h?.id && h?.image && !heroes[h.id]) heroes[h.id] = h.image;
  for (const c of CARDS) if (c?.id && c?.image && !cards[c.id]) cards[c.id] = c.image;

  return { heroes, cards };
}

export async function loadGameData(basePath = DATA_BASE_PATH) {
  if (loaded) return;

  const [
    runtime,
    branches,
    heroes,
    enemies,
    cards,
    economy,
    assetRegistry,
    assetIndex,
    finalArt,
    uiAssets
  ] = await Promise.all([
    loadJson(`${basePath}/runtime.json`),
    loadJson(`${basePath}/branches.json`),
    loadJson(`${basePath}/heroes.json`),
    loadJson(`${basePath}/enemies.json`),
    loadJson(`${basePath}/cards.json`),
    loadJson(`${basePath}/economy.json`),
    loadJson(`${basePath}/asset_manifest.json`),
    loadJson(`${basePath}/asset_index.json`),
    loadJson(`${basePath}/final_art.json`),
    loadJson(`${basePath}/ui_assets.json`)
  ]);

  RUNTIME = { ...RUNTIME, ...runtime };
  BRANCHES = branches;
  HEROES = heroes;
  ENEMIES = enemies;
  CARDS = cards;
  ECONOMY = economy;
  ASSET_REGISTRY = assetRegistry;
  ASSET_MANIFEST = buildSimpleAssetManifest(assetIndex);
  FINAL_ART_MANIFEST = flattenPathManifest(finalArt.images || finalArt);
  CARD_FRAMES_MANIFEST = { ...(uiAssets.cardFrames || {}) };
  BRANCH_ICONS_MANIFEST = { ...(uiAssets.branchIcons || {}) };
  MARKET_UI_MANIFEST = { ...(uiAssets.marketUi || {}) };

  loaded = true;
}

export function isGameDataLoaded() {
  return loaded;
}

export function requireGameData() {
  if (!loaded) throw new Error("Game data non caricati. Chiama loadGameData() prima di creare GameState o scene gameplay.");
}
