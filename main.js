// Header: dark background once scrolled
const header = document.getElementById('header');
const onScroll = () => header.classList.toggle('is-scrolled', scrollY > 60);
addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Side panel — accessible dialog: Esc closes, focus stays inside, focus returns to the button
const panel = document.getElementById('panel');
const overlay = document.getElementById('overlay');
const panelBtn = document.getElementById('panelBtn');
const focusables = () => [...panel.querySelectorAll('a[href], button')];
const togglePanel = (open) => {
  panel.classList.toggle('open', open); overlay.classList.toggle('open', open);
  panel.setAttribute('aria-hidden', String(!open));
  panelBtn.setAttribute('aria-expanded', String(open));
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) setTimeout(() => document.getElementById('panelClose').focus(), 50);
  else panelBtn.focus();
};
panelBtn.onclick = () => togglePanel(true);
document.getElementById('panelClose').onclick = () => togglePanel(false);
overlay.onclick = () => togglePanel(false);
panel.querySelectorAll('a').forEach(a => a.addEventListener('click', () => togglePanel(false)));
addEventListener('keydown', e => {
  if (!panel.classList.contains('open')) return;
  if (e.key === 'Escape') togglePanel(false);
  if (e.key === 'Tab') {
    const f = focusables(), first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});

// Hero slider — strip-mask wipe ported from the ScrollGallery component.
// The incoming image is revealed in 20 horizontal strips, bottom to top, each
// strip starting a little later; it scales from 1.25 down to 1 while the title
// rolls out upward and the next one rolls in from below. Autoplays.
const hero = document.getElementById('hero');
if (hero) {
  const imgs = [...hero.querySelectorAll('.hero__img')];
  const titles = [...hero.querySelectorAll('.hero__title')];
  const STRIPS = 20, REVEAL_SPEED = 2, WIPE_MS = 1800, HOLD_MS = 6500;
  const SCALE_FROM = 1.25, SCALE_STEP = 0.125, TITLE_AT = 0.3, TITLE_MS = 300;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Same geometry as createStripBounds(): strip 0 is the bottom one and goes first.
  const strips = Array.from({ length: STRIPS }, (_, j) => {
    const fromBottom = STRIPS - j - 1, step = 100 / STRIPS;
    return { lower: (fromBottom + 1) * step, upper: fromBottom * step - 0.1, delay: (j / STRIPS) * 0.5 };
  });
  const stripMask = (p) => {
    const iv = [];
    for (const s of strips) {
      const adj = Math.max(0, Math.min(1, (p - s.delay) * REVEAL_SPEED));
      if (adj > 0) iv.push({ top: s.lower - adj * (s.lower - s.upper), bottom: s.lower });
    }
    if (!iv.length) return 'linear-gradient(to bottom, transparent 0%, transparent 100%)';
    iv.sort((a, b) => a.top - b.top);
    const merged = [{ ...iv[0] }];
    for (const n of iv.slice(1)) {
      const last = merged[merged.length - 1];
      n.top <= last.bottom ? (last.bottom = Math.max(last.bottom, n.bottom)) : merged.push({ ...n });
    }
    const stops = []; let cur = 0;
    for (const { top, bottom } of merged) {
      if (top > cur) stops.push(`transparent ${cur}%`, `transparent ${top}%`);
      stops.push(`black ${top}%`, `black ${bottom}%`); cur = bottom;
    }
    if (cur < 100) stops.push(`transparent ${cur}%`, 'transparent 100%');
    return `linear-gradient(to bottom, ${stops.join(', ')})`;
  };
  const setMask = (el, v) => { el.style.maskImage = v; el.style.webkitMaskImage = v; };
  const setScale = (el, s) => { el.style.transform = `translate3d(0,0,0) scale(${s})`; };
  const ease = (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);

  let current = -1, busy = false, timer;
  const switchTitle = (next) => {
    const prev = titles[current];
    if (prev) { prev.classList.add('is-leaving'); prev.classList.remove('is-active'); }
    setTimeout(() => {
      if (prev) prev.classList.remove('is-leaving');
      titles[next].classList.add('is-active');
    }, prev ? TITLE_MS : 0);
  };

  const go = (i) => {
    const next = (i + imgs.length) % imgs.length;
    if (busy || next === current) return;
    const from = imgs[current], to = imgs[next], prevIndex = current;
    if (reduce) {
      if (from) from.classList.remove('is-active');
      setMask(to, 'none'); setScale(to, 1); to.classList.add('is-active');
      if (titles[prevIndex]) titles[prevIndex].classList.remove('is-active');
      titles[next].classList.add('is-active'); current = next; return;
    }
    busy = true;
    const fromStart = from ? parseFloat((from.style.transform.match(/scale\(([\d.]+)\)/) || [])[1] || 1) : 1;
    if (from) from.style.transition = 'none';
    to.style.transition = 'none';
    setScale(to, SCALE_FROM); setMask(to, stripMask(0));
    to.classList.add('is-entering');
    let titleDone = false;
    const t0 = performance.now();
    const frame = (now) => {
      const p = Math.min(1, (now - t0) / WIPE_MS), e = ease(p);
      setMask(to, stripMask(e));
      setScale(to, SCALE_FROM - SCALE_STEP * e);              // 1.25 -> 1.125
      if (from) setScale(from, fromStart + (1 - fromStart) * e); // settle the outgoing one to 1
      if (!titleDone && e >= TITLE_AT) { titleDone = true; switchTitle(next); current = next; }
      if (p < 1) return requestAnimationFrame(frame);
      if (from) from.classList.remove('is-active');
      to.classList.remove('is-entering'); to.classList.add('is-active');
      setMask(to, 'none');
      // finish the 1.125 -> 1 settle while the slide is on screen
      to.style.transition = `transform ${HOLD_MS}ms cubic-bezier(.2,.6,.3,1)`;
      requestAnimationFrame(() => setScale(to, 1));
      busy = false;
    };
    requestAnimationFrame(frame);
  };
  let paused = false;
  const start = () => { clearInterval(timer); timer = setInterval(() => { if (!paused && !document.hidden) go(current + 1); }, WIPE_MS + HOLD_MS); };
  hero.querySelectorAll('.hero__arrows button').forEach(b =>
    b.addEventListener('click', () => { go(current + Number(b.dataset.dir)); start(); }));
  ['mouseenter', 'focusin'].forEach(ev => hero.addEventListener(ev, () => { paused = true; }));
  ['mouseleave', 'focusout'].forEach(ev => hero.addEventListener(ev, () => { paused = false; }));
  go(0); start();   // the first image also wipes in on load
}

// Reveal on scroll
const io = new IntersectionObserver(entries => entries.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// Video: load only when it is about to be seen (it is ~17 MB); pause toggle
const video = document.querySelector('video[data-src]');
if (video) {
  const toggle = document.getElementById('videoToggle');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const setState = () => {
    toggle.classList.toggle('is-paused', video.paused);
    toggle.setAttribute('aria-label', video.paused ? 'Reproducir video' : 'Pausar video');
  };
  const vio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) { if (!video.paused && video.src) video.pause(); return; }
    if (!video.src) { video.src = video.dataset.src; toggle.hidden = false; }
    if (!reduceMotion && !video.dataset.userPaused) video.play().catch(() => {});
    setState();
  }), { rootMargin: '300px 0px' });
  vio.observe(video);
  toggle.addEventListener('click', () => {
    if (video.paused) { delete video.dataset.userPaused; video.play(); } else { video.dataset.userPaused = '1'; video.pause(); }
  });
  video.addEventListener('play', setState); video.addEventListener('pause', setState);
}

// Video: expand from inset frame to full-bleed while scrolling
const videoSection = document.getElementById('videoScroll');
const frame = document.getElementById('videoFrame');
// Big type parallax
const parallax = [...document.querySelectorAll('[data-speed]')];

const tick = () => {
  const vh = innerHeight;
  if (frame && innerWidth > 1024) {
    const r = videoSection.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, -r.top / (r.height - vh)));
    const x = 18 * (1 - p), y = 4 * (1 - p);
    frame.style.clipPath = `inset(${y}% ${x}% ${y}% ${x}% round ${6 * (1 - p)}px)`;
  }
  parallax.forEach(el => {
    const r = el.getBoundingClientRect();
    const offset = (r.top + r.height / 2 - vh / 2) * Number(el.dataset.speed);
    el.style.transform = `translateX(${offset}px)`;
  });
  requestAnimationFrame(tick);
};
if ((frame || parallax.length) && !matchMedia('(prefers-reduced-motion: reduce)').matches) requestAnimationFrame(tick);

// Banner carousel — slides hidden by CSS (desktop-only banners on phones) are skipped
const track = document.getElementById('bannerTrack');
if (track) {
  const section = track.closest('.banners');
  const dotsEl = document.getElementById('bannerDots');
  let slides = [], bi = 0, bannerTimer, paused = false;
  const visible = () => [...track.children].filter(s => getComputedStyle(s).display !== 'none');
  const goBanner = (i) => {
    bi = (i + slides.length) % slides.length;
    track.style.transform = `translateX(${-bi * 100}%)`;
    [...dotsEl.children].forEach((d, k) => { d.classList.toggle('on', k === bi); d.setAttribute('aria-current', k === bi ? 'true' : 'false'); });
    slides.forEach((s, k) => { s.tabIndex = k === bi ? 0 : -1; s.setAttribute('aria-hidden', String(k !== bi)); });
  };
  const build = () => {
    slides = visible(); dotsEl.innerHTML = '';
    slides.forEach((_, i) => {
      const d = document.createElement('button');
      d.setAttribute('aria-label', `Ir al banner ${i + 1} de ${slides.length}`);
      d.onclick = () => { goBanner(i); startBanners(); };
      dotsEl.appendChild(d);
    });
    goBanner(0);
  };
  const startBanners = () => { clearInterval(bannerTimer); bannerTimer = setInterval(() => { if (!paused && !document.hidden) goBanner(bi + 1); }, 5000); };
  section.querySelector('.banners__nav.prev').onclick = () => { goBanner(bi - 1); startBanners(); };
  section.querySelector('.banners__nav.next').onclick = () => { goBanner(bi + 1); startBanners(); };
  ['mouseenter', 'focusin'].forEach(ev => section.addEventListener(ev, () => { paused = true; }));
  ['mouseleave', 'focusout'].forEach(ev => section.addEventListener(ev, () => { paused = false; }));
  matchMedia('(max-width:640px)').addEventListener('change', build);
  build(); startBanners();
}

// ---------- Inner pages ----------
// "Ver más cursos" toggle
const moreBtn = document.getElementById('moreBtn');
if (moreBtn) {
  const more = document.querySelector('.course-list__more');
  moreBtn.addEventListener('click', () => {
    const open = more.hidden;
    more.hidden = !open;
    more.querySelectorAll('.reveal').forEach(el => el.classList.add('in'));
    moreBtn.innerHTML = open ? '<span>−</span> Ver menos cursos' : '<span>+</span> Ver más cursos';
  });
}

// Gallery lightbox — arrows, keyboard (← → Esc) and counter
const lightbox = document.getElementById('lightbox');
if (lightbox) {
  const img = lightbox.querySelector('img');
  const count = lightbox.querySelector('.lightbox__count');
  const items = [...document.querySelectorAll('.gallery__item')];
  let li = 0, opener = null;
  const show = (i) => {
    li = (i + items.length) % items.length;
    img.src = items[li].dataset.full;
    img.alt = items[li].querySelector('img').alt;
    count.textContent = `${li + 1} / ${items.length}`;
  };
  const close = () => { lightbox.hidden = true; document.body.style.overflow = ''; if (opener) opener.focus(); };
  items.forEach((b, i) => b.addEventListener('click', () => {
    opener = b; show(i); lightbox.hidden = false; document.body.style.overflow = 'hidden';
    lightbox.querySelector('.lightbox__close').focus();
  }));
  lightbox.querySelector('.lightbox__nav--prev').onclick = () => show(li - 1);
  lightbox.querySelector('.lightbox__nav--next').onclick = () => show(li + 1);
  lightbox.querySelector('.lightbox__close').onclick = close;
  lightbox.addEventListener('click', e => { if (e.target === lightbox) close(); });
  addEventListener('keydown', e => {
    if (lightbox.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(li - 1);
    if (e.key === 'ArrowRight') show(li + 1);
  });
}

// Contact form
// To receive messages by email, create a free form at formspree.io (or similar)
// with PGB's address and paste its URL here. Until then, the message is sent
// through WhatsApp, which always works.
const FORM_ENDPOINT = '';
const form = document.getElementById('contactForm');
if (form) {
  const note = document.getElementById('formNote');
  const say = (msg, error = false) => { note.textContent = msg; note.classList.toggle('is-error', error); };
  form.addEventListener('submit', async e => {
    e.preventDefault();
    let firstBad = null;
    form.querySelectorAll('[required]').forEach(f => {
      const bad = !f.value.trim() || (f.type === 'email' && !f.checkValidity());
      f.setAttribute('aria-invalid', String(bad));
      if (bad && !firstBad) firstBad = f;
    });
    if (firstBad) { say('Revisa los campos marcados: todos son obligatorios y el correo debe ser válido.', true); firstBad.focus(); return; }
    const d = Object.fromEntries(new FormData(form));
    if (FORM_ENDPOINT) {
      say('Enviando…');
      try {
        const r = await fetch(FORM_ENDPOINT, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(d) });
        if (!r.ok) throw new Error();
        form.reset(); say('¡Gracias! Recibimos tu consulta y te responderemos pronto.');
      } catch { say('No pudimos enviar el mensaje. Escríbenos por WhatsApp al 507 6462-6739.', true); }
      return;
    }
    const text = `Hola, soy ${d.nombre} (${d.email}). Consulta sobre ${d.consulta}:\n\n${d.mensaje}`;
    window.open(`https://wa.me/50764626739?text=${encodeURIComponent(text)}`, '_blank', 'noopener');
    say('Abrimos WhatsApp con tu mensaje listo: solo pulsa enviar. Si no se abrió, escríbenos al 507 6462-6739.');
  });
  form.querySelectorAll('[required]').forEach(f => f.addEventListener('input', () => f.removeAttribute('aria-invalid')));
}

// Sticky footer: size the clip box to the footer content; disable the reveal
// when the footer would not fit on screen.
const stickyFooter = document.querySelector('.sticky-footer');
if (stickyFooter) {
  const inner = stickyFooter.querySelector('.sticky-footer__inner');
  const size = () => {
    stickyFooter.classList.add('is-static');            // measure natural height
    const h = inner.scrollHeight;
    stickyFooter.style.setProperty('--fh', h + 'px');
    stickyFooter.classList.toggle('is-static', h > innerHeight * 0.92);
  };
  size();
  addEventListener('resize', size);
  addEventListener('load', size);
  const fio = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { stickyFooter.querySelectorAll('.fade-blur').forEach(el => el.classList.add('in')); fio.disconnect(); }
  }), { threshold: 0.2 });
  fio.observe(stickyFooter);
}

// Course listing: client-side sorting
document.querySelectorAll('[data-sort]').forEach(select => {
  const grid = select.closest('.shop').querySelector('.shop__grid');
  const cards = [...grid.children];
  cards.forEach((c, i) => { c.dataset.index = i; });
  select.addEventListener('change', () => {
    const v = select.value;
    const by = {
      'default': (a, b) => a.dataset.index - b.dataset.index,
      'price-asc': (a, b) => a.dataset.price - b.dataset.price,
      'price-desc': (a, b) => b.dataset.price - a.dataset.price,
      'hours-asc': (a, b) => a.dataset.hours - b.dataset.hours,
      'title': (a, b) => a.dataset.title.localeCompare(b.dataset.title, 'es'),
    }[v];
    [...grid.children].sort(by).forEach(c => { c.classList.add('in'); grid.appendChild(c); });
  });
});
