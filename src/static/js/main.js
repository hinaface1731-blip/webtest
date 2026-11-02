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
  burger.addEventListener('click', () => {
    const open = mnav.hidden;
    mnav.hidden = !open;
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    document.body.style.overflow = open ? 'hidden' : '';
  });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !mnav.hidden) burger.click(); });

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
    const img = lb.querySelector('img');
    const close = () => { lb.hidden = true; };
    $$('[data-lightbox]').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault(); img.src = a.getAttribute('href'); img.alt = a.querySelector('img').alt; lb.hidden = false; lb.querySelector('button').focus();
    }));
    lb.addEventListener('click', close);
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && !lb.hidden) close(); });
  }

  /* ---------- форма запроса -> письмо */
  const form = $('#rform');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const f = new FormData(form);
      let bad = false;
      ['name', 'contact'].forEach((k) => {
        const inp = form.elements[k]; const empty = !String(f.get(k)).trim();
        inp.classList.toggle('is-bad', empty); bad ||= empty;
      });
      if (bad) return;
      const subject = `Запрос КП${f.get('product') ? ': ' + f.get('product') : ''}`;
      const body = `Имя / организация: ${f.get('name')}\nКонтакт: ${f.get('contact')}\nПрибор: ${f.get('product') || 'нужна консультация'}\n\n${f.get('msg')}`;
      location.href = `mailto:info@asu-expert.ru?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  }

  if (reduce) $$('.rv').forEach((el) => el.classList.add('is-in'));
})();
