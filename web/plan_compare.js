'use strict';
// NAY-003 read-only catalog UX. No writes, payment or provisioning calls.
(function () {
  const host = document.getElementById('plan-list');
  const period = document.getElementById('plan-period');
  const result = document.getElementById('plan-result');
  const compare = document.getElementById('plan-compare');
  const summary = document.getElementById('plan-selection');
  const table = document.getElementById('plan-compare-output');
  if (!host || !period || !result || !compare || !summary || !table) return;

  let all = [];
  const selected = new Set();
  const unknown = () => 'Not confirmed';
  const create = (tag, name, text) => {
    const element = document.createElement(tag);
    if (name) element.className = name;
    if (text !== undefined) element.textContent = String(text);
    return element;
  };
  function valid(p) {
    return p && typeof p.code === 'string' && typeof p.title === 'string' &&
      ['Daily', 'Weekly', 'Monthly', 'Trip-based'].includes(p.period) &&
      typeof p.audience === 'string' && typeof p.description === 'string' &&
      ['price_ngn', 'data_gb', 'voice_minutes', 'sms_count'].every(k => p[k] === null) &&
      p.available_for_purchase === false && p.hotspot === 'Not confirmed' && p.rollover === 'Not confirmed';
  }
  function renderTable() {
    table.replaceChildren();
    const chosen = all.filter(p => selected.has(p.code));
    if (chosen.length < 2) {
      summary.textContent = `${selected.size} of 3 selected. Choose 2 or 3 plans to compare.`;
      return;
    }
    summary.textContent = `${chosen.length} concept plans selected. All figures remain unconfirmed.`;
    const t = create('table', 'comparison-table');
    const caption = create('caption', '', 'Concept-only plan comparison — prices and allowances are unconfirmed');
    const head = document.createElement('thead');
    const hr = document.createElement('tr');
    ['Detail', ...chosen.map(p => p.title)].forEach(label => hr.append(create('th', '', label)));
    head.append(hr);
    const body = document.createElement('tbody');
    const rows = [
      ['Duration', p => p.period],
      ['Intended audience', p => p.audience],
      ['Mobile data', p => unknown(p.data_gb)],
      ['Voice minutes', p => unknown(p.voice_minutes)],
      ['SMS allowance', p => unknown(p.sms_count)],
      ['Price (NGN)', p => unknown(p.price_ngn)],
      ['Hotspot', p => p.hotspot],
      ['Rollover', p => p.rollover],
      ['Purchase', () => 'Unavailable — simulation only'],
    ];
    for (const [heading, read] of rows) {
      const tr = document.createElement('tr');
      const th = create('th', '', heading); th.scope = 'row'; tr.append(th);
      for (const p of chosen) tr.append(create('td', '', read(p)));
      body.append(tr);
    }
    t.append(caption, head, body);
    table.append(t);
  }
  function render() {
    host.replaceChildren();
    const visible = all.filter(p => period.value === 'all' || p.period === period.value);
    result.textContent = `${visible.length} concept plans shown. No prices or allowances have been verified.`;
    for (const p of visible) {
      const card = create('article', 'plan concept-plan');
      card.append(create('span', 'period', p.period));
      card.append(create('h3', '', p.title));
      card.append(create('p', '', p.description));
      card.append(create('p', 'plan-audience', `For: ${p.audience}`));
      const facts = create('dl', 'plan-facts');
      for (const [label, value] of [
        ['Data', p.data_gb], ['Voice', p.voice_minutes], ['SMS', p.sms_count], ['Price', p.price_ngn]
      ]) {
        facts.append(create('dt', '', label), create('dd', '', unknown(value)));
      }
      card.append(facts, create('p', 'tag', 'Concept only · Not purchasable'));
      const selectLabel = create('label', 'plan-select');
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = selected.has(p.code);
      checkbox.disabled = !checkbox.checked && selected.size >= 3;
      checkbox.setAttribute('aria-label', `Compare ${p.title}`);
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) selected.add(p.code); else selected.delete(p.code);
        table.replaceChildren();
        render();
      });
      selectLabel.append(checkbox, create('span', '', 'Add to comparison'));
      card.append(selectLabel);
      host.append(card);
    }
    compare.disabled = selected.size < 2;
    summary.textContent = `${selected.size} of 3 selected. Choose 2 or 3 plans to compare.`;
  }
  period.addEventListener('change', render);
  compare.addEventListener('click', renderTable);
  async function load() {
    try {
      const response = await fetch('/api/v1/plans', {cache: 'no-store'});
      if (!response.ok) throw new Error('Catalog read failed');
      const body = await response.json();
      if (!Array.isArray(body.plans) || !body.plans.length || !body.plans.every(valid) ||
          new Set(body.plans.map(p => p.code)).size !== body.plans.length) {
        throw new Error('Unverified or unsafe catalog');
      }
      all = body.plans;
      render();
    } catch (_) {
      all = []; selected.clear(); host.replaceChildren(); table.replaceChildren();
      period.disabled = true; compare.disabled = true;
      result.textContent = 'Plan concepts are temporarily unavailable. No purchases or activations can be made.';
      summary.textContent = 'No plans selected.';
    }
  }
  load();
})();
