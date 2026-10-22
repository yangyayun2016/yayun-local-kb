import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseIpApiCo,
  parseIpWhoIs,
  parseIpInfo,
  PROVIDERS,
} from '../lib/providers.js';

test('parseIpApiCo normalizes a valid payload', () => {
  const r = parseIpApiCo({
    ip: '1.2.3.4',
    city: 'Berlin',
    region: 'Land Berlin',
    country: 'DE',
    country_code: 'DE',
    country_name: 'Germany',
    latitude: 52.52,
    longitude: 13.405,
    timezone: 'Europe/Berlin',
    org: 'AS3320 Deutsche Telekom AG',
  });
  assert.equal(r.countryCode, 'DE');
  assert.equal(r.city, 'Berlin');
  assert.equal(r.lat, 52.52);
  assert.equal(r.lon, 13.405);
  assert.equal(r.timezone, 'Europe/Berlin');
  assert.equal(r.isp, 'AS3320 Deutsche Telekom AG');
  assert.equal(r.provider, 'ipapi.co');
});

test('parseIpApiCo returns null on error payload', () => {
  assert.equal(parseIpApiCo({ error: true, reason: 'RateLimited' }), null);
  assert.equal(parseIpApiCo(null), null);
});

test('parseIpWhoIs normalizes nested connection/timezone', () => {
  const r = parseIpWhoIs({
    ip: '9.9.9.9',
    success: true,
    country: 'France',
    country_code: 'FR',
    region: 'Île-de-France',
    city: 'Paris',
    latitude: 48.8566,
    longitude: 2.3522,
    connection: { isp: 'Orange S.A.' },
    timezone: { id: 'Europe/Paris' },
  });
  assert.equal(r.countryCode, 'FR');
  assert.equal(r.isp, 'Orange S.A.');
  assert.equal(r.timezone, 'Europe/Paris');
  assert.equal(r.provider, 'ipwho.is');
});

test('parseIpWhoIs returns null when success=false', () => {
  assert.equal(parseIpWhoIs({ success: false, message: 'nope' }), null);
});

test('parseIpInfo splits loc "lat,lon"', () => {
  const r = parseIpInfo({
    ip: '8.8.8.8',
    city: 'Mountain View',
    region: 'California',
    country: 'US',
    loc: '37.4056,-122.0775',
    org: 'AS15169 Google LLC',
    timezone: 'America/Los_Angeles',
  });
  assert.equal(r.countryCode, 'US');
  assert.equal(r.lat, 37.4056);
  assert.equal(r.lon, -122.0775);
  assert.equal(r.timezone, 'America/Los_Angeles');
  assert.equal(r.provider, 'ipinfo.io');
});

test('parseIpInfo returns null without loc', () => {
  assert.equal(parseIpInfo({ ip: '8.8.8.8', country: 'US' }), null);
});

test('lat/lon accepted as strings too', () => {
  const r = parseIpApiCo({
    country_code: 'IT',
    latitude: '41.9028',
    longitude: '12.4964',
    timezone: 'Europe/Rome',
  });
  assert.equal(r.lat, 41.9028);
  assert.equal(r.lon, 12.4964);
});

test('PROVIDERS registry: order + ipinfo token wiring', () => {
  assert.deepEqual(PROVIDERS.map((p) => p.name), ['ipapi.co', 'ipwho.is', 'ipinfo.io']);
  const ipinfo = PROVIDERS.find((p) => p.name === 'ipinfo.io');
  assert.equal(ipinfo.url(''), 'https://ipinfo.io/json');
  assert.equal(ipinfo.url('tok EN'), 'https://ipinfo.io/json?token=tok%20EN');
  // token-less providers ignore the argument
  assert.equal(PROVIDERS[0].url('anything'), 'https://ipapi.co/json/');
});
