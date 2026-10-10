// Catalogue rules shared by the page and its validation fixtures.
export const DEFAULT_GROUPS = [
  { id: 'small-combat-craft', name: 'Small combat craft' },
  { id: 'fleet-warships', name: 'Fleet warships' },
  { id: 'transports-and-support', name: 'Transports & support' },
  { id: 'satellites-and-defence', name: 'Satellites & defence' },
  { id: 'stations-and-infrastructure', name: 'Stations & infrastructure' },
  { id: 'weapons-and-components', name: 'Weapons & components' },
  { id: 'environment-and-planets', name: 'Environment & planets' },
  { id: 'hud-and-mission-mods', name: 'HUD & mission mods' },
  { id: 'cockpits', name: 'Cockpits' },
];

const legacyGroups = {
  'alliance-fighters': 'small-combat-craft',
  'coalition-fighters': 'small-combat-craft',
  'torpedo-bombers': 'small-combat-craft',
  'alliance-capital-ships': 'fleet-warships',
  'coalition-capital-ships': 'fleet-warships',
  'uncategorised-ships': 'transports-and-support',
  weapons: 'weapons-and-components',
  'environment-and-planets': 'environment-and-planets',
  hud: 'hud-and-mission-mods',
};

export function catalogueGroups(catalogue) {
  return catalogue.groups?.length ? catalogue.groups : DEFAULT_GROUPS;
}

export function groupForCategory(catalogue, categoryId) {
  const category = catalogue.categories.find(item => item.id === categoryId);
  return category?.group || legacyGroups[categoryId] || catalogueGroups(catalogue)[0]?.id;
}

export function selectLivery(asset, requestedId = null) {
  const liveries = asset.liveries || [];
  return liveries.find(livery => livery.id === requestedId)
    || liveries.find(livery => livery.id === asset.defaultLivery)
    || liveries[0]
    || null;
}

export function requirementsFor(asset, requestedId = null) {
  const livery = selectLivery(asset, requestedId);
  const seen = new Set();
  return [...(asset.requires || []), ...(livery?.requires || [])].filter(requirement => {
    if (typeof requirement !== 'string' || !requirement.trim()) return false;
    const key = requirement.trim().toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).map(requirement => requirement.trim());
}

// These fields describe one release or preview, and must never leak into another livery.
const liveryFields = new Set([
  'preview', 'images', 'model', 'previewType', 'previewSource', 'defaultPreview',
  'download', 'release', 'checksum', 'checksumUrl', 'downloadBytes', 'version',
  'tag', 'assetRevision', 'previewArtworkRevision', 'modFolder', 'notes', 'validationSummary',
]);

export function resolveAsset(asset, requestedId = null) {
  const livery = selectLivery(asset, requestedId);
  if (!livery) return { ...asset, requires: requirementsFor(asset), liveryId: null, liveryName: null };
  const shared = Object.fromEntries(Object.entries(asset).filter(([key]) => !liveryFields.has(key)));
  return {
    ...shared,
    ...livery,
    id: asset.id,
    name: asset.name,
    category: asset.category,
    folder: livery.folder || asset.folder,
    description: livery.description ?? asset.description,
    engine: livery.engine ?? asset.engine,
    engineStatus: livery.engineStatus ?? asset.engineStatus,
    status: livery.status || 'coming-soon',
    notes: [...new Set([...(asset.notes || []), ...(livery.notes || [])])],
    requires: requirementsFor(asset, livery.id),
    liveryId: livery.id,
    liveryName: livery.name,
  };
}

export function assetStatus(asset) {
  return asset.liveries?.length
    ? (asset.liveries.some(livery => livery.status === 'available') ? 'available' : 'coming-soon')
    : asset.status;
}

export function countAssets(assets, { includeUnconfirmed = false } = {}) {
  const unique = new Map();
  for (const asset of assets) {
    if (!includeUnconfirmed && asset.countsTowardProgress === false) continue;
    if (!unique.has(asset.id)) unique.set(asset.id, asset);
  }
  const total = unique.size;
  const available = [...unique.values()].filter(asset => assetStatus(asset) === 'available').length;
  return { total, available, percentage: total ? available / total * 100 : 0 };
}

export function resolveDependencies(catalogue, asset, requestedId = null) {
  return requirementsFor(asset, requestedId).map(modFolder => {
    const key = modFolder.toLowerCase();
    const matches = [];
    for (const candidate of catalogue.assets) {
      if (candidate.modFolder?.trim().toLowerCase() === key) {
        matches.push({ modFolder, assetId: candidate.id, liveryId: null, name: candidate.name, status: assetStatus(candidate), matched: true });
      }
      for (const livery of candidate.liveries || []) {
        if (livery.modFolder?.trim().toLowerCase() !== key) continue;
        matches.push({ modFolder, assetId: candidate.id, liveryId: livery.id, name: `${candidate.name} — ${livery.name}`, status: livery.status, matched: true });
      }
    }
    return matches.find(match => match.status === 'available') || matches[0]
      || { modFolder, assetId: null, liveryId: null, name: modFolder, status: null, matched: false };
  });
}

function textValues(value) {
  if (Array.isArray(value)) return value.flatMap(textValues);
  if (value && typeof value === 'object') return Object.values(value).flatMap(textValues);
  return value == null ? [] : [String(value)];
}

export function filterAssets(catalogue, {
  group = catalogueGroups(catalogue)[0]?.id,
  category = 'all', status = 'all', faction = 'all', query = '', searchAllGroups = false,
} = {}) {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const globalSearch = terms.length > 0 && searchAllGroups;
  return catalogue.assets.filter(asset => {
    if (!globalSearch && groupForCategory(catalogue, asset.category) !== group) return false;
    if (!globalSearch && category !== 'all' && asset.category !== category) return false;
    if (status !== 'all' && assetStatus(asset) !== status) return false;
    if (faction !== 'all' && asset.faction !== faction) return false;
    if (!terms.length) return true;
    const type = catalogue.categories.find(item => item.id === asset.category);
    const groupName = catalogueGroups(catalogue).find(item => item.id === groupForCategory(catalogue, asset.category))?.name;
    const searchable = textValues([
      asset.id, asset.name, asset.description, asset.aliases, asset.faction,
      asset.classification, asset.shipClass, asset.carrierClass, asset.class,
      asset.type, asset.subtype, asset.role, asset.taxonomy, asset.scopeNote,
      type?.name, groupName, asset.liveries?.map(livery => livery.name),
    ]).join(' ').toLowerCase();
    return terms.every(term => searchable.includes(term));
  });
}

export function resolveLocation(catalogue, params = new URLSearchParams()) {
  const read = key => typeof params.get === 'function' ? params.get(key) : params[key];
  const asset = catalogue.assets.find(item => item.id === read('asset')) || null;
  const category = catalogue.categories.find(item => item.id === read('category'));
  const groups = catalogueGroups(catalogue);
  const requestedGroup = groups.find(item => item.id === read('group'))?.id;
  // A legacy ?category= URL remains valid; an asset URL always identifies its own group.
  const group = asset ? groupForCategory(catalogue, asset.category)
    : category ? groupForCategory(catalogue, category.id)
    : requestedGroup || groups[0]?.id;
  return {
    group,
    category: category && groupForCategory(catalogue, category.id) === group ? category.id : 'all',
    assetId: asset?.id || null,
    liveryId: asset ? selectLivery(asset, read('livery'))?.id || null : null,
  };
}
