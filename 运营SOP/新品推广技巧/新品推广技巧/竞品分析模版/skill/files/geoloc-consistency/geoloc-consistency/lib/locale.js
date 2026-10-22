// lib/locale.js
// Infer a locale bundle (navigator.language / navigator.languages / Accept-Language)
// from an ISO country code, refined by IANA timezone for multilingual countries.

// Primary locale list per country (first entry is the primary UI language).
const COUNTRY_LOCALE = {
  US: ['en-US'], GB: ['en-GB'], IE: ['en-IE'], AU: ['en-AU'], NZ: ['en-NZ'],
  CA: ['en-CA', 'fr-CA'], DE: ['de-DE'], AT: ['de-AT'], CH: ['de-CH', 'fr-CH', 'it-CH'],
  FR: ['fr-FR'], BE: ['nl-BE', 'fr-BE'], LU: ['fr-LU', 'de-LU'], NL: ['nl-NL'],
  ES: ['es-ES'], PT: ['pt-PT'], IT: ['it-IT'], SE: ['sv-SE'], NO: ['nb-NO'],
  DK: ['da-DK'], FI: ['fi-FI'], PL: ['pl-PL'], CZ: ['cs-CZ'], SK: ['sk-SK'],
  HU: ['hu-HU'], RO: ['ro-RO'], BG: ['bg-BG'], GR: ['el-GR'], TR: ['tr-TR'],
  RU: ['ru-RU'], UA: ['uk-UA'], JP: ['ja-JP'], KR: ['ko-KR'], CN: ['zh-CN'],
  TW: ['zh-TW'], HK: ['zh-HK', 'en-HK'], SG: ['en-SG', 'zh-SG'], IN: ['en-IN', 'hi-IN'],
  BR: ['pt-BR'], MX: ['es-MX'], AR: ['es-AR'], CL: ['es-CL'], CO: ['es-CO'],
  ZA: ['en-ZA'], IL: ['he-IL'], SA: ['ar-SA'], AE: ['ar-AE', 'en-AE'], TH: ['th-TH'],
  VN: ['vi-VN'], ID: ['id-ID'], MY: ['ms-MY', 'en-MY'], PH: ['en-PH'], EG: ['ar-EG'],
};

// Timezone-specific overrides for countries whose language depends on region.
const TZ_LOCALE = {
  'America/Montreal': ['fr-CA', 'en-CA'],
  'America/Toronto': ['en-CA', 'fr-CA'],
  'America/Vancouver': ['en-CA'],
  'America/Edmonton': ['en-CA'],
  'America/Winnipeg': ['en-CA'],
  'America/Halifax': ['en-CA'],
  'Europe/Zurich': ['de-CH', 'fr-CH', 'it-CH'],
  'Europe/Brussels': ['nl-BE', 'fr-BE'],
};

const DEFAULT = ['en-US'];

function baseLang(locale) {
  return String(locale).split('-')[0];
}

// Build navigator.languages: [primary, ...secondaries, base langs, 'en'] deduped.
export function buildLanguages(locales) {
  const out = [];
  const seen = new Set();
  const push = (v) => {
    if (v && !seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  };
  for (const loc of locales) {
    push(loc);
    push(baseLang(loc));
  }
  push('en'); // universal fallback
  return out;
}

// Build an Accept-Language header value with descending q-values.
// First item has no q (implicit 1.0); each subsequent drops 0.1, floored at 0.1.
export function buildAcceptLanguage(languages) {
  const parts = [];
  let q = 1.0;
  for (let i = 0; i < languages.length; i++) {
    if (i === 0) {
      parts.push(languages[i]);
    } else {
      q = Math.max(0.1, Math.round((q - 0.1) * 10) / 10);
      parts.push(`${languages[i]};q=${q.toFixed(1)}`);
    }
  }
  return parts.join(',');
}

export function inferLocale(countryCode, timeZone) {
  const tz = timeZone || '';
  const cc = String(countryCode || '').toUpperCase();

  let locales;
  if (TZ_LOCALE[tz]) {
    locales = TZ_LOCALE[tz];
  } else if (COUNTRY_LOCALE[cc]) {
    locales = COUNTRY_LOCALE[cc];
  } else {
    locales = DEFAULT;
  }

  const languages = buildLanguages(locales);
  return {
    locale: locales[0],
    language: languages[0],
    languages,
    acceptLanguage: buildAcceptLanguage(languages),
    source: TZ_LOCALE[tz] ? 'timezone' : COUNTRY_LOCALE[cc] ? 'country' : 'default',
  };
}
