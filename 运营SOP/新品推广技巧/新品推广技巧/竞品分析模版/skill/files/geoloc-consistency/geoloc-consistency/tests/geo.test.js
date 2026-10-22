import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  haversineMeters,
  jitterCoord,
  pickResidentialCoord,
  extractNodes,
  overpassQuery,
} from '../lib/geo.js';

test('haversine ~ known distance (Berlin<->Paris ≈ 878 km)', () => {
  const d = haversineMeters(
    { lat: 52.52, lon: 13.405 },
    { lat: 48.8566, lon: 2.3522 }
  );
  assert.ok(Math.abs(d - 878000) < 15000, `got ${d}`);
});

test('jitter stays within the requested radius', () => {
  const center = { lat: 52.52, lon: 13.405 };
  let seed = 0.42;
  const rng = () => {
    seed = (seed * 9301 + 49297) % 233280 / 233280;
    return seed;
  };
  for (let i = 0; i < 500; i++) {
    const p = jitterCoord(center.lat, center.lon, 1000, rng);
    const d = haversineMeters(center, { lat: p.lat, lon: p.lon });
    assert.ok(d <= 1000 + 5, `jitter escaped radius: ${d}`);
    assert.equal(p.source, 'jitter');
  }
});

test('extractNodes pulls only node elements', () => {
  const nodes = extractNodes({
    elements: [
      { type: 'way', id: 1, nodes: [10, 11] },
      { type: 'node', id: 10, lat: 52.5, lon: 13.4 },
      { type: 'node', id: 11, lat: 52.6, lon: 13.5 },
      { type: 'node', id: 12 }, // missing coords -> skipped
    ],
  });
  assert.equal(nodes.length, 2);
});

test('pickResidentialCoord prefers nodes inside the precision radius', () => {
  const center = { lat: 52.52, lon: 13.405 };
  const json = {
    elements: [
      { type: 'way', id: 1, nodes: [10, 99] },
      { type: 'node', id: 10, lat: 52.5205, lon: 13.4055 }, // ~50 m away
      { type: 'node', id: 99, lat: 53.0, lon: 14.0 }, // far outside
    ],
  };
  const r = pickResidentialCoord(json, center, 500, () => 0.9);
  assert.equal(r.source, 'osm');
  const d = haversineMeters(center, { lat: r.lat, lon: r.lon });
  assert.ok(d <= 500, `picked node outside radius: ${d}`);
});

test('pickResidentialCoord returns null when no nodes', () => {
  assert.equal(pickResidentialCoord({ elements: [] }, { lat: 0, lon: 0 }, 500), null);
});

test('pickResidentialCoord falls back to nearest label when all outside', () => {
  const center = { lat: 0, lon: 0 };
  const json = { elements: [{ type: 'node', id: 1, lat: 1, lon: 1 }] };
  const r = pickResidentialCoord(json, center, 100, () => 0);
  assert.equal(r.source, 'osm-nearest');
});

test('overpassQuery embeds coords and doubled radius (min 300)', () => {
  const q = overpassQuery(52.52, 13.405, 100);
  assert.ok(q.includes('highway=residential'));
  assert.ok(q.includes('around:300,52.52,13.405'));
  const q2 = overpassQuery(1, 2, 1500);
  assert.ok(q2.includes('around:3000,1,2'));
});
