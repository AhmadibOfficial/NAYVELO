'use strict';
// Deliberately isolated from API clients and persistence: synthetic choices only.
(() => {
  const get = id => document.getElementById(id);
  const flow = get('onboarding-flow');
  const heading = get('onboarding-step');
  const content = get('onboarding-content');
  const back = get('onboarding-back');
  const next = get('onboarding-next');
  let step = 0;
  let acknowledged = false;
  let preference = 'Explore plans';
  const preferences = ['Explore plans', 'Learn about eSIM'];
  function element(tag, text) {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  }
  function render(moveFocus = true) {
    content.replaceChildren();
    get('onboarding-progress').textContent = `Step ${step + 1} of 3 — simulation only`;
    heading.textContent = ['Understand the demo', 'Choose a demo interest', 'Simulation complete'][step];
    back.disabled = step === 0;
    next.hidden = step === 2;
    next.disabled = step === 0 && !acknowledged;
    next.textContent = step === 1 ? 'Complete simulation' : 'Continue simulation';
    if (step === 0) {
      const label = element('label', '');
      const check = element('input', '');
      check.type = 'checkbox';
      check.checked = acknowledged;
      check.addEventListener('change', () => {
        acknowledged = check.checked;
        next.disabled = !acknowledged;
      });
      label.append(check, element('span', 'I understand this is a local simulation and creates no subscriber account or network service.'));
      content.append(label);
    } else if (step === 1) {
      const group = element('fieldset', '');
      group.append(element('legend', 'What would you like to explore? (demo only)'));
      for (const choice of preferences) {
        const label = element('label', '');
        const radio = element('input', '');
        radio.type = 'radio';
        radio.name = 'demo-interest';
        radio.value = choice;
        radio.checked = preference === choice;
        radio.addEventListener('change', () => { if (radio.checked) preference = choice; });
        label.append(radio, element('span', choice));
        group.append(label);
      }
      content.append(group);
    } else {
      content.append(element('p', `Demo interest: ${preference}. No subscriber account was created. No registration or telecom request was sent. No payment, number assignment or network activation occurred.`));
    }
    if (moveFocus) heading.focus();
  }
  back.addEventListener('click', () => { if (step > 0) { step--; render(); } });
  next.addEventListener('click', () => {
    if (!acknowledged || step >= 2) return;
    step++;
    render();
  });
  get('onboarding-reset').addEventListener('click', () => {
    step = 0;
    acknowledged = false;
    preference = preferences[0];
    render();
  });
  render(false);
  flow.hidden = false;
})();
