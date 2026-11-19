// Progressive enhancement: every outfit and detail page also works without JS.
(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const grid = document.querySelector('#outfit-grid');
  const filterKeys = ['occasion', 'concern'];
  const chips = [...document.querySelectorAll('[data-filter]')];
  const state = { occasion: '', concern: '' };

  function readLocation() {
    const query = new URLSearchParams(location.search);
    for (const key of filterKeys) {
      const value = query.get(key) || '';
      state[key] = chips.some(chip => chip.dataset.filter === key && chip.dataset.value === value) ? value : '';
    }
  }

  function render(updateUrl = false) {
    const active = filterKeys.some(key => state[key]);
    const query = new URLSearchParams();
    for (const key of filterKeys) if (state[key]) query.set(key, state[key]);
    let count = 0;
    for (const card of grid.children) {
      const matches = (!state.occasion || card.dataset.occasions.split('|').includes(state.occasion))
        && (!state.concern || card.dataset.concerns.split('|').includes(state.concern));
      card.hidden = !matches;
      if (matches) count++;
      const link = card.querySelector('a');
      const url = new URL(link.href);
      url.search = query.toString();
      link.href = url.href;
    }
    for (const chip of chips) {
      const selected = state[chip.dataset.filter] === chip.dataset.value;
      chip.classList.toggle('is-active', selected);
      chip.setAttribute('aria-pressed', String(selected));
    }
    document.querySelector('#result-count').innerHTML = `共 <strong>${count}</strong> 套穿搭`;
    document.querySelector('#clear-filters').hidden = !active;
    document.querySelector('#empty-state').hidden = count > 0;
    document.querySelector('#collection-end').hidden = count === 0;
    if (updateUrl) {
      const url = new URL(location.href);
      url.search = query.toString();
      history.replaceState(null, '', url);
    }
  }

  if (grid) {
    readLocation();
    render();
    for (const chip of chips) chip.addEventListener('click', () => {
      state[chip.dataset.filter] = chip.dataset.value;
      render(true);
    });
    for (const id of ['clear-filters', 'empty-reset']) {
      document.getElementById(id).addEventListener('click', () => {
        state.occasion = '';
        state.concern = '';
        render(true);
        if (id === 'empty-reset') document.querySelector('[data-filter="occasion"]').focus({ preventScroll: true });
      });
    }
    window.addEventListener('popstate', () => { readLocation(); render(); });
  } else {
    const query = new URLSearchParams();
    for (const key of filterKeys) {
      const value = params.get(key);
      if (value) query.set(key, value);
    }
    for (const link of document.querySelectorAll('[data-back-link]')) {
      const url = new URL(link.href);
      url.search = query.toString();
      link.href = url.href;
    }
  }
})();
