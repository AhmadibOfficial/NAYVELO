'use strict';
// This read-only interface never calls a partner. Only the local demo GET is permitted.
(function () {
  const codes=['nominal_ack','timeout','duplicate_response','out_of_order','mismatched_tag',
    'schema_drift','partner_error','pii_injection','empty_response'];
  const outcomes=['ACCEPTED','REJECTED_TIMEOUT','REJECTED_DUPLICATE','REJECTED_SEQUENCE',
    'REJECTED_CORRELATION','REJECTED_SCHEMA','REJECTED_PARTNER_ERROR',
    'REJECTED_SCHEMA','REJECTED_NO_RESPONSE'];
  const warning='EDUCATIONAL OFFLINE CONTRACT LAB ONLY. All responses are fictional; no carrier, eSIM provisioning, payment, identity or external partner is connected or certified.';
  function validate(x) {
    if (!x || typeof x !== 'object' || Array.isArray(x)) throw Error('Invalid partner laboratory report');
    const required=['schema_version','mode','integration_state','network_connected','payments_enabled',
      'real_subscribers_enabled','activation_enabled','certification_status','disclaimer','scenario_count',
      'scenarios','verdict_meaning'];
    if (Object.keys(x).sort().join('|') !== required.sort().join('|') ||
      x.schema_version !== 1 || x.mode !== 'SIMULATION_ONLY' ||
      x.integration_state !== 'NOT_AUTHORIZED' || x.network_connected !== false ||
      x.payments_enabled !== false || x.real_subscribers_enabled !== false ||
      x.activation_enabled !== false || x.certification_status !== 'NOT_VERIFIED' ||
      x.disclaimer !== warning || x.scenario_count !== 9 ||
      x.verdict_meaning !== 'ACCEPTED describes a fixed fictional response only; never partner certification.' ||
      !Array.isArray(x.scenarios) || x.scenarios.length !== 9) throw Error('Unsafe partner laboratory report');
    x.scenarios.forEach((s,i)=>{
      if (!s || typeof s !== 'object' || Array.isArray(s) ||
        Object.keys(s).sort().join('|') !== 'accepted|code|explanation|label|outcome' ||
        s.code !== codes[i] || s.outcome !== outcomes[i] ||
        s.accepted !== (i===0) || typeof s.label !== 'string' ||
        typeof s.explanation !== 'string' || s.explanation.length < 30 ||
        s.explanation.length > 180 || /https?:|@|token=|nin=|eid=/i.test(s.explanation)) {
        throw Error('Unsafe partner response');
      }
    });
    return x;
  }
  const root=typeof document !== 'undefined' ? document.querySelector('#partner-lab') : null;
  if (!root) {if (typeof module!=='undefined' && module.exports) module.exports={validate};return;}
  const choose=root.querySelector('[data-partner-select]');
  const output=root.querySelector('[data-partner-result]');
  const status=root.querySelector('[data-partner-status]');
  let data=null;
  function render(code) {
    const selected=data?.scenarios.find(s=>s.code===code);
    if (!selected) {output.textContent='No valid fictional scenario selected.';return;}
    output.replaceChildren();
    const strong=document.createElement('strong');strong.textContent=selected.outcome;
    const detail=document.createElement('p');detail.textContent=selected.explanation;
    const disclaimer=document.createElement('p');disclaimer.textContent=
      selected.accepted ? 'Only a fictional contract response was accepted; no real carrier verified.' :
        'Rejected safely. No retry, registration, network or payment action occurred.';
    output.append(strong,detail,disclaimer);
    status.textContent=`Scenario ${data.scenarios.indexOf(selected)+1} of ${data.scenario_count}: ${selected.label}`;
  }
  choose.disabled=true;
  fetch('/api/v1/demo-partner-lab',{method:'GET',credentials:'omit',cache:'no-store'})
    .then(r=>{if (!r.ok)throw Error('Offline lab unavailable');return r.json();})
    .then(v=>{
      data=validate(v);
      choose.replaceChildren(...data.scenarios.map(s=>{
        const option=document.createElement('option');option.value=s.code;option.textContent=s.label;return option;
      }));
      choose.disabled=false;choose.value=codes[0];render(codes[0]);
    })
    .catch(()=>{
      choose.disabled=true;
      status.textContent='Local demonstration unavailable. All actual carrier operations remain disabled.';
      output.textContent='No integration or certification can be inferred.';
    });
  choose.addEventListener('change',()=>render(choose.value));
  if (typeof module!=='undefined' && module.exports) module.exports={validate};
}());
