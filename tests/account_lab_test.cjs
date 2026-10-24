'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../web/account_lab.js'),'utf8');
const html = fs.readFileSync(path.join(__dirname,'../web/index.html'),'utf8');
const policy = JSON.parse(fs.readFileSync(path.join(__dirname,'../shared/demo_accounts.json'),'utf8'));
const {create,change,updatePrivacy,allowed,initial} = require('../web/account_lab.js');
assert.deepEqual(Object.keys(initial).sort(),policy.profiles.map(x=>x.alias).sort());
assert.deepEqual(allowed,policy.allowedTransitions);
assert.deepEqual(create().privacy,policy.optionalPrivacyDefaults);
assert.equal(policy.simulationOnly,true);
assert.equal(policy.persistence,'memory_only');
assert.equal(policy.authentication,'none');
assert.equal(policy.personalDataCollected,false);
const first = create();
const second = create('DEMO-BETA');
assert.equal(first.status,'preview');
assert.equal(second.status,'paused');
assert.equal(change(first,'paused').status,'paused');
assert.equal(first.status,'preview','No in-place modification to original');
assert.equal(change(second,'preview').status,'preview');
for(const state of ['locked','closed']) {
  assert.throws(()=>change({...first,status:state},'preview'),/Blocked/);
}
assert.throws(()=>change(first,'activated'),/Blocked/);
assert.throws(()=>change(first,'preview'),/Blocked/);
assert.throws(()=>create('DEMO-REAL'),/Unknown/);
assert.throws(()=>updatePrivacy(first,'location',true),/Invalid/);
assert.throws(()=>updatePrivacy(first,'productNews','true'),/Invalid/);
assert.equal(updatePrivacy(first,'productAnalytics',true).privacy.productAnalytics,true);
assert.equal(first.privacy.productAnalytics,false);
for(const forbidden of ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'document.cookie', 'navigator.sendBeacon', 'WebSocket', 'indexedDB']) {
  assert.equal(source.includes(forbidden),false,`Unexpected browser side effect: ${forbidden}`);
}
assert.match(html,/id="account-lab"/);
assert.match(html,/aria-live="polite"/);
assert.match(html,/data-lab-preference="productAnalytics"/);
assert.match(html,/data-lab-preference="productNews"/);
assert.match(html,/data-lab-transition="locked"/);
assert.match(html,/data-lab-reset/);
// Evaluate in a sandbox that throws on any unexpected network or storage behavior.
class E {
  constructor(dataset={}) {this.dataset=dataset;this.listeners={};this.value='';this.checked=false;this.disabled=false;this.textContent='';}
  addEventListener(name,fn){this.listeners[name]=fn;}
  emit(type){this.listeners[type]();}
}
const selector = new E();
const stateText = new E();
const status = new E();
const events = new E();
const reset = new E();
const buttons = ['paused','preview','locked','closed'].map(labTransition=>new E({labTransition}));
const toggles = ['productAnalytics','productNews'].map(labPreference=>new E({labPreference}));
const root = {querySelector(q){return ({'[data-lab-alias]':selector,'[data-lab-state]':stateText,'[data-lab-status]':status,'[data-lab-events]':events,'[data-lab-reset]':reset})[q];},querySelectorAll(q){return q==='[data-lab-transition]'?buttons:q==='[data-lab-preference]'?toggles:[];}};
const context = {document:{querySelector:q=>q==='#account-lab'?root:null},module:{exports:{}},fetch(){throw Error('Network forbidden');},localStorage:{setItem(){throw Error('Storage forbidden');}}};
vm.runInNewContext(source,context,{timeout:1000});
assert.match(stateText.textContent,/DEMO-ALPHA: PREVIEW/);
assert.equal(toggles[0].checked,false);
buttons.find(b=>b.dataset.labTransition==='paused').emit('click');
assert.match(stateText.textContent,/PAUSED/);
toggles[0].checked=true;toggles[0].emit('change');
assert.equal(toggles[0].checked,true);
buttons.find(b=>b.dataset.labTransition==='locked').emit('click');
assert.equal(buttons.find(b=>b.dataset.labTransition==='preview').disabled,true);
reset.emit('click');
assert.match(stateText.textContent,/PREVIEW/);
assert.equal(toggles[0].checked,false);
selector.value='DEMO-BETA';selector.emit('change');
assert.match(stateText.textContent,/DEMO-BETA: PAUSED/);
console.log('NAY-005 browser state, privacy defaults, UI interactions and zero network/storage checks passed.');
