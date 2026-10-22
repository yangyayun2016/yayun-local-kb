// popup/popup.js
const $ = (id) => document.getElementById(id);
const FIELDS = {
  locationEnabled: 'checkbox',
  timezoneEnabled: 'checkbox',
  languageEnabled: 'checkbox',
  precisionMeters: 'number',
  refreshMinutes: 'number',
  ipinfoToken: 'text',
};

function send(msg) {
  return new Promise((resolve) => chrome.runtime.sendMessage(msg, resolve));
}

function loadInto(settings) {
  for (const [id, type] of Object.entries(FIELDS)) {
    const el = $(id);
    if (!el) continue;
    if (type === 'checkbox') el.checked = !!settings[id];
    else el.value = settings[id];
  }
}

function collect() {
  const out = {};
  for (const [id, type] of Object.entries(FIELDS)) {
    const el = $(id);
    if (type === 'checkbox') out[id] = el.checked;
    else if (type === 'number') out[id] = parseInt(el.value, 10);
    else out[id] = el.value.trim();
  }
  return out;
}

function render(override, error) {
  const box = $('status');
  $('src').textContent = override && override.coordSource ? override.coordSource : '';
  if (error) {
    box.innerHTML = `<div class="err">Error: ${escapeHtml(error)}</div>`;
    return;
  }
  if (!override) {
    box.innerHTML = '<div class="muted">No profile yet — click “Refresh now”.</div>';
    return;
  }
  const m = override.meta || {};
  const c = override.coord || {};
  const rows = [
    ['IP', m.ip],
    ['Country', `${m.city || ''} ${m.region || ''} (${m.countryCode || '?'})`.trim()],
    ['ISP', m.isp],
    ['Timezone', override.timezone],
    ['Language', override.language],
    ['Accept-Language', override.acceptLanguage],
    ['Coord', c.lat != null ? `${c.lat}, ${c.lon}` : ''],
    ['Updated', m.updatedAt ? new Date(m.updatedAt).toLocaleTimeString() : ''],
  ];
  box.innerHTML = rows
    .filter(([, v]) => v)
    .map(
      ([k, v]) =>
        `<div class="kv"><span class="muted">${k}</span><b class="mono">${escapeHtml(String(v))}</b></div>`
    )
    .join('');
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

async function init() {
  const state = await send({ type: 'getState' });
  loadInto(state.settings);
  render(state.override, null);
}

$('save').addEventListener('click', async () => {
  $('save').disabled = true;
  const res = await send({ type: 'saveSettings', settings: collect() });
  render(res && res.override, res && !res.ok ? res.error : null);
  $('save').disabled = false;
});

$('refresh').addEventListener('click', async () => {
  const btn = $('refresh');
  btn.disabled = true;
  btn.textContent = 'Refreshing…';
  const res = await send({ type: 'refresh' });
  render(res && res.override, res && !res.ok ? res.error : null);
  btn.disabled = false;
  btn.textContent = 'Refresh now';
});

init();
