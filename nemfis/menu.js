const menuButton = document.querySelector('.menu-button');
const menu = document.querySelector('#primary-links');

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
