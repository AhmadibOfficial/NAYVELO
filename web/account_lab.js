'use strict';
/* NAY-005: DEMO ALIASES ONLY. No fetch, XHR, storage, login, credentials or remote calls. */
(function () {
  const initial = Object.freeze({'DEMO-ALPHA':'preview', 'DEMO-BETA':'paused'});
  const allowed = Object.freeze({
    preview: Object.freeze(['paused','locked','closed']),
    paused: Object.freeze(['preview','locked','closed']),
    locked: Object.freeze([]),
    closed: Object.freeze([])
  });
  const privacyKeys = Object.freeze(['productAnalytics','productNews']);
  function create(alias = 'DEMO-ALPHA') {
    if (!Object.prototype.hasOwnProperty.call(initial, alias)) throw Error('Unknown fictional alias');
    return {alias, status:initial[alias], privacy:{productAnalytics:false, productNews:false}, events:[]};
  }
  function change(current, target) {
    if (!allowed[current.status]?.includes(target)) throw Error('Blocked demo transition');
    return {...current, status:target, events:[...current.events, `${current.status} → ${target}`].slice(-5)};
  }
  function updatePrivacy(current, key, value) {
    if (!privacyKeys.includes(key) || typeof value !== 'boolean') throw Error('Invalid preference');
    return {...current, privacy:{...current.privacy, [key]:value}};
  }
  function init(root, doc) {
    const selector = root.querySelector('[data-lab-alias]');
    const stateText = root.querySelector('[data-lab-state]');
    const status = root.querySelector('[data-lab-status]');
    const events = root.querySelector('[data-lab-events]');
    const reset = root.querySelector('[data-lab-reset]');
    const buttons = [...root.querySelectorAll('[data-lab-transition]')];
    const toggles = [...root.querySelectorAll('[data-lab-preference]')];
    let current = create();
    function render(message) {
      stateText.textContent = `Fictional ${current.alias}: ${current.status.toUpperCase()}`;
      status.textContent = message || 'Local demonstration only; nothing has been saved or sent.';
      events.textContent = current.events.length ? `Local sample transitions: ${current.events.join(', ')}` : 'No simulated transitions yet.';
      selector.value = current.alias;
      for (const b of buttons) b.disabled = !allowed[current.status].includes(b.dataset.labTransition);
      for (const t of toggles) t.checked = current.privacy[t.dataset.labPreference] === true;
    }
    selector.addEventListener('change', () => { current = create(selector.value); render('Switched fictional example. Prior local choices discarded.'); });
    for (const b of buttons) b.addEventListener('click', () => {
      try {current = change(current, b.dataset.labTransition);render('Only the fictional account state changed in memory.');}
      catch (_) {render('This transition is prohibited by the local demo policy.');}
    });
    for (const t of toggles) t.addEventListener('change', () => {
      current = updatePrivacy(current, t.dataset.labPreference, !!t.checked);
      render('Preference changed on this screen only; no tracking or messaging occurs.');
    });
    reset.addEventListener('click', () => {current = create(current.alias);render('Demo reset: status and optional preferences restored to safe defaults.');});
    render();
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {create,change,updatePrivacy,allowed,initial};
  if (typeof document !== 'undefined') {
    const root = document.querySelector('#account-lab');
    if (root) init(root,document);
  }
})();
