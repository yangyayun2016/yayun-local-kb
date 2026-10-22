// lib/geo.js
// Pure geospatial helpers: distance, meter<->degree conversion, jitter fallback,
// and picking a residential road coordinate from an Overpass response.

const EARTH_R = 6371000; // meters
const DEG = Math.PI / 180;

export function haversineMeters(a, b) {
  const dLat = (b.lat - a.lat) * DEG;
  const dLon = (b.lon - a.lon) * DEG;
  const la1 = a.lat * DEG;
  const la2 = b.lat * DEG;
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(la1) * Math.cos(la2) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_R * Math.asin(Math.min(1, Math.sqrt(h)));
}

// Meters -> degrees of latitude (constant) and longitude (scaled by latitude).
export function metersToLatDeg(m) {
  return m / 111320;
}
export function metersToLonDeg(m, atLat) {
  const scale = Math.cos(atLat * DEG);
  return m / (111320 * (scale || 1e-6));
}

// Uniformly random point within `radiusMeters` of (lat,lon).
// rng() must return [0,1); injectable for deterministic tests.
export function jitterCoord(lat, lon, radiusMeters, rng = Math.random) {
  const angle = rng() * 2 * Math.PI;
  const r = Math.sqrt(rng()) * radiusMeters; // sqrt => uniform area distribution
  const dLat = metersToLatDeg(r * Math.sin(angle));
  const dLon = metersToLonDeg(r * Math.cos(angle), lat);
  return {
    lat: +(lat + dLat).toFixed(6),
    lon: +(lon + dLon).toFixed(6),
    source: 'jitter',
  };
}

// Collect node coordinates from an Overpass JSON response.
// With "(._;>;); out body;" Overpass returns both ways and the nodes they use.
export function extractNodes(overpassJson) {
  const els = (overpassJson && overpassJson.elements) || [];
  const nodes = [];
  for (const e of els) {
    if (e.type === 'node' && typeof e.lat === 'number' && typeof e.lon === 'number') {
      nodes.push({ lat: e.lat, lon: e.lon });
    }
  }
  return nodes;
}

// Pick a residential coordinate near `center`, preferring nodes inside the
// precision radius. Returns null when nothing usable is found (caller then jitters).
export function pickResidentialCoord(overpassJson, center, precisionMeters, rng = Math.random) {
  const nodes = extractNodes(overpassJson);
  if (!nodes.length) return null;

  const within = nodes.filter(
    (n) => haversineMeters(center, n) <= precisionMeters
  );
  const pool = within.length ? within : nodes;

  // Deterministic-ish selection: shuffle index via rng, avoid always the first.
  const idx = Math.floor(rng() * pool.length) % pool.length;
  const chosen = pool[idx];
  return {
    lat: +chosen.lat.toFixed(6),
    lon: +chosen.lon.toFixed(6),
    source: within.length ? 'osm' : 'osm-nearest',
  };
}

// Build the Overpass QL query string for residential roads around a point.
export function overpassQuery(lat, lon, radiusMeters) {
  const r = Math.max(300, Math.round(radiusMeters * 2));
  return (
    `[out:json][timeout:25];` +
    `way(around:${r},${lat},${lon})[highway=residential];` +
    `(._;>;);out body;`
  );
}
