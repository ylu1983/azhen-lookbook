// Progressive enhancement: every outfit and detail page also works without JS.
(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const grid = document.querySelector('#outfit-grid');
  const filterKeys = ['occasion', 'concern'];
  const chips = [...document.querySelectorAll('[data-filter]')];
  const state = { occasion: '', concern: '' };
  const filterBar = document.querySelector('.filter-bar');

  function revealSelections() {
    for (const options of document.querySelectorAll('.filter-options')) {
      const overflow = options.scrollWidth > options.clientWidth + 1;
      options.closest('.filter-row').classList.toggle('is-scrollable', overflow);
      if (!overflow) continue;
      const selected = options.querySelector('.is-active');
      const bounds = options.getBoundingClientRect();
      const chip = selected.getBoundingClientRect();
      const inset = 8;
      if (chip.left < bounds.left + inset) {
        options.scrollLeft += chip.left - bounds.left - inset;
      } else if (chip.right > bounds.right - inset) {
        options.scrollLeft += chip.right - bounds.right + inset;
      }
    }
  }

  function syncFilterLayout() {
    revealSelections();
    document.documentElement.style.setProperty('--filter-offset', `${filterBar.offsetHeight + 16}px`);
  }

  function changeFilters(update) {
    const results = document.querySelector('.collection-results');
    // Capture before hiding cards: scroll anchoring may otherwise move the page.
    const shouldReveal = filterBar.getBoundingClientRect().top <= 0
      || results.getBoundingClientRect().top > window.innerHeight - 120;
    update();
    render(true);
    if (shouldReveal || !document.querySelector('#empty-state').hidden) {
      const top = window.scrollY + results.getBoundingClientRect().top - filterBar.offsetHeight;
      window.scrollTo({ top, behavior: 'instant' });
    }
  }

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
    syncFilterLayout();
  }

  if (grid) {
    readLocation();
    render();
    for (const chip of chips) chip.addEventListener('click', () => {
      changeFilters(() => { state[chip.dataset.filter] = chip.dataset.value; });
    });
    for (const id of ['clear-filters', 'empty-reset']) {
      document.getElementById(id).addEventListener('click', () => {
        changeFilters(() => {
          state.occasion = '';
          state.concern = '';
        });
        if (id === 'empty-reset') document.querySelector('[data-filter="occasion"]').focus({ preventScroll: true });
      });
    }
    window.addEventListener('popstate', () => { readLocation(); render(); });
    window.addEventListener('pageshow', syncFilterLayout);
    new ResizeObserver(syncFilterLayout).observe(filterBar);
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
