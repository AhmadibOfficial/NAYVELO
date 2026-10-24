'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(path.join(ROOT, 'shared/plans.json'), 'utf8'));
const source = fs.readFileSync(path.join(ROOT, 'web/plan_compare.js'), 'utf8');
class Element {
  constructor(tag='div') {
    this.tagName = tag; this.children=[]; this.listeners={}; this.value='';
    this.disabled=false; this.checked=false; this.textContent='';
  }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = [...items]; }
  addEventListener(event, fn) { this.listeners[event]=fn; }
  setAttribute(name, value) { this[name]=value; }
  fire(event) { const fn=this.listeners[event]; assert(fn, `missing ${event} handler`); fn(); }
}
const ids = Object.fromEntries(
  ['plan-list','plan-period','plan-result','plan-compare','plan-selection','plan-compare-output']
    .map(id => [id, new Element()])
);
ids['plan-period'].value = 'all';
const calls=[];
const document = {
  getElementById: id => ids[id],
  createElement: tag => new Element(tag),
};
const context = {
  document,
  fetch: async (url, options) => {
    calls.push([url, options]);
    return {ok: true, json: async () => catalog};
  },
};
vm.runInNewContext(source, context, {filename: 'plan_compare.js'});
async function run() {
  // Fetch/json microtasks complete in next turn.
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(calls.map(c => c[0]), ['/api/v1/plans']);
  assert.equal(ids['plan-list'].children.length, 6);
  assert.match(ids['plan-result'].textContent, /6 concept plans shown/);
  ids['plan-period'].value = 'Weekly'; ids['plan-period'].fire('change');
  assert.equal(ids['plan-list'].children.length, 1);
  ids['plan-period'].value = 'all'; ids['plan-period'].fire('change');
  assert.equal(ids['plan-list'].children.length, 6);
  for (const card of ids['plan-list'].children.slice(0, 2)) {
    const label = card.children.at(-1);
    const checkbox = label.children[0];
    checkbox.checked = true; checkbox.fire('change');
  }
  assert.equal(ids['plan-compare'].disabled, false);
  ids['plan-compare'].fire('click');
  assert.equal(ids['plan-compare-output'].children.length, 1);
  const table = ids['plan-compare-output'].children[0];
  assert.equal(table.tagName, 'table');
  assert.equal(table.children[2].children.length, 9); // duration to purchase
  const rows = table.children[2].children;
  assert.equal(rows[3].children[1].textContent, 'Not confirmed'); // voice
  assert.equal(rows[5].children[2].textContent, 'Not confirmed'); // NGN price
  assert.equal(rows[8].children[1].textContent, 'Unavailable — simulation only');
  assert.equal(calls.length, 1, 'only a read-only plan API request may be made');
  console.log('NAY-003 web filter/compare and no-network-write regression passed.');
}
run().catch(error => {console.error(error); process.exitCode=1;});
