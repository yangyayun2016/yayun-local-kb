import { test } from 'node:test';
import assert from 'node:assert/strict';
import { timezoneOffsetMinutes } from '../lib/tz.js';

// getTimezoneOffset semantics: positive = behind UTC (west).
test('UTC is always 0', () => {
  assert.equal(timezoneOffsetMinutes('UTC', new Date('2025-01-15T12:00:00Z')), 0);
  assert.equal(timezoneOffsetMinutes('UTC', new Date('2025-07-15T12:00:00Z')), 0);
});

test('Europe/Berlin: CET winter (+1) vs CEST summer (+2)', () => {
  assert.equal(
    timezoneOffsetMinutes('Europe/Berlin', new Date('2025-01-15T12:00:00Z')),
    -60
  );
  assert.equal(
    timezoneOffsetMinutes('Europe/Berlin', new Date('2025-07-15T12:00:00Z')),
    -120
  );
});

test('America/Los_Angeles: PST winter (-8) vs PDT summer (-7)', () => {
  assert.equal(
    timezoneOffsetMinutes('America/Los_Angeles', new Date('2025-01-15T12:00:00Z')),
    480
  );
  assert.equal(
    timezoneOffsetMinutes('America/Los_Angeles', new Date('2025-07-15T12:00:00Z')),
    420
  );
});

test('Asia/Kolkata: half-hour offset (+5:30) no DST', () => {
  assert.equal(
    timezoneOffsetMinutes('Asia/Kolkata', new Date('2025-01-15T12:00:00Z')),
    -330
  );
  assert.equal(
    timezoneOffsetMinutes('Asia/Kolkata', new Date('2025-07-15T12:00:00Z')),
    -330
  );
});

test('Australia/Adelaide: southern-hemisphere DST inverts seasons', () => {
  // Jan = summer (ACDT, +10:30 -> -630) ; Jul = winter (ACST, +9:30 -> -570)
  assert.equal(
    timezoneOffsetMinutes('Australia/Adelaide', new Date('2025-01-15T12:00:00Z')),
    -630
  );
  assert.equal(
    timezoneOffsetMinutes('Australia/Adelaide', new Date('2025-07-15T12:00:00Z')),
    -570
  );
});

test('offset flips exactly at a DST boundary', () => {
  // US DST 2025 begins 2025-03-09 10:00 UTC (02:00 local -> 03:00 local)
  const before = new Date('2025-03-09T09:59:00Z');
  const after = new Date('2025-03-09T10:01:00Z');
  assert.equal(timezoneOffsetMinutes('America/Los_Angeles', before), 480); // PST
  assert.equal(timezoneOffsetMinutes('America/Los_Angeles', after), 420); // PDT
});
