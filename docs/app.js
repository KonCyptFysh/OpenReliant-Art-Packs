import {
  catalogueGroups, groupForCategory, selectLivery, resolveAsset, assetStatus,
  countAssets, requirementsFor, resolveDependencies, filterAssets, resolveLocation,
} from './catalogue-utils.js';

const $ = selector => document.querySelector(selector);
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
const formatSize = bytes => Number.isFinite(bytes) ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : 'ZIP';
const previewSource = (asset, photo = null) => photo?.sourceLabel || asset.previewSource || (asset.previewType === 'render' ? 'Blender material preview' : 'In-game capture');
const previewLabel = asset => asset.previewType === 'mixed' ? 'Image gallery' : asset.previewType === 'render' ? 'Render gallery' : 'Photo gallery';
const previewSummary = asset => asset.milestone === 'long-term' ? 'Long-term milestone' : asset.workStatus === 'planned' ? 'Planned' : asset.previewType === 'mixed' ? 'Artwork + in-game gallery' : asset.previewType === 'render' ? (asset.model ? '3D + rendered previews' : 'Rendered previews') : asset.model ? '3D + in-game preview' : asset.images?.length > 1 ? `${asset.images.length} in-game photos` : asset.preview ? 'In-game preview' : 'Work in progress';
const displayName = asset => asset.liveryName ? `${asset.name} — ${asset.liveryName}` : asset.name;
const statusLabel = status => status === 'available' ? 'Beta available' : 'Coming soon';
const dialog = $('#asset-dialog');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let catalogue, selectedGroup, selectedCategory = 'all', currentAsset, currentLiveryId;
let previewSequence = 0, viewerImport, galleryIndex = 0, previewKind;

function currentSelection() {
  return currentAsset ? resolveAsset(currentAsset, currentLiveryId) : null;
}

function assetURL(asset, liveryId = null) {
  const url = new URL(location.href);
  url.search = '';
  url.searchParams.set('group', groupForCategory(catalogue, asset.category));
  url.searchParams.set('category', asset.category);
  url.searchParams.set('asset', asset.id);
  if (liveryId) url.searchParams.set('livery', liveryId);
  url.hash = '';
  return url.href;
}

function updateURL() {
  if (!catalogue || !selectedGroup) return;
  const url = new URL(location.href);
  url.searchParams.set('group', selectedGroup);
  if (selectedCategory !== 'all') url.searchParams.set('category', selectedCategory);
  else url.searchParams.delete('category');
  const query = $('#search').value.trim();
  if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
  if (query && !$('#search-all-groups').checked) url.searchParams.set('scope', 'group');
  else url.searchParams.delete('scope');
  for (const [key, selector] of [['status', '#status-filter'], ['faction', '#faction-filter']]) {
    if ($(selector).value !== 'all') url.searchParams.set(key, $(selector).value);
    else url.searchParams.delete(key);
  }
  if (currentAsset) url.searchParams.set('asset', currentAsset.id); else url.searchParams.delete('asset');
  if (currentLiveryId) url.searchParams.set('livery', currentLiveryId); else url.searchParams.delete('livery');
  history.replaceState(null, '', url);
}

function renderProgress() {
  const counts = countAssets(catalogue.assets);
  $('#available-count').textContent = String(counts.available).padStart(2, '0');
  $('#collection-count').textContent = String(catalogueGroups(catalogue).length).padStart(2, '0');
  $('#engine-version').textContent = catalogue.engine;
  $('#progress-heading').textContent = `${counts.available} of ${counts.total} assets available`;
  $('#progress-percentage').textContent = `${Number(counts.percentage.toFixed(1))}%`;
  const progress = $('#collection-progress');
  progress.max = counts.total || 1;
  progress.value = counts.available;
  progress.textContent = `${counts.available} of ${counts.total}`;
  progress.setAttribute('aria-valuetext', `${counts.available} of ${counts.total} tracked assets and packs available`);
  if (catalogue.progress?.description) $('#progress-description').textContent = catalogue.progress.description;
  if (catalogue.progress?.scopeDescription) $('#progress-scope').textContent = catalogue.progress.scopeDescription;
}

function renderNavigation() {
  const nav = $('#group-nav');
  const scrollTop = nav.scrollTop;
  nav.innerHTML = '<ul class="catalogue-tree">' + catalogueGroups(catalogue).map(group => {
    const counts = countAssets(catalogue.assets.filter(asset => groupForCategory(catalogue, asset.category) === group.id), { includeUnconfirmed: true });
    const categories = catalogue.categories.filter(category => groupForCategory(catalogue, category.id) === group.id);
    const children = categories.map(category => {
      const categoryCounts = countAssets(catalogue.assets.filter(asset => asset.category === category.id), { includeUnconfirmed: true });
      return `<li><button type="button" class="category-button subcategory-button" data-group="${escapeHTML(group.id)}" data-category="${escapeHTML(category.id)}" aria-pressed="${group.id === selectedGroup && category.id === selectedCategory}" aria-label="${escapeHTML(category.name)}, ${categoryCounts.available} available of ${categoryCounts.total} listed"><span>${escapeHTML(category.name)}</span><small aria-hidden="true">${categoryCounts.available}/${categoryCounts.total}</small></button></li>`;
    }).join('');
    return `<li class="catalogue-group${group.id === selectedGroup ? ' current-group' : ''}"><button type="button" id="nav-${escapeHTML(group.id)}" class="category-button group-button" data-group="${escapeHTML(group.id)}" aria-pressed="${group.id === selectedGroup && selectedCategory === 'all'}" aria-label="All ${escapeHTML(group.name)}, ${counts.available} available of ${counts.total} listed"><span>${escapeHTML(group.name)}</span><small aria-hidden="true">${counts.available}/${counts.total}</small></button><ul class="subcategory-list" aria-labelledby="nav-${escapeHTML(group.id)}">${children}</ul></li>`;
  }).join('') + '</ul>';
  nav.scrollTop = scrollTop;
}

function render() {
  if (!catalogue) return;
  const query = $('#search').value.trim();
  const globalSearch = Boolean(query && $('#search-all-groups').checked);
  const group = catalogueGroups(catalogue).find(item => item.id === selectedGroup);
  const category = catalogue.categories.find(item => item.id === selectedCategory);
  const assets = filterAssets(catalogue, {
    group: selectedGroup, category: selectedCategory, query,
    status: $('#status-filter').value, faction: $('#faction-filter').value,
    searchAllGroups: $('#search-all-groups').checked,
  });
  $('#search-scope').hidden = !query;
  $('#search-help').textContent = globalSearch ? 'Searching all groups; category filtering resumes when you clear the search.' : 'Search by name, alias or ship class.';
  $('#clear-search').hidden = !query;
  $('#category-heading').textContent = globalSearch ? 'Search across the collection' : category?.name || group?.name || 'Collection';
  $('#group-description').textContent = globalSearch ? 'Matches from every group. Availability and faction filters still apply.' : category?.description || group?.description || '';
  $('#result-count').textContent = `${assets.length} ${assets.length === 1 ? 'entry' : 'entries'}`;
  const emptyCategory = !query && $('#status-filter').value === 'all' && $('#faction-filter').value === 'all'
    && !catalogue.assets.some(asset => groupForCategory(catalogue, asset.category) === selectedGroup && (selectedCategory === 'all' || asset.category === selectedCategory));
  $('#asset-grid').innerHTML = assets.length ? assets.map(asset => {
    const selected = resolveAsset(asset);
    const type = catalogue.categories.find(item => item.id === asset.category);
    const dependencyCount = requirementsFor(asset).length;
    const pending = asset.scopeStatus === 'pending-audit';
    return `<button type="button" class="asset-card" data-asset="${escapeHTML(asset.id)}" aria-label="Preview ${escapeHTML(asset.name)}"><div class="card-media">${selected.preview ? `<img src="${escapeHTML(selected.preview)}" loading="lazy" width="960" height="720" alt="${escapeHTML(`${selected.images?.[0]?.caption || displayName(selected)} — ${previewSource(selected)}`)}">` : `<div class="placeholder-art"><span class="placeholder-icon" aria-hidden="true">◇</span><span>${pending ? 'ARTWORK SCOPE PENDING' : selected.workStatus === 'planned' ? 'PLANNED ARTWORK' : 'ARTWORK IN PROGRESS'}</span></div>`}<span class="card-badge ${assetStatus(asset) === 'available' ? 'available' : ''}">${statusLabel(assetStatus(asset))}</span></div><div class="card-body"><span class="card-kicker">${escapeHTML(type?.name || '')}</span><h4>${escapeHTML(asset.name)}</h4>${selected.liveryName ? `<span class="card-livery">${escapeHTML(selected.liveryName)}</span>` : ''}<p>${escapeHTML(asset.description)}</p>${dependencyCount ? `<span class="dependency-badge">Requires ${dependencyCount} ${dependencyCount === 1 ? 'pack' : 'packs'}</span>` : ''}${pending ? '<span class="scope-badge">Artwork scope pending</span>' : ''}<div class="card-foot"><span>${previewSummary(selected)}</span><span aria-hidden="true">↗</span></div></div></button>`;
  }).join('') : emptyCategory ? `<div class="category-placeholder"><span class="placeholder-icon" aria-hidden="true">◇</span><h4>Coming soon</h4><p>${escapeHTML(category?.description || group?.description || 'New artwork is planned for this collection.')}<br>Individual entries will appear here as their scope is confirmed.</p></div>` : '<div class="empty-state"><h4>No matching entries</h4><p>Try another type, faction or availability filter, or search across all groups.</p><button type="button" class="text-button" id="reset-filters">Clear filters</button></div>';
}

function closePreview() {
  previewSequence++;
  $('#preview-stage').replaceChildren();
  currentAsset = null;
  currentLiveryId = null;
  if (dialog.open) dialog.close();
  updateURL();
}

function galleryImages(asset) {
  return asset.images?.length ? asset.images : asset.preview ? [{ src: asset.preview, caption: displayName(asset) }] : [];
}

function stepGallery(direction) {
  const photos = galleryImages(currentSelection() || {});
  if (previewKind !== 'image' || photos.length < 2) return;
  galleryIndex = (galleryIndex + direction + photos.length) % photos.length;
  showPreview('image');
}

async function showPreview(requestedKind) {
  const asset = currentSelection();
  if (!asset) return;
  const photos = galleryImages(asset);
  const kind = requestedKind === 'model' && asset.model ? 'model' : photos.length ? 'image' : asset.model ? 'model' : 'image';
  const sequence = ++previewSequence;
  previewKind = kind;
  $('.detail-media').classList.toggle('photo-gallery', kind === 'image' && photos.length > 1);
  $('#gallery-controls').hidden = true;
  $('#show-3d').setAttribute('aria-pressed', kind === 'model');
  $('#show-image').setAttribute('aria-pressed', kind === 'image');
  $('#rotate-toggle').hidden = true;
  const stage = $('#preview-stage');
  stage.replaceChildren();
  const modelFailure = () => {
    if (sequence !== previewSequence) return;
    if (photos.length) {
      showPreview('image');
      $('#preview-hint').textContent = '3D is unavailable here. Showing this selection’s image preview.';
    } else {
      stage.innerHTML = '<div class="placeholder-art"><span class="placeholder-icon" aria-hidden="true">◇</span><span>3D PREVIEW UNAVAILABLE</span></div>';
      $('#preview-hint').textContent = 'The 3D preview could not load. Please try again later.';
    }
  };
  if (kind === 'model' && asset.model) {
    $('#preview-hint').textContent = 'Loading 3D preview…';
    if (asset.preview) {
      const poster = document.createElement('img');
      poster.src = asset.preview;
      poster.alt = `${displayName(asset)} — ${previewSource(asset)}`;
      stage.append(poster);
    }
    try {
      viewerImport ??= import('./vendor/model-viewer-4.3.1.min.js');
      await viewerImport;
      await customElements.whenDefined('model-viewer');
      if (sequence !== previewSequence) return;
      const viewer = document.createElement('model-viewer');
      viewer.setAttribute('src', asset.model);
      viewer.setAttribute('alt', `Interactive 3D preview of ${displayName(asset)}. Drag to rotate, scroll or pinch to zoom.`);
      viewer.setAttribute('camera-controls', '');
      viewer.setAttribute('touch-action', 'pan-y');
      viewer.setAttribute('shadow-intensity', '1');
      viewer.setAttribute('environment-image', 'neutral');
      viewer.setAttribute('exposure', '1.1');
      viewer.setAttribute('camera-orbit', '35deg 65deg auto');
      viewer.setAttribute('loading', 'eager');
      if (!reducedMotion) viewer.setAttribute('auto-rotate', '');
      viewer.addEventListener('load', () => {
        if (sequence !== previewSequence) return;
        $('#preview-hint').textContent = 'Drag to rotate · Scroll or pinch to zoom';
        $('#rotate-toggle').hidden = false;
        $('#rotate-toggle').textContent = viewer.hasAttribute('auto-rotate') ? 'Pause rotation' : 'Rotate model';
      });
      viewer.addEventListener('error', modelFailure);
      stage.replaceChildren(viewer);
    } catch {
      modelFailure();
    }
  } else if (photos.length) {
    galleryIndex = Math.min(galleryIndex, photos.length - 1);
    const photo = photos[galleryIndex];
    const image = document.createElement('img');
    image.src = photo.src;
    image.alt = `${photo.caption || displayName(asset)} — ${previewSource(asset, photo)}`;
    image.addEventListener('error', () => {
      if (sequence !== previewSequence) return;
      image.remove();
      $('#preview-hint').textContent = 'This image could not load. Try another preview or reload the page.';
    }, { once: true });
    stage.append(image);
    $('#gallery-controls').hidden = photos.length < 2;
    $('#gallery-caption').textContent = photo.caption || displayName(asset);
    $('#gallery-count').textContent = `${galleryIndex + 1} / ${photos.length}`;
    $('#preview-hint').textContent = previewSource(asset, photo);
  } else {
    stage.innerHTML = '<div class="placeholder-art"><span class="placeholder-icon" aria-hidden="true">◇</span><span>COMING SOON</span></div>';
    $('#preview-hint').textContent = asset.workStatus === 'planned' ? 'Planned artwork; no preview yet.' : 'No preview has been published for this selection yet.';
  }
}

function dependencyPanel() {
  const dependencies = resolveDependencies(catalogue, currentAsset, currentLiveryId);
  if (!dependencies.length) return '';
  return `<section class="dependency-panel" aria-labelledby="required-packs-heading"><h3 id="required-packs-heading">Required packs</h3><p>Install, enable and load each required pack before this pack in OpenReliant. The loader skips packs whose requirements are not met.</p><ul>${dependencies.map(dependency => {
    const target = dependency.matched && catalogue.assets.find(item => item.id === dependency.assetId);
    return `<li>${target ? `<a class="dependency-link" href="${escapeHTML(assetURL(target, dependency.liveryId))}" data-asset="${escapeHTML(target.id)}"${dependency.liveryId ? ` data-livery="${escapeHTML(dependency.liveryId)}"` : ''}>${escapeHTML(dependency.name)} <span aria-hidden="true">↗</span></a><span class="dependency-status">${statusLabel(dependency.status)}</span>` : `<strong>${escapeHTML(dependency.name)}</strong><span class="dependency-status">External pack</span>`}<code>${escapeHTML(dependency.modFolder)}</code>${target ? '' : '<p>Obtain this mod from its publisher, then enable and load it before this pack.</p>'}</li>`;
  }).join('')}</ul><p class="dependency-note">Availability above describes published downloads. This page cannot check which mods are installed on your computer.</p></section>`;
}

function renderDetails() {
  const asset = currentSelection();
  if (!asset) return;
  const category = catalogue.categories.find(item => item.id === asset.category);
  const available = asset.status === 'available';
  const downloadable = available && Boolean(asset.download);
  const photos = galleryImages(asset);
  const secondaryLinks = [];
  if (downloadable && asset.release) secondaryLinks.push(`<a href="${escapeHTML(asset.release)}">Release notes</a>`);
  if (downloadable && asset.checksum) secondaryLinks.push(`<a href="${escapeHTML(asset.checksumUrl || `${asset.download}.sha256`)}">Checksum</a>`);
  if (downloadable && asset.folder) secondaryLinks.push(`<a href="${escapeHTML(`${catalogue.repository}/tree/main/${asset.folder.split('/').map(encodeURIComponent).join('/')}/source`)}">Editable source</a>`);
  const liveryPicker = currentAsset.liveries?.length ? `<div class="livery-picker"><label for="livery-select">Livery</label><select id="livery-select" aria-controls="preview-stage asset-release-details">${currentAsset.liveries.map(livery => `<option value="${escapeHTML(livery.id)}"${livery.id === currentLiveryId ? ' selected' : ''}>${escapeHTML(livery.name)}${livery.status === 'available' ? '' : ' — Coming soon'}</option>`).join('')}</select></div>` : '';
  const compatibility = asset.engineStatus === 'to-be-confirmed' ? 'To be confirmed' : asset.engine || catalogue.engine;
  $('#asset-details').innerHTML = `<p class="eyebrow">${escapeHTML(category?.name || '')}</p><h2 id="asset-title">${escapeHTML(asset.name)}</h2>${liveryPicker}<p class="asset-description">${escapeHTML(asset.description)}</p>${asset.scopeStatus === 'pending-audit' ? '<p class="scope-note">Artwork scope pending: this named vessel is listed for reference while its shared model and texture requirements are confirmed.</p>' : ''}<div id="asset-release-details"><dl class="detail-facts"><div><dt>Status</dt><dd>${available ? 'Public beta' : 'Coming soon'}</dd></div><div><dt>OpenReliant</dt><dd>${escapeHTML(compatibility)}</dd></div>${asset.milestone === 'long-term' ? '<div><dt>Milestone</dt><dd>Long term</dd></div>' : ''}${asset.shipClass ? `<div class="ship-class-fact"><dt>Ship class</dt><dd>${escapeHTML(asset.shipClass)}</dd></div>` : ''}${asset.assetRevision ? `<div><dt>Artwork revision</dt><dd>${escapeHTML(asset.assetRevision)}</dd></div>` : ''}${asset.version ? `<div><dt>Pack version</dt><dd>${escapeHTML(asset.version)}</dd></div>` : ''}${downloadable ? `<div><dt>Download</dt><dd>${formatSize(asset.downloadBytes)}${Number.isFinite(asset.downloadBytes) ? ' · ZIP' : ''}</dd></div>` : ''}${asset.modFolder ? `<div class="mod-folder-fact"><dt>Mod folder</dt><dd><code>${escapeHTML(asset.modFolder)}</code></dd></div>` : ''}</dl>${asset.notes?.length ? `<div class="detail-notes"><h3>${available ? 'Still on the workbench' : 'Planned work'}</h3><ul>${asset.notes.map(note => `<li>${escapeHTML(note)}</li>`).join('')}</ul></div>` : ''}${dependencyPanel()}${downloadable ? `<a class="button primary" href="${escapeHTML(asset.download)}">Download ${escapeHTML(displayName(asset))} <span aria-hidden="true">↓</span></a>${secondaryLinks.length ? `<div class="secondary-links">${secondaryLinks.join('')}</div>` : ''}` : '<button class="button coming-button" disabled>Coming soon</button>'}<p class="detail-warning">${asset.model ? 'The 3D hull preview uses reduced textures and browser lighting; loadout weapons and engine effects are omitted. ' : ''}${asset.previewType === 'mixed' ? 'The cover is a composition of the mod artwork; the other images are engine captures. ' : asset.previewType === 'render' ? 'The still images are Blender material previews; lighting differs in game. ' : asset.model ? 'Check the in-game capture for the current engine appearance. ' : ''}${available ? escapeHTML(asset.validationSummary || 'Beta testing covers format checks and bounded rendering on Linux; broader gameplay and other platforms are still to be tested.') : 'This selection has no published download yet.'}</p></div>`;
  $('#show-3d').hidden = !asset.model;
  $('#show-image').hidden = !photos.length;
  $('#show-image').textContent = photos.length > 1 ? previewLabel(asset) : asset.previewType === 'render' ? 'Rendered preview' : 'In-game capture';
}

function openAsset(id, liveryId = null) {
  if (!catalogue) return;
  const asset = catalogue.assets.find(item => item.id === id);
  if (!asset) return;
  const group = groupForCategory(catalogue, asset.category);
  if (selectedGroup !== group || (selectedCategory !== 'all' && selectedCategory !== asset.category)) {
    selectedGroup = group;
    selectedCategory = asset.category;
    renderNavigation();
    render();
  }
  currentAsset = asset;
  currentLiveryId = selectLivery(asset, liveryId)?.id || null;
  galleryIndex = 0;
  previewSequence++;
  renderDetails();
  if (!dialog.open) dialog.showModal();
  else $('.close-dialog').focus({ preventScroll: true });
  dialog.scrollTop = 0;
  updateURL();
  const selected = currentSelection();
  showPreview(selected.defaultPreview === 'image' ? 'image' : selected.model ? 'model' : 'image');
}

function changeLivery(id) {
  if (!currentAsset) return;
  const previousKind = previewKind;
  currentLiveryId = selectLivery(currentAsset, id)?.id || null;
  galleryIndex = 0;
  previewSequence++;
  renderDetails();
  updateURL();
  showPreview(previousKind);
  // Rendering the release fields replaces the control; retain the keyboard user's place.
  $('#livery-select')?.focus({ preventScroll: true });
}

function refreshFilters() {
  render();
  updateURL();
}

document.addEventListener('click', event => {
  const group = event.target.closest('#group-nav button[data-group]');
  if (group) {
    selectedGroup = group.dataset.group;
    selectedCategory = group.dataset.category || 'all';
    $('#search').value = '';
    renderNavigation();
    refreshFilters();
    // Navigation is rerendered to update selection; preserve keyboard focus.
    [...$('#group-nav').querySelectorAll('button')].find(button => button.dataset.group === selectedGroup && (button.dataset.category || 'all') === selectedCategory)?.focus({ preventScroll: true });
  }
  const asset = event.target.closest('[data-asset]');
  if (asset && !(event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)) {
    event.preventDefault();
    openAsset(asset.dataset.asset, asset.dataset.livery || null);
  }
  if (event.target.closest('#reset-filters')) {
    $('#search').value = '';
    $('#status-filter').value = 'all';
    $('#faction-filter').value = 'all';
    selectedCategory = 'all';
    renderNavigation();
    refreshFilters();
    $('#search').focus();
  }
});
$('#search').addEventListener('input', refreshFilters);
$('#clear-search').addEventListener('click', () => { $('#search').value = ''; refreshFilters(); $('#search').focus(); });
$('#search-all-groups').addEventListener('change', refreshFilters);
$('#status-filter').addEventListener('change', refreshFilters);
$('#faction-filter').addEventListener('change', refreshFilters);
$('#asset-details').addEventListener('change', event => { if (event.target.id === 'livery-select') changeLivery(event.target.value); });
$('.close-dialog').addEventListener('click', closePreview);
dialog.addEventListener('cancel', event => { event.preventDefault(); closePreview(); });
dialog.addEventListener('click', event => { if (event.target === dialog) closePreview(); });
$('#show-3d').addEventListener('click', () => showPreview('model'));
$('#show-image').addEventListener('click', () => showPreview('image'));
$('#gallery-previous').addEventListener('click', () => stepGallery(-1));
$('#gallery-next').addEventListener('click', () => stepGallery(1));
dialog.addEventListener('keydown', event => {
  if (previewKind !== 'image' || galleryImages(currentSelection() || {}).length < 2 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest('input, textarea, select, [contenteditable]')) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    stepGallery(event.key === 'ArrowLeft' ? -1 : 1);
  }
});
$('#rotate-toggle').addEventListener('click', () => {
  const viewer = $('model-viewer');
  if (!viewer) return;
  viewer.toggleAttribute('auto-rotate');
  $('#rotate-toggle').textContent = viewer.hasAttribute('auto-rotate') ? 'Pause rotation' : 'Rotate model';
});

try {
  const response = await fetch('catalog.json', { cache: 'no-cache' });
  if (!response.ok) throw new Error('Catalogue unavailable');
  catalogue = await response.json();
  const params = new URLSearchParams(location.search);
  const initial = resolveLocation(catalogue, params);
  selectedGroup = initial.group;
  selectedCategory = initial.category;
  const factions = [...new Set(catalogue.assets.map(asset => asset.faction).filter(Boolean))].sort();
  const factionNames = { alliance: 'Alliance', coalition: 'Coalition', shared: 'Shared / both factions', neutral: 'Neutral' };
  $('#faction-filter').innerHTML = '<option value="all">All factions</option>' + factions.map(faction => `<option value="${escapeHTML(faction)}">${escapeHTML(factionNames[faction] || faction)}</option>`).join('');
  $('#search').value = params.get('q') || '';
  $('#search-all-groups').checked = params.get('scope') !== 'group';
  if (['available', 'coming-soon'].includes(params.get('status'))) $('#status-filter').value = params.get('status');
  if (factions.includes(params.get('faction'))) $('#faction-filter').value = params.get('faction');
  renderProgress();
  renderNavigation();
  render();
  if (initial.assetId) openAsset(initial.assetId, initial.liveryId);
} catch {
  $('#asset-grid').innerHTML = '<div class="empty-state"><h4>The collection could not load.</h4><p>Please reload, or <a href="https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases">browse the downloads on GitHub</a>.</p></div>';
}
