'use strict';
// NAY-006: one localhost GET for a fixed, synthetic fixture. No writes, storage,
// authentication, payment, analytics, subscription or carrier operations.
(function (root) {
  const FIELDS = ['schema_version','mode','source','currency','usage_unit','forecast_days',
    'sample_allowance_mib','sample_rate_kobo_per_gib','days','illustrative_history','disclaimer'];
  const matches = (value, fields) => value && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).sort().join('|') === [...fields].sort().join('|');
  const int = (v, low, high) => Number.isSafeInteger(v) && v >= low && v <= high;
  const estimateKobo = (mib, rateKobo) => {
    if (!int(mib,0,1000000) || !int(rateKobo,1,10000000)) throw Error('Invalid assumption');
    return Math.floor((mib * rateKobo + 512) / 1024);
  };
  const forecastMib = (days, horizon=30) => {
    if (!Array.isArray(days) || !days.length || days.length>31 || !int(horizon,1,31) ||
        !days.every(d=>int(d.usage_mib,0,1000000))) throw Error('Invalid usage');
    return Math.floor((days.reduce((a,d)=>a+d.usage_mib,0)*horizon+Math.floor(days.length/2))/days.length);
  };
  function verify(data) {
    if (!matches(data,FIELDS) || data.mode!=='SIMULATION_ONLY' ||
        data.source!=='FIXED_SYNTHETIC_FIXTURE' || data.schema_version!==1 || data.currency!=='NGN' ||
        data.usage_unit!=='MiB' || data.forecast_days!==30 || data.sample_allowance_mib!==8192 ||
        data.sample_rate_kobo_per_gib!==125000 || typeof data.disclaimer!=='string' || !data.disclaimer.startsWith('Fictional usage') ||
        !Array.isArray(data.days) || data.days.length!==7 || !Array.isArray(data.illustrative_history) ||
        data.illustrative_history.length!==3) throw Error('Untrusted or non-synthetic fixture');
    data.days.forEach((d,i)=>{
      if (!matches(d,['date','usage_mib']) || d.date!==`2026-10-${String(i+1).padStart(2,'0')}` ||
          !int(d.usage_mib,0,4096)) throw Error('Invalid daily fixture');
    });
    data.illustrative_history.forEach((h,i)=>{
      if (!matches(h,['period','usage_mib','estimate_kobo']) ||
          h.period!==`2026-${String(i+7).padStart(2,'0')}` || !int(h.usage_mib,0,100000) ||
          h.estimate_kobo!==estimateKobo(h.usage_mib,125000)) throw Error('Invalid historical fixture');
    });
    return data;
  }
  function calculate(data, rateNgn, capNgn) {
    verify(data);
    if (!int(rateNgn,500,5000) || !int(capNgn,1000,50000)) throw Error('Invalid controls');
    const used = data.days.reduce((n,d)=>n+d.usage_mib,0);
    const forecast = forecastMib(data.days);
    const expectedKobo = estimateKobo(forecast,rateNgn*100);
    return {used,remaining:Math.max(0,data.sample_allowance_mib-used),forecast,
      expectedKobo,overCap:expectedKobo>capNgn*100};
  }
  const money = k => `₦${(k/100).toLocaleString('en-NG',{minimumFractionDigits:2,maximumFractionDigits:2})}`;
  if (typeof module !== 'undefined' && module.exports) module.exports={verify,calculate,estimateKobo,forecastMib,money};
  if (!root || typeof document==='undefined') return;
  const $ = q=>root.querySelector(q);
  const status=$('[data-billing-status]'), output=$('[data-billing-results]');
  const rate=$('[data-billing-rate]'), cap=$('[data-billing-cap]'), history=$('[data-billing-history]');
  const bars=$('[data-billing-bars]'), reset=$('[data-billing-reset]');
  if (!status||!output||!rate||!cap||!history||!bars||!reset) return;
  let fixture=null;
  const el=(tag,txt)=>{const e=document.createElement(tag);e.textContent=txt;return e;};
  function render(){
    if(!fixture)return;
    const r=calculate(fixture,Number(rate.value),Number(cap.value));
    output.replaceChildren();bars.replaceChildren();history.replaceChildren();
    for(const [label,value] of [
      ['Seven fictional days',`${r.used.toLocaleString('en-NG')} MiB`],
      ['Remaining of fictional allowance',`${r.remaining.toLocaleString('en-NG')} MiB`],
      ['30-day usage projection',`${r.forecast.toLocaleString('en-NG')} MiB`],
      ['Illustrative 30-day expense',money(r.expectedKobo)]]){
      const item=el('div',label);item.className='billing-metric';
      const strong=el('strong',value);item.append(strong);output.append(item);
    }
    for(const d of fixture.days){
      const row=el('div','');row.className='billing-bar-row';
      const label=el('span',d.date.slice(-2));
      const track=el('div','');track.className='billing-track';
      const fill=el('div','');fill.className='billing-fill';
      fill.style.width=`${Math.round(100*d.usage_mib/4096)}%`;
      track.append(fill);row.append(label,track,el('span',`${d.usage_mib} MiB`));bars.append(row);
    }
    const table=el('table','');
    const caption=el('caption','Fictional historical usage estimates — no invoices or payments');
    const head=el('thead','');const hr=el('tr','');
    for(const s of ['Example period','Synthetic usage','Illustrative estimate']) {const th=el('th',s);th.scope='col';hr.append(th);}
    head.append(hr);const body=el('tbody','');
    for(const record of fixture.illustrative_history){
      const tr=el('tr','');
      for(const val of [record.period,`${record.usage_mib} MiB`,money(record.estimate_kobo)])tr.append(el('td',val));
      body.append(tr);
    }
    table.append(caption,head,body);history.append(table);
    status.textContent = r.overCap
      ? 'Illustrative 30-day projection exceeds your hypothetical budget. No charge will occur.'
      : 'Illustrative 30-day projection is within your hypothetical budget. No charge will occur.';
  }
  rate.addEventListener('change',render);cap.addEventListener('change',render);
  reset.addEventListener('click',()=>{rate.value='1250';cap.value='5000';render();});
  // Only allowed request is a local, read-only GET returning a fixed fictional fixture.
  fetch('/api/v1/demo-usage',{method:'GET',cache:'no-store',credentials:'omit'})
    .then(r=>{if(!r.ok)throw Error('Unavailable');return r.json();})
    .then(data=>{fixture=verify(data);rate.disabled=false;cap.disabled=false;reset.disabled=false;render();})
    .catch(()=>{fixture=null;rate.disabled=true;cap.disabled=true;reset.disabled=true;
      status.textContent='Fictional usage data unavailable. No charges, accounts or telecom connections are possible.';});
})(typeof document==='undefined'?null:document.querySelector('#billing-lab'));
