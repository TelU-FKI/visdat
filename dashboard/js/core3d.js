/* Local GLB hologram with measurable load and performance fallbacks. */
(() => {
  function create(host, data, HUD) {
    if (!host) throw new Error('Panels.Core3D requires a host element');
    host.classList.add('p1-core');
    host.dataset.glbStatus = 'loading';

    const canvas = makeCanvas();
    const fallback = makeFallbackImage();
    host.replaceChildren(fallback, canvas);
    const status = makeStatusElement();
    const debug = new URLSearchParams(location.search).get('debug') === '1';
    if (debug) document.body.append(status);

    const diagnostics = window.HUD_DEBUG ||= {};
    diagnostics.glb = {
      status: 'loading',
      loader: 'THREE.GLTFLoader r160 IIFE',
      loaderCalls: 0,
      source: 'assets/core.glb (file:// embedded copy)',
    };

    let renderer = null;
    let scene = null;
    let camera = null;
    let root = null;
    let mixer = null;
    let animationFrame = 0;
    let lastFrame = 0;
    let lastRender = 0;
    let disposed = false;
    let monitorAfter = Infinity;
    let consecutiveSlowWindows = 0;
    let renderDurations = [];
    let state = HUD?.state || {};
    let resizeObserver = null;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
      || new URLSearchParams(location.search).get('motion') === '0';
    const pulse = { value: 0 };
    const rotatingRings = [];
    const sectors = [];

    function makeCanvas() {
      const element = document.createElement('canvas');
      element.className = 'p1-core__canvas';
      Object.assign(element.style, {
        position: 'absolute', inset: '0', width: '100%', height: '100%',
        pointerEvents: 'none', opacity: '0.36',
      });
      return element;
    }

    function makeFallbackImage() {
      const image = document.createElement('img');
      image.className = 'p1-core__still';
      image.src = 'assets/core_still.png';
      image.alt = '';
      image.draggable = false;
      Object.assign(image.style, {
        position: 'absolute', inset: '14%', width: '72%', height: '72%',
        objectFit: 'contain', opacity: '0.055', pointerEvents: 'none',
      });
      return image;
    }

    function makeStatusElement() {
      const output = document.createElement('output');
      output.className = 'p1-glb-status';
      output.dataset.testid = 'glb-status';
      output.hidden = new URLSearchParams(location.search).get('debug') !== '1';
      output.textContent = 'GLB: memuat';
      Object.assign(output.style, {
        position: 'fixed', left: '8px', bottom: '8px', zIndex: '2500',
        padding: '6px 9px', color: '#9defff', background: '#061522e8',
        border: '1px solid #26d7f4', font: '18px monospace',
      });
      return output;
    }

    function setStatus(loaded, reason = '') {
      const value = loaded ? 'loaded' : 'fallback';
      host.dataset.glbStatus = value;
      if (reason) host.dataset.glbReason = reason;
      else delete host.dataset.glbReason;
      diagnostics.glb.status = value;
      diagnostics.glb.error = reason || undefined;
      status.textContent = loaded ? 'GLB: dimuat' : 'GLB: gagal, pakai pengganti';
      status.dataset.status = value;
    }

    function showFallback(reason) {
      if (disposed || diagnostics.glb.status === 'fallback') return;
      diagnostics.glb.fallbackReason = reason;
      canvas.hidden = true;
      fallback.hidden = false;
      renderer?.dispose();
      renderer = null;
      if (animationFrame) cancelAnimationFrame(animationFrame);
      animationFrame = 0;
      setStatus(false, reason);
    }

    function monthIndex(current) {
      if (current?.month === 'ALL') return 0;
      return Math.max(0, (Number(String(current?.month || '').slice(5)) || 1) - 1) % 12;
    }

    function applySectors() {
      const active = monthIndex(state);
      diagnostics.glb.activeSector = active;
      diagnostics.glb.activeSectorName = `sector_${String(active).padStart(2, '0')}`;
      for (const sector of sectors) {
        const selected = sector.index === active;
        for (const material of sector.materials) {
          material.color.set(selected ? 0xffb238 : 0x14758d);
          material.transparent = true;
          material.opacity = selected ? 0.78 : 0.18;
          material.needsUpdate = true;
        }
        sector.node.userData.p1Selected = selected;
        sector.node.scale.setScalar(selected ? 1.45 : 0.9);
        if (selected && sector.materials[0]) {
          diagnostics.glb.activeSectorMaterial = {
            color: sector.materials[0].color.getHexString(),
            opacity: sector.materials[0].opacity,
          };
        }
      }
    }

    function onStateChange() {
      const next = HUD?.state || state;
      const changed = next.month !== state.month || next.mode !== state.mode;
      state = next;
      applySectors();
      if (changed) pulseRings();
    }

    function pulseRings() {
      if (reduced) return;
      diagnostics.glb.pulseCount = (diagnostics.glb.pulseCount || 0) + 1;
      if (!window.gsap) {
        pulse.value = 1;
        return;
      }
      window.gsap.killTweensOf(pulse);
      window.gsap.fromTo(pulse, { value: 0 }, {
        value: 1, duration: 0.28, yoyo: true, repeat: 1, ease: 'power2.out',
      });
    }

    function resizeRenderer() {
      if (!renderer || !camera) return;
      renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.25));
      renderer.setSize(host.clientWidth, host.clientHeight, false);
      camera.aspect = host.clientWidth / Math.max(1, host.clientHeight);
      camera.updateProjectionMatrix();
    }

    function median(values) {
      const sorted = [...values].sort((a, b) => a - b);
      return sorted[Math.floor(sorted.length / 2)] || 0;
    }

    function recordRenderDuration(duration) {
      if (performance.now() < monitorAfter) return;
      renderDurations.push(duration);
      if (renderDurations.length < 30) return;
      const measuredMedian = median(renderDurations);
      renderDurations = [];
      diagnostics.glb.renderMedianMs = Number(measuredMedian.toFixed(2));
      diagnostics.glb.renderWindows = (diagnostics.glb.renderWindows || 0) + 1;
      consecutiveSlowWindows = measuredMedian > 33 ? consecutiveSlowWindows + 1 : 0;
      if (consecutiveSlowWindows >= 2) {
        showFallback(`3D render median ${measuredMedian.toFixed(1)} ms > 33 ms for 2 windows`);
      }
    }

    function animate(timestamp) {
      animationFrame = 0;
      if (disposed || document.hidden || !renderer) return;
      const delta = lastFrame ? Math.min((timestamp - lastFrame) / 1000, 0.05) : 0;
      lastFrame = timestamp;
      if (!reduced) {
        mixer?.update(delta);
        for (let index = 0; index < rotatingRings.length; index++) {
          const ring = rotatingRings[index];
          ring.rotation.y += delta * (index % 2 ? -0.075 : 0.055);
          ring.scale.setScalar(1 + pulse.value * 0.045);
        }
      }
      if (timestamp - lastRender >= 1000 / 30) {
        const start = performance.now();
        renderer.render(scene, camera);
        const elapsed = performance.now() - start;
        lastRender = timestamp;
        recordRenderDuration(elapsed);
      }
      if (renderer) animationFrame = requestAnimationFrame(animate);
    }

    function decodeEmbeddedGlb() {
      const encoded = window.P1_CORE_GLB_DATA;
      if (!encoded) throw new Error('Embedded core GLB data unavailable');
      const binary = atob(encoded);
      const buffer = new ArrayBuffer(binary.length);
      const bytes = new Uint8Array(buffer);
      for (let index = 0; index < binary.length; index++) bytes[index] = binary.charCodeAt(index);
      return buffer;
    }

    function materialsOf(object) {
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      return materials.filter(Boolean);
    }

    function tuneRing(node) {
      node.traverse(mesh => {
        if (!mesh.isMesh) return;
        const copies = materialsOf(mesh).map(original => {
          const material = original.clone();
          material.color?.set(0x1acdf0);
          material.emissive?.set(0x1acdf0);
          if (material.emissive) material.emissiveIntensity = 1.4;
          material.transparent = true;
          material.opacity = 0.5;
          return material;
        });
        mesh.material = Array.isArray(mesh.material) ? copies : copies[0];
      });
      rotatingRings.push(node);
    }

    function tuneSector(node, index) {
      node.scale.setScalar(1);
      const materials = [];
      node.traverse(mesh => {
        if (!mesh.isMesh) return;
        const originals = materialsOf(mesh);
        const copies = originals.map(() => new window.THREE.MeshBasicMaterial({
          color: 0x14758d, transparent: true, opacity: 0.18,
          depthWrite: false, side: window.THREE.DoubleSide, toneMapped: false,
        }));
        mesh.material = Array.isArray(mesh.material) ? copies : copies[0];
        materials.push(...copies);
      });
      sectors.push({ node, index, materials });
    }

    function indexModel(model) {
      const nodes = new Map();
      model.traverse(object => { if (object.name) nodes.set(object.name, object); });
      const orb = nodes.get('core_orb');
      const ticks = nodes.get('ticks');
      softenGroup(orb, 0.12);
      softenGroup(ticks, 0.12);
      for (const name of ['ring_a', 'ring_b', 'ring_c']) {
        const ring = nodes.get(name);
        if (ring) tuneRing(ring);
      }
      for (let index = 0; index < 12; index++) {
        const sector = nodes.get(`sector_${String(index).padStart(2, '0')}`);
        if (sector) tuneSector(sector, index);
      }
      diagnostics.glb.nodeNames = [...nodes.keys()];
      diagnostics.glb.sectorMaterialCounts = sectors.map(item => ({ index: item.index, count: item.materials.length }));
      return nodes;
    }

    function softenGroup(group, opacity) {
      if (!group) return;
      group.traverse(object => {
        if (!object.isMesh) return;
        for (const material of materialsOf(object)) {
          material.transparent = true;
          material.opacity = opacity;
          if (material.emissive) material.emissiveIntensity = opacity;
        }
      });
    }

    function runAssemblyAnimations(animations, THREE) {
      mixer = new THREE.AnimationMixer(root);
      for (const clip of animations || []) {
        const action = mixer.clipAction(clip);
        action.setLoop(THREE.LoopOnce, 1);
        action.clampWhenFinished = true;
        action.play();
      }
      if (!animations?.length) return;
      fallback.hidden = false;
      fallback.style.opacity = '0.035';
      window.setTimeout(() => {
        if (disposed || diagnostics.glb.status !== 'loaded') return;
        window.gsap?.to(fallback, { opacity: 0, duration: 0.4, onComplete: () => { fallback.hidden = true; } });
      }, 800);
    }

    function loadModel() {
      const THREE = window.THREE;
      if (!THREE?.GLTFLoader) {
        showFallback('GLTFLoader unavailable');
        return Promise.resolve(false);
      }
      const loader = new THREE.GLTFLoader();
      diagnostics.glb.loaderCalls++;
      diagnostics.glb.loaderCall = 'parse';
      let buffer;
      try { buffer = decodeEmbeddedGlb(); }
      catch (error) {
        showFallback(error.message);
        return Promise.resolve(false);
      }
      return new Promise((resolve, reject) => loader.parse(buffer, 'assets/', resolve, reject))
        .then(gltf => {
          if (disposed) return false;
          if (root) scene.remove(root);
          root = gltf.scene;
          root.scale.setScalar(0.5);
          scene.add(root);
          runAssemblyAnimations(gltf.animations, THREE);
          indexModel(root);
          applySectors();
          canvas.hidden = false;
          setStatus(true);
          return true;
        })
        .catch(error => {
          showFallback(error?.message || String(error));
          return false;
        });
    }

    function initializeRenderer() {
      const THREE = window.THREE;
      if (window.HUD_DEBUG_FORCE_NO_WEBGL || !THREE?.WebGLRenderer) {
        showFallback(window.HUD_DEBUG_FORCE_NO_WEBGL ? 'WebGL unavailable (forced QA)' : 'WebGL unavailable');
        return;
      }
      try {
        renderer = new THREE.WebGLRenderer({
          canvas, alpha: true, antialias: false, powerPreference: 'low-power',
        });
        renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.25));
        renderer.setSize(host.clientWidth, host.clientHeight, false);
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(32, host.clientWidth / Math.max(1, host.clientHeight), 0.1, 100);
        camera.position.z = 5;
        const material = new THREE.MeshBasicMaterial({
          color: 0x26d7f4, transparent: true, opacity: 0.45, wireframe: true,
        });
        const placeholder = new THREE.Group();
        for (let index = 0; index < 3; index++) {
          const ring = new THREE.Mesh(new THREE.TorusGeometry(1 + index * 0.25, 0.012, 4, 80), material);
          ring.name = `ring_${String.fromCharCode(97 + index)}`;
          ring.rotation.x = Math.PI / 2 + index * 0.48;
          placeholder.add(ring);
          rotatingRings.push(ring);
        }
        root = placeholder;
        scene.add(root);
        loadModel().then(loaded => {
          if (loaded && !animationFrame) animationFrame = requestAnimationFrame(animate);
        });
        animationFrame = requestAnimationFrame(animate);
      } catch (error) {
        showFallback(error?.message || String(error));
      }
    }

    function beginPerformanceWarmup() {
      monitorAfter = performance.now() + 3000;
      renderDurations = [];
      consecutiveSlowWindows = 0;
      diagnostics.glb.performanceMonitor = 'warming up for 3000ms after intro';
    }

    function onVisibilityChange() {
      if (document.hidden) {
        if (animationFrame) cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      } else if (!animationFrame && renderer) {
        animationFrame = requestAnimationFrame(animate);
      }
    }

    const offMonth = HUD?.on?.('month', onStateChange);
    const offMode = HUD?.on?.('mode', onStateChange);
    const onIntroFinished = () => beginPerformanceWarmup();
    window.addEventListener('p1-intro-finished', onIntroFinished);
    document.addEventListener('visibilitychange', onVisibilityChange);
    resizeObserver = new ResizeObserver(resizeRenderer);
    resizeObserver.observe(host);
    initializeRenderer();

    return {
      update(nextState) { state = nextState || state; applySectors(); },
      introIn(timeline, at = 0) {
        return timeline?.fromTo?.(host, { opacity: 0, scale: 0.82 }, { opacity: 1, scale: 1, duration: 0.7, ease: 'power2.out' }, at);
      },
      resize: resizeRenderer,
      destroy() {
        disposed = true;
        if (animationFrame) cancelAnimationFrame(animationFrame);
        offMonth?.(); offMode?.();
        window.removeEventListener('p1-intro-finished', onIntroFinished);
        document.removeEventListener('visibilitychange', onVisibilityChange);
        resizeObserver?.disconnect();
        renderer?.dispose();
        status.remove();
        host.replaceChildren();
      },
    };
  }

  window.Panels ||= {};
  window.Panels.Core3D = { create };
})();
