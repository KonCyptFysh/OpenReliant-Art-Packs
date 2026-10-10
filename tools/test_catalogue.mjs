import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Load the browser ES module without adding a package manager or changing this
// buildless repository's module configuration.
const utilitySource = readFileSync(new URL('../docs/catalogue-utils.js', import.meta.url), 'utf8');
const utilities = await import(`data:text/javascript;base64,${Buffer.from(utilitySource).toString('base64')}`);
const {
  selectLivery, resolveAsset, assetStatus, countAssets, requirementsFor,
  resolveDependencies, filterAssets, resolveLocation,
} = utilities;

function ship() {
  return {
    id: 'example', name: 'Example', category: 'alliance-fighters', faction: 'alliance',
    folder: 'Alliance Fighters/Example', description: 'Shared hull description',
    notes: ['Shared installation note'], requires: ['base-art'],
    status: 'available', defaultLivery: 'worn-paint',
    liveries: [
      {
        id: 'worn-paint', name: 'Worn Paint', status: 'available',
        model: 'models/worn.glb', preview: 'assets/worn.webp',
        images: [{ src: 'assets/worn.webp', caption: 'Worn front' }, { src: 'assets/worn-rear.webp', caption: 'Worn rear' }],
        download: 'https://example.com/worn.zip', release: 'https://example.com/worn',
        checksum: 'a'.repeat(64), downloadBytes: 10, version: '1.0',
        modFolder: 'example-worn', notes: ['Worn-specific note'],
        engine: '0.8.1', requires: ['base-art', 'worn-support'],
      },
      {
        id: 'restored-paint', name: 'Restored Paint', status: 'available',
        model: 'models/restored.glb', preview: 'assets/restored.webp',
        images: [{ src: 'assets/restored.webp', caption: 'Restored overview' }],
        download: 'https://example.com/restored.zip', release: 'https://example.com/restored',
        checksum: 'b'.repeat(64), downloadBytes: 20, version: '2.0',
        modFolder: 'example-restored', notes: ['Restored-specific note'],
        engine: '0.9.0', requires: ['restored-support'],
      },
      { id: 'alternate', name: 'Alternate Livery', status: 'coming-soon' },
    ],
  };
}

function catalogue() {
  return {
    groups: [{ id: 'small-combat-craft', name: 'Fighters & Bombers' }, { id: 'fleet-warships', name: 'Fleet Warships' }],
    categories: [
      { id: 'alliance-fighters', name: 'Alliance Fighters', group: 'small-combat-craft' },
      { id: 'coalition-fighters', name: 'Coalition Fighters', group: 'small-combat-craft' },
      { id: 'cruisers', name: 'Cruisers', group: 'fleet-warships' },
    ],
    assets: [
      ship(),
      { id: 'saber', name: 'Saber', aliases: ['Sabre'], faction: 'coalition', category: 'coalition-fighters', status: 'coming-soon' },
      { id: 'kiev', name: 'CS Kiev', shipClass: 'Tornado-class Cruiser', faction: 'coalition', category: 'cruisers', status: 'coming-soon' },
      { id: 'kirov', name: 'CS Kirov', shipClass: 'Tornado-class Cruiser', faction: 'coalition', category: 'cruisers', status: 'coming-soon', countsTowardProgress: false, scopeStatus: 'pending-audit' },
    ],
  };
}

test('a hull counts once despite several liveries or a repeated input reference', () => {
  const data = catalogue();
  const counts = countAssets([...data.assets, data.assets[0]]);
  assert.equal(counts.total, 3);
  assert.equal(counts.available, 1);
  assert.ok(Math.abs(counts.percentage - 100 / 3) < 1e-9);
  assert.equal(countAssets(data.assets, { includeUnconfirmed: true }).total, 4);
});

test('an empty planned roster has finite zero progress', () => {
  assert.deepEqual(countAssets([]), { total: 0, available: 0, percentage: 0 });
});

test('availability follows released liveries, not the selected future paint', () => {
  const asset = ship();
  assert.equal(assetStatus(asset), 'available');
  assert.equal(resolveAsset(asset, 'alternate').status, 'coming-soon');
  asset.liveries.forEach(livery => { livery.status = 'coming-soon'; });
  assert.equal(assetStatus(asset), 'coming-soon');
});

test('an unknown livery deep link falls back to the configured default', () => {
  const asset = ship();
  asset.defaultLivery = 'restored-paint';
  assert.equal(selectLivery(asset, 'does-not-exist').id, 'restored-paint');
  assert.equal(selectLivery(asset, 'worn-paint').id, 'worn-paint');
});

test('selecting another livery changes model, photos, package and dependencies together', () => {
  const asset = ship();
  const resolved = resolveAsset(asset, 'restored-paint');
  assert.equal(resolved.id, 'example');
  assert.equal(resolved.name, 'Example');
  assert.equal(resolved.liveryName, 'Restored Paint');
  assert.equal(resolved.model, 'models/restored.glb');
  assert.equal(resolved.preview, 'assets/restored.webp');
  assert.deepEqual(resolved.images.map(image => image.caption), ['Restored overview']);
  assert.equal(resolved.download, 'https://example.com/restored.zip');
  assert.equal(resolved.checksum, 'b'.repeat(64));
  assert.equal(resolved.modFolder, 'example-restored');
  assert.equal(resolved.engine, '0.9.0');
  assert.deepEqual(resolved.requires, ['base-art', 'restored-support']);
  assert.deepEqual(resolved.notes, ['Shared installation note', 'Restored-specific note']);
  assert.equal(asset.liveries[0].model, 'models/worn.glb');
});

test('an unreleased livery cannot inherit another paint\'s media or download', () => {
  const asset = ship();
  // Even stale legacy presentation metadata is not a fallback for a new livery.
  Object.assign(asset, { model: 'legacy.glb', preview: 'legacy.png', images: [{ src: 'legacy.png' }],
    download: 'https://example.com/legacy.zip', previewArtworkRevision: 'legacy', version: 'old' });
  const resolved = resolveAsset(asset, 'alternate');
  for (const field of ['model', 'preview', 'images', 'download', 'version', 'previewArtworkRevision', 'checksum', 'modFolder']) {
    assert.equal(resolved[field], undefined, `${field} leaked into the planned livery`);
  }
  assert.equal(resolved.status, 'coming-soon');
  assert.deepEqual(resolved.notes, ['Shared installation note']);
});

test('a standalone HUD pack retains its own images and release data', () => {
  const hud = { id: 'hud', name: 'HUD', status: 'available', images: [{ src: 'hud.png', caption: 'HUD' }], download: 'hud.zip', notes: ['HUD note'] };
  const resolved = resolveAsset(hud, 'worn-paint');
  assert.deepEqual(resolved.images, hud.images);
  assert.equal(resolved.download, 'hud.zip');
  assert.deepEqual(resolved.notes, hud.notes);
  assert.equal(resolved.liveryId, null);
});

test('shared and livery-specific native requirements combine without case duplicates', () => {
  const asset = ship();
  asset.requires = ['Base-Art'];
  asset.liveries[0].requires = ['base-art', 'Worn-Support'];
  assert.deepEqual(requirementsFor(asset, 'worn-paint'), ['Base-Art', 'Worn-Support']);
});

test('requirements resolve by native folder name, independently of display name and case', () => {
  const data = catalogue();
  data.assets.push({ id: 'art-library', name: 'Friends and Foes', category: 'alliance-fighters', status: 'coming-soon', modFolder: 'friends-and-foes' });
  const consumer = { id: 'indicators', requires: ['FRIENDS-AND-FOES'] };
  assert.deepEqual(resolveDependencies(data, consumer), [{
    modFolder: 'FRIENDS-AND-FOES', assetId: 'art-library', liveryId: null,
    name: 'Friends and Foes', status: 'coming-soon', matched: true,
  }]);
});

test('an external requirement has no invented gallery link or availability claim', () => {
  const dependency = resolveDependencies(catalogue(), { id: 'consumer', requires: ['external-pack'] })[0];
  assert.equal(dependency.matched, false);
  assert.equal(dependency.assetId, null);
  assert.equal(dependency.status, null);
  assert.equal(dependency.name, 'external-pack');
});

test('a native folder shared by editions resolves to an available edition', () => {
  const data = catalogue();
  data.assets.push({
    id: 'paint-base', name: 'Base paint', category: 'alliance-fighters', status: 'available', defaultLivery: 'worn',
    liveries: [
      { id: 'future', name: 'Future', status: 'coming-soon', modFolder: 'common-base' },
      { id: 'worn', name: 'Worn Paint', status: 'available', modFolder: 'common-base' },
    ],
  });
  const dependency = resolveDependencies(data, { id: 'consumer', requires: ['COMMON-BASE'] })[0];
  assert.equal(dependency.status, 'available');
  assert.equal(dependency.liveryId, 'worn');
});

test('global search finds an alias outside the chosen group', () => {
  const matches = filterAssets(catalogue(), { group: 'fleet-warships', query: 'Sabre', searchAllGroups: true });
  assert.deepEqual(matches.map(asset => asset.id), ['saber']);
  assert.equal(filterAssets(catalogue(), { group: 'fleet-warships', query: 'Sabre' }).length, 0);
});

test('global search preserves faction and availability filters', () => {
  const data = catalogue();
  assert.equal(filterAssets(data, { query: 'Tornado', searchAllGroups: true, faction: 'alliance' }).length, 0);
  assert.equal(filterAssets(data, { query: 'Tornado', searchAllGroups: true, status: 'available' }).length, 0);
  assert.deepEqual(filterAssets(data, { query: 'Tornado cruiser', searchAllGroups: true }).map(asset => asset.id), ['kiev', 'kirov']);
});

test('type, faction and group filters select their stated scopes', () => {
  const matches = filterAssets(catalogue(), { group: 'small-combat-craft', category: 'coalition-fighters', faction: 'coalition' });
  assert.deepEqual(matches.map(asset => asset.id), ['saber']);
});

test('historic fighter category links select the right group and type', () => {
  const result = resolveLocation(catalogue(), new URLSearchParams('category=coalition-fighters'));
  assert.equal(result.group, 'small-combat-craft');
  assert.equal(result.category, 'coalition-fighters');
});

test('asset links override an unrelated group and retain the selected livery', () => {
  const result = resolveLocation(catalogue(), new URLSearchParams('group=fleet-warships&asset=example&livery=restored-paint'));
  assert.equal(result.group, 'small-combat-craft');
  assert.equal(result.assetId, 'example');
  assert.equal(result.liveryId, 'restored-paint');
});

test('invalid navigation parameters leave a usable default collection', () => {
  const result = resolveLocation(catalogue(), new URLSearchParams('group=missing&category=missing&asset=missing'));
  assert.equal(result.group, 'small-combat-craft');
  assert.equal(result.category, 'all');
  assert.equal(result.assetId, null);
});

test('real catalogue progress, preview resolution and planned dependency agree', () => {
  const data = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url), 'utf8'));
  const tracked = data.assets.filter(asset => asset.countsTowardProgress !== false);
  const counts = countAssets(data.assets);
  assert.equal(counts.total, tracked.length);
  assert.equal(counts.available, tracked.filter(asset => asset.status === 'available').length);
  for (const asset of data.assets) {
    assert.equal(assetStatus(asset), asset.status, asset.id);
    if (asset.liveries) assert.ok(selectLivery(asset), asset.id);
    const edition = resolveAsset(asset);
    if (asset.status === 'available') assert.ok(edition.download, asset.id);
  }
  const consumer = data.assets.find(asset => asset.id === 'vanilla-mission-damage-indicators');
  const [dependency] = resolveDependencies(data, consumer);
  assert.equal(dependency.assetId, 'friends-and-foes');
  assert.equal(dependency.modFolder, 'friends-and-foes');
  assert.equal(dependency.status, data.assets.find(asset => asset.id === 'friends-and-foes').status);
});

// Execute the real entry script against controls parsed from the shipped HTML.
// This is a DOM fixture for startup/selection, not a browser or layout test.
test('the shipped page starts and both hierarchy levels select the expected assets', async () => {
  const html = readFileSync(new URL('../docs/index.html', import.meta.url), 'utf8');
  const source = readFileSync(new URL('../docs/app.js', import.meta.url), 'utf8');
  const data = JSON.parse(readFileSync(new URL('../docs/catalog.json', import.meta.url), 'utf8'));
  const events = new Map();
  let focused;
  const attributes = text => Object.fromEntries([...text.matchAll(/([\w-]+)="([^"]*)"/g)].map(match => [match[1], match[2]]));
  function element(tag, attrs) {
    return {
      attrs, innerHTML: '', textContent: '', scrollTop: 0,
      value: tag === 'select' ? 'all' : '', checked: false,
      dataset: Object.fromEntries(Object.entries(attrs).filter(([name]) => name.startsWith('data-')).map(([name, value]) => [name.slice(5), value])),
      addEventListener() {}, setAttribute(name, value) { this.attrs[name] = String(value); },
      focus() { focused = this; },
      closest(selector) { return selector === '#group-nav button[data-group]' && this.dataset.group ? this : null; },
      querySelectorAll(selector) {
        assert.equal(selector, 'button');
        return [...this.innerHTML.matchAll(/<button\b([^>]*)>/g)].map(match => element('button', attributes(match[1])));
      },
    };
  }
  const nodes = [...html.matchAll(/<(\w+)\b([^>]*)>/g)].map(match => element(match[1], attributes(match[2])));
  const document = {
    querySelector(selector) {
      if (selector.startsWith('#')) return nodes.find(node => node.attrs.id === selector.slice(1)) || null;
      if (selector.startsWith('.')) return nodes.find(node => (node.attrs.class || '').split(/\s+/).includes(selector.slice(1))) || null;
      throw new Error('Unhandled fixture selector: ' + selector);
    },
    addEventListener(type, handler) { events.set(type, handler); },
  };
  const location = new URL('https://example.test/?group=small-combat-craft');
  const history = { replaceState(_state, _title, url) { location.href = url; } };
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  const entry = new AsyncFunction('document', 'matchMedia', 'fetch', 'location', 'history', 'utilities',
    source.replace(/import\s*\{([\s\S]*?)\}\s*from\s*['"][^'"]+['"];?/, 'const {$1} = utilities;'));
  await entry(document, () => ({ matches: false }), async () => ({ ok: true, json: async () => data }), location, history, utilities);
  const node = id => document.querySelector('#' + id);
  const counts = countAssets(data.assets);
  assert.equal(node('progress-heading').textContent, counts.available + ' of ' + counts.total + ' assets available');
  assert.equal(node('group-nav').querySelectorAll('button').length, data.groups.length + data.categories.length);
  assert.ok(node('asset-grid').innerHTML.includes('class="asset-card"'));

  for (const categoryId of ['torpedo-bombers', null]) {
    const button = node('group-nav').querySelectorAll('button').find(button => button.dataset.group === 'small-combat-craft' && (button.dataset.category || null) === categoryId);
    assert.ok(button);
    events.get('click')({ target: button });
    const expected = filterAssets(data, { group: 'small-combat-craft', category: categoryId || 'all' });
    assert.equal((node('asset-grid').innerHTML.match(/class="asset-card"/g) || []).length, expected.length);
    assert.equal(location.searchParams.get('category'), categoryId);
    assert.equal(focused.dataset.category || null, categoryId);
    const selected = node('group-nav').querySelectorAll('button').filter(button => button.attrs['aria-pressed'] === 'true');
    assert.equal(selected.length, 1);
    assert.equal(selected[0].dataset.category || null, categoryId);
  }
});
