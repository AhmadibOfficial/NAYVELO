'use strict';
// NAY-007 publicly visible, fictional role demonstration only. Never an admin security boundary.
(function (root) {
  const keys = (o, expect) => o && typeof o==='object' && !Array.isArray(o) &&
      Object.keys(o).sort().join('|')===[...expect].sort().join('|');
  const integer = (v, min, max) => Number.isSafeInteger(v) && v>=min && v<=max;
  const codes=['daily-flex','smart-weekly','monthly-plus','family-connect','business-pro','global-roam'];
  const ops=['documentation','support','partnership'];
  const opLabels=['Readiness guide review','Simulated support queue','Carrier integration prerequisite'];
  const roles=['viewer','analyst','operator'];
  function validate(data) {
    if (!keys(data,['schema_version','mode','source','period','plan_concepts','weeks','plan_interest','demo_operations','disclaimer']) ||
      data.schema_version!==1 || data.mode!=='SIMULATION_ONLY' || data.source!=='PUBLIC_FIXED_FICTIONAL_DATA' ||
      data.period!=='Four invented example weeks; not current activity' || data.plan_concepts!==6 ||
      typeof data.disclaimer!=='string' || !data.disclaimer.startsWith('Fictional administrative exercise only.') ||
      !data.disclaimer.includes('NOT authentication') ||
      !Array.isArray(data.weeks) || data.weeks.length!==4 ||
      !Array.isArray(data.plan_interest) || data.plan_interest.length!==6 ||
      !Array.isArray(data.demo_operations) || data.demo_operations.length!==3) throw Error('Unsafe synthetic analytics fixture');
    data.weeks.forEach((w,i)=>{
      if(!keys(w,['label','visits','onboarding_previews','help_requests'])||w.label!==`Example week ${i+1}`||
        !['visits','onboarding_previews','help_requests'].every(k=>integer(w[k],0,10000))||
        w.onboarding_previews>w.visits||w.help_requests>w.visits) throw Error('Invalid fictional week');
    });
    data.plan_interest.forEach((p,i)=>{
      if(!keys(p,['code','count'])||p.code!==codes[i]||!integer(p.count,0,10000))throw Error('Invalid plan concepts');
    });
    data.demo_operations.forEach((o,i)=>{
      if(!keys(o,['code','label','state'])||o.code!==ops[i]||o.label!==opLabels[i]||
        o.state!==(i===2?'not_authorized':'illustrative_only'))throw Error('Unsafe fictional operations');
    });
    return data;
  }
  function roleView(data,role) {
    validate(data);
    if(!roles.includes(role))throw Error('Unknown mock role');
    const summary={fictional_visits:data.weeks.reduce((n,w)=>n+w.visits,0),
      fictional_previews:data.weeks.reduce((n,w)=>n+w.onboarding_previews,0),plan_concepts:6};
    const view={role,summary,mode:'SIMULATION_ONLY',role_simulated:true};
    if(role!=='viewer'){
      view.weekly_trends=data.weeks;
      view.plan_interest=data.plan_interest;
    }
    if(role==='operator')view.demo_operations=data.demo_operations;
    return view;
  }
  if(typeof module!=='undefined' && module.exports)module.exports={validate,roleView};
  if(!root || typeof document==='undefined')return;
  const get=q=>root.querySelector(q);
  const role=get('[data-admin-role]'),metrics=get('[data-admin-metrics]'),
    trends=get('[data-admin-trends]'),plans=get('[data-admin-plans]'),
    operations=get('[data-admin-operations]'),status=get('[data-admin-status]');
  if(!role||!metrics||!trends||!plans||!operations||!status)return;
  let fixture=null;
  const el=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n;};
  function render(){
    if(!fixture)return;
    const view=roleView(fixture,role.value);
    metrics.replaceChildren();trends.replaceChildren();plans.replaceChildren();operations.replaceChildren();
    for(const [label,v] of [['Example visits',view.summary.fictional_visits],
      ['Onboarding previews',view.summary.fictional_previews],['Unpriced plan concepts',view.summary.plan_concepts]]){
      const card=el('div',label);card.className='admin-metric';card.append(el('strong',String(v)));metrics.append(card);
    }
    if(view.weekly_trends){
      trends.append(el('h3','Synthetic weekly activity'));
      const graph=el('div','');graph.className='admin-bars';
      const max=Math.max(...view.weekly_trends.map(w=>w.visits),1);
      for(const w of view.weekly_trends){
        const row=el('div','');row.className='admin-row';
        const track=el('div','');track.className='admin-track';
        const fill=el('div','');fill.className='admin-fill';fill.style.width=`${Math.round(100*w.visits/max)}%`;
        track.append(fill);row.append(el('span',w.label),track,el('span',String(w.visits)));graph.append(row);
      }
      trends.append(graph);
      const table=el('table','');table.className='admin-table';
      const caption=el('caption','Fictional weekly trend totals; no actual visitors');table.append(caption);
      const head=el('thead','');const hr=el('tr','');
      for(const label of ['Example week','Preview actions','Help examples']) {const th=el('th',label);th.scope='col';hr.append(th);}
      head.append(hr);table.append(head);const tbody=el('tbody','');
      for(const w of view.weekly_trends){const tr=el('tr','');tr.append(el('td',w.label),el('td',String(w.onboarding_previews)),el('td',String(w.help_requests)));tbody.append(tr);}
      table.append(tbody);trends.append(table);
      plans.append(el('h3','Fictional plan interest, not subscribers'));
      for(const p of view.plan_interest){const item=el('p',`${p.code}: ${p.count} invented expressions of interest`);item.className='admin-label';plans.append(item);}
    } else {
      trends.append(el('p','Viewer role: synthetic trends hidden in this demonstration.'));
    }
    if(view.demo_operations){
      operations.append(el('h3','Read-only operations scenario'));
      for(const op of view.demo_operations)operations.append(el('p',`${op.label}: ${op.state.replaceAll('_',' ')}`));
    }
    status.textContent=`${view.role} simulation selected. Public fictional data only; this is NOT a login or permission grant.`;
  }
  role.addEventListener('change',()=>{
    if(!roles.includes(role.value)) {role.value='viewer';}
    render();
  });
  // No accounts, tokens, browser storage, telemetry, mutations, external fetches, or credential forwarding.
  fetch('/api/v1/demo-admin',{method:'GET',credentials:'omit',cache:'no-store'})
    .then(r=>{if(!r.ok)throw Error('Demo unavailable');return r.json();})
    .then(raw=>{fixture=validate(raw);role.disabled=false;role.value='viewer';render();})
    .catch(()=>{fixture=null;role.disabled=true;metrics.replaceChildren();trends.replaceChildren();plans.replaceChildren();operations.replaceChildren();
      status.textContent='Synthetic management demo unavailable. No admin or subscriber access is possible.';});
})(typeof document==='undefined'?null:document.querySelector('#admin-lab'));
