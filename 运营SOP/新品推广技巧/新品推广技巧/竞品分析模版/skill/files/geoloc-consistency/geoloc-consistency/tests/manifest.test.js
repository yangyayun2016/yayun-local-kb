import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));

test('is Manifest V3 with module service worker', () => {
  assert.equal(manifest.manifest_version, 3);
  assert.equal(manifest.background.service_worker, 'background.js');
  assert.equal(manifest.background.type, 'module');
});

test('MAIN-world patch injected at document_start', () => {
  const main = manifest.content_scripts.find((c) => c.world === 'MAIN');
  assert.ok(main, 'a MAIN-world content script must exist');
  assert.deepEqual(main.js, ['inject.js']);
  assert.equal(main.run_at, 'document_start');
  assert.equal(main.all_frames, true);
});

test('ISOLATED bridge injected at document_start', () => {
  const iso = manifest.content_scripts.find(
    (c) => (c.world || 'ISOLATED') === 'ISOLATED'
  );
  assert.ok(iso, 'an ISOLATED bridge must exist');
  assert.deepEqual(iso.js, ['content.js']);
  assert.equal(iso.run_at, 'document_start');
});

test('required permissions + host access declared', () => {
  for (const p of ['storage', 'alarms', 'declarativeNetRequest']) {
    assert.ok(manifest.permissions.includes(p), `missing permission ${p}`);
  }
  const hosts = manifest.host_permissions.join(' ');
  assert.ok(hosts.includes('ipapi.co'));
  assert.ok(hosts.includes('overpass-api.de'));
  assert.ok(hosts.includes('<all_urls>')); // required for DNR modifyHeaders
});

test('inject.js captures Intl/Date originals BEFORE patching them', () => {
  const src = readFileSync(join(root, 'inject.js'), 'utf8');
  const capture = src.indexOf('_DTF = Intl.DateTimeFormat');
  const patch = src.indexOf("Object.defineProperty(Intl, 'DateTimeFormat'");
  assert.ok(capture > -1 && patch > -1, 'both capture and patch must be present');
  assert.ok(capture < patch, 'originals must be captured before Intl is patched');

  const capTZO = src.indexOf('_getTZO = Date.prototype.getTimezoneOffset');
  const patchTZO = src.indexOf('Date.prototype.getTimezoneOffset = function');
  assert.ok(capTZO < patchTZO, 'getTimezoneOffset original captured before override');
});

test('inject.js hook installation is synchronous (no await before patches)', () => {
  const src = readFileSync(join(root, 'inject.js'), 'utf8');
  // The IIFE must not await/return a promise before installing hooks.
  assert.ok(!/await\s/.test(src), 'inject.js must not use await (would delay hooks)');
});
