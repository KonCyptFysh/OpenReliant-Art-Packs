const $ = (selector) => document.querySelector(selector);
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const formatSize = bytes => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
const previewSource = (asset, photo = null) => photo?.sourceLabel || asset.previewSource || (asset.previewType === 'render' ? 'Blender material preview' : `Captured in OpenReliant ${asset.engine || '0.7.0'}`);
const previewLabel = asset => asset.previewType === 'mixed' ? 'Image gallery' : asset.previewType === 'render' ? 'Render gallery' : 'Photo gallery';
const previewSummary = asset => asset.workStatus === 'planned' ? 'Planned' : asset.previewType === 'mixed' ? 'Artwork + in-game gallery' : asset.previewType === 'render' ? (asset.model ? '3D + rendered previews' : 'Rendered previews') : asset.model ? '3D + in-game preview' : asset.images?.length > 1 ? `${asset.images.length} in-game photos` : asset.preview ? 'In-game preview' : 'Work in progress';
const dialog = $('#asset-dialog');
let catalogue, selectedCategory, currentAsset, previewSequence = 0, viewerImport, galleryIndex = 0, previewKind;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
function updateURL(asset = null) {
  const url = new URL(location.href);
  url.searchParams.set('category', selectedCategory);
  if (asset) url.searchParams.set('asset', asset.id); else url.searchParams.delete('asset');
  history.replaceState(null, '', url);
}
function render() {
  if (!catalogue) return;
  const query = $('#search').value.toLowerCase().trim();
  const status = $('#status-filter').value;
  const category = catalogue.categories.find(c => c.id === selectedCategory);
  $('#category-nav').innerHTML = catalogue.categories.map(c => `<button type="button" class="category-button" data-category="${c.id}" aria-pressed="${c.id === selectedCategory}"><span>${escapeHTML(c.name)}</span><small>${String(catalogue.assets.filter(a => a.category === c.id).length).padStart(2,'0')}</small></button>`).join('');
  const assets = catalogue.assets.filter(a => a.category === selectedCategory && (status === 'all' || a.status === status) && `${a.name} ${a.description}`.toLowerCase().includes(query));
  $('#category-heading').textContent = category.name;
  $('#result-count').textContent = `${assets.length} ${assets.length === 1 ? 'asset' : 'assets'}`;
  $('#asset-grid').innerHTML = assets.length ? assets.map(a => `<button type="button" class="asset-card" data-asset="${a.id}" aria-label="Preview ${escapeHTML(a.name)}"><div class="card-media">${a.preview ? `<img src="${a.preview}" loading="lazy" width="960" height="720" alt="${escapeHTML(a.images?.[0]?.caption || a.name)} — ${previewSource(a)}">` : `<div class="placeholder-art"><span class="placeholder-icon" aria-hidden="true">◇</span><span>${a.workStatus === 'planned' ? 'PLANNED ARTWORK' : 'ARTWORK IN PROGRESS'}</span></div>`}<span class="card-badge ${a.status === 'available' ? 'available' : ''}">${a.status === 'available' ? 'Beta available' : 'Coming soon'}</span></div><div class="card-body"><span class="card-kicker">${escapeHTML(category.name)}</span><h4>${escapeHTML(a.name)}</h4><p>${escapeHTML(a.description)}</p><div class="card-foot"><span>${previewSummary(a)}</span><span aria-hidden="true">↗</span></div></div></button>`).join('') : (!query && status !== 'available' && !catalogue.assets.some(a => a.category === selectedCategory)) ? `<div class="category-placeholder"><span class="placeholder-icon" aria-hidden="true">◇</span><p class="eyebrow">${escapeHTML(category.name)}</p><h4>Coming soon</h4><p>${escapeHTML(category.description)}<br>New packs will appear here when they’re ready.</p></div>` : '<div class="empty-state"><h4>No matching packs</h4><p>Try another search or availability filter.</p></div>';
}
function closePreview() {
  previewSequence++;
  $('#preview-stage').replaceChildren();
  currentAsset = null;
  if (dialog.open) dialog.close();
  updateURL();
}
function galleryImages(asset) {
  return asset.images?.length ? asset.images : asset.preview ? [{ src: asset.preview, caption: asset.name }] : [];
}
function stepGallery(direction) {
  const photos = galleryImages(currentAsset || {});
  if (previewKind !== 'image' || photos.length < 2) return;
  galleryIndex = (galleryIndex + direction + photos.length) % photos.length;
  showPreview('image');
}
async function showPreview(kind) {
  const asset = currentAsset;
  if (!asset) return;
  const sequence = ++previewSequence;
  previewKind = kind;
  $('.detail-media').classList.toggle('photo-gallery', kind === 'image' && galleryImages(asset).length > 1);
  $('#gallery-controls').hidden = true;
  $('#show-3d').classList.toggle('active', kind === 'model');
  $('#show-image').classList.toggle('active', kind === 'image');
  $('#show-3d').setAttribute('aria-pressed', kind === 'model');
  $('#show-image').setAttribute('aria-pressed', kind === 'image');
  $('#rotate-toggle').hidden = true;
  const stage = $('#preview-stage');
  stage.replaceChildren();
  if (kind === 'model' && asset.model) {
    $('#preview-hint').textContent = 'Loading 3D preview…';
    if (asset.preview) {
      const poster = document.createElement('img'); poster.src = asset.preview; poster.alt = `${asset.name} — ${previewSource(asset)}`; stage.append(poster);
    }
    try {
      viewerImport ??= import('./vendor/model-viewer-4.3.1.min.js');
      await viewerImport;
      await customElements.whenDefined('model-viewer');
      if (sequence !== previewSequence) return;
      const viewer = document.createElement('model-viewer');
      viewer.setAttribute('src', asset.model);
      viewer.setAttribute('alt', `Interactive 3D preview of ${asset.name}. Drag to rotate, scroll or pinch to zoom.`);
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
      viewer.addEventListener('error', () => {
        if (sequence === previewSequence) {
          showPreview('image');
          $('#preview-hint').textContent = `3D is unavailable here. Showing ${asset.previewType === 'render' ? 'the rendered preview' : 'the in-game capture'}.`;
        }
      });
      stage.replaceChildren(viewer);
    } catch {
      if (sequence === previewSequence) { showPreview('image'); $('#preview-hint').textContent = `3D is unavailable here. Showing ${asset.previewType === 'render' ? 'the rendered preview' : 'the in-game capture'}.`; }
    }
  } else if (galleryImages(asset).length) {
    const photos = galleryImages(asset);
    const photo = photos[galleryIndex];
    const image = document.createElement('img');
    image.src = photo.src;
    image.alt = `${photo.caption} — ${previewSource(asset, photo)}`;
    stage.append(image);
    $('#gallery-controls').hidden = photos.length < 2;
    $('#gallery-caption').textContent = photo.caption;
    $('#gallery-count').textContent = `${galleryIndex + 1} / ${photos.length}`;
    $('#preview-hint').textContent = previewSource(asset, photo);
  } else {
    stage.innerHTML = '<div class="placeholder-art"><span class="placeholder-icon" aria-hidden="true">◇</span><span>COMING SOON</span></div>';
    $('#preview-hint').textContent = asset.workStatus === 'planned' ? 'Planned artwork; no preview yet.' : 'Artwork is still being revised.';
  }
}
function openAsset(id) {
  if (!catalogue) return;
  const asset = catalogue.assets.find(a => a.id === id);
  if (!asset) return;
  if (selectedCategory !== asset.category) { selectedCategory = asset.category; render(); }
  currentAsset = asset;
  galleryIndex = 0;
  const category = catalogue.categories.find(c => c.id === asset.category);
  const available = asset.status === 'available';
  $('#asset-details').innerHTML = `<p class="eyebrow">${escapeHTML(category.name)}</p><h2 id="asset-title">${escapeHTML(asset.name)}</h2><p class="asset-description">${escapeHTML(asset.description)}</p><dl class="detail-facts"><div><dt>Status</dt><dd>${available ? 'Public beta' : 'Coming soon'}</dd></div><div><dt>OpenReliant</dt><dd>${escapeHTML(asset.engine || catalogue.engine)}</dd></div>${asset.assetRevision ? `<div><dt>Artwork revision</dt><dd>${escapeHTML(asset.assetRevision)}</dd></div>` : ''}${available ? `<div><dt>Download</dt><dd>${formatSize(asset.downloadBytes)} · ZIP</dd></div>` : ''}</dl><div class="detail-notes"><h3>Still on the workbench</h3><ul>${(asset.notes || []).map(note => `<li>${escapeHTML(note)}</li>`).join('')}</ul></div>${available ? `<a class="button primary" href="${escapeHTML(asset.download)}">Download ${escapeHTML(asset.name)} <span aria-hidden="true">↓</span></a><div class="secondary-links"><a href="${escapeHTML(asset.release)}">Release notes</a><a href="${escapeHTML(asset.download)}.sha256">Checksum</a><a href="${catalogue.repository}/tree/main/${asset.folder.split('/').map(encodeURIComponent).join('/')}/source">Editable source</a></div>` : '<button class="button coming-button" disabled>Coming soon</button>'}<p class="detail-warning">${asset.model ? 'The 3D hull preview uses reduced textures and browser lighting; loadout weapons and engine effects are omitted. ' : ''}${asset.previewType === 'mixed' ? 'The cover is a composition of the mod artwork; the other images are engine captures. ' : asset.previewType === 'render' ? 'The still images are Blender material previews; lighting differs in game. ' : asset.model ? 'Check the in-game capture for the current engine appearance. ' : ''}${available ? 'Beta testing covers format checks and bounded rendering on Linux; broader gameplay and other platforms are still to be tested.' : 'This entry has no published download yet.'}</p>`;
  $('#show-3d').hidden = !asset.model;
  $('#show-image').hidden = !galleryImages(asset).length;
  $('#show-image').textContent = galleryImages(asset).length > 1 ? previewLabel(asset) : asset.previewType === 'render' ? 'Rendered preview' : 'In-game capture';
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
  updateURL(asset);
  showPreview(asset.defaultPreview === 'image' ? 'image' : asset.model ? 'model' : 'image');
}
document.addEventListener('click', event => {
  const category = event.target.closest('[data-category]');
  if (category) { selectedCategory = category.dataset.category; $('#search').value = ''; render(); updateURL(); }
  const asset = event.target.closest('[data-asset]');
  if (asset) openAsset(asset.dataset.asset);
});
$('#search').addEventListener('input', render);
$('#status-filter').addEventListener('change', render);
$('.close-dialog').addEventListener('click', closePreview);
dialog.addEventListener('cancel', event => { event.preventDefault(); closePreview(); });
dialog.addEventListener('click', event => { if (event.target === dialog) closePreview(); });
$('#show-3d').addEventListener('click', () => showPreview('model'));
$('#show-image').addEventListener('click', () => showPreview('image'));
$('#gallery-previous').addEventListener('click', () => stepGallery(-1));
$('#gallery-next').addEventListener('click', () => stepGallery(1));
dialog.addEventListener('keydown', event => {
  if (previewKind !== 'image' || galleryImages(currentAsset || {}).length < 2 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest('input, textarea, select, [contenteditable]')) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    stepGallery(event.key === 'ArrowLeft' ? -1 : 1);
  }
});
$('#rotate-toggle').addEventListener('click', () => {
  const viewer = $('model-viewer'); if (!viewer) return;
  viewer.toggleAttribute('auto-rotate');
  $('#rotate-toggle').textContent = viewer.hasAttribute('auto-rotate') ? 'Pause rotation' : 'Rotate model';
});
try {
  const response = await fetch('catalog.json', { cache: 'no-cache' }); if (!response.ok) throw new Error('Catalogue unavailable');
  catalogue = await response.json();
  const params = new URLSearchParams(location.search);
  selectedCategory = catalogue.categories.some(c => c.id === params.get('category')) ? params.get('category') : catalogue.categories[0].id;
  $('#collection-count').textContent = String(catalogue.categories.length).padStart(2,'0');
  $('#available-count').textContent = String(catalogue.assets.filter(a => a.status === 'available').length).padStart(2,'0');
  render();
  if (params.get('asset')) openAsset(params.get('asset'));
} catch {
  $('#asset-grid').innerHTML = '<div class="empty-state"><h4>The collection could not load.</h4><p>Please reload, or <a href="https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases">browse the downloads on GitHub</a>.</p></div>';
}
