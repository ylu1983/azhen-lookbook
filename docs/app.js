// Progressive enhancement: every outfit and detail page also works without JS.
(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const grid = document.querySelector('#outfit-grid');
  const filterKeys = ['occasion', 'concern'];
  const chips = [...document.querySelectorAll('[data-filter]')];
  const state = { occasion: '', concern: '' };

  // Browser focus scrolling does not consistently account for a fixed action.
  const inquiry = document.querySelector('.detail-navigation a[href="#inquiry"]');
  if (inquiry) document.addEventListener('focusin', event => {
    const target = event.target;
    if (!(target instanceof HTMLElement) || inquiry.contains(target)
      || getComputedStyle(inquiry).position !== 'fixed') return;
    requestAnimationFrame(() => {
      if (document.activeElement !== target) return;
      const visibleBottom = inquiry.getBoundingClientRect().top - 16;
      const bottom = target.getBoundingClientRect().bottom;
      if (bottom > visibleBottom) window.scrollBy({ top: bottom - visibleBottom, behavior: 'instant' });
    });
  });
  const filterBar = document.querySelector('.filter-bar');

  function updateScrollEdge(options) {
    const selected = options.querySelector('.is-active');
    const previous = selected?.previousElementSibling;
    let fragment = false;
    if (previous && !previous.matches(':focus-visible')) {
      const bounds = options.getBoundingClientRect();
      const chip = selected.getBoundingClientRect();
      const before = previous.getBoundingClientRect();
      const style = getComputedStyle(previous);
      const textEnd = before.right - parseFloat(style.paddingRight) - parseFloat(style.borderRightWidth);
      // Cover only a tiny cut-off text tail, never a readable option or the selected chip.
      fragment = before.left < bounds.left && textEnd > bounds.left
        && textEnd <= bounds.left + 14 && chip.left >= bounds.left + 14;
    }
    options.classList.toggle('has-leading-fragment', fragment);
  }

  function revealChip(options, selected) {
    const bounds = options.getBoundingClientRect();
    const chip = selected.getBoundingClientRect();
    const inset = 8;
    if (chip.left < bounds.left + inset) {
      options.scrollLeft += chip.left - bounds.left - inset;
    } else if (chip.right > bounds.right - inset) {
      options.scrollLeft += chip.right - bounds.right + inset;
    }
    updateScrollEdge(options);
  }

  function revealSelections() {
    for (const options of document.querySelectorAll('.filter-options')) {
      const overflow = options.scrollWidth > options.clientWidth + 1;
      options.closest('.filter-row').classList.toggle('is-scrollable', overflow);
      if (!overflow) {
        options.classList.remove('has-leading-fragment');
        continue;
      }
      revealChip(options, options.querySelector('.is-active'));
    }
  }

  function syncFilterLayout() {
    revealSelections();
    document.documentElement.style.setProperty('--filter-offset', `${filterBar.offsetHeight + 16}px`);
  }

  function changeFilters(update) {
    const results = document.querySelector('.collection-results');
    update();
    render(true);
    const revealResults = () => {
      const top = window.scrollY + results.getBoundingClientRect().top - filterBar.offsetHeight - 16;
      window.scrollTo({ top, behavior: 'instant' });
    };
    revealResults();
    // Button focus and scroll anchoring can run after the click handler.
    // Re-align once they settle so guidance cannot remain behind the sticky bar.
    requestAnimationFrame(revealResults);
  }
  const cards = grid ? [...grid.children] : [];

  function matches(card, occasion, concern) {
    return (!occasion || card.dataset.occasions.split('|').includes(occasion))
      && (!concern || card.dataset.concerns.split('|').includes(concern));
  }

  function renderRecovery() {
    const container = document.querySelector('#empty-alternatives');
    container.replaceChildren();
    for (const key of filterKeys) {
      if (!state[key] || !state[filterKeys.find(other => other !== key)]) continue;
      const count = cards.filter(card => matches(card,
        key === 'occasion' ? state.occasion : '',
        key === 'concern' ? state.concern : '')).length;
      if (!count) continue;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'recovery-button';
      button.textContent = `保留「${state[key]}」，看 ${count} 套`;
      button.addEventListener('click', () => {
        changeFilters(() => { state[filterKeys.find(other => other !== key)] = ''; });
        document.querySelector('#result-count').focus({ preventScroll: true });
      });
      container.append(button);
    }
  }
  const copyButton = document.querySelector('.copy-inquiry');
  if (copyButton) {
    const message = document.querySelector('#inquiry-message');
    const status = document.querySelector('#copy-status');
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(message.value);
        status.textContent = '已複製，開啟 Instagram 後貼上即可。';
      } catch {
        message.focus();
        message.select();
        message.setSelectionRange(0, message.value.length);
        status.textContent = '請長按已選取的內容，選擇「複製」，再到 Instagram 貼上。';
      }
    });
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
    for (const card of cards) {
      const visible = matches(card, state.occasion, state.concern);
      card.hidden = !visible;
      if (visible) count++;
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
    document.querySelector('#arm-guidance').hidden = state.concern !== '手臂粗不敢穿無袖';
    if (!count) renderRecovery();
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
    for (const options of document.querySelectorAll('.filter-options')) {
      options.addEventListener('scroll', () => updateScrollEdge(options), { passive: true });
      options.addEventListener('focusin', event => {
        if (!event.target.matches('.filter-chip:focus-visible')) return;
        revealChip(options, event.target);
        // Native keyboard focus scrolling can settle after focusin.
        requestAnimationFrame(() => {
          if (event.target === document.activeElement) revealChip(options, event.target);
        });
      });
    }
    new ResizeObserver(syncFilterLayout).observe(filterBar);
  } else {
    const query = new URLSearchParams();
    for (const key of filterKeys) {
      const value = params.get(key);
      if (value) query.set(key, value);
    }
    for (const link of document.querySelectorAll('[data-back-link], .related-grid .outfit-link')) {
      const url = new URL(link.href);
      url.search = query.toString();
      // Return to the results, not the tall collection introduction at large text sizes.
      if (link.matches('[data-back-link]')) url.hash = 'outfit-grid';
      link.href = url.href;
    }
  }
})();
