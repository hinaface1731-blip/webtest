// Responsive site navigation (one <nav> tree; native popover when collapsed).
// Without this script the header stays in the collapsed layout and still works.
const header = document.querySelector(".site-header");
const inner = header?.querySelector(".header-inner");
const menu = header?.querySelector("#site-menu");

if (header && inner && menu) {
  const dropdowns = [...header.querySelectorAll(".nav-dropdown")].map((item) => ({
    item,
    trigger: item.querySelector(".dropdown-trigger"),
    list: item.querySelector(".dropdown-list"),
    preview: false,
  }));

  let isWide = null;
  let lastWidth = 0;

  function applySubmenus(wide) {
    for (const d of dropdowns) {
      if (wide) d.list.setAttribute("popover", "auto");
      else d.list.removeAttribute("popover");
      d.list.hidden = !wide;
      d.preview = false;
      d.trigger.setAttribute("aria-expanded", "false");
    }
  }

  function sync() {
    const width = header.clientWidth;
    // While collapsed only re-measure when the header has grown (avoids thrash).
    if (isWide === false && width <= lastWidth) {
      lastWidth = width;
      return;
    }
    lastWidth = width;

    const wasOpen = menu.matches(":popover-open");
    header.classList.add("is-measuring", "is-wide");
    const wide = inner.scrollWidth <= inner.clientWidth;
    header.classList.toggle("is-wide", wide);
    requestAnimationFrame(() => header.classList.remove("is-measuring"));

    if (wide === isWide) return;
    isWide = wide;

    if (wide) {
      menu.removeAttribute("popover");
    } else {
      menu.setAttribute("popover", "auto");
      if (wasOpen) menu.showPopover();
    }
    applySubmenus(wide);
  }

  const ro = new ResizeObserver(sync);
  ro.observe(header);
  ro.observe(menu);

  const canHover = matchMedia("(hover: hover)");
  const anchorSupported = CSS.supports("position-area", "block-end");

  for (const d of dropdowns) {
    const { item, trigger, list } = d;

    // Narrow layout: plain disclosure toggled with `hidden`.
    trigger.addEventListener("click", (event) => {
      if (isWide) {
        if (d.preview) {
          // Pin a hover-previewed submenu instead of toggling it closed.
          d.preview = false;
          event.preventDefault();
        }
        return; // popovertarget handles the rest
      }
      list.hidden = !list.hidden;
      trigger.setAttribute("aria-expanded", String(!list.hidden));
    });

    // Wide layout: the native toggle event drives aria-expanded.
    list.addEventListener("toggle", (event) => {
      if (!isWide) return;
      const open = event.newState === "open";
      trigger.setAttribute("aria-expanded", String(open));
      if (!open) d.preview = false;
      if (open && !anchorSupported) positionFallback(trigger, list);
    });

    item.addEventListener("pointerenter", (event) => {
      if (!isWide || !canHover.matches || event.pointerType === "touch") return;
      if (list.matches(":popover-open")) return;
      d.preview = true;
      list.showPopover({ source: trigger });
    });

    item.addEventListener("pointerleave", () => {
      if (isWide && d.preview && list.matches(":popover-open")) list.hidePopover();
      d.preview = false;
    });

    item.addEventListener("focusout", (event) => {
      if (!isWide || !event.relatedTarget) return;
      if (!item.contains(event.relatedTarget) && list.matches(":popover-open")) {
        list.hidePopover();
      }
    });
  }

  // Without CSS Anchor Positioning, place the submenu below its trigger manually.
  function positionFallback(trigger, list) {
    const t = trigger.getBoundingClientRect();
    const size = list.getBoundingClientRect();
    let top = t.bottom + 8;
    if (top + size.height > innerHeight) top = Math.max(0, t.top - size.height - 8);
    const left = Math.min(Math.max(0, t.left), innerWidth - size.width);
    list.style.top = `${top}px`;
    list.style.left = `${left}px`;
  }
}
