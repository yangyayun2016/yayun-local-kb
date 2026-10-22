// lib/providers.js
// Multiple IP-geolocation providers with fallback. Each parser normalizes a
// provider-specific JSON payload into a common shape or returns null on failure.
//
// Normalized shape:
// { ip, countryCode, country, region, city, lat, lon, isp, timezone, provider }

function num(v) {
  const n = typeof v === 'string' ? parseFloat(v) : v;
  return Number.isFinite(n) ? n : null;
}

// ipapi.co/json/
export function parseIpApiCo(j) {
  if (!j || j.error) return null;
  const lat = num(j.latitude);
  const lon = num(j.longitude);
  const cc = j.country_code || j.country;
  if (lat == null || lon == null || !cc) return null;
  return {
    ip: j.ip || null,
    countryCode: String(cc).toUpperCase(),
    country: j.country_name || null,
    region: j.region || null,
    city: j.city || null,
    lat,
    lon,
    isp: j.org || null,
    timezone: j.timezone || null,
    provider: 'ipapi.co',
  };
}

// ipwho.is
export function parseIpWhoIs(j) {
  if (!j || j.success === false) return null;
  const lat = num(j.latitude);
  const lon = num(j.longitude);
  if (lat == null || lon == null || !j.country_code) return null;
  return {
    ip: j.ip || null,
    countryCode: String(j.country_code).toUpperCase(),
    country: j.country || null,
    region: j.region || null,
    city: j.city || null,
    lat,
    lon,
    isp: (j.connection && (j.connection.isp || j.connection.org)) || null,
    timezone: (j.timezone && j.timezone.id) || null,
    provider: 'ipwho.is',
  };
}

// ipinfo.io/json  (loc is "lat,lon"; timezone present on free tier)
export function parseIpInfo(j) {
  if (!j || j.error) return null;
  let lat = null, lon = null;
  if (typeof j.loc === 'string' && j.loc.includes(',')) {
    const [a, b] = j.loc.split(',');
    lat = num(a);
    lon = num(b);
  }
  if (lat == null || lon == null || !j.country) return null;
  return {
    ip: j.ip || null,
    countryCode: String(j.country).toUpperCase(),
    country: j.country_name || null,
    region: j.region || null,
    city: j.city || null,
    lat,
    lon,
    isp: j.org || null,
    timezone: j.timezone || null,
    provider: 'ipinfo.io',
  };
}

// Provider registry. `url(token)` returns the request URL; token only used by ipinfo.
export const PROVIDERS = [
  {
    name: 'ipapi.co',
    url: () => 'https://ipapi.co/json/',
    parse: parseIpApiCo,
  },
  {
    name: 'ipwho.is',
    url: () => 'https://ipwho.is/',
    parse: parseIpWhoIs,
  },
  {
    name: 'ipinfo.io',
    url: (token) =>
      token ? `https://ipinfo.io/json?token=${encodeURIComponent(token)}` : 'https://ipinfo.io/json',
    parse: parseIpInfo,
  },
];
