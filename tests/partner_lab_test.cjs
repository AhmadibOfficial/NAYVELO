'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../shared/partner_lab.json'),'utf8'));
const expected=['ACCEPTED','REJECTED_TIMEOUT','REJECTED_DUPLICATE','REJECTED_SEQUENCE',
  'REJECTED_CORRELATION','REJECTED_SCHEMA','REJECTED_PARTNER_ERROR','REJECTED_SCHEMA','REJECTED_NO_RESPONSE'];
const report={schema_version:1,mode:'SIMULATION_ONLY',integration_state:'NOT_AUTHORIZED',
  network_connected:false,payments_enabled:false,real_subscribers_enabled:false,
  activation_enabled:false,certification_status:'NOT_VERIFIED',
  disclaimer:fixture.disclaimer,scenario_count:9,
  verdict_meaning:'ACCEPTED describes a fixed fictional response only; never partner certification.',
  scenarios:fixture.scenarios.map((s,i)=>({code:s.code,label:s.label,
    explanation:s.explanation,outcome:expected[i],accepted:i===0}))};
const script=fs.readFileSync(path.join(__dirname,'../web/partner_lab.js'),'utf8');
const exported={exports:{}};
vm.runInNewContext(script,{module:exported,document:{querySelector:()=>null}});
const {validate}=exported.exports;
assert.equal(validate(report).scenario_count,9);
for(const bad of [{...report,network_connected:true}, {...report,certification_status:'APPROVED'},
  {...report,subscriber_id:'real'}, {...report,scenarios:[...report.scenarios.slice(0,8)]},
  {...report,scenarios:report.scenarios.map((s,i)=>i===0?{...s,accepted:false}:s)}]) {
  assert.throws(()=>validate(bad));
}
class Node {
  constructor(){this.textContent='';this.value='';this.disabled=false;this.children=[];this.handlers={};}
  replaceChildren(...items){this.children=items;}
  append(...items){this.children.push(...items);}
  addEventListener(event,handler){this.handlers[event]=handler;}
}
const map=new Map([
  ['[data-partner-select]',new Node()],['[data-partner-result]',new Node()],
  ['[data-partner-status]',new Node()],
]);
const root={querySelector:s=>map.get(s)};
let fetchCalls=0, args=null;
const sandbox={document:{querySelector:s=>s==='#partner-lab'?root:null,
  createElement:()=>new Node()},module:{exports:{}},
  fetch:(...params)=>{fetchCalls++;args=params;return Promise.resolve({ok:true,json:()=>Promise.resolve(report)});}};
vm.runInNewContext(script,sandbox);
setImmediate(()=>{
  try {
    assert.equal(fetchCalls,1);
    assert.equal(args[0],'/api/v1/demo-partner-lab');
    assert.equal(args[1].method,'GET');
    assert.equal(args[1].credentials,'omit');
    const selector=map.get('[data-partner-select]');
    assert.equal(selector.disabled,false);
    assert.equal(selector.children.length,9);
    assert.equal(map.get('[data-partner-result]').children[0].textContent,'ACCEPTED');
    selector.value='pii_injection';selector.handlers.change();
    assert.equal(map.get('[data-partner-result]').children[0].textContent,'REJECTED_SCHEMA');
    assert.match(map.get('[data-partner-status]').textContent,/8 of 9/);
    console.log('NAY-009: strict JS validation, keyboard-native selector, and only local demo GET passed.');
  }catch(e){console.error(e);process.exitCode=1;}
});
