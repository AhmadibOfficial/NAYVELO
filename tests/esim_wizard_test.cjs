'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

class Element {
  constructor(tag = 'div') {
    this.tag = tag;
    this.children = [];
    this.listeners = {};
    this.hidden = false;
    this.disabled = false;
    this.attributes = {};
    this.textContent = '';
  }
  replaceChildren(...children) { this.children = children; }
  append(...children) { this.children.push(...children); }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  focus() { this.focused = true; }
  click() { assert.equal(this.disabled, false, 'Disabled control cannot be clicked'); this.listeners.click(); }
  querySelector(selector) {
    return findAll(this, (node) => selector === 'h4' && node.tag === 'h4')[0] || null;
  }
}
function findAll(root, predicate) {
  return [root, ...root.children.flatMap((c) => findAll(c, predicate))].filter(predicate);
}
const panel = new Element();
const status = new Element();
const progress = new Element();
const back = new Element('button');
const next = new Element('button');
const reset = new Element('button');
const root = {
  querySelector: (selector) => ({
    '[data-wizard-panel]': panel,
    '[data-wizard-status]': status,
    '[data-wizard-progress]': progress,
    '[data-wizard-back]': back,
    '[data-wizard-next]': next,
    '[data-wizard-reset]': reset,
  })[selector]
};
global.document = {querySelector: (selector) => selector === '#esim-wizard' ? root : null,
  createElement: (tag) => new Element(tag)};

const source = fs.readFileSync(path.join(__dirname, '..', 'web', 'esim_wizard.js'), 'utf8');
const {evaluate, STEPS, OPTIONS} = require('../web/esim_wizard.js');
assert.deepEqual(STEPS, ['platform', 'setting', 'unlocked']);
for (const key of STEPS) assert.equal(OPTIONS[key].length, 3);
assert.equal(evaluate({}).level, 'incomplete');
assert.equal(evaluate({platform: 'iphone', setting: 'yes', unlocked: 'yes'}).level, 'potential');
assert.match(evaluate({platform: 'iphone', setting: 'yes', unlocked: 'yes'}).message, /not a compatibility check/i);
assert.equal(evaluate({platform: 'android', setting: 'no', unlocked: 'yes'}).level, 'review');
assert.equal(evaluate({platform: 'android', setting: 'yes', unlocked: 'no'}).level, 'review');
assert.equal(evaluate({platform: 'android', setting: 'unsure', unlocked: 'yes'}).level, 'unknown');
assert.equal(evaluate({platform: 'unsure', setting: 'yes', unlocked: 'unsure'}).level, 'unknown');
assert.equal(evaluate({platform: 'something', setting: 'yes', unlocked: 'yes'}).level, 'incomplete');
assert.doesNotMatch(source, /\b(?:fetch|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|indexedDB|geolocation)\s*\(/i);
assert.doesNotMatch(source, /(?:\.\s*(?:fetch|sendBeacon|localStorage|sessionStorage|indexedDB|geolocation)\b)/i);

function select(index) {
  const controls = findAll(panel, (e) => e.tag === 'input');
  assert.equal(controls.length, 3);
  controls[index].checked = true;
  controls[index].listeners.change();
}
assert.equal(next.disabled, true);
select(1); // Android
assert.equal(next.disabled, false);
next.click();
assert.equal(progress.textContent, 'Step 2 of 4');
assert.match(findAll(panel, (e) => e.tag === 'p').at(-1).textContent, /Samsung/);
select(0); // setting visible
next.click();
assert.equal(progress.textContent, 'Step 3 of 4');
back.click();
assert.equal(progress.textContent, 'Step 2 of 4');
next.click();
select(0); // unlocked
next.click();
assert.equal(progress.textContent, 'Step 4 of 4 · Educational summary');
assert.match(status.textContent, /Not verified/);
assert.match(findAll(panel, (e) => e.tag === 'h4')[0].textContent, /Potentially ready/);
assert.equal(next.hidden, true);
reset.click();
assert.equal(progress.textContent, 'Step 1 of 4');
assert.equal(next.disabled, true);
console.log('NAY-004 decision table, keyboard-ready interactions, uncertainty and no-network/no-storage passed.');
