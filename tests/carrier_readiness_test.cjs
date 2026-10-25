'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const script=fs.readFileSync(path.resolve(__dirname,'../web/carrier_readiness.js'),'utf8');
const html=fs.readFileSync(path.resolve(__dirname,'../web/index.html'),'utf8');
const fixture=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../shared/carrier_readiness.json'),'utf8'));
assert.match(html,/id="carrier-readiness"/);
assert.match(html,/data-carrier-gates/);
assert.match(html,/data-carrier-status[^>]*role="status"/);
for (const bad of ['localStorage','sessionStorage','WebSocket','XMLHttpRequest','navigator.sendBeacon','navigator.credentials','document.cookie','indexedDB','/api/v1/activate','/api/v1/carrier/']) {
  assert.equal(script.includes(bad),false,'Unexpected persistence or remote action: '+bad);
}
function elem(){return {textContent:'',children:[],replaceChildren(...xs){this.children=xs;}};}
async function exercise(poison=false){
 const map={};for(const key of ['summary','boundaries','gates','status'])map['[data-carrier-'+key+']']=elem();
 let fetches=0;
 const doc={querySelector(s){return s==='#carrier-readiness'?{querySelector(k){return map[k];}}:null;},createElement:()=>elem()};
 const context={document:doc,fetch(url,options){fetches++;
   assert.equal(url,'/api/v1/demo-carrier-readiness');assert.deepEqual(Object.keys(options).sort(),['cache','credentials','method']);
   assert.equal(options.method,'GET');assert.equal(options.credentials,'omit');
   return Promise.resolve({ok:true,json:()=>Promise.resolve(poison?{...fixture,network_connected:true}:fixture)});
 }};
 vm.runInNewContext(script,context,{timeout:1000});
 await new Promise(resolve=>setImmediate(resolve));
 return {map,fetches};
}
(async()=>{
 const good=await exercise();assert.equal(good.fetches,1);
 assert.match(good.map['[data-carrier-summary]'].textContent,/0 connected interfaces/);
 assert.equal(good.map['[data-carrier-boundaries]'].children.length,5);
 assert.equal(good.map['[data-carrier-gates]'].children.length,8);
 const bad=await exercise(true);assert.equal(bad.map['[data-carrier-summary]'].textContent,'');
 assert.match(bad.map['[data-carrier-status]'].textContent,/unavailable/);
 console.log('NAY-008 browser-only read path, blocked gates and negative fixture tests passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
