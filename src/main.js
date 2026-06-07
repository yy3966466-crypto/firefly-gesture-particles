import * as THREE from 'three';
import { isMobile, PARTICLE_COUNT, dist, rand } from './utils.js';
import { createVideoElement } from './camera.js';
import { createScene, handleResize, setVideoAspect } from './scene.js';

// ── 粒子 Shader ──
const vertShader = /* glsl */ `
  attribute float size;
  attribute float alpha;
  varying float vAlpha;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (200.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
    vAlpha = alpha;
  }
`;

const fragShader = /* glsl */ `
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float glow = exp(-d * 4.0);
    gl_FragColor = vec4(1.0, 1.0, 1.0, glow * vAlpha);
  }
`;

// ── 粒子系统 ──
function createParticles(w, h) {
  const count = PARTICLE_COUNT;
  const pos = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);
  const baseX = new Float32Array(count);
  const baseY = new Float32Array(count);
  const phase = new Float32Array(count);
  const amp = new Float32Array(count);
  const freq = new Float32Array(count);
  const vx = new Float32Array(count);
  const vy = new Float32Array(count);

  for (let i = 0; i < count; i++) {
    baseX[i] = rand(0, w);
    baseY[i] = rand(0, h);
    pos[i * 3] = baseX[i];
    pos[i * 3 + 1] = baseY[i];
    sizes[i] = rand(1.5, 3.5);
    alphas[i] = rand(0.3, 0.7);
    phase[i] = rand(0, Math.PI * 2);
    amp[i] = rand(15, 50);
    freq[i] = rand(0.3, 1.0);
    vx[i] = 0;
    vy[i] = 0;
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));

  const mat = new THREE.ShaderMaterial({
    vertexShader: vertShader,
    fragmentShader: fragShader,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: false
  });

  const points = new THREE.Points(geo, mat);
  return { points, geo, mat, pos, sizes, alphas, baseX, baseY, phase, amp, freq, vx, vy, count };
}

// ── 水波纹动画 ──
const ripples = [];

function spawnRipple(x, y) {
  ripples.push({ x, y, radius: 0, strength: 1.0, life: 0, maxLife: 2.5 });
}

function updateParticles(p, time, dt, w, h) {
  for (let i = 0; i < p.count; i++) {
    // 默认波浪
    let tx = p.baseX[i] + p.amp[i] * Math.sin(p.freq[i] * time + p.phase[i]);
    let ty = p.baseY[i] + p.amp[i] * 0.6 * Math.cos(p.freq[i] * time * 1.2 + p.phase[i] + 1);

    // 涟漪力
    for (const r of ripples) {
      const d = dist(tx, ty, r.x, r.y);
      if (d < r.radius + 40 && d > 0.1) {
        const force = r.strength * (1 - d / (r.radius + 40)) * 30;
        const dx = (tx - r.x) / d;
        const dy = (ty - r.y) / d;
        tx += dx * force;
        ty += dy * force;
        p.vx[i] += dx * force * 0.5;
        p.vy[i] += dy * force * 0.5;
      }
    }

    // 惯性衰减
    tx += p.vx[i];
    ty += p.vy[i];
    p.vx[i] *= 0.92;
    p.vy[i] *= 0.92;

    // 边界
    if (tx < 0) tx = 0;
    if (tx > w) tx = w;
    if (ty < 0) ty = 0;
    if (ty > h) ty = h;

    p.pos[i * 3] = tx;
    p.pos[i * 3 + 1] = ty;
  }

  // 更新涟漪
  for (let i = ripples.length - 1; i >= 0; i--) {
    ripples[i].life += dt;
    ripples[i].radius += dt * 200;
    ripples[i].strength = 1 - ripples[i].life / ripples[i].maxLife;
    if (ripples[i].life >= ripples[i].maxLife) ripples.splice(i, 1);
  }

  p.geo.attributes.position.needsUpdate = true;
}

// ── 涟漪视觉环 ──
function createRippleVisuals(scene) {
  const rings = [];
  return {
    spawn(x, y) {
      const geo = new THREE.RingGeometry(5, 8, 48);
      const mat = new THREE.MeshBasicMaterial({
        color: 0xffffff, side: THREE.DoubleSide, transparent: true, opacity: 0.4, depthTest: false, depthWrite: false
      });
      const ring = new THREE.Mesh(geo, mat);
      ring.position.set(x, y, 0.1);
      scene.add(ring);
      rings.push({ mesh: ring, mat, age: 0, maxAge: 1.5, r: 10 });
    },
    update(dt) {
      for (let i = rings.length - 1; i >= 0; i--) {
        const r = rings[i];
        r.age += dt;
        const t = r.age / r.maxAge;
        if (t >= 1) {
          scene.remove(r.mesh);
          r.mesh.geometry.dispose();
          r.mat.dispose();
          rings.splice(i, 1);
          continue;
        }
        const radius = 10 + 280 * t;
        r.mesh.geometry.dispose();
        r.mesh.geometry = new THREE.RingGeometry(radius - 2, radius + 2, 48);
        r.mat.opacity = 0.4 * (1 - t);
      }
    }
  };
}

// ── 主程序 ──
async function main() {
  const video = createVideoElement();
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
  });
  video.srcObject = stream;
  await video.play();
  setTimeout(() => setVideoAspect(video), 300);

  const { renderer, scene, camera, bgPlane } = createScene(video);
  const p = createParticles(window.innerWidth, window.innerHeight);
  scene.add(p.points);

  const ringViz = createRippleVisuals(scene);

  // UI
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('guidance').classList.remove('hidden');
  setTimeout(() => document.getElementById('guidance').classList.add('hidden'), 4000);

  // 触摸/点击 → 涟漪
  function onInteract(e) {
    const x = e.touches ? e.touches[0].clientX : e.clientX;
    const y = e.touches ? e.touches[0].clientY : e.clientY;
    spawnRipple(x, y);
    ringViz.spawn(x, y);
  }
  window.addEventListener('touchstart', onInteract, { passive: true });
  window.addEventListener('click', onInteract);

  // 渲染循环
  let last = performance.now();
  function loop(now) {
    requestAnimationFrame(loop);
    let dt = (now - last) / 1000;
    if (dt <= 0) dt = 0.016;
    if (dt > 0.1) dt = 0.1;
    last = now;
    updateParticles(p, now / 1000, dt, window.innerWidth, window.innerHeight);
    ringViz.update(dt);
    renderer.render(scene, camera);
  }
  requestAnimationFrame(loop);

  window.addEventListener('resize', () => {
    handleResize({ renderer, camera, bgPlane });
    setVideoAspect(video);
  });
}

main().catch(err => {
  document.getElementById('loading').innerHTML =
    `<p style="color:#ff6b6b;">启动失败: ${err.message}<br><small>请使用 HTTPS 并允许摄像头</small></p>`;
});
