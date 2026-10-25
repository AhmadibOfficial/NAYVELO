'use strict';
// PUBLIC, READ-ONLY DESIGN DEMONSTRATION — NEVER a carrier SDK.
(function () {
  const root = typeof document !== 'undefined' ? document.querySelector('#carrier-readiness') : null;
  if (!root) return;
  const summary = root.querySelector('[data-carrier-summary]');
  const boundaries = root.querySelector('[data-carrier-boundaries]');
  const gates = root.querySelector('[data-carrier-gates]');
  const status = root.querySelector('[data-carrier-status]');
  function exact(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error('Invalid readiness fixture');
    const keys = ['schema_version','mode','source','integration_state','network_connected',
      'esim_provisioning_enabled','real_subscribers_enabled','payments_enabled',
      'description','boundaries','certification_gates','disclaimer'];
    if (Object.keys(value).sort().join('|') !== keys.sort().join('|') ||
        value.schema_version !== 1 || value.mode !== 'SIMULATION_ONLY' ||
        value.source !== 'PUBLIC_FIXED_INTERFACE_DESIGN' || value.integration_state !== 'NOT_AUTHORIZED' ||
        value.network_connected !== false || value.esim_provisioning_enabled !== false ||
        value.real_subscribers_enabled !== false || value.payments_enabled !== false) throw Error('Unsafe readiness fixture');
    const codes = ['network_access','esim_provisioning','service_management','usage_reporting','subscriber_registration'];
    const reqs = ['ncc_licensing','wholesale_contract','rsp_partner','subscriber_compliance','security_assurance','interoperability','service_operations','commercial_assurance'];
    if (!Array.isArray(value.boundaries) || value.boundaries.length !== codes.length ||
        !Array.isArray(value.certification_gates) || value.certification_gates.length !== reqs.length) throw Error('Unsafe checklist length');
    for (let i=0;i<codes.length;i++) {
      const item = value.boundaries[i];
      if (!item || Object.keys(item).sort().join('|') !== ['code','detail','label','state'].join('|') ||
          item.code !== codes[i] || item.state !== 'BLOCKED' || typeof item.label !== 'string' ||
          typeof item.detail !== 'string') throw Error('Unexpected network status');
    }
    for (let i=0;i<reqs.length;i++) {
      const item = value.certification_gates[i];
      if (!item || Object.keys(item).sort().join('|') !== 'code|label|status' ||
          item.code !== reqs[i] || item.status !== 'NOT_VERIFIED' || typeof item.label !== 'string') throw Error('Unexpected evidence status');
    }
    if (typeof value.description !== 'string' || !value.description.startsWith('Architecture exercise only.') ||
        typeof value.disclaimer !== 'string' || !value.disclaimer.startsWith('PUBLIC DESIGN DEMONSTRATION ONLY.')) throw Error('Missing warning');
    return value;
  }
  function paragraph(className, text) {
    const p = document.createElement('p'); p.className=className; p.textContent=text; return p;
  }
  function render(data) {
    const x=exact(data);
    summary.textContent='0 connected interfaces · 0 verified gates · SIMULATION_ONLY';
    boundaries.replaceChildren(...x.boundaries.map(item => paragraph('carrier-item', `${item.label} — BLOCKED. ${item.detail}`)));
    gates.replaceChildren(...x.certification_gates.map(item => paragraph('carrier-item', `${item.label} — NOT VERIFIED`)));
    status.textContent='Read-only contract demonstration. Nothing is licensed, certified or connected.';
  }
  fetch('/api/v1/demo-carrier-readiness', {method:'GET',credentials:'omit',cache:'no-store'})
    .then(response => {if (!response.ok) throw Error('Fixture unavailable'); return response.json();})
    .then(render)
    .catch(() => {status.textContent='Carrier contract demonstration unavailable. No network action is possible.';});
  if (typeof module !== 'undefined' && module.exports) module.exports={exact};
}());
