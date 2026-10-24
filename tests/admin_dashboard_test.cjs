'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'../web/admin_dashboard.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'../web/index.html'),'utf8');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../shared/synthetic_admin.json'),'utf8'));
const {validate,roleView}=require('../web/admin_dashboard.js');
assert.equal(validate(fixture).mode,'SIMULATION_ONLY');
assert.equal(roleView(fixture,'viewer').summary.fictional_visits,599);
assert.equal(roleView(fixture,'viewer').weekly_trends,undefined);
assert.equal(roleView(fixture,'analyst').weekly_trends.length,4);
assert.equal(roleView(fixture,'analyst').demo_operations,undefined);
assert.equal(roleView(fixture,'operator').demo_operations[2].state,'not_authorized');
assert.throws(()=>roleView(fixture,'superuser'),/Unknown mock role/);
assert.throws(()=>validate({...fixture,phone_number:'09000000000'}),/Unsafe/);
assert.throws(()=>validate({...fixture,mode:'LIVE'}),/Unsafe/);
assert.throws(()=>validate({...fixture,weeks:[...fixture.weeks,{label:'Extra'}]}),/Unsafe/);
assert.throws(()=>validate({...fixture,plan_interest:[{...fixture.plan_interest[0],subscriber_id:'x'},...fixture.plan_interest.slice(1)]}),/Invalid/);
assert.match(html,/id="admin-lab"/);
assert.match(html,/data-admin-role/);
assert.match(html,/data-admin-status[^>]*role="status"/);
for(const forbidden of ['localStorage','sessionStorage','navigator.sendBeacon','WebSocket','XMLHttpRequest','indexedDB','document.cookie','/api/v1/payments','/api/v1/activate']) {
  assert.equal(code.includes(forbidden),false,`Unexpected side-effect call: ${forbidden}`);
}
class E{
  constructor(){this.disabled=true;this.textContent='';this.value='viewer';this.children=[];this.listeners={};this.style={};}
  addEventListener(t,f){this.listeners[t]=f;}
  fire(t){this.listeners[t]();}
  append(...items){this.children.push(...items);}
  replaceChildren(...items){this.children=items;}
}
function make(bad=false){
  const e={};
  for(const n of ['role','metrics','trends','plans','operations','status'])e[`[data-admin-${n}]`]=new E();
  const root={querySelector:s=>e[s]};let reads=0;
  const ctx={document:{querySelector:s=>s==='#admin-lab'?root:null,createElement:()=>new E()},
    fetch(url,opt){reads++;assert.equal(url,'/api/v1/demo-admin');assert.deepEqual(Object.keys(opt).sort(),['cache','credentials','method']);assert.equal(opt.method,'GET');assert.equal(opt.credentials,'omit');
      return Promise.resolve({ok:true,json:()=>Promise.resolve(bad?{...fixture,credentials:'unsafe'}:fixture)});}};
  vm.runInNewContext(code,ctx,{timeout:1500});
  return {e,reads:()=>reads};
}
const pass=make(),deny=make(true);
setImmediate(()=>{
  try{
    assert.equal(pass.reads(),1);
    const p=pass.e;
    assert.equal(p['[data-admin-role]'].disabled,false);
    assert.equal(p['[data-admin-metrics]'].children.length,3);
    assert.equal(p['[data-admin-trends]'].children.length,1);
    p['[data-admin-role]'].value='analyst';p['[data-admin-role]'].fire('change');
    assert.ok(p['[data-admin-trends]'].children.length>=2);
    assert.ok(p['[data-admin-plans]'].children.length>=7);
    p['[data-admin-role]'].value='operator';p['[data-admin-role]'].fire('change');
    assert.equal(p['[data-admin-operations]'].children.length,4);
    p['[data-admin-role]'].value='root';p['[data-admin-role]'].fire('change');
    assert.equal(p['[data-admin-role]'].value,'viewer');
    assert.equal(deny.reads(),1);
    assert.equal(deny.e['[data-admin-role]'].disabled,true);
    assert.match(deny.e['[data-admin-status]'].textContent,/unavailable/);
    console.log('NAY-007 synthetic browser role scopes, validation, offline privacy and read-only GET passed.');
  }catch(e){console.error(e);process.exitCode=1;}
});
