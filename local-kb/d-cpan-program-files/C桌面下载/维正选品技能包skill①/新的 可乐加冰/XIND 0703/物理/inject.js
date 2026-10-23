// inject.js  (MAIN world, document_start)
// Installs all spoofing hooks synchronously so they win the race against page JS.
// The actual override VALUES arrive a tick later from content.js via a DOM attribute.
// Until then, every hook transparently falls through to the original behaviour.
(function () {
  'use strict';

  const ATTR = 'data-gcx-override';
  const EVT = 'gcx-override';

  // Live config; null/disabled => pass-through. Read by every hook at call time.
  let cfg = null;

  function readCfg() {
    try {
      const raw = document.documentElement.getAttribute(ATTR);
      cfg = raw ? JSON.parse(raw) : null;
    } catch (e) {
      cfg = null;
    }
  }
  document.addEventListener(EVT, readCfg);
  readCfg(); // in case the attribute is already present

  // ---- capture originals BEFORE patching (avoid recursion) -----------------
  const _DTF = Intl.DateTimeFormat;
  const _NF = Intl.NumberFormat;
  const _Collator = Intl.Collator;
  const _getTZO = Date.prototype.getTimezoneOffset;

  // ---- DST-aware offset (mirror of lib/tz.js — keep in sync) ---------------
  function tzOffsetMinutes(timeZone, date) {
    const dtf = new _DTF('en-US', {
      timeZone,
      hourCycle: 'h23',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    });
    const parts = dtf.formatToParts(date);
    const m = {};
    for (const p of parts) if (p.type !== 'literal') m[p.type] = p.value;
    let hour = parseInt(m.hour, 10);
    if (hour === 24) hour = 0;
    const asUTC = Date.UTC(
      parseInt(m.year, 10), parseInt(m.month, 10) - 1, parseInt(m.day, 10),
      hour, parseInt(m.minute, 10), parseInt(m.second, 10)
    );
    const realUTC = Math.floor(date.getTime() / 1000) * 1000;
    const off = -Math.round((asUTC - realUTC) / 60000);
    return off === 0 ? 0 : off; // avoid -0
  }

  const on = (k) => cfg && cfg[k];

  // ==== 1. Geolocation ======================================================
  function makePosition() {
    const c = cfg.coord || {};
    return {
      coords: {
        latitude: c.lat,
        longitude: c.lon,
        accuracy: cfg.accuracy || 1000,
        altitude: null,
        altitudeAccuracy: null,
        heading: null,
        speed: null,
      },
      timestamp: Date.now(),
    };
  }

  try {
    const geo = navigator.geolocation;
    if (geo) {
      const _get = geo.getCurrentPosition.bind(geo);
      const _watch = geo.watchPosition.bind(geo);
      const _clear = geo.clearWatch.bind(geo);
      const watchers = new Map();
      let watchSeq = 1 << 20; // avoid colliding with real ids

      geo.getCurrentPosition = function (success, error, options) {
        if (on('locationActive') && cfg.coord && typeof success === 'function') {
          Promise.resolve().then(() => success(makePosition()));
          return undefined;
        }
        return _get(success, error, options);
      };

      geo.watchPosition = function (success, error, options) {
        if (on('locationActive') && cfg.coord && typeof success === 'function') {
          const id = watchSeq++;
          watchers.set(id, true);
          Promise.resolve().then(() => {
            if (watchers.has(id)) success(makePosition());
          });
          return id;
        }
        return _watch(success, error, options);
      };

      geo.clearWatch = function (id) {
        if (watchers.has(id)) {
          watchers.delete(id);
          return undefined;
        }
        return _clear(id);
      };
    }
  } catch (e) { /* noop */ }

  // ==== 2. permissions.query -> geolocation granted =========================
  try {
    const perms = navigator.permissions;
    if (perms && typeof perms.query === 'function') {
      const _query = perms.query.bind(perms);
      perms.query = function (desc) {
        if (on('locationActive') && desc && desc.name === 'geolocation') {
          const status = {
            state: 'granted',
            onchange: null,
            addEventListener() {},
            removeEventListener() {},
            dispatchEvent() { return false; },
          };
          return Promise.resolve(status);
        }
        return _query(desc);
      };
    }
  } catch (e) { /* noop */ }

  // ==== 3. Date.prototype.getTimezoneOffset (DST-aware) =====================
  try {
    Date.prototype.getTimezoneOffset = function () {
      if (on('timezoneActive') && cfg.timezone) {
        try { return tzOffsetMinutes(cfg.timezone, this); } catch (e) { /* fall back */ }
      }
      return _getTZO.call(this);
    };
  } catch (e) { /* noop */ }

  // ==== 4. Intl.DateTimeFormat (default timeZone + locale) ==================
  function wrapDateTimeFormat() {
    function Patched(locales, options) {
      const opts = options ? Object.assign({}, options) : {};
      let loc = locales;
      const tzInjected = on('timezoneActive') && cfg.timezone && !opts.timeZone;
      const locInjected = on('languageActive') && cfg.locale && loc === undefined;
      if (tzInjected) opts.timeZone = cfg.timezone;
      if (locInjected) loc = cfg.locale;

      const inst = new _DTF(loc, opts);
      const _resolved = inst.resolvedOptions.bind(inst);
      inst.resolvedOptions = function () {
        const ro = _resolved();
        if (tzInjected) ro.timeZone = cfg.timezone;
        if (locInjected) ro.locale = cfg.locale;
        return ro;
      };
      return inst;
    }
    Patched.prototype = _DTF.prototype;
    Patched.supportedLocalesOf = _DTF.supportedLocalesOf.bind(_DTF);
    return Patched;
  }

  // ==== 5. Intl.NumberFormat / Collator (default locale) ====================
  function wrapLocaleCtor(Orig) {
    function Patched(locales, options) {
      let loc = locales;
      const locInjected = on('languageActive') && cfg.locale && loc === undefined;
      if (locInjected) loc = cfg.locale;
      const inst = new Orig(loc, options);
      if (locInjected) {
        const _resolved = inst.resolvedOptions.bind(inst);
        inst.resolvedOptions = function () {
          const ro = _resolved();
          ro.locale = cfg.locale;
          return ro;
        };
      }
      return inst;
    }
    Patched.prototype = Orig.prototype;
    Patched.supportedLocalesOf = Orig.supportedLocalesOf.bind(Orig);
    return Patched;
  }

  try {
    Object.defineProperty(Intl, 'DateTimeFormat', {
      value: wrapDateTimeFormat(), writable: true, configurable: true,
    });
    Object.defineProperty(Intl, 'NumberFormat', {
      value: wrapLocaleCtor(_NF), writable: true, configurable: true,
    });
    Object.defineProperty(Intl, 'Collator', {
      value: wrapLocaleCtor(_Collator), writable: true, configurable: true,
    });
  } catch (e) { /* noop */ }

  // ==== 6. navigator.language / navigator.languages =========================
  try {
    const _language = navigator.language;
    const _languages = navigator.languages ? navigator.languages.slice() : [];
    Object.defineProperty(navigator, 'language', {
      configurable: true,
      get() {
        return on('languageActive') && cfg.language ? cfg.language : _language;
      },
    });
    Object.defineProperty(navigator, 'languages', {
      configurable: true,
      get() {
        return on('languageActive') && cfg.languages
          ? Object.freeze(cfg.languages.slice())
          : _languages;
      },
    });
  } catch (e) { /* noop */ }
})();
