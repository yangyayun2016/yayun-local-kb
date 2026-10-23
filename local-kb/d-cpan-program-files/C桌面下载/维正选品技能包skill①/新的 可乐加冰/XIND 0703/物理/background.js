// background.js  (MV3 service worker, ES module)
// Orchestrates: egress-IP geolocation (provider fallback) -> residential coord
// (Overpass, jitter fallback) -> locale inference -> stored override + DNR header.
// Network calls live here; all math/parsing comes from the pure lib/ modules.

import { PROVIDERS } from './lib/providers.js';
import { inferLocale } from './lib/locale.js';
import {
  overpassQuery,
  pickResidentialCoord,
  jitterCoord,
} from './lib/geo.js';

const OVERPASS_ENDPOINT = 'https://overpass-api.de/api/interpreter';
const ALARM = 'geo-refresh';
const DNR_RULE_ID = 1;

const DEFAULT_SETTINGS = {
  locationEnabled: true,
  timezoneEnabled: true,
  languageEnabled: true,
  precisionMeters: 1500, // "district" preset
  refreshMinutes: 60,
  ipinfoToken: '',
};

async function getSettings() {
  const { settings } = await chrome.storage.local.get('settings');
  return { ...DEFAULT_SETTINGS, ...(settings || {}) };
}

// ---- network helpers -------------------------------------------------------

async function fetchJson(url, opts, timeoutMs = 8000) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...opts, signal: ctrl.signal, cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

// Query providers in order; return the first successfully-parsed geolocation.
async function detectGeo(token) {
  const errors = [];
  for (const p of PROVIDERS) {
    try {
      const json = await fetchJson(p.url(token));
      const parsed = p.parse(json);
      if (parsed && parsed.lat != null && parsed.lon != null) return parsed;
      errors.push(`${p.name}: unparseable`);
    } catch (e) {
      errors.push(`${p.name}: ${e.message}`);
    }
  }
  throw new Error('all providers failed -> ' + errors.join('; '));
}

// Pick a residential-road coordinate near the IP center; jitter on failure.
async function chooseCoordinate(geo, precisionMeters) {
  try {
    const q = overpassQuery(geo.lat, geo.lon, precisionMeters);
    const json = await fetchJson(
      OVERPASS_ENDPOINT,
      { method: 'POST', body: 'data=' + encodeURIComponent(q) },
      25000
    );
    const picked = pickResidentialCoord(
      json,
      { lat: geo.lat, lon: geo.lon },
      precisionMeters
    );
    if (picked) return picked;
  } catch (e) {
    // fall through to jitter
  }
  return jitterCoord(geo.lat, geo.lon, precisionMeters);
}

// ---- override assembly -----------------------------------------------------

async function computeOverride() {
  const settings = await getSettings();
  const geo = await detectGeo(settings.ipinfoToken);
  const coord = await chooseCoordinate(geo, settings.precisionMeters);
  const loc = inferLocale(geo.countryCode, geo.timezone);

  const override = {
    // flags mirror the toggles so the page patch knows what to spoof
    locationActive: settings.locationEnabled,
    timezoneActive: settings.timezoneEnabled,
    languageActive: settings.languageEnabled,

    coord: { lat: coord.lat, lon: coord.lon },
    accuracy: Math.max(20, Math.round(settings.precisionMeters * 0.4)),
    coordSource: coord.source,

    timezone: geo.timezone || null,

    locale: loc.locale,
    language: loc.language,
    languages: loc.languages,
    acceptLanguage: loc.acceptLanguage,

    meta: {
      ip: geo.ip,
      countryCode: geo.countryCode,
      country: geo.country,
      region: geo.region,
      city: geo.city,
      isp: geo.isp,
      provider: geo.provider,
      updatedAt: Date.now(),
    },
  };

  await chrome.storage.local.set({ override });
  await syncAcceptLanguageRule(override, settings);
  return override;
}

// ---- declarativeNetRequest: outgoing Accept-Language -----------------------

async function syncAcceptLanguageRule(override, settings) {
  const remove = [DNR_RULE_ID];
  const add = [];
  if (settings.languageEnabled && override && override.acceptLanguage) {
    add.push({
      id: DNR_RULE_ID,
      priority: 1,
      action: {
        type: 'modifyHeaders',
        requestHeaders: [
          {
            header: 'Accept-Language',
            operation: 'set',
            value: override.acceptLanguage,
          },
        ],
      },
      condition: {
        urlFilter: '*',
        resourceTypes: [
          'main_frame', 'sub_frame', 'stylesheet', 'script', 'image',
          'font', 'object', 'xmlhttprequest', 'ping', 'media',
          'websocket', 'other',
        ],
      },
    });
  }
  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: remove,
    addRules: add,
  });
}

async function clearAcceptLanguageRule() {
  await chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [DNR_RULE_ID],
    addRules: [],
  });
}

// ---- refresh + scheduling --------------------------------------------------

let refreshing = false;
async function refresh() {
  if (refreshing) return { ok: false, error: 'busy' };
  refreshing = true;
  try {
    const override = await computeOverride();
    return { ok: true, override };
  } catch (e) {
    return { ok: false, error: String(e && e.message ? e.message : e) };
  } finally {
    refreshing = false;
  }
}

async function scheduleAlarm() {
  const { refreshMinutes } = await getSettings();
  await chrome.alarms.clear(ALARM);
  await chrome.alarms.create(ALARM, {
    periodInMinutes: Math.max(5, refreshMinutes),
  });
}

// ---- lifecycle + messaging -------------------------------------------------

chrome.runtime.onInstalled.addListener(async () => {
  const { settings } = await chrome.storage.local.get('settings');
  if (!settings) await chrome.storage.local.set({ settings: DEFAULT_SETTINGS });
  await scheduleAlarm();
  refresh();
});

chrome.runtime.onStartup.addListener(async () => {
  await scheduleAlarm();
  refresh();
});

chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === ALARM) refresh();
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    if (msg && msg.type === 'refresh') {
      sendResponse(await refresh());
    } else if (msg && msg.type === 'getState') {
      const { settings, override } = await chrome.storage.local.get([
        'settings',
        'override',
      ]);
      sendResponse({
        settings: { ...DEFAULT_SETTINGS, ...(settings || {}) },
        override: override || null,
      });
    } else if (msg && msg.type === 'saveSettings') {
      const next = { ...DEFAULT_SETTINGS, ...(msg.settings || {}) };
      await chrome.storage.local.set({ settings: next });
      await scheduleAlarm();
      if (!next.languageEnabled) await clearAcceptLanguageRule();
      // recompute with new settings so DNR + coord reflect changes
      sendResponse(await refresh());
    } else {
      sendResponse({ ok: false, error: 'unknown message' });
    }
  })();
  return true; // async response
});
