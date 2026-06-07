import * as THREE from 'three';
import { PARTICLE_COUNT, rand, dist, lerp } from './utils.js';
import { createVideoElement } from './camera.js';
import { createScene, handleResize, setVideoAspect } from './scene.js';
import { initHandDetector, countFingers, getIndexTip } from './hand-detector.js';
import { textToPositions } from './text-particles.js';

// ══════════════ Shader ══════════════
const vertShader = /* glsl */ `
  attribute float size; attribute float alpha;
  varying float vAlpha;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (200.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
    vAlpha = alpha;
  }`;
const fragShader = /* glsl */ `
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    gl_FragColor = vec4(1.0, 1.0, 1.0, exp(-d * 3.5) * vAlpha);
  }`;

// ══════════════ 文字粒子模板 ══════════════
let textTargetClaude = null;
let textTargetLove = null;

function ensureTextTargets() {
  if (!textTargetClaude) textTargetClaude = textToPositions('claude code', { fontSize: 70, particleCount: PARTICLE_COUNT });
  if (!textTargetLove) textTargetLove = textToPositions('love life', { fontSize: 70, particleCount: PARTICLE_COUNT });
}

// ══════════════ 粒子系统 ══════════════
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
    baseX[i] = rand(0, w); baseY[i] = rand(0, h);
    pos[i * 3] = baseX[i]; pos[i * 3 + 1] = baseY[i];
    sizes[i] = rand(1.5, 4);
    alphas[i] = rand(0.25, 0.65);
    phase[i] = rand(0, Math.PI * 2);
    amp[i] = rand(10, 45);
    freq[i] = rand(0.2, 0.8);
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
  geo.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));

  const mat = new THREE.ShaderMaterial({
    vertexShader: vertShader, fragmentShader: fragShader,
    transparent: true, blending: THREE.AdditiveBlending,
    depthWrite: false, depthTest: false
  });

  return { points: new THREE.Points(geo, mat), geo, mat, pos, sizes, alphas,
    baseX, baseY, phase, amp, freq, vx, vy, count };
}

// ══════════════ 状态机 ══════════════
const State = { IDLE: 0, ONE_EXPLODE: 1, TWO_FORM: 2, TWO_HOLD: 3, THREE_FORM: 4, THREE_HOLD: 5 };
let state = State.IDLE;
let stateTimer = 0;
let stateTargets = null;   // 当前动画的目标位置
let stateStartPos = null;  // 动画起始位置快照
let prevFingers = 0;

function handleGesture(p, screenW, screenH) {
  const fingers = countFingers();
  const dt = 0.016;

  // 手指变化检测
  if (fingers !== prevFingers) {
    if (fingers === 1 && state === State.IDLE) {
      // 1 指：食指指尖聚集 → 炸开
      state = State.ONE_EXPLODE;
      stateTimer = 0;
      const tip = getIndexTip(screenW, screenH);
      if (tip) {
        for (let i = 0; i < p.count; i++) {
          const angle = rand(0, Math.PI * 2);
          const speed = rand(30, 80);
          p.vx[i] = Math.cos(angle) * speed;
          p.vy[i] = Math.sin(angle) * speed;
          p.pos[i * 3] = tip.x;
          p.pos[i * 3 + 1] = tip.y;
          p.alphas[i] = 1.0;
          p.sizes[i] = rand(2, 5);
        }
        p.geo.attributes.position.needsUpdate = true;
      }
    } else if (fingers === 2 && (state === State.IDLE || state === State.ONE_EXPLODE)) {
      ensureTextTargets();
      state = State.TWO_FORM;
      stateTimer = 0;
      stateTargets = textTargetClaude;
      stateStartPos = new Float32Array(p.pos);
      for (let i = 0; i < p.count; i++) { p.sizes[i] = rand(2, 5); p.alphas[i] = 0.9; }
    } else if (fingers === 3 && (state === State.IDLE || state === State.ONE_EXPLODE)) {
      ensureTextTargets();
      state = State.THREE_FORM;
      stateTimer = 0;
      stateTargets = textTargetLove;
      stateStartPos = new Float32Array(p.pos);
      for (let i = 0; i < p.count; i++) { p.sizes[i] = rand(2, 5); p.alphas[i] = 0.9; }
    }
  }

  prevFingers = fingers;
  return fingers;
}

function updateState(p, dt, screenW, screenH) {
  stateTimer += dt;

  switch (state) {
    case State.ONE_EXPLODE:
      // 炸开后粒子自由飞行，自然衰减回归
      for (let i = 0; i < p.count; i++) {
        p.vx[i] *= 0.93; p.vy[i] *= 0.93;
        p.pos[i * 3] += p.vx[i] * dt;
        p.pos[i * 3 + 1] += p.vy[i] * dt;
        p.alphas[i] = Math.max(0.3, p.alphas[i] - dt * 0.5);
      }
      p.geo.attributes.position.needsUpdate = true;
      if (stateTimer > 2.5) { state = State.IDLE; stateTimer = 0; }
      break;

    case State.TWO_FORM:
    case State.THREE_FORM: {
      const t = Math.min(stateTimer / 1.2, 1.0); // 1.2s 形成文字
      const cx = screenW / 2, cy = screenH / 2;
      for (let i = 0; i < p.count; i++) {
        const tx = cx + (stateTargets[i]?.x || 0);
        const ty = cy + (stateTargets[i]?.y || 0);
        p.pos[i * 3] = lerp(stateStartPos[i * 3], tx, t);
        p.pos[i * 3 + 1] = lerp(stateStartPos[i * 3 + 1], ty, t);
        p.alphas[i] = 0.9;
      }
      p.geo.attributes.position.needsUpdate = true;
      if (t >= 1.0) {
        const nextState = state === State.TWO_FORM ? State.TWO_HOLD : State.THREE_HOLD;
        state = nextState;
        stateTimer = 0;
      }
      break;
    }

    case State.TWO_HOLD:
      if (stateTimer > 5.0) { state = State.IDLE; stateTimer = 0; stateTargets = null; }
      break;

    case State.THREE_HOLD:
      if (stateTimer > 6.0) { state = State.IDLE; stateTimer = 0; stateTargets = null; }
      break;
  }
}

// ══════════════ 涟漪 ══════════════
function createRipples() { return []; }
function spawnRipple(ripples, x, y) {
  ripples.push({ x, y, radius: 0, life: 0, maxLife: 3.0, strength: 1.0 });
}

function updateParticlesBase(p, time, dt, w, h, ripples) {
  const active = (state !== State.TWO_FORM && state !== State.THREE_FORM &&
                  state !== State.TWO_HOLD && state !== State.THREE_HOLD);
  if (!active) return;

  for (let i = 0; i < p.count; i++) {
    let tx = p.baseX[i] + p.amp[i] * Math.sin(p.freq[i] * time + p.phase[i]);
    let ty = p.baseY[i] + p.amp[i] * 0.6 * Math.cos(p.freq[i] * time * 1.2 + p.phase[i] + 1);

    // 涟漪力
    for (const r of ripples) {
      const d = dist(tx, ty, r.x, r.y);
      if (d < r.radius + 50 && d > 0.05) {
        const f = r.strength * (1 - d / (r.radius + 50)) * 20;
        tx += (tx - r.x) / d * f;
        ty += (ty - r.y) / d * f;
        p.vx[i] += (tx - r.x) / d * f * 0.3;
        p.vy[i] += (ty - r.y) / d * f * 0.3;
      }
    }

    tx += p.vx[i]; ty += p.vy[i];
    p.vx[i] *= 0.9; p.vy[i] *= 0.9;

    if (tx < 0) tx = 0; if (tx > w) tx = w;
    if (ty < 0) ty = 0; if (ty > h) ty = h;

    p.pos[i * 3] = tx; p.pos[i * 3 + 1] = ty;
  }

  // 涟漪生命周期
  for (let i = ripples.length - 1; i >= 0; i--) {
    ripples[i].life += dt;
    ripples[i].radius += dt * 180;
    ripples[i].strength = 1 - ripples[i].life / ripples[i].maxLife;
    if (ripples[i].life >= ripples[i].maxLife) ripples.splice(i, 1);
  }

  p.geo.attributes.position.needsUpdate = true;
}

// 涟漪视觉环
function createRingViz(scene) {
  const rings = [];
  return {
    spawn(x, y) {
      const geo = new THREE.RingGeometry(3, 5, 40);
      const mat = new THREE.MeshBasicMaterial({
        color: 0xffffff, side: THREE.DoubleSide, transparent: true,
        opacity: 0.35, depthTest: false, depthWrite: false
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(x, y, 0.1);
      scene.add(mesh);
      rings.push({ mesh, mat, age: 0, maxAge: 2.0 });
    },
    update(dt) {
      for (let i = rings.length - 1; i >= 0; i--) {
        const r = rings[i];
        r.age += dt;
        const t = r.age / r.maxAge;
        if (t >= 1) {
          scene.remove(r.mesh); r.mesh.geometry.dispose(); r.mat.dispose();
          rings.splice(i, 1);
          continue;
        }
        const rad = 8 + 250 * t;
        r.mesh.geometry.dispose();
        r.mesh.geometry = new THREE.RingGeometry(rad - 1.5, rad + 1.5, 40);
        r.mat.opacity = 0.35 * (1 - t);
      }
    }
  };
}

// ══════════════ 主程序 ══════════════
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
  const ringViz = createRingViz(scene);
  const ripples = createRipples();

  // UI
  const loadingEl = document.getElementById('loading');
  const loadingText = loadingEl.querySelector('p');
  const guidanceEl = document.getElementById('guidance');
  const statusEl = document.getElementById('status-indicator');
  const statusLabel = statusEl.querySelector('.label');

  loadingText.textContent = '正在加载手势模型...';
  const { hands } = await initHandDetector(video, msg => { loadingText.textContent = msg; });
  loadingEl.classList.add('hidden');
  guidanceEl.classList.remove('hidden');
  setTimeout(() => guidanceEl.classList.add('hidden'), 4000);

  // 触摸涟漪
  function onTouch(e) {
    e.preventDefault();
    const cx = e.touches ? e.touches[0].clientX : e.clientX;
    const cy = e.touches ? e.touches[0].clientY : e.clientY;
    spawnRipple(ripples, cx, cy);
    ringViz.spawn(cx, cy);
  }
  window.addEventListener('touchstart', onTouch, { passive: false });
  window.addEventListener('click', e => {
    // 点涟漪
    spawnRipple(ripples, e.clientX, e.clientY);
    ringViz.spawn(e.clientX, e.clientY);
  });

  // 渲染
  let last = performance.now();
  function loop(now) {
    requestAnimationFrame(loop);
    let dt = (now - last) / 1000;
    if (dt <= 0) dt = 0.016; if (dt > 0.1) dt = 0.1;
    last = now;
    const w = window.innerWidth, h = window.innerHeight;

    const fingers = handleGesture(p, w, h);
    updateState(p, dt, w, h);
    updateParticlesBase(p, now / 1000, dt, w, h, ripples);
    ringViz.update(dt);

    // 状态指示（含调试）
    const labels = { 0: '', 1: '炸开', 2: 'claude code', 3: 'love life' };
    const st = state === State.TWO_HOLD ? 2 : state === State.THREE_HOLD ? 3 :
              state === State.TWO_FORM ? 2 : state === State.THREE_FORM ? 3 :
              state === State.ONE_EXPLODE ? 1 : 0;
    const r = window.__lastResults;
    statusEl.className = fingers > 0 ? 'active' : '';
    statusLabel.textContent = `f:${fingers} s:${state} r:${r ? 'Y' : 'N'}`;

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
    `<p style="color:#ff6b6b;">启动失败: ${err.message}</p>`;
});
