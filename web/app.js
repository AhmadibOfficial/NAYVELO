'use strict';
const planList = document.querySelector('#plan-list');
function make(tag, cls, value) {const n=document.createElement(tag);if(cls)n.className=cls;n.textContent=value;return n;}
async function loadPlans(){
  try {
    const response = await fetch('/api/v1/plans', {cache:'no-store'});
    if(!response.ok) throw new Error('Catalog temporarily unavailable');
    const data=await response.json();
    planList.replaceChildren();
    for (const plan of data.plans){
      const card=make('article','plan','');
      card.append(make('span','period',plan.period),make('h3','',plan.title),make('p','',plan.audience),make('span','tag','Concept · Not available to purchase'));
      planList.append(card);
    }
  } catch (_) {planList.replaceChildren(make('p','','Unable to load plan concepts. Run the local NAYVELO demo server.'));}
}
const checks=[...document.querySelectorAll('input.step')];
const result=document.querySelector('#readiness-result');
function renderReadiness(){
 const count=checks.filter(e=>e.checked).length;
 result.textContent = count===3 ? 'Checklist complete. This does not verify device compatibility; confirm with your manufacturer and a licensed operator.' : `${count} of 3 checks complete. This is guidance, not a compatibility verification.`;
}
checks.forEach(e=>e.addEventListener('change',renderReadiness));
document.querySelector('#reset-checks').addEventListener('click',()=>{checks.forEach(e=>e.checked=false);renderReadiness()});
renderReadiness();
