'use strict';
/* NAY-004: entirely in-memory education; no identifiers, registration, telemetry or networking. */
(function () {
  const STEPS = ['platform', 'setting', 'unlocked'];
  const OPTIONS = {
    platform: [
      ['iphone', 'iPhone (iOS)'], ['android', 'Android'], ['unsure', 'Not sure']
    ],
    setting: [
      ['yes', 'Yes, I can see an eSIM option'],
      ['no', 'No, I cannot see one'],
      ['unsure', 'I have not checked']
    ],
    unlocked: [
      ['yes', 'Yes, it is network-unlocked'],
      ['no', 'No, it may be carrier-locked'],
      ['unsure', 'I do not know']
    ]
  };
  const QUESTIONS = {
    platform: 'Which type of phone do you use?',
    setting: 'Can you find an option to add an eSIM in Settings?',
    unlocked: 'Is your phone unlocked for use with other network operators?'
  };
  const GUIDES = {
    iphone: 'On iPhone, look in Settings → Cellular or Mobile Data → Add eSIM. You can check Carrier Lock in Settings → General → About. Regional models differ.',
    android: 'On Samsung Galaxy, look in Settings → Connections → SIM manager → Add eSIM. On Pixel, use Settings → Network & internet → SIMs → Add SIM. Android menus vary by manufacturer.',
    unsure: 'Identify the manufacturer and model using your own Settings app. Do not enter, copy, photograph, or share IMEI or EID with this guide.'
  };
  function evaluate(answers) {
    const a = answers || {};
    if (!STEPS.every((step) => OPTIONS[step].some(([value]) => value === a[step]))) {
      return {level: 'incomplete', title: 'Complete the guide', message: 'Answer each question for educational next steps.'};
    }
    if (a.setting === 'no') {
      return {level: 'review', title: 'Check manufacturer guidance', message: 'You did not find an eSIM setting. Your model or regional variant might not support eSIM; manufacturer verification is needed.'};
    }
    if (a.unlocked === 'no') {
      return {level: 'review', title: 'Ask about network unlocking', message: 'A carrier restriction may prevent service with a different operator. Ask your current carrier or seller before making plans.'};
    }
    if (a.setting === 'yes' && a.unlocked === 'yes') {
      return {level: 'potential', title: 'Potentially ready for further verification', message: 'Your answers suggest eSIM might be available. This is not a compatibility check. Confirm your exact regional model and future licensed carrier eligibility.'};
    }
    return {level: 'unknown', title: 'More checking is needed', message: 'Your answers are not enough to assess readiness. Check manufacturer information and ask a licensed operator.'};
  }
  function init(root, doc) {
    const panel = root.querySelector('[data-wizard-panel]');
    const status = root.querySelector('[data-wizard-status]');
    const progress = root.querySelector('[data-wizard-progress]');
    const back = root.querySelector('[data-wizard-back]');
    const next = root.querySelector('[data-wizard-next]');
    const reset = root.querySelector('[data-wizard-reset]');
    const state = {step: 0, answers: {}};
    function el(tag, text, className) {
      const node = doc.createElement(tag);
      if (text !== null) node.textContent = text;
      if (className) node.className = className;
      return node;
    }
    function render() {
      const finished = state.step === STEPS.length;
      panel.replaceChildren();
      progress.textContent = finished ? 'Step 4 of 4 · Educational summary' : `Step ${state.step + 1} of 4`;
      back.hidden = state.step === 0;
      next.hidden = finished;
      reset.hidden = !finished && state.step === 0 && Object.keys(state.answers).length === 0;
      if (finished) {
        const outcome = evaluate(state.answers);
        panel.append(el('h4', outcome.title), el('p', outcome.message));
        panel.append(el('p', 'NAYVELO is a simulator. No active eSIM service, activation, purchases, or confirmed carrier compatibility.', 'wizard-disclaimer'));
        status.textContent = `Educational result: ${outcome.title}. Not verified.`;
        panel.querySelector('h4').setAttribute('tabindex', '-1');
        panel.querySelector('h4').focus();
        return;
      }
      const key = STEPS[state.step];
      const fieldset = doc.createElement('fieldset');
      const legend = el('legend', QUESTIONS[key]);
      legend.setAttribute('tabindex', '-1');
      fieldset.append(legend);
      for (const [value, label] of OPTIONS[key]) {
        const row = el('label', null, 'wizard-choice');
        const radio = doc.createElement('input');
        radio.type = 'radio';
        radio.name = 'esim-' + key;
        radio.value = value;
        radio.checked = state.answers[key] === value;
        radio.addEventListener('change', () => { state.answers[key] = value; next.disabled = false; status.textContent = 'Option selected. Continue when ready.'; });
        row.append(radio, el('span', label));
        fieldset.append(row);
      }
      panel.append(fieldset);
      if (key === 'platform' && state.answers.platform && GUIDES[state.answers.platform]) {
        panel.append(el('p', GUIDES[state.answers.platform], 'wizard-hint'));
      }
      if (key === 'setting') panel.append(el('p', GUIDES[state.answers.platform] || GUIDES.unsure, 'wizard-hint'));
      if (key === 'unlocked') panel.append(el('p', 'Never enter your IMEI, EID, serial number, phone number or national identity number here.', 'wizard-hint'));
      next.disabled = !state.answers[key];
      next.textContent = state.step === STEPS.length - 1 ? 'Show guidance' : 'Continue';
      status.textContent = 'This guide does not verify compatibility or collect device information.';
      legend.focus();
    }
    next.addEventListener('click', () => {
      if (state.step >= STEPS.length || !state.answers[STEPS[state.step]]) return;
      state.step += 1;
      render();
    });
    back.addEventListener('click', () => { if (state.step > 0) { state.step -= 1; render(); } });
    reset.addEventListener('click', () => { state.step = 0; state.answers = {}; render(); });
    render();
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {evaluate, STEPS, OPTIONS};
  if (typeof document !== 'undefined') {
    const root = document.querySelector('#esim-wizard');
    if (root) init(root, document);
  }
})();
