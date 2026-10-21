'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Node {
  constructor(tag) { this.tag = tag; this.children = []; this.listeners = {}; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  addEventListener(event, callback) { this.listeners[event] = callback; }
  focus() { this.focused = true; }
  fire(event) { this.listeners[event](); }
}
function boot() {
  const ids = Object.fromEntries(['flow', 'step', 'content', 'back', 'next', 'reset', 'progress'].map(id => ['onboarding-' + id, new Node('div')]));
  let attempts = 0;
  const forbidden = () => { attempts++; throw Error('Network or storage access forbidden'); };
  const context = { document: { getElementById: id => ids[id], createElement: tag => new Node(tag) } };
  for (const key of ['fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource', 'localStorage', 'sessionStorage', 'indexedDB', 'navigator', 'location']) {
    Object.defineProperty(context, key, { get: forbidden });
  }
  vm.runInNewContext(fs.readFileSync('web/onboarding.js', 'utf8'), context);
  return { ids, attempts: () => attempts };
}
const {ids, attempts} = boot();
const get = id => ids['onboarding-' + id];
assert.equal(get('flow').hidden, false);
assert.equal(get('next').disabled, true);
get('next').fire('click'); // Even a synthetic click cannot bypass acknowledgement.
assert.match(get('progress').textContent, /Step 1/);
const check = get('content').children[0].children[0];
check.checked = true;
check.fire('change');
get('next').fire('click');
assert.match(get('progress').textContent, /Step 2/);
assert.equal(get('step').focused, true);
const radios = get('content').children[0].children.slice(1).map(label => label.children[0]);
assert.deepEqual(radios.map(r => r.type), ['radio', 'radio']);
radios[1].checked = true;
radios[1].fire('change');
get('back').fire('click');
assert.match(get('progress').textContent, /Step 1/);
get('next').fire('click');
get('next').fire('click');
assert.match(get('content').children[0].textContent, /Learn about eSIM.*No subscriber account was created/);
assert.equal(get('next').hidden, true);
get('next').fire('click');
assert.match(get('progress').textContent, /Step 3/);
get('reset').fire('click');
assert.equal(get('next').disabled, true);
assert.equal(get('content').children[0].children[0].checked, false);
assert.equal(boot().ids['onboarding-next'].disabled, true);
assert.equal(attempts(), 0);
console.log('Onboarding transitions, acknowledgement, reset, focus and no network/storage access passed.');
