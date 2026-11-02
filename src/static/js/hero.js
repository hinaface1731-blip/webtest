/* 3D-сцена главной: камера опускается по стволу скважины вслед за каротажным зондом.
   Стенка ствола — облако точек, муфтовые соединения — светящиеся кольца. */
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const canvas = document.getElementById('well');
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

function supportsWebGL() {
  try { return !!document.createElement('canvas').getContext('webgl2'); } catch { return false; }
}

if (canvas && supportsWebGL()) init();

function init() {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.setClearColor(0x05080d, 1);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x05080d, 0.022);
  const camera = new THREE.PerspectiveCamera(62, 1, 0.1, 200);

  const R = 4.2;           // радиус ствола
  const LEN = 160;         // длина участка, который зацикливается
  const SEG = LEN / 32;    // шаг муфт

  /* стенка скважины: точки на цилиндре со смещением «породы» */
  const N = innerWidth < 700 ? 16000 : 34000;
  const pos = new Float32Array(N * 3);
  const col = new Float32Array(N * 3);
  const cA = new THREE.Color(0x2f7dff);
  const cB = new THREE.Color(0x9fb3cc);
  const cC = new THREE.Color(0xff3b2f);
  for (let i = 0; i < N; i++) {
    const a = Math.random() * Math.PI * 2;
    const z = -Math.random() * LEN;
    // пласты: радиус и цвет меняются по глубине
    const layer = Math.sin(z * 0.35) * 0.5 + Math.sin(z * 0.11 + 1.3) * 0.5;
    const r = R + layer * 0.35 + (Math.random() - 0.5) * 0.25;
    pos[i * 3] = Math.cos(a) * r;
    pos[i * 3 + 1] = Math.sin(a) * r;
    pos[i * 3 + 2] = z;
    const c = cB.clone().lerp(cA, (layer + 1) / 2 * 0.8);
    if (Math.random() < 0.012) c.copy(cC);
    const k = 0.5 + Math.random() * 0.7;
    col[i * 3] = c.r * k; col[i * 3 + 1] = c.g * k; col[i * 3 + 2] = c.b * k;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const dot = makeDot();
  const mat = new THREE.PointsMaterial({ size: 0.11, map: dot, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true });
  // два одинаковых блока подряд — бесшовная прокрутка
  const wallA = new THREE.Points(g, mat);
  const wallB = new THREE.Points(g, mat);
  wallB.position.z = -LEN;
  scene.add(wallA, wallB);

  /* муфтовые кольца */
  const rings = new THREE.Group();
  for (let z = 0; z > -LEN * 2; z -= SEG) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(R + 0.05, Math.abs(z) % (SEG * 4) < 0.01 ? 0.02 : 0.008, 6, 120),
      new THREE.MeshBasicMaterial({ color: Math.abs(z) % (SEG * 4) < 0.01 ? 0xff3b2f : 0x2f7dff, transparent: true, opacity: Math.abs(z) % (SEG * 4) < 0.01 ? 0.7 : 0.28 }),
    );
    ring.position.z = z;
    rings.add(ring);
  }
  scene.add(rings);

  /* зонд на кабеле */
  const probe = new THREE.Group();
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0xc9d4e2, metalness: 0.45, roughness: 0.32 });
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 5.4, 40, 1), bodyMat);
  body.rotation.x = Math.PI / 2;
  probe.add(body);
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.38, 0.9, 40), bodyMat);
  tip.rotation.x = -Math.PI / 2; tip.position.z = -3.15;
  probe.add(tip);
  const glow = new THREE.MeshBasicMaterial({ color: 0xff3b2f });
  [-1.6, -0.2, 1.2].forEach((z) => {
    const band = new THREE.Mesh(new THREE.CylinderGeometry(0.392, 0.392, 0.12, 40), glow);
    band.rotation.x = Math.PI / 2; band.position.z = z; probe.add(band);
  });
  const blue = new THREE.MeshBasicMaterial({ color: 0x2f7dff });
  const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.06, 30), blue);
  lens.rotation.x = Math.PI / 2; lens.position.z = -3.6; probe.add(lens);
  const cable = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 60, 8), new THREE.MeshStandardMaterial({ color: 0x1b2533, metalness: 0.6, roughness: 0.5 }));
  cable.rotation.x = Math.PI / 2; cable.position.z = 32.7; probe.add(cable);
  scene.add(probe);

  const redLight = new THREE.PointLight(0xff3b2f, 14, 16, 1.6);
  scene.add(redLight);
  const blueLight = new THREE.PointLight(0x2f7dff, 10, 20, 1.6);
  scene.add(blueLight);
  scene.add(new THREE.HemisphereLight(0xbcd4ff, 0x1a0c0a, 1.4));
  const key = new THREE.DirectionalLight(0xffffff, 1.4);
  key.position.set(3, 4, 6); scene.add(key);

  /* состояние */
  let depth = 0;
  let speed = reduce ? 0 : 3.2;
  let boost = 0;
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', (e) => {
    mouse.tx = (e.clientX / innerWidth - 0.5) * 2;
    mouse.ty = (e.clientY / innerHeight - 0.5) * 2;
  }, { passive: true });
  let lastScroll = scrollY;
  addEventListener('scroll', () => { boost += Math.min(30, Math.abs(scrollY - lastScroll) * 0.08); lastScroll = scrollY; }, { passive: true });

  function resize() {
    const w = canvas.clientWidth; const h = canvas.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.fov = w < 700 ? 78 : 62;
    // на широких экранах ось скважины смещена вправо, чтобы не прятаться под заголовком
    if (w > 900) camera.setViewOffset(w, h, -w * 0.2, -h * 0.04, w, h); else camera.clearViewOffset();
    camera.updateProjectionMatrix();
  }
  addEventListener('resize', resize);
  resize();

  let visible = true;
  new IntersectionObserver(([en]) => { visible = en.isIntersecting; }).observe(canvas);

  const clock = new THREE.Clock();
  function frame() {
    requestAnimationFrame(frame);
    if (!visible) { clock.getDelta(); return; }
    const dt = Math.min(0.05, clock.getDelta());
    boost *= 0.92;
    depth += (speed + boost) * dt;
    const t = clock.elapsedTime;

    // бесшовная прокрутка стенки и колец
    const shift = depth % LEN;
    wallA.position.z = shift;
    wallB.position.z = shift - LEN;
    rings.position.z = depth % (SEG * 4);

    mouse.x += (mouse.tx - mouse.x) * 0.04;
    mouse.y += (mouse.ty - mouse.y) * 0.04;
    camera.position.set(mouse.x * 1.1 + 1.2, -mouse.y * 0.8 + 0.9, 6.5);
    camera.lookAt(0.4 + mouse.x * 0.4, 0.2, -12);
    camera.rotation.z += Math.sin(t * 0.2) * 0.02;

    probe.position.set(Math.sin(t * 0.7) * 0.25 + 0.5, Math.cos(t * 0.5) * 0.18 - 0.2, -4.6 + Math.sin(t * 0.4) * 0.6);
    probe.rotation.set(0.32 + Math.sin(t * 0.3) * 0.04, -0.42, t * 0.25);
    redLight.position.set(probe.position.x, probe.position.y, probe.position.z - 1);
    blueLight.position.set(probe.position.x, probe.position.y, probe.position.z - 5);
    glow.color.setHSL(0.01, 1, 0.5 + Math.sin(t * 4) * 0.08);

    renderer.render(scene, camera);
  }
  frame();
}

function makeDot() {
  const c = document.createElement('canvas');
  c.width = c.height = 64;
  const x = c.getContext('2d');
  const gr = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)');
  gr.addColorStop(0.3, 'rgba(255,255,255,.6)');
  gr.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = gr; x.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
