import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  inferLocale,
  buildLanguages,
  buildAcceptLanguage,
} from '../lib/locale.js';

test('single-language country: DE', () => {
  const r = inferLocale('DE', 'Europe/Berlin');
  assert.equal(r.language, 'de-DE');
  assert.deepEqual(r.languages, ['de-DE', 'de', 'en']);
  assert.equal(r.acceptLanguage, 'de-DE,de;q=0.9,en;q=0.8');
  assert.equal(r.source, 'country');
});

test('US stays en-US with en fallback dedup', () => {
  const r = inferLocale('US', 'America/New_York');
  assert.equal(r.language, 'en-US');
  assert.deepEqual(r.languages, ['en-US', 'en']);
  assert.equal(r.acceptLanguage, 'en-US,en;q=0.9');
});

test('timezone override: Montreal => French-first Canada', () => {
  const r = inferLocale('CA', 'America/Montreal');
  assert.equal(r.language, 'fr-CA');
  assert.equal(r.source, 'timezone');
  assert.ok(r.languages.includes('en-CA'));
});

test('timezone override: Toronto => English-first Canada', () => {
  const r = inferLocale('CA', 'America/Toronto');
  assert.equal(r.language, 'en-CA');
  assert.equal(r.source, 'timezone');
});

test('multilingual country without tz override: CH', () => {
  const r = inferLocale('CH', 'Europe/Zurich');
  // Zurich has an explicit tz entry, still de-first
  assert.equal(r.language, 'de-CH');
  assert.ok(r.languages.includes('fr-CH'));
  assert.ok(r.languages.includes('it-CH'));
});

test('unknown country falls back to en-US', () => {
  const r = inferLocale('ZZ', 'Factory');
  assert.equal(r.language, 'en-US');
  assert.equal(r.source, 'default');
});

test('lowercase country code is normalized', () => {
  const r = inferLocale('fr', 'Europe/Paris');
  assert.equal(r.language, 'fr-FR');
});

test('buildLanguages dedups base langs', () => {
  assert.deepEqual(buildLanguages(['pt-BR']), ['pt-BR', 'pt', 'en']);
  assert.deepEqual(buildLanguages(['en-GB']), ['en-GB', 'en']);
});

test('buildAcceptLanguage floors q at 0.1', () => {
  const many = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'];
  const header = buildAcceptLanguage(many);
  assert.ok(header.startsWith('a,b;q=0.9,'));
  assert.ok(header.includes(';q=0.1'));
  assert.ok(!/q=0\.0/.test(header));
});
