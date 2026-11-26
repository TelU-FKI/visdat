/* Accessible DOM labels projected on a responsive, rotating Fibonacci sphere. */
(() => {
  const TAU = Math.PI * 2;
  const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches
    || new URLSearchParams(location.search).get('motion') === '0';

  function deferHeavyPanels(registry) {
    window.__P1_INTRO_DONE__ = Boolean(window.__P1_INTRO_DONE__);
    for (const name of ['P3', 'P6']) {
      let module;
      Object.defineProperty(registry, name, {
        configurable: true,
        enumerable: true,
        get: () => module,
        set: implementation => { module = lazyPanelModule(implementation, name); },
      });
    }
  }


  function lazyPanelModule(implementation, name) {
    return {
      create(element, data, HUD) {
        let instance = null;
        let destroyed = false;
        const start = () => {
          if (instance || destroyed || !window.__P1_INTRO_DONE__) return;
          element.replaceChildren();
          delete element.dataset.p1Deferred;
          instance = implementation.create(element, data, HUD);
        };
        const onIntroFinished = () => start();
        if (window.__P1_INTRO_DONE__) start();
        else {
          element.dataset.p1Deferred = name;
          element.innerHTML = `<div class="p1-deferred" role="status">${name} dimuat setelah intro</div>`;
          window.addEventListener('p1-intro-finished', onIntroFinished, { once: true });
        }
        return {
          update(state) { instance?.update?.(state); },
          resize() { instance?.resize?.(); },
          introIn(timeline, at) { return instance?.introIn?.(timeline, at); },
          destroy() {
            destroyed = true;
            window.removeEventListener('p1-intro-finished', onIntroFinished);
            instance?.destroy?.();
            element.replaceChildren();
          },
        };
      },
    };
  }

  function create(element, data, HUD) {
    if (!element) throw new Error('Panels.Sphere requires a host element');
    element.classList.add('p1-sphere');
    const panel = element.closest('.hero-panel');
    if (panel && element.parentElement !== panel) panel.appendChild(element);

    const layer = document.createElement('div');
    layer.className = 'p1-sphere__words';
    const tooltip = document.createElement('div');
    tooltip.className = 'p1-sphere__tooltip';
    tooltip.setAttribute('role', 'status');
    tooltip.hidden = true;
    element.append(layer, tooltip);
    moveNoteToFooter(element);

    const words = new Map();
    const points = new Map();
    let state = HUD?.state || { month: '2026-01', mode: 'khas', term: null, motion: true };
    let active = [];
    let rotation = 0;
    let lastPaint = 0;
    let lastFrame = 0;
    let animationFrame = 0;
    let renderVersion = 0;
    let dragging = null;
    let hovered = false;
    let rendering = false;
    let disposed = false;
    let layoutWidth = 1;
    let layoutHeight = 1;
    let paintCount = 0;

    const motionEnabled = () => !reducedMotion() && state.motion !== false;
    const sourceRows = current => {
      const source = window.IHSG_DATA || data;
      const month = source?.terms?.[current.month] || source?.terms?.['2026-01'] || {};
      return month[current.mode] || month.freq || month.khas || [];
    };

    function moveNoteToFooter(host) {
      const note = document.getElementById('hero-note');
      const footer = host.closest('.hero-panel')?.querySelector('.panel-footer');
      if (!note || !footer || footer.contains(note)) return;
      note.classList.add('p1-note-footer');
      footer.append(note);
      note.textContent = 'Pilih kata untuk menelusuri judul';
    }

    function visibleLimit() {
      if (layoutWidth >= 800) return 80;
      if (layoutWidth >= 600) return 55;
      return 40;
    }

    function displayLabel(label) {
      const text = String(label ?? '');
      return [...text].length > 22 ? `${[...text].slice(0, 21).join('').trimEnd()}…` : text;
    }

    function sizeFor(item, rank) {
      const score = Math.max(0, Number(item.score ?? item.df_share ?? 0));
      return rank <= 15
        ? clamp(18 + Math.sqrt(score * 45), 18, 23)
        : clamp(12 + Math.sqrt(score * 25), 12, 17);
    }

    function fibonacciPoints(rows) {
      const count = rows.length;
      rows.forEach((item, index) => {
        const latitude = 1 - 2 * (index + 0.5) / count;
        const radius = Math.sqrt(Math.max(0, 1 - latitude * latitude));
        const longitude = index * GOLDEN_ANGLE;
        const depth = Math.sin(longitude) * radius;
        const tilt = 1.05;
        const y = latitude * Math.cos(tilt) - depth * Math.sin(tilt);
        const z = latitude * Math.sin(tilt) + depth * Math.cos(tilt);
        const id = String(item.id ?? item.label);
        points.set(id, { x: Math.cos(longitude) * radius, y, z, index });
        const node = words.get(id);
        const size = sizeFor(item, index + 1);
        node.dataset.baseSize = String(size);
        node.dataset.rank = String(index + 1);
        node.style.fontSize = `${size}px`;
      });
    }

    function cacheWordSizes(rows) {
      rows.forEach(item => {
        const node = words.get(String(item.id ?? item.label));
        node.dataset.baseWidth = String(node.offsetWidth);
        node.dataset.baseHeight = String(node.offsetHeight);
      });
    }

    function layout() {
      layoutWidth = Math.max(1, element.clientWidth);
      layoutHeight = Math.max(1, element.clientHeight);
      if (!active.length) return;
      fibonacciPoints(active);
      cacheWordSizes(active);
      renderPositions();
    }

    function projectWords() {
      const cosine = Math.cos(rotation);
      const sine = Math.sin(rotation);
      return active.flatMap(item => {
        const id = String(item.id ?? item.label);
        const node = words.get(id);
        const point = points.get(id);
        if (!point) return [];
        const x = point.x * cosine + point.z * sine;
        const z = point.z * cosine - point.x * sine;
        const perspective = 1 / (1.15 - z * 0.12);
        const baseSize = Number(node.dataset.baseSize) || 18;
        const top = point.index < 15;
        const scale = top
          ? Math.max(18 / baseSize, 0.58 + (z + 1) * 0.21)
          : 0.65 + (z + 1) * 0.175;
        const boxWidth = Number(node.dataset.baseWidth) * scale + 8;
        const boxHeight = Number(node.dataset.baseHeight) * scale + 8;
        return [{
          node,
          z,
          scale,
          top,
          x: clamp(layoutWidth / 2 + x * layoutWidth * 0.46 * perspective, boxWidth / 2, layoutWidth - boxWidth / 2),
          y: clamp(layoutHeight / 2 - point.y * layoutHeight * 0.48 * perspective, boxHeight / 2, layoutHeight - boxHeight / 2),
          width: boxWidth,
          height: boxHeight,
        }];
      });
    }

    function seedNarrowHeadlines(projected) {
      if (layoutWidth >= 800) return;
      projected.filter(word => word.top).forEach(word => {
        const index = Number(word.node.dataset.rank) - 1;
        const column = index % 2;
        const row = Math.floor(index / 2);
        word.x = layoutWidth * (column === 0 ? 0.25 : 0.75)
          + Math.sin(index * 2.17 + rotation * 0.1) * 22;
        word.y = layoutHeight * (row + 0.5) / 8
          + Math.cos(index * 1.71 + rotation * 0.1) * 2;
      });
    }

    function separateHeadlines(projected) {
      const topWords = projected.filter(word => word.top);
      for (let pass = 0; pass < 90; pass++) {
        let changed = false;
        for (let left = 0; left < topWords.length; left++) {
          for (let right = left + 1; right < topWords.length; right++) {
            const a = topWords[left];
            const b = topWords[right];
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const overlapX = (a.width + b.width) / 2 + 3 - Math.abs(dx);
            const overlapY = (a.height + b.height) / 2 + 3 - Math.abs(dy);
            if (overlapX <= 0 || overlapY <= 0) continue;
            changed = true;
            if (overlapX < overlapY) {
              const shift = overlapX / 2 + 0.15;
              const direction = dx < 0 ? -1 : 1;
              a.x -= direction * shift;
              b.x += direction * shift;
            } else {
              const shift = overlapY / 2 + 0.15;
              const direction = dy < 0 ? -1 : 1;
              a.y -= direction * shift;
              b.y += direction * shift;
            }
            clampWord(a);
            clampWord(b);
          }
        }
        if (!changed) break;
      }
    }

    function clampWord(word) {
      word.x = clamp(word.x, word.width / 2, layoutWidth - word.width / 2);
      word.y = clamp(word.y, word.height / 2, layoutHeight - word.height / 2);
    }

    function overlaps(a, b) {
      return Math.abs(a.x - b.x) < (a.width + b.width) / 2
        && Math.abs(a.y - b.y) < (a.height + b.height) / 2;
    }

    function renderWords(projected) {
      const topWords = projected.filter(word => word.top);
      let visibleCount = 0;
      let visibleUnder18 = 0;
      for (const word of projected) {
        const baseSize = Number(word.node.dataset.baseSize) || 18;
        const renderedSize = baseSize * word.scale;
        const backgroundCollision = !word.top && topWords.some(top => overlaps(word, top));
        const visible = renderedSize >= 14 && !backgroundCollision;
        const depthOpacity = word.z < 0 ? 0.35 + (word.z + 1) * 0.15 : 0.5 + word.z * 0.45;
        word.node.style.transform = `translate3d(${word.x.toFixed(1)}px,${word.y.toFixed(1)}px,0) translate(-50%,-50%) scale(${word.scale.toFixed(3)})`;
        word.node.style.opacity = visible ? String(clamp(depthOpacity, 0.35, 0.95)) : '0';
        word.node.style.zIndex = String(Math.round((word.z + 1) * 50));
        word.node.dataset.depth = word.z.toFixed(3);
        word.node.dataset.renderedFontSize = renderedSize.toFixed(1);
        word.node.dataset.hiddenReason = visible ? '' : renderedSize < 14 ? 'size' : 'headline-collision';
        if (visible) visibleCount++;
        if (visible && renderedSize < 18) visibleUnder18++;
      }
      element.dataset.visibleWordCount = String(visibleCount);
      const heroCount = document.getElementById('hero-count');
      const heroText = `${visibleCount} DARI ${active.length} KATA`;
      if (heroCount && !rendering && heroCount.textContent !== heroText) heroCount.textContent = heroText;
      element.dataset.visibleUnder18 = String(visibleUnder18);
      element.dataset.rotation = rotation.toFixed(4);
      paintCount++;
      element.dataset.p1Paints = String(paintCount);
    }

    function renderPositions() {
      const projected = projectWords();
      seedNarrowHeadlines(projected);
      separateHeadlines(projected);
      renderWords(projected);
    }

    function createWord(item) {
      const id = String(item.id ?? item.label);
      let node = words.get(id);
      if (node) {
        node.textContent = displayLabel(item.label);
        node.title = String(item.label ?? '');
        node.dataset.fullLabel = String(item.label ?? '');
        node.classList.toggle('is-selected', state.term === id);
        return;
      }
      node = document.createElement('button');
      node.type = 'button';
      node.className = 'p1-word';
      node.dataset.term = id;
      node.setAttribute('aria-label', `${item.label}, ${item.df ?? ''} artikel`);
      Object.assign(node.style, {
        position: 'absolute', left: '0', top: '0', transformOrigin: 'center',
        background: 'transparent', border: '0', padding: '0', lineHeight: '1',
        color: '#8de9f7', font: '600 18px/1 system-ui', whiteSpace: 'nowrap', cursor: 'pointer',
      });
      node.textContent = displayLabel(item.label);
      node.title = String(item.label ?? '');
      node.dataset.fullLabel = String(item.label ?? '');
      node.dataset.cat = item.cat || 'term';
      node.classList.toggle('is-selected', state.term === id);
      node.addEventListener('click', () => HUD?.set?.({ term: item.id }));
      node.addEventListener('pointerenter', () => showTooltip(item));
      node.addEventListener('pointerleave', hideTooltip);
      node.addEventListener('focus', () => showTooltip(item));
      node.addEventListener('blur', hideTooltip);
      node.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        HUD?.set?.({ term: item.id });
      });
      words.set(id, node);
      layer.append(node);
    }

    function showTooltip(item) {
      hovered = true;
      tooltip.textContent = `${item.label} · muncul di ${item.df ?? ''} artikel`;
      tooltip.hidden = false;
    }

    function hideTooltip() {
      hovered = false;
      tooltip.hidden = true;
    }

    function scheduleRender(s) {
      state = s || state;
      element.dataset.month = state.month;
      element.dataset.mode = state.mode;
      const rows = sourceRows(state).slice(0, visibleLimit());
      element.dataset.activeCount = String(rows.length);
      element.dataset.firstRow = rows[0]?.id || '';
      const ids = new Set(rows.map(item => String(item.id ?? item.label)));
      for (const [id, node] of words) {
        if (ids.has(id)) continue;
        node.remove();
        words.delete(id);
        points.delete(id);
      }
      active = rows;
      const version = ++renderVersion;
      let index = 0;
      rendering = true;
      const batch = () => {
        if (disposed || version !== renderVersion) return;
        const limit = Math.min(index + 20, rows.length);
        while (index < limit) createWord(rows[index++]);
        if (index < rows.length) {
          requestAnimationFrame(batch);
          return;
        }
        rendering = false;
        layout();
        const count = document.getElementById('hero-count');
        if (count) count.textContent = `${active.length} KATA`;
        element.setAttribute('aria-label', `${active.length} kata ${state.mode}`);
      };
      requestAnimationFrame(batch);
    }

    function tick(timestamp) {
      animationFrame = 0;
      if (disposed || document.hidden) return;
      const interval = dragging ? 1000 / 60 : 1000 / 30;
      if (timestamp - lastPaint >= interval && !rendering) {
        const delta = lastFrame ? Math.min((timestamp - lastFrame) / 1000, 0.05) : 0;
        lastFrame = timestamp;
        if (motionEnabled() && !dragging && !hovered) rotation += delta * 0.08;
        renderPositions();
        lastPaint = timestamp;
      }
      if (motionEnabled() || dragging) animationFrame = requestAnimationFrame(tick);
    }

    function start() {
      if ((!motionEnabled() && !dragging) || animationFrame || disposed || document.hidden) return;
      animationFrame = requestAnimationFrame(tick);
    }

    function stop() {
      if (animationFrame) cancelAnimationFrame(animationFrame);
      animationFrame = 0;
    }

    function onResize() {
      const width = element.clientWidth;
      const height = element.clientHeight;
      if (width === layoutWidth && height === layoutHeight) return;
      layoutWidth = Math.max(1, width);
      layoutHeight = Math.max(1, height);
      scheduleRender(state);
    }

    function onPointerDown(event) {
      if (event.target.closest('.p1-word')) return;
      dragging = { x: event.clientX, rotation };
      element.setPointerCapture?.(event.pointerId);
      start();
    }

    function onPointerMove(event) {
      if (!dragging) return;
      rotation = dragging.rotation + (event.clientX - dragging.x) / Math.max(180, layoutWidth) * TAU;
      if (!motionEnabled()) renderPositions();
    }

    function onPointerUp() {
      dragging = null;
      if (motionEnabled()) start();
      else stop();
    }
    function onVisibilityChange() { document.hidden ? stop() : start(); }

    element.addEventListener('pointerdown', onPointerDown);
    element.addEventListener('pointermove', onPointerMove);
    element.addEventListener('pointerup', onPointerUp);
    element.addEventListener('pointercancel', onPointerUp);
    document.addEventListener('visibilitychange', onVisibilityChange);
    layoutWidth = Math.max(1, element.clientWidth);
    layoutHeight = Math.max(1, element.clientHeight);
    const resizeObserver = new ResizeObserver(onResize);
    resizeObserver.observe(element);
    const offMonth = HUD?.on?.('month', () => scheduleRender(HUD.state));
    const offMode = HUD?.on?.('mode', () => scheduleRender(HUD.state));
    const offTerm = HUD?.on?.('term', () => scheduleRender(HUD.state));
    scheduleRender(state);
    start();

    return {
      update: scheduleRender,
      introIn(timeline, at = 0) {
        return timeline?.fromTo?.(layer, { opacity: 0, scale: 0.92 }, { opacity: 1, scale: 1, duration: 0.55, ease: 'back.out(1.2)' }, at);
      },
      resize: onResize,
      destroy() {
        disposed = true;
        stop();
        resizeObserver.disconnect();
        document.removeEventListener('visibilitychange', onVisibilityChange);
        offMonth?.(); offMode?.(); offTerm?.();
        element.replaceChildren();
      },
    };
  }

  window.Panels ||= {};
  deferHeavyPanels(window.Panels);
  window.Panels.Sphere = { create };
})();
