/* АСУ-ЭКСПЕРТ — общий скрипт. Без зависимостей.
   Всё содержимое видно и без скрипта: скрипт только добавляет движение и подбор прибора. */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- шапка */
  const hdr = $('#hdr');
  const onScroll = () => hdr.classList.toggle('is-scrolled', scrollY > 8);
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- мобильное меню */
  const burger = $('#burger');
  const mnav = $('#mnav');
  // Меню — нативный popover (кнопка открывает его через popovertarget, Esc и клик мимо закрывают).
  // Старым браузерам без Popover API подгружаем полифил только при необходимости.
  if (!Object.hasOwn(HTMLElement.prototype, 'popover')) {
    import('https://unpkg.com/@oddbird/popover-polyfill@0.7.3/dist/popover.min.js').catch(() => {});
  }
  mnav.addEventListener('toggle', (e) => {
    const open = e.newState === 'open';
    burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  });

  /* ---------- появление частей раздела: заголовок, текст, картинка */
  const io = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
  }), { rootMargin: '0px 0px -6% 0px' });
  $$('.rv').forEach((el) => io.observe(el));

  /* ---------- неподвижная половина главной: картинка меняется вместе с разделом */
  const stage = $('.stage');
  if (stage) {
    const figs = $$('figure', stage);
    const show = (i) => figs.forEach((f) => {
      const on = f.dataset.stage === String(i);
      f.classList.toggle('is-on', on);
      const v = f.querySelector('video');
      if (v) { if (on && !reduce) v.play().catch(() => {}); else v.pause(); }
    });
    const sio = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) show(en.target.dataset.stage);
    }), { rootMargin: '-45% 0px -45% 0px' });
    $$('.reading [data-stage]').forEach((s) => sio.observe(s));
  }

  /* ---------- подбор прибора по методам */
  const methods = $$('.methods button');
  if (methods.length) {
    const rows = $$('#pickerList li');
    const count = $('#pickerCount');
    const forms = (n) => (n % 10 === 1 && n % 100 !== 11 ? 'прибор' : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? 'прибора' : 'приборов');
    const apply = () => {
      const on = methods.filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.dataset.m);
      let n = 0;
      rows.forEach((li) => {
        const has = li.dataset.m.split(' ');
        const ok = on.every((m) => has.includes(m));
        li.hidden = !ok;
        if (ok) n++;
      });
      count.textContent = on.length
        ? (n ? `Подходит ${n} ${forms(n)}` : 'Нет прибора, который делает всё сразу. Снимите один из методов или напишите нам: соберём комплект.')
        : `Все приборы каталога: ${rows.length}`;
    };
    methods.forEach((b) => b.addEventListener('click', () => {
      b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true'));
      apply();
    }));
  }

  /* ---------- оглавление документации */
  const tocLinks = $$('.toc a');
  if (tocLinks.length) {
    const map = new Map(tocLinks.map((a) => [a.getAttribute('href').slice(1), a]));
    const tio = new IntersectionObserver((entries) => entries.forEach((en) => {
      if (en.isIntersecting) { tocLinks.forEach((a) => a.classList.remove('is-on')); map.get(en.target.id)?.classList.add('is-on'); }
    }), { rootMargin: '-20% 0px -70% 0px' });
    map.forEach((_, id) => { const h = document.getElementById(id); if (h) tio.observe(h); });
  }

  /* ---------- новости: год и поиск */
  const nsearch = $('#nsearch');
  if (nsearch) {
    const rows = $$('.nrow'); const groups = $$('.ngroup'); const chips = $$('.ychip');
    rows.forEach((r) => { r._t = r.querySelector('p').textContent; r._l = r._t.toLowerCase(); });
    let year = 'all';
    const apply = () => {
      const q = nsearch.value.trim().toLowerCase();
      let total = 0;
      groups.forEach((g) => {
        let n = 0;
        const yearOk = year === 'all' || g.dataset.y === year;
        g.querySelectorAll('.nrow').forEach((r) => {
          const ok = yearOk && (!q || r._l.includes(q));
          r.hidden = !ok;
          const p = r.querySelector('p');
          if (ok && q) {
            const i = r._l.indexOf(q);
            p.textContent = '';
            const m = document.createElement('mark'); m.textContent = r._t.slice(i, i + q.length);
            p.append(r._t.slice(0, i), m, r._t.slice(i + q.length));
          } else if (p.childElementCount) p.textContent = r._t;
          if (ok) n++;
        });
        g.hidden = n === 0; total += n;
      });
      $('#nempty').hidden = total > 0;
    };
    nsearch.addEventListener('input', apply);
    chips.forEach((c) => c.addEventListener('click', () => {
      chips.forEach((x) => x.classList.toggle('is-on', x === c)); year = c.dataset.y; apply();
    }));
  }

  /* ---------- лайтбокс документов */
  const lb = $('#lightbox');
  if (lb) {
    // Нативный <dialog>: showModal() даёт верхний слой, ловушку фокуса и Esc;
    // closedby="any" закрывает по клику на фон. Где closedby нет (Safari), закрываем вручную.
    const img = lb.querySelector('img');
    $$('[data-lightbox]').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault(); img.src = a.getAttribute('href'); img.alt = a.querySelector('img').alt; lb.showModal();
    }));
    if (!('closedBy' in HTMLDialogElement.prototype)) {
      lb.addEventListener('click', (e) => {
        if (e.target !== lb) return;
        const r = lb.getBoundingClientRect();
        const inside = r.top <= e.clientY && e.clientY <= r.bottom && r.left <= e.clientX && e.clientX <= r.right;
        if (!inside) lb.close();
      });
    }
  }

  /* ---------- форма запроса -> письмо */
  const form = $('#rform');
  if (form) {
    // aria-invalid следует за :user-invalid, текст ошибки привязан через aria-describedby
    // только пока ошибка видна, чтобы его не зачитывали заранее.
    const linkError = (el, shown) => {
      const id = el.dataset.error;
      if (!id) return;
      const ids = (el.getAttribute('aria-describedby') || '').split(/\s+/).filter((x) => x && x !== id);
      if (shown) ids.push(id);
      if (ids.length) el.setAttribute('aria-describedby', ids.join(' ')); else el.removeAttribute('aria-describedby');
    };
    const sync = (el) => {
      if (!el.matches?.('input, select, textarea')) return;
      const bad = el.matches(':user-invalid');
      el.setAttribute('aria-invalid', String(bad));
      linkError(el, bad);
    };
    [...form.elements].forEach(sync);
    form.addEventListener('blur', (e) => sync(e.target), true);
    form.addEventListener('input', (e) => sync(e.target));
    form.addEventListener('change', (e) => sync(e.target), true);
    form.addEventListener('invalid', (e) => sync(e.target), true);

    // Браузер сам проверяет обязательные поля и переводит фокус на первое неверное;
    // submit срабатывает только для заполненной формы.
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const f = new FormData(form);
      const subject = `Запрос КП${f.get('product') ? ': ' + f.get('product') : ''}`;
      const body = `Имя / организация: ${f.get('name')}\nКонтакт: ${f.get('contact')}\nПрибор: ${f.get('product') || 'нужна консультация'}\n\n${f.get('msg')}`;
      location.href = `mailto:info@asu-expert.ru?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  }

  if (reduce) $$('.rv').forEach((el) => el.classList.add('is-in'));
})();
