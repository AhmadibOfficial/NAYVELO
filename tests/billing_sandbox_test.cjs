'use strict';
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../web/billing_sandbox.js'),'utf8');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../shared/synthetic_billing.json'),'utf8'));
const html=fs.readFileSync(path.join(__dirname,'../web/index.html'),'utf8');
const {verify,calculate,estimateKobo,forecastMib}=require('../web/billing_sandbox.js');
assert.deepEqual(verify(fixture),fixture);
assert.equal(estimateKobo(1024,125000),125000);
assert.equal(estimateKobo(1,125000),122);
assert.equal(forecastMib([{usage_mib:100}],30),3000);
assert.equal(calculate(fixture,1250,5000).used,3936);
assert.equal(calculate(fixture,5000,1000).overCap,true);
assert.throws(()=>calculate(fixture,-5,5000),/Invalid/);
assert.throws(()=>verify({...fixture,mode:'PRODUCTION'}),/Untrusted/);
assert.throws(()=>verify({...fixture,phone:'REDUCTED'}),/Untrusted/);
assert.throws(()=>verify({...fixture,days:[...fixture.days,{date:'2026-10-08',usage_mib:5}]}),/Untrusted/);
assert.match(html,/id="billing-lab"/);
assert.match(html,/data-billing-results/);
assert.match(html,/data-billing-history/);
assert.match(html,/aria-live="polite"/);
for(const forbidden of ['XMLHttpRequest','localStorage','sessionStorage','navigator.sendBeacon','WebSocket','indexedDB','/api/v1/payments','/api/v1/activate','/api/v1/subscribe','/api/v1/checkout']){
  assert.equal(source.includes(forbidden),false,`Side effect prohibited: ${forbidden}`);
}
class E{
  constructor(){this.listeners={};this.value='';this.disabled=true;this.textContent='';this.children=[];this.style={};}
  addEventListener(type,fn){this.listeners[type]=fn;}
  emit(type){this.listeners[type]();}
  append(...children){this.children.push(...children);}
  replaceChildren(...items){this.children=items;}
}
const elements={};
for(const id of ['status','results','rate','cap','history','bars','reset']) elements[`[data-billing-${id}]`]=new E();
const root={querySelector(q){return elements[q]||null;}};
elements['[data-billing-rate]'].value='1250';
elements['[data-billing-cap]'].value='5000';
const requested=[];
const context={
 document:{querySelector:q=>q==='#billing-lab'?root:null,createElement:()=>new E()},
 fetch(url,opts){requested.push({url,opts});return Promise.resolve({ok:true,json:()=>Promise.resolve(fixture)});},
 localStorage:{setItem(){throw Error('storage forbidden');}},
 XMLHttpRequest:function(){throw Error('network forbidden');},
};
vm.runInNewContext(source,context,{timeout:1000});
setImmediate(()=>{
  try{
    assert.equal(requested.length,1);
    assert.equal(requested[0].url,'/api/v1/demo-usage');
    assert.equal(requested[0].opts.method,'GET');
    assert.equal(requested[0].opts.credentials,'omit');
    assert.equal(elements['[data-billing-results]'].children.length,4);
    assert.equal(elements['[data-billing-bars]'].children.length,7);
    assert.equal(elements['[data-billing-history]'].children.length,1);
    elements['[data-billing-rate]'].value='5000';
    elements['[data-billing-cap]'].value='1000';
    elements['[data-billing-rate]'].emit('change');
    assert.match(elements['[data-billing-status]'].textContent,/exceeds/);
    elements['[data-billing-reset]'].emit('click');
    assert.equal(elements['[data-billing-rate]'].value,'1250');
    assert.equal(elements['[data-billing-cap]'].value,'5000');
    console.log('NAY-006 browser projection, historical examples, read-only GET and privacy gates passed.');
  }catch(err){console.error(err);process.exitCode=1;}
});
// An unavailable/poisoned local fixture must disable the controls, never fall back
// to a fabricated real bill or attempt a second route.
const broken={...fixture, subscriber_id:'disallowed'};
const failed = {};
for (const id of ['status','results','rate','cap','history','bars','reset']) failed[`[data-billing-${id}]`]=new E();
failed['[data-billing-rate]'].value='1250';
failed['[data-billing-cap]'].value='5000';
let reads=0;
vm.runInNewContext(source,{
  document:{querySelector:q=>q==='#billing-lab'?{querySelector:id=>failed[id]}:null,createElement:()=>new E()},
  fetch(url,opts){reads++;assert.equal(url,'/api/v1/demo-usage');assert.equal(opts.method,'GET');
    return Promise.resolve({ok:true,json:()=>Promise.resolve(broken)});},
},{timeout:1000});
setImmediate(()=>{
  try{
    assert.equal(reads,1);
    assert.equal(failed['[data-billing-rate]'].disabled,true);
    assert.equal(failed['[data-billing-cap]'].disabled,true);
    assert.match(failed['[data-billing-status]'].textContent,/unavailable/);
  }catch(err){console.error(err);process.exitCode=1;}
});
