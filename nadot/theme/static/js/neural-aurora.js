(function() {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (typeof THREE === 'undefined') return;
  if (sessionStorage.getItem('na_no_canvas') === '1') return;

  var scene, camera, renderer;
  var starField, dataDots, glowOrbs, connectionLines, lightBeacon, floatingNodes;
  var mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  var isActive = false;
  var frameId = null;
  var clock = new THREE.Clock();
  var colors = {};
  var nodes = [];
  var orbMeshes = [];

  var isMobile = /Mobi|Android/i.test(navigator.userAgent);
  var DPR = Math.min(window.devicePixelRatio, 2);

  function getCSSVar(name) {
    try {
      return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    } catch (e) {
      return '';
    }
  }

  function hexToThree(hex) {
    if (!hex || hex === 'transparent') return 0x14b8a6;
    hex = hex.replace('#', '');
    return parseInt(hex, 16);
  }

  function readColors() {
    var isDark = document.documentElement.classList.contains('dark');
    colors = {
      bg: hexToThree(getCSSVar('--bg-primary')),
      teal: hexToThree(getCSSVar('--aurora-teal')),
      purple: hexToThree(getCSSVar('--aurora-purple')),
      cyan: hexToThree(getCSSVar('--aurora-cyan')),
      pink: hexToThree(getCSSVar('--aurora-pink')),
      isDark: isDark,
    };
  }

  function initNeuralAurora() {
    try {
      var container = document.getElementById('neural-aurora-bg');
      if (!container || isActive) return;

      var testCanvas = document.createElement('canvas');
      var gl = testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl');
      if (!gl) {
        sessionStorage.setItem('na_no_canvas', '1');
        container.style.display = 'none';
        return;
      }

      isActive = true;
      clock = new THREE.Clock();
      scene = new THREE.Scene();
      readColors();
      scene.background = new THREE.Color(colors.bg);

      var W = window.innerWidth;
      var H = window.innerHeight;

      camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 100);
      camera.position.set(0, 0, 14);

      renderer = new THREE.WebGLRenderer({
        antialias: !isMobile,
        powerPreference: 'high-performance',
        alpha: false,
      });
      renderer.setSize(W, H);
      renderer.setPixelRatio(DPR);
      container.appendChild(renderer.domElement);

      container.style.opacity = '0';
      container.style.transition = 'opacity 1.2s ease';
      requestAnimationFrame(function() {
        container.style.opacity = '1';
      });

      createStarField();
      createDataDots();
      createGlowOrbs();
      createFloatingNodes();
      createConnectionLines();
      createLightBeacon();

      window.addEventListener('mousemove', onMouseMove, { passive: true });
      window.addEventListener('resize', onResize, { passive: true });
      window.addEventListener('themeChanged', onThemeChange);
      document.addEventListener('webglcontextlost', onContextLost);

      animate();

      window.__neuralAurora = { init: initNeuralAurora, destroy: destroyNeuralAurora };
    } catch (e) {
      console.warn('Neural aurora init failed:', e);
      sessionStorage.setItem('na_no_canvas', '1');
      var container = document.getElementById('neural-aurora-bg');
      if (container) container.style.display = 'none';
    }
  }

  function updateMaterialColors() {
    readColors();
    if (!scene) return;
    scene.background = new THREE.Color(colors.bg);

    if (starField) starField.material.color.setHex(colors.teal);
    if (dataDots) dataDots.material.color.setHex(colors.cyan);

    if (connectionLines) {
      connectionLines.system.material.color.setHex(colors.teal);
    }

    if (lightBeacon) {
      lightBeacon.material.color.setHex(colors.teal);
    }

    if (orbMeshes.length) {
      orbMeshes.forEach(function(orb, i) {
        var c = i % 3 === 0 ? colors.teal : (i % 3 === 1 ? colors.purple : colors.cyan);
        orb.material.color.setHex(c);
      });
    }

    if (nodes.length) {
      nodes.forEach(function(node, i) {
        var c = i % 2 === 0 ? colors.cyan : colors.pink;
        node.mesh.material.color.setHex(c);
      });
    }
  }

  function createStarField() {
    var count = isMobile ? 400 : 900;
    var positions = new Float32Array(count * 3);
    var sizes = new Float32Array(count);

    for (var i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 60;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 60;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 40 - 10;
      sizes[i] = Math.random() * 0.12 + 0.02;
    }

    var geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    var material = new THREE.PointsMaterial({
      size: 0.06,
      color: colors.teal,
      transparent: true,
      opacity: 0.25,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
      depthWrite: false,
    });

    starField = new THREE.Points(geometry, material);
    scene.add(starField);
  }

  function createDataDots() {
    var count = isMobile ? 180 : 400;
    var positions = new Float32Array(count * 3);
    var speeds = new Float32Array(count);
    var offsets = new Float32Array(count);

    for (var i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 30;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 24;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 16;
      speeds[i] = Math.random() * 0.3 + 0.1;
      offsets[i] = Math.random() * Math.PI * 2;
    }

    var geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.userData = { speeds: speeds, offsets: offsets, initialPositions: new Float32Array(positions) };

    var material = new THREE.PointsMaterial({
      size: 0.12,
      color: colors.cyan,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
      depthWrite: false,
    });

    dataDots = new THREE.Points(geometry, material);
    dataDots.userData = { speeds: speeds, offsets: offsets };
    scene.add(dataDots);
  }

  function createGlowOrbs() {
    var count = isMobile ? 3 : 6;
    glowOrbs = [];
    orbMeshes = [];

    var orbColors = [colors.teal, colors.purple, colors.cyan, colors.teal, colors.pink, colors.purple];

    for (var i = 0; i < count; i++) {
      var size = Math.random() * 1.2 + 0.8;
      var geometry = new THREE.SphereGeometry(size, 24, 24);
      var material = new THREE.MeshBasicMaterial({
        color: orbColors[i],
        transparent: true,
        opacity: 0.03,
        depthWrite: false,
      });

      var orb = new THREE.Mesh(geometry, material);
      orb.position.set(
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 14,
        (Math.random() - 0.5) * 12 - 6,
      );

      var glowGeometry = new THREE.SphereGeometry(size * 2.5, 16, 16);
      var glowMaterial = new THREE.MeshBasicMaterial({
        color: orbColors[i],
        transparent: true,
        opacity: 0.015,
        depthWrite: false,
      });
      var glow = new THREE.Mesh(glowGeometry, glowMaterial);

      orb.add(glow);
      scene.add(orb);

      glowOrbs.push({
        mesh: orb,
        glow: glow,
        phaseX: Math.random() * Math.PI * 2,
        phaseY: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.15 + 0.08,
        radiusX: Math.random() * 4 + 2,
        radiusY: Math.random() * 3 + 1.5,
        baseX: orb.position.x,
        baseY: orb.position.y,
        baseZ: orb.position.z,
        pulsePhase: Math.random() * Math.PI * 2,
      });
      orbMeshes.push(orb);
    }
  }

  function createFloatingNodes() {
    var count = isMobile ? 8 : 16;
    nodes = [];

    for (var i = 0; i < count; i++) {
      var pos = new THREE.Vector3(
        (Math.random() - 0.5) * 16,
        (Math.random() - 0.5) * 12,
        (Math.random() - 0.5) * 8 - 3,
      );

      var sphere = new THREE.Mesh(
        new THREE.SphereGeometry(0.08, 10, 10),
        new THREE.MeshBasicMaterial({
          color: i % 2 === 0 ? colors.cyan : colors.pink,
          transparent: true,
          opacity: 0.7,
          depthWrite: false,
        }),
      );
      sphere.position.copy(pos);

      var glowRing = new THREE.Mesh(
        new THREE.RingGeometry(0.12, 0.2, 16),
        new THREE.MeshBasicMaterial({
          color: i % 2 === 0 ? colors.cyan : colors.pink,
          transparent: true,
          opacity: 0.2,
          side: THREE.DoubleSide,
          depthWrite: false,
        }),
      );
      glowRing.position.copy(pos);

      scene.add(sphere);
      scene.add(glowRing);

      nodes.push({
        mesh: sphere,
        ring: glowRing,
        initialPos: pos.clone(),
        phase: Math.random() * Math.PI * 2,
        floatSpeed: Math.random() * 0.3 + 0.2,
        floatAmp: Math.random() * 0.3 + 0.15,
        ringPhase: Math.random() * Math.PI * 2,
      });
    }
  }

  function createConnectionLines() {
    var pairs = [];
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var d = nodes[i].initialPos.distanceTo(nodes[j].initialPos);
        if (d < 6 && Math.random() < 0.5) {
          pairs.push({ a: i, b: j, maxDist: d });
        }
      }
    }

    var positions = new Float32Array(pairs.length * 6);
    var alphas = new Float32Array(pairs.length);

    pairs.forEach(function(p, idx) {
      positions[idx * 6] = nodes[p.a].initialPos.x;
      positions[idx * 6 + 1] = nodes[p.a].initialPos.y;
      positions[idx * 6 + 2] = nodes[p.a].initialPos.z;
      positions[idx * 6 + 3] = nodes[p.b].initialPos.x;
      positions[idx * 6 + 4] = nodes[p.b].initialPos.y;
      positions[idx * 6 + 5] = nodes[p.b].initialPos.z;
      alphas[idx] = 0;
    });

    var geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    var material = new THREE.LineBasicMaterial({
      color: colors.teal,
      transparent: true,
      opacity: 0.08,
      depthWrite: false,
    });

    connectionLines = {
      system: new THREE.LineSegments(geometry, material),
      pairs: pairs,
      alphas: alphas,
    };
    scene.add(connectionLines.system);
  }

  function createLightBeacon() {
    var geometry = new THREE.SphereGeometry(0.4, 16, 16);
    var material = new THREE.MeshBasicMaterial({
      color: colors.teal,
      transparent: true,
      opacity: 0.15,
      depthWrite: false,
    });
    lightBeacon = new THREE.Mesh(geometry, material);
    lightBeacon.position.set(0, 0, 4);
    scene.add(lightBeacon);
  }

  function animate() {
    if (!isActive) return;
    frameId = requestAnimationFrame(animate);

    var t = clock.getElapsedTime();

    mouse.targetX += (mouse.x - mouse.targetX) * 0.05;
    mouse.targetY += (mouse.y - mouse.targetY) * 0.05;

    if (starField) {
      starField.rotation.y = t * 0.008;
      starField.rotation.x = Math.sin(t * 0.005) * 0.04;
    }

    if (dataDots) {
      var posArr = dataDots.geometry.attributes.position.array;
      var speeds = dataDots.userData.speeds;
      var offsets = dataDots.userData.offsets;
      var count = posArr.length / 3;

      for (var di = 0; di < count; di++) {
        var i3 = di * 3;
        var ox = posArr[i3];
        var oy = posArr[i3 + 1];
        var driftX = Math.sin(t * speeds[di] + offsets[di]) * 0.15;
        var driftY = Math.cos(t * speeds[di] * 0.7 + offsets[di]) * 0.15;
        var mPullX = (mouse.targetX * 0.3 - ox * 0.01) * 0.01;
        var mPullY = (mouse.targetY * 0.3 - oy * 0.01) * 0.01;
        posArr[i3] += driftX * 0.005 + mPullX;
        posArr[i3 + 1] += driftY * 0.005 + mPullY;
      }
      dataDots.geometry.attributes.position.needsUpdate = true;
    }

    if (glowOrbs) {
      glowOrbs.forEach(function(orb) {
        orb.mesh.position.x = orb.baseX + Math.sin(t * orb.speed + orb.phaseX) * orb.radiusX;
        orb.mesh.position.y = orb.baseY + Math.cos(t * orb.speed * 0.8 + orb.phaseY) * orb.radiusY;
        orb.mesh.position.z = orb.baseZ + Math.sin(t * orb.speed * 0.5 + orb.phaseX) * 1.5;

        var pulse = 0.5 + Math.sin(t * 0.5 + orb.pulsePhase) * 0.5;
        orb.mesh.material.opacity = 0.02 + pulse * 0.025;
        orb.glow.material.opacity = 0.01 + pulse * 0.015;
      });
    }

    if (nodes.length) {
      nodes.forEach(function(node, i) {
        var float = Math.sin(t * node.floatSpeed + node.phase) * node.floatAmp;
        node.mesh.position.y = node.initialPos.y + float;
        node.mesh.position.x = node.initialPos.x + Math.sin(t * 0.2 + node.phase) * 0.1;
        node.ring.position.copy(node.mesh.position);
        node.ring.material.opacity = 0.1 + Math.sin(t * 0.6 + node.ringPhase) * 0.1;
        var ringScale = 0.8 + Math.sin(t * 0.4 + node.ringPhase) * 0.3;
        node.ring.scale.set(ringScale, ringScale, 1);
        node.ring.lookAt(camera.position);
      });
    }

    if (connectionLines) {
      var posArr2 = connectionLines.system.geometry.attributes.position.array;
      connectionLines.pairs.forEach(function(p, idx) {
        var i3 = idx * 6;
        var nodeA = nodes[p.a];
        var nodeB = nodes[p.b];
        if (!nodeA || !nodeB) return;
        posArr2[i3] = nodeA.mesh.position.x;
        posArr2[i3 + 1] = nodeA.mesh.position.y;
        posArr2[i3 + 2] = nodeA.mesh.position.z;
        posArr2[i3 + 3] = nodeB.mesh.position.x;
        posArr2[i3 + 4] = nodeB.mesh.position.y;
        posArr2[i3 + 5] = nodeB.mesh.position.z;

        var currentDist = nodeA.mesh.position.distanceTo(nodeB.mesh.position);
        var fade = Math.max(0, 1 - currentDist / p.maxDist);
        var pulse = 0.5 + Math.sin(t * 0.5 + idx) * 0.5;
        connectionLines.alphas[idx] = fade * pulse;
      });
      connectionLines.system.geometry.attributes.position.needsUpdate = true;

      var totalAlpha = 0;
      var alphaCount = 0;
      for (var ci = 0; ci < connectionLines.alphas.length; ci++) {
        totalAlpha += connectionLines.alphas[ci];
        alphaCount++;
      }
      connectionLines.system.material.opacity = 0.04 + (totalAlpha / (alphaCount || 1)) * 0.12;
    }

    if (lightBeacon) {
      var bx = mouse.targetX * 2;
      var by = mouse.targetY * 2;
      lightBeacon.position.x += (bx - lightBeacon.position.x) * 0.03;
      lightBeacon.position.y += (by - lightBeacon.position.y) * 0.03;
      lightBeacon.position.z = 3 + Math.sin(t * 0.3) * 0.5;
      lightBeacon.material.opacity = 0.08 + Math.sin(t * 0.5) * 0.04;
    }

    renderer.render(scene, camera);
  }

  function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  }

  var resizeTimeout;
  function onResize() {
    if (resizeTimeout) cancelAnimationFrame(resizeTimeout);
    resizeTimeout = requestAnimationFrame(function() {
      if (!camera || !renderer) return;
      var W = window.innerWidth;
      var H = window.innerHeight;
      camera.aspect = W / H;
      camera.updateProjectionMatrix();
      renderer.setSize(W, H);
      renderer.setPixelRatio(DPR);
    });
  }

  function onThemeChange(e) {
    if (!scene) return;
    updateMaterialColors();
  }

  function onContextLost() {
    sessionStorage.setItem('na_no_canvas', '1');
    destroyNeuralAurora();
  }

  function destroyNeuralAurora() {
    if (!isActive) return;
    isActive = false;

    if (frameId) cancelAnimationFrame(frameId);

    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('resize', onResize);
    window.removeEventListener('themeChanged', onThemeChange);
    document.removeEventListener('webglcontextlost', onContextLost);

    if (renderer) {
      renderer.dispose();
      var container = document.getElementById('neural-aurora-bg');
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
    }

    scene = null;
    camera = null;
    renderer = null;
    starField = null;
    dataDots = null;
    glowOrbs = null;
    connectionLines = null;
    lightBeacon = null;
    floatingNodes = null;
    nodes = [];
    orbMeshes = [];
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNeuralAurora);
  } else {
    initNeuralAurora();
  }
})();
