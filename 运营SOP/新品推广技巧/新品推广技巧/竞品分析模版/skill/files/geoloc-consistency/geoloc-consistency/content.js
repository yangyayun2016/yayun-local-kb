// content.js  (ISOLATED world, document_start)
// The MAIN-world patch (inject.js) installs hooks synchronously at document_start
// but needs the override VALUES, which live in chrome.storage (async) and are not
// reachable from the MAIN world. This bridge relays them across the world boundary
// using a DOM attribute (strings always cross cleanly) plus a plain Event.

const ATTR = 'data-gcx-override';
const EVT = 'gcx-override';

function push(override) {
  try {
    const root = document.documentElement;
    if (!root) return;
    root.setAttribute(ATTR, JSON.stringify(override || null));
    document.dispatchEvent(new Event(EVT));
  } catch (e) {
    // ignore: page CSP cannot block attribute writes, but be defensive
  }
}

// Initial delivery.
chrome.storage.local.get('override').then((r) => push(r.override || null));

// Live updates when the background recomputes the override.
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.override) {
    push(changes.override.newValue || null);
  }
});
