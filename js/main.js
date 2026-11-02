/* АСУ-ЭКСПЕРТ — общий скрипт всех страниц.
   Работает и без GSAP/Lenis (если CDN недоступен) — тогда анимации проще. */
(() => {
  const doc = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const hasGsap = () => window.gsap && window.ScrollTrigger;

  /* ---------- плавный скролл */
  let lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    if (hasGsap()) {
      gsap.registerPlugin(ScrollTrigger);
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((t) => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
    $$('a[href^="#"]').forEach((a) => a.addEventListener('click', (ev) => {
      const id = a.getAttribute('href');
      if (id.length > 1 && $(id)) { ev.preventDefault(); lenis.scrollTo(id, { offset: -80 }); }
    }));
  } else if (hasGsap()) {
    gsap.registerPlugin(ScrollTrigger);
  }

  /* ---------- шапка и глубиномер */
  const hdr = $('#hdr');
  const gauge = $('.gauge');
  const depthVal = $('#depthVal');
  const MAX_DEPTH = 4000; // м — максимальная длина кабеля для видеокаротажа
  let lastY = 0;
  const onScroll = () => {
    const y = window.scrollY;
    const max = Math.max(1, doc.scrollHeight - innerHeight);
    const p = Math.min(1, y / max);
    hdr.classList.toggle('is-scrolled', y > 20);
    const mnavOpen = !$('#mnav').hidden;
    hdr.classList.toggle('is-hidden', !mnavOpen && y > 400 && y > lastY + 4);
    if (y < lastY - 4 || y < 400) hdr.classList.remove('is-hidden');
    lastY = y;
    if (gauge) {
      gauge.classList.toggle('is-on', y > 120);
      gauge.style.setProperty('--p', p.toFixed(4));
      depthVal.textContent = (p * MAX_DEPTH).toFixed(1).padStart(6, '0');
    }
  };
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
    if (lenis) open ? lenis.stop() : lenis.start();
  });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !mnav.hidden) burger.click(); });

  /* ---------- подсветка под курсором на кнопках и карточках */
  $$('.btn, .dir').forEach((el) => el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - r.left}px`);
    el.style.setProperty('--my', `${e.clientY - r.top}px`);
  }));

  /* ---------- появление при скролле */
  const io = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  $$('.reveal').forEach((el) => io.observe(el));

  /* ---------- заголовки по словам */
  if (hasGsap() && !reduce) {
    $$('.split').forEach((h) => {
      const walk = (node) => {
        [...node.childNodes].forEach((n) => {
          if (n.nodeType === 3) {
            const frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach((part) => {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.append(part); return; }
              const w = document.createElement('span');
              w.className = 'w'; w.textContent = part; frag.append(w);
            });
            n.replaceWith(frag);
          } else if (n.nodeType === 1) walk(n);
        });
      };
      walk(h);
      gsap.from(h.querySelectorAll('.w'), {
        yPercent: 60, opacity: 0, rotate: 3, duration: 1, ease: 'expo.out', stagger: 0.045,
        scrollTrigger: { trigger: h, start: 'top 88%' },
      });
    });
  }

  /* ---------- счётчики */
  const countIO = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (!en.isIntersecting) return;
    const el = en.target; countIO.unobserve(el);
    const to = +el.dataset.to; const suf = el.dataset.suffix || '';
    if (reduce) { el.textContent = to + suf; return; }
    const t0 = performance.now(); const dur = 1600;
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / dur); const v = Math.round(to * (1 - Math.pow(1 - k, 4)));
      el.textContent = v + (k === 1 ? suf : '');
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }), { threshold: 0.6 });
  $$('.count').forEach((el) => countIO.observe(el));

  /* ---------- циферблаты станции цементирования */
  const dialIO = new IntersectionObserver((entries) => entries.forEach((en) => {
    if (!en.isIntersecting) return;
    const d = en.target; dialIO.unobserve(d);
    d.querySelector('.dial-v').style.strokeDasharray = `${235.6 * +d.dataset.v} 314.2`;
  }), { threshold: 0.5 });
  $$('.dial').forEach((d) => dialIO.observe(d));

  /* ---------- каротажные кривые на фоне заголовков внутренних страниц */
  $$('.phero-log').forEach((cv) => {
    const ctx = cv.getContext('2d');
    const curves = [
      { color: 'rgba(255,59,47,.55)', amp: 0.09, seed: Math.random() * 100, x: 0.62 },
      { color: 'rgba(47,125,255,.55)', amp: 0.07, seed: Math.random() * 100, x: 0.74 },
      { color: 'rgba(255,181,71,.35)', amp: 0.05, seed: Math.random() * 100, x: 0.86 },
    ];
    const noise = (y, s) => Math.sin(y * 0.021 + s) * 0.5 + Math.sin(y * 0.057 + s * 2) * 0.3 + Math.sin(y * 0.13 + s * 3) * 0.2;
    let off = 0;
    const draw = () => {
      const dpr = Math.min(2, devicePixelRatio || 1);
      const w = cv.clientWidth; const h = cv.clientHeight;
      if (cv.width !== w * dpr || cv.height !== h * dpr) { cv.width = w * dpr; cv.height = h * dpr; }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      // сетка глубин
      ctx.strokeStyle = 'rgba(150,180,220,.06)'; ctx.lineWidth = 1;
      for (let y = (-off % 40); y < h; y += 40) { ctx.beginPath(); ctx.moveTo(w * 0.55, y); ctx.lineTo(w, y); ctx.stroke(); }
      for (let x = w * 0.55; x < w; x += w * 0.06) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
      curves.forEach((c) => {
        ctx.beginPath(); ctx.strokeStyle = c.color; ctx.lineWidth = 1.4;
        for (let y = 0; y <= h; y += 3) {
          const x = w * c.x + noise(y + off, c.seed) * w * c.amp;
          y ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
      });
      if (!reduce) { off += 0.35; requestAnimationFrame(draw); }
    };
    draw();
  });

  /* ---------- горизонтальная лента кадров видеокаротажа */
  const frames = $('#frames');
  if (frames) {
    const rail = frames.parentElement;
    if (hasGsap() && !reduce && innerWidth > 1080) {
      const dist = () => frames.scrollWidth - rail.clientWidth;
      gsap.to(frames, {
        x: () => -dist(), ease: 'none',
        scrollTrigger: { trigger: '.video-pin', start: 'top top', end: () => `+=${dist()}`, pin: true, scrub: 0.6, invalidateOnRefresh: true },
      });
      $$('.frame img', frames).forEach((img) => gsap.fromTo(img, { scale: 1.25 }, {
        scale: 1, ease: 'none',
        scrollTrigger: { trigger: '.video-pin', start: 'top top', end: () => `+=${dist()}`, scrub: true },
      }));
    } else {
      rail.style.overflowX = 'auto';
      rail.style.scrollSnapType = 'x mandatory';
      $$('.frame', frames).forEach((f) => { f.style.scrollSnapAlign = 'center'; });
    }
  }

  /* ---------- параллакс фото лаборатории */
  if (hasGsap() && !reduce) {
    const fl = $('.feature-log');
    if (fl) gsap.fromTo(fl, { y: 80 }, { y: -40, ease: 'none', scrollTrigger: { trigger: '.feature', scrub: true } });
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

  /* ---------- новости: год + поиск */
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
            p.innerHTML = '';
            p.append(r._t.slice(0, i));
            const m = document.createElement('mark'); m.textContent = r._t.slice(i, i + q.length); p.append(m);
            p.append(r._t.slice(i + q.length));
          } else if (p.childElementCount) p.textContent = r._t;
          if (ok) n++;
        });
        g.hidden = n === 0; total += n;
      });
      $('#nempty').hidden = total > 0;
      if (hasGsap()) ScrollTrigger.refresh();
    };
    nsearch.addEventListener('input', apply);
    chips.forEach((c) => c.addEventListener('click', () => {
      chips.forEach((x) => x.classList.toggle('is-on', x === c)); year = c.dataset.y; apply();
    }));
  }

  /* ---------- лайтбокс сертификатов */
  const lb = $('#lightbox');
  if (lb) {
    const img = lb.querySelector('img');
    const close = () => { lb.hidden = true; lenis?.start(); };
    $$('[data-lightbox]').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault(); img.src = a.getAttribute('href'); lb.hidden = false; lenis?.stop();
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

  addEventListener('load', () => hasGsap() && ScrollTrigger.refresh());
})();
