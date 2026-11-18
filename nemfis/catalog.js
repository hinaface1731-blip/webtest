const controls = document.querySelector('.catalog-controls');
const filters = [...controls.querySelectorAll('[data-filter]')];
const search = document.querySelector('#device-search');
const status = document.querySelector('#catalog-status');
const empty = document.querySelector('.empty-state');
const menuButton = document.querySelector('.menu-button');
const menu = document.querySelector('#primary-links');

function normalize(value) {
  return value.toLocaleLowerCase('ru').replaceAll('ё', 'е').replace(/[^\p{L}\p{N}]/gu, '');
}

const groups = [...document.querySelectorAll('.product-group')].map((group) => ({
  element: group,
  products: [...group.querySelectorAll('.product')].map((product) => ({
    element: product,
    index: normalize(`${product.querySelector('h4').textContent} ${product.dataset.keywords ?? ''} ${product.querySelector('p').textContent}`),
  })),
}));

let category = 'all';

function renderCatalog(announce = true) {
  const query = normalize(search.value);
  let total = 0;

  for (const { element, products } of groups) {
    const matchesCategory = category === 'all' || category === element.id;
    let hasMatches = false;
    for (const product of products) {
      const visible = matchesCategory && product.index.includes(query);
      product.element.hidden = !visible;
      if (visible) {
        hasMatches = true;
        total += 1;
      }
    }
    element.hidden = !hasMatches;
  }

  for (const button of filters) {
    button.setAttribute('aria-pressed', String(button.dataset.filter === category));
  }
  empty.hidden = total > 0;
  if (announce) status.textContent = total ? `Найдено позиций: ${total}` : 'По этому запросу ничего не найдено.';
}

function selectCategory(value, { clearSearch = false, announce = true } = {}) {
  category = value;
  if (clearSearch) search.value = '';
  renderCatalog(announce);
}

for (const button of filters) {
  button.addEventListener('click', () => selectCategory(button.dataset.filter));
}
search.addEventListener('input', () => renderCatalog());
document.querySelector('#reset-catalog').addEventListener('click', () => {
  selectCategory('all', { clearSearch: true });
  search.focus();
});

function applyCategoryFromHash() {
  const value = location.hash.slice(1);
  const target = groups.find(({ element }) => element.id === value)?.element;
  if (target) {
    selectCategory(value, { clearSearch: true, announce: false });
    target.scrollIntoView();
  }
}

for (const link of document.querySelectorAll('[data-method]')) {
  link.addEventListener('click', (event) => {
    if (event.ctrlKey || event.shiftKey || event.metaKey || event.altKey) return;
    selectCategory(link.dataset.method, { clearSearch: true });
  });
}

controls.hidden = false;
applyCategoryFromHash();
window.addEventListener('hashchange', applyCategoryFromHash);

if ('showPopover' in HTMLElement.prototype) {
  const narrow = matchMedia('(max-width: 58rem)');
  const updateMenu = () => {
    menu.toggleAttribute('popover', narrow.matches);
    menuButton.hidden = !narrow.matches;
  };

  narrow.addEventListener('change', updateMenu);
  menu.addEventListener('click', (event) => {
    if (menu.hasAttribute('popover') && event.target.closest('a')) {
      menu.hidePopover();
    }
  });
  updateMenu();
}
