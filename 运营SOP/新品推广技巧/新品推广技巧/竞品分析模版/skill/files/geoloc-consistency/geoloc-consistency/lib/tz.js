// lib/tz.js
// DST-aware IANA timezone offset, matching Date.prototype.getTimezoneOffset semantics.
// getTimezoneOffset() returns minutes where positive means BEHIND UTC (west of UTC).
// e.g. America/Los_Angeles winter -> +480 ; Europe/Berlin summer -> -120.
//
// IMPORTANT: The identical function body is mirrored inside inject.js (page MAIN world,
// which cannot import ES modules). Keep the two in sync. This file is the tested source.

export function timezoneOffsetMinutes(timeZone, date, DTF = Intl.DateTimeFormat) {
  const dtf = new DTF('en-US', {
    timeZone,
    hourCycle: 'h23',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const parts = dtf.formatToParts(date);
  const m = {};
  for (const p of parts) {
    if (p.type !== 'literal') m[p.type] = p.value;
  }
  let hour = parseInt(m.hour, 10);
  if (hour === 24) hour = 0; // some engines emit 24 for midnight under h23
  // Interpret the target-zone wall-clock time as if it were UTC.
  const asUTC = Date.UTC(
    parseInt(m.year, 10),
    parseInt(m.month, 10) - 1,
    parseInt(m.day, 10),
    hour,
    parseInt(m.minute, 10),
    parseInt(m.second, 10)
  );
  // Compare against the real UTC instant (truncated to whole seconds to match parts).
  const realUTC = Math.floor(date.getTime() / 1000) * 1000;
  // (wallclock-as-utc) - (real-utc) = signed offset east-of-UTC in ms.
  // getTimezoneOffset wants west-positive minutes, hence the negation.
  const off = -Math.round((asUTC - realUTC) / 60000);
  return off === 0 ? 0 : off; // avoid -0
}
