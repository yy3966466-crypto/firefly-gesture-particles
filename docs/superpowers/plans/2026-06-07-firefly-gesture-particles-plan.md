# 萤火虫手势粒子交互 · 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 Three.js + MediaPipe Hands 的浏览器端手势粒子交互应用，萤火虫粒子默认波浪流动，手势触发涟漪/炸开/光环效果。

**Architecture:** 摄像头帧 → MediaPipe 手部追踪 → 手势分类状态机 → 粒子物理引擎 → Three.js Shader 渲染。所有模块通过 main.js 主循环串联，音效层监听手势事件触发 Web Audio 合成。

**Tech Stack:** Three.js (CDN r170), MediaPipe Hands (CDN), Web Audio API, ES Modules + import map

---

### Task 1: 项目脚手架

**Files:**
- Create: `d:/bishe/firefly-particles/index.html`
- Create: `d:/bishe/firefly-particles/style.css`
- Create: `d:/bishe/firefly-particles/src/utils.js`

- [ ] **Step 1: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>萤火虫 · 手势粒子交互</title>
  <link rel="stylesheet" href="style.css">
  <script type="importmap">
  {
    "imports": {
      "three": "https://unpkg.com/three@0.170.0/build/three.module.js"
    }
  }
  </script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils@0.3.1675466862/camera_utils.js" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/hands.js" crossorigin="anonymous"></script>
</head>
<body>
  <div id="loading">
    <div class="spinner"></div>
    <p>正在加载手势模型...</p>
  </div>
  <div id="guidance" class="hidden">
    <p>试试张开手掌 ✨</p>
  </div>
  <div id="status-indicator" class="waiting">
    <span class="dot"></span>
    <span class="label"></span>
  </div>
  <canvas id="canvas"></canvas>
  <script type="module" src="src/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: 创建 style.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 100%; height: 100%; overflow: hidden; background: #000; }

#canvas {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
}

#loading {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; z-index: 10; color: rgba(180, 255, 160, 0.8);
  font-family: -apple-system, sans-serif; transition: opacity 0.6s;
}
#loading.hidden { opacity: 0; pointer-events: none; }

.spinner {
  width: 32px; height: 32px; margin: 0 auto 16px;
  border: 2px solid rgba(180, 255, 160, 0.2);
  border-top-color: rgba(180, 255, 160, 0.8); border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

#guidance {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 5; font-family: -apple-system, sans-serif; font-size: 22px;
  color: rgba(200, 255, 170, 0.9); text-shadow: 0 0 20px rgba(180, 255, 160, 0.4);
  transition: opacity 0.8s; pointer-events: none;
}
#guidance.hidden { opacity: 0; }

#status-indicator {
  position: fixed; bottom: 24px; right: 24px; z-index: 5;
  display: flex; align-items: center; gap: 8px;
  font-family: -apple-system, sans-serif; font-size: 12px;
  color: rgba(180, 255, 160, 0.6); transition: color 0.3s;
}
#status-indicator .dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: rgba(128, 128, 128, 0.5); transition: background 0.3s, box-shadow 0.3s;
}
#status-indicator.active { color: rgba(180, 255, 160, 0.9); }
#status-indicator.active .dot {
  background: rgba(160, 255, 140, 0.9);
  box-shadow: 0 0 8px rgba(160, 255, 140, 0.6);
}
```

- [ ] **Step 3: 创建 src/utils.js**

```javascript
export function isMobile() {
  return /Android|iPhone|iPad|iPod|webOS/i.test(navigator.userAgent)
    || (navigator.maxTouchPoints > 1 && window.innerWidth < 1024);
}

export const PARTICLE_COUNT = isMobile() ? 180 : 300;

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

export function dist(x1, y1, x2, y2) {
  const dx = x2 - x1, dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy);
}

export function mapRange(value, inMin, inMax, outMin, outMax) {
  return ((value - inMin) / (inMax - inMin)) * (outMax - outMin) + outMin;
}

export function rand(min, max) {
  return Math.random() * (max - min) + min;
}
```

- [ ] **Step 4: Commit**

```bash
git add firefly-particles/
git commit -m "feat: add project scaffolding (HTML, CSS, utils)"
```

---

### Task 2: 摄像头模块

**Files:**
- Create: `d:/bishe/firefly-particles/src/camera.js`

- [ ] **Step 1: 创建 camera.js**

```javascript
export async function initCamera(videoElement) {
  const constraints = {
    video: {
      facingMode: 'user',
      width: { ideal: 1280 },
      height: { ideal: 720 }
    }
  };

  const stream = await navigator.mediaDevices.getUserMedia(constraints);
  videoElement.srcObject = stream;
  videoElement.setAttribute('playsinline', '');
  await videoElement.play();

  return {
    stream,
    width: videoElement.videoWidth,
    height: videoElement.videoHeight
  };
}

export function createVideoElement() {
  const video = document.createElement('video');
  video.style.display = 'none';
  document.body.appendChild(video);
  return video;
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/camera.js
git commit -m "feat: add camera module with getUserMedia"
```

---

### Task 3: Three.js 场景 + 摄像头背景

**Files:**
- Create: `d:/bishe/firefly-particles/src/scene.js`

- [ ] **Step 1: 创建 scene.js — 初始化 Three.js 场景、正交相机、视频背景面片**

```javascript
import * as THREE from 'three';

export function createScene(videoElement) {
  const canvas = document.getElementById('canvas');
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();

  const camera = new THREE.OrthographicCamera(
    0, window.innerWidth, window.innerHeight, 0, 0.1, 10
  );
  camera.position.z = 5;

  // 视频纹理
  const videoTexture = new THREE.VideoTexture(videoElement);
  videoTexture.minFilter = THREE.LinearFilter;
  videoTexture.magFilter = THREE.LinearFilter;

  // 镜像背景面片：x 方向翻转纹理实现镜像
  const bgGeometry = new THREE.PlaneGeometry(window.innerWidth, window.innerHeight);
  // 翻转 uv.x 实现水平镜像
  const uvs = bgGeometry.attributes.uv;
  for (let i = 0; i < uvs.count; i++) {
    uvs.setX(i, 1 - uvs.getX(i));
  }
  uvs.needsUpdate = true;

  const bgMaterial = new THREE.MeshBasicMaterial({ map: videoTexture });
  const bgPlane = new THREE.Mesh(bgGeometry, bgMaterial);
  bgPlane.position.set(window.innerWidth / 2, window.innerHeight / 2, -1);
  scene.add(bgPlane);

  return { renderer, scene, camera, videoTexture, bgPlane, canvas };
}

export function handleResize({ renderer, camera, bgPlane }) {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h);
  camera.right = w;
  camera.bottom = h;
  camera.updateProjectionMatrix();
  bgPlane.geometry.dispose();
  bgPlane.geometry = new THREE.PlaneGeometry(w, h);
  const uvs = bgPlane.geometry.attributes.uv;
  for (let i = 0; i < uvs.count; i++) {
    uvs.setX(i, 1 - uvs.getX(i));
  }
  uvs.needsUpdate = true;
  bgPlane.position.set(w / 2, h / 2, -1);
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/scene.js
git commit -m "feat: add Three.js scene with mirrored camera background"
```

---

### Task 4: 粒子 Shader + 粒子引擎（基础）

**Files:**
- Create: `d:/bishe/firefly-particles/src/particle-engine.js`

- [ ] **Step 1: 创建 particle-engine.js — 粒子系统初始化 + 默认波浪动画**

```javascript
import * as THREE from 'three';
import { PARTICLE_COUNT, rand } from './utils.js';

const vertexShader = /* glsl */ `
  attribute float size;
  attribute float alpha;
  varying float vAlpha;
  varying float vBrightness;
  uniform float uTime;

  void main() {
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (250.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
    vAlpha = alpha;
    vBrightness = 0.5 + 0.5 * sin(position.x * 0.03 + position.y * 0.02 + uTime * 1.5);
  }
`;

const fragmentShader = /* glsl */ `
  varying float vAlpha;
  varying float vBrightness;
  uniform vec3 uColor1;
  uniform vec3 uColor2;

  void main() {
    float d = length(gl_PointCoord - vec2(0.5)) * 2.0;
    float core = exp(-d * 5.0) * 0.7;
    float glow = exp(-d * 2.5) * 0.3;
    float alpha = (core + glow) * vAlpha * vBrightness;
    vec3 color = mix(uColor1, uColor2, core);
    gl_FragColor = vec4(color, alpha);
  }
`;

export function createParticleSystem(width, height) {
  const count = PARTICLE_COUNT;
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const alphas = new Float32Array(count);

  // 粒子元数据：相位、振幅（用于波浪）
  const phases = new Float32Array(count);
  const amplitudes = new Float32Array(count);
  const frequencies = new Float32Array(count);
  const basePositions = new Float32Array(count * 2);

  for (let i = 0; i < count; i++) {
    const x = rand(0, width);
    const y = rand(0, height);
    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = 0;
    sizes[i] = rand(2, 6);
    alphas[i] = rand(0.4, 0.9);
    phases[i] = rand(0, Math.PI * 2);
    amplitudes[i] = rand(20, 60);
    frequencies[i] = rand(0.5, 1.5);
    basePositions[i * 2] = x;
    basePositions[i * 2 + 1] = y;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
  geometry.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));

  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uColor1: { value: new THREE.Color('#b4ffa0') },
      uColor2: { value: new THREE.Color('#f0ffc8') }
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    depthTest: false
  });

  const points = new THREE.Points(geometry, material);
  // 粒子在 z=0，位于背景面片 (z=-1) 前方
  points.position.z = 0;

  return {
    points, geometry, material,
    positions, sizes, alphas,
    phases, amplitudes, frequencies, basePositions,
    count
  };
}

export function updateParticleWave(particles, time, dt) {
  const { positions, basePositions, phases, amplitudes, frequencies, count } = particles;

  for (let i = 0; i < count; i++) {
    const bx = basePositions[i * 2];
    const by = basePositions[i * 2 + 1];
    const phase = phases[i];
    const amp = amplitudes[i];
    const freq = frequencies[i];
    const angle = freq * time + phase;

    positions[i * 3] = bx + amp * Math.sin(angle);
    positions[i * 3 + 1] = by + amp * 0.6 * Math.cos(angle * 1.3);
  }

  particles.geometry.attributes.position.needsUpdate = true;
  particles.material.uniforms.uTime.value = time;
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/particle-engine.js
git commit -m "feat: add particle engine with firefly shader and wave animation"
```

---

### Task 5: 物理引擎核心

**Files:**
- Create: `d:/bishe/firefly-particles/src/physics.js`

- [ ] **Step 1: 创建 physics.js — 速度积分、阻尼、力场基础设施**

```javascript
import { dist, clamp } from './utils.js';

export function createPhysicsEngine(particleCount) {
  // 每个粒子的速度 (vx, vy)
  const velocities = new Float32Array(particleCount * 2);

  // 外力累加器 (fx, fy)，每帧清零
  const forces = new Float32Array(particleCount * 2);

  // 粒子当前是否受外力驱动（true 时波浪被抑制）
  const driven = new Uint8Array(particleCount);

  return { velocities, forces, driven };
}

/**
 * 积分：将力转换为速度，应用阻尼，更新位置。
 * positions 会被原地修改。
 */
export function integrate(positions, basePositions, engine, dt, width, height) {
  const { velocities, forces, driven } = engine;
  const count = velocities.length / 2;
  const damping = 0.95;

  for (let i = 0; i < count; i++) {
    const idx2 = i * 2;
    const idx3 = i * 3;

    if (driven[i]) {
      // 外力驱动模式
      velocities[idx2] += forces[idx2] * dt;
      velocities[idx2 + 1] += forces[idx2 + 1] * dt;
      velocities[idx2] *= damping;
      velocities[idx2 + 1] *= damping;

      positions[idx3] += velocities[idx2] * dt;
      positions[idx3 + 1] += velocities[idx2 + 1] * dt;

      // 边界反弹
      if (positions[idx3] < 0) { positions[idx3] = 0; velocities[idx2] *= -0.3; }
      if (positions[idx3] > width) { positions[idx3] = width; velocities[idx2] *= -0.3; }
      if (positions[idx3 + 1] < 0) { positions[idx3 + 1] = 0; velocities[idx3 + 1] *= -0.3; }
      if (positions[idx3 + 1] > height) { positions[idx3 + 1] = height; velocities[idx3 + 1] *= -0.3; }

      // 速度很小时退出驱动模式
      if (Math.abs(velocities[idx2]) < 0.5 && Math.abs(velocities[idx3 + 1]) < 0.5) {
        velocities[idx2] = 0;
        velocities[idx3 + 1] = 0;
        driven[i] = 0;
        // 更新 basePositions 为当前位置，让粒子从新位置开始波浪
        basePositions[idx2] = positions[idx3];
        basePositions[idx3 + 1] = positions[idx3 + 1];
      }
    }

    // 清零力累加器
    forces[idx3] = 0;
    forces[idx3 + 1] = 0;
  }
}

/**
 * 应用径向力场：从 center 点向外排斥（或向内吸引）。
 * force > 0 为排斥，force < 0 为吸引。
 */
export function applyRadialForce(positions, engine, centerX, centerY, force, radius) {
  const { forces, driven } = engine;
  const count = forces.length / 2;

  for (let i = 0; i < count; i++) {
    const idx2 = i * 2;
    const idx3 = i * 3;
    const d = dist(positions[idx3], positions[idx3 + 1], centerX, centerY);

    if (d < radius && d > 0.1) {
      const strength = force / (d * d + 100);
      const dx = (positions[idx3] - centerX) / d;
      const dy = (positions[idx3 + 1] - centerY) / d;
      forces[idx2] += dx * strength;
      forces[idx2 + 1] += dy * strength;
      driven[i] = 1;
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/physics.js
git commit -m "feat: add physics engine core (integration, damping, radial force)"
```

---

### Task 6: 手势检测模块

**Files:**
- Create: `d:/bishe/firefly-particles/src/hand-detector.js`

- [ ] **Step 1: 创建 hand-detector.js — 初始化 MediaPipe Hands + 提取关键点**

```javascript
export async function initHandDetector() {
  const hands = new Hands({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`
  });

  hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.5
  });

  await hands.initialize();
  return hands;
}

/**
 * 从 video 检测手部，返回 landmarks 列表（屏幕坐标，已镜像）。
 * 每个 landmark 为 { x, y } 像素坐标。
 */
export async function detectHands(hands, videoElement) {
  if (!videoElement || videoElement.readyState < 2) return [];

  const results = await hands.send({ image: videoElement });

  if (!results || !results.multiHandLandmarks) return [];

  const width = videoElement.videoWidth;
  const height = videoElement.videoHeight;

  return results.multiHandLandmarks.map((landmarks, idx) => {
    const handedness = results.multiHandedness?.[idx]?.label || 'unknown';
    const points = landmarks.map(l => ({
      x: (1 - l.x) * width,   // 镜像 x
      y: l.y * height
    }));
    return { points, handedness };
  });
}

/** MediaPipe 手部关键点索引 */
export const LANDMARK = {
  WRIST: 0,
  THUMB_TIP: 4,
  INDEX_TIP: 8,
  MIDDLE_TIP: 12,
  RING_TIP: 16,
  PINKY_TIP: 20,
  INDEX_MCP: 5,
  MIDDLE_MCP: 9,
  RING_MCP: 13,
  PINKY_MCP: 17
};
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/hand-detector.js
git commit -m "feat: add MediaPipe hand detection with mirror coordinate mapping"
```

---

### Task 7: 手势分类器

**Files:**
- Create: `d:/bishe/firefly-particles/src/gesture-classifier.js`

- [ ] **Step 1: 创建 gesture-classifier.js — 状态机 + 手指间距 + 画圈检测**

```javascript
import { dist } from './utils.js';
import { LANDMARK } from './hand-detector.js';

const FINGER_TIPS = [
  LANDMARK.THUMB_TIP,
  LANDMARK.INDEX_TIP,
  LANDMARK.MIDDLE_TIP,
  LANDMARK.RING_TIP,
  LANDMARK.PINKY_TIP
];

const FINGER_MCP = [
  LANDMARK.THUMB_TIP - 2,  // thumb MCP ≈ point 2
  LANDMARK.INDEX_MCP,
  LANDMARK.MIDDLE_MCP,
  LANDMARK.RING_MCP,
  LANDMARK.PINKY_MCP
];

/**
 * 计算五指平均展开程度（指尖到对应掌指关节的距离，归一化）。
 * 返回值约为 0.02~0.25。
 */
function fingertipSpread(points) {
  let sum = 0;
  for (let i = 0; i < 5; i++) {
    const tip = points[FINGER_TIPS[i]];
    const mcp = points[FINGER_MCP[i]];
    if (tip && mcp) sum += dist(tip.x, tip.y, mcp.x, mcp.y);
  }
  return sum / 5;
}

export const GestureState = {
  IDLE: 'idle',
  PALM: 'palm',
  FIST_ATTRACT: 'fist_attract',
  FIST_EXPLODE: 'fist_explode',
  FIST_RECOVER: 'fist_recover',
  CIRCLE_DRAW: 'circle_draw',
  CIRCLE_HOLD: 'circle_hold'
};

const SPREAD_THRESHOLD = 60;   // 手掌阈值（像素，视频坐标下）
const FIST_THRESHOLD = 25;     // 握拳阈值

export function createGestureClassifier() {
  return {
    state: GestureState.IDLE,
    stateTimer: 0,            // 当前状态已持续时间 (s)
    handCenter: { x: 0, y: 0 },
    indexTrail: [],           // [{ x, y, time }]
    circleCenter: null,       // 拟合圆心
    circleRadius: 0,          // 拟合半径
  };
}

/**
 * 每帧调用，返回当前手势状态。
 * @param {Array} hands - detectHands 的返回值
 * @param {number} dt - 帧间隔 (s)
 * @param {number} screenW - 屏幕宽度（用于坐标映射）
 * @param {number} screenH - 屏幕高度
 */
export function classifyGesture(classifier, hands, dt, videoW, videoH, screenW, screenH) {
  const c = classifier;
  c.stateTimer += dt;

  if (!hands || hands.length === 0) {
    // 没有手 → 回到 idle
    if (c.state !== GestureState.IDLE) {
      c.state = GestureState.IDLE;
      c.stateTimer = 0;
    }
    return c;
  }

  const primaryHand = hands[0];
  const points = primaryHand.points;
  const wrist = points[LANDMARK.WRIST];
  const indexTip = points[LANDMARK.INDEX_TIP];

  // 手中心（手腕 + 中指的中间），映射到屏幕坐标
  const midTip = points[LANDMARK.MIDDLE_TIP];
  const rawCx = (wrist.x + (midTip?.x || wrist.x)) / 2;
  const rawCy = (wrist.y + (midTip?.y || wrist.y)) / 2;
  c.handCenter = {
    x: (rawCx / videoW) * screenW,
    y: (rawCy / videoH) * screenH
  };

  const spread = fingertipSpread(points);

  // === 状态机 ===
  switch (c.state) {
    case GestureState.IDLE:
      if (spread > SPREAD_THRESHOLD) {
        c.state = GestureState.PALM;
        c.stateTimer = 0;
      } else if (spread < FIST_THRESHOLD) {
        c.state = GestureState.FIST_ATTRACT;
        c.stateTimer = 0;
      }
      // 追踪食指轨迹用于画圈检测
      updateIndexTrail(c, indexTip, 1.0, videoW, videoH, screenW, screenH);
      break;

    case GestureState.PALM:
      if (spread <= SPREAD_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_ATTRACT:
      if (spread < FIST_THRESHOLD && c.stateTimer > 0.3) {
        c.state = GestureState.FIST_EXPLODE;
        c.stateTimer = 0;
      } else if (spread >= FIST_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_EXPLODE:
      if (c.stateTimer > 0.1) {
        c.state = GestureState.FIST_RECOVER;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_RECOVER:
      if (c.stateTimer > 2.0 || spread > SPREAD_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.CIRCLE_DRAW:
      updateIndexTrail(c, indexTip, dt, videoW, videoH, screenW, screenH);
      if (checkCircleComplete(c)) {
        c.state = GestureState.CIRCLE_HOLD;
        c.stateTimer = 0;
      } else if (spread > SPREAD_THRESHOLD || spread < FIST_THRESHOLD) {
        // 被其他手势打断
        c.indexTrail = [];
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.CIRCLE_HOLD:
      if (c.stateTimer > 3.0) {
        c.indexTrail = [];
        c.circleCenter = null;
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;
  }

  return c;
}

function updateIndexTrail(c, indexTip, dt, videoW, videoH, screenW, screenH) {
  if (!indexTip) return;

  const sx = (indexTip.x / videoW) * screenW;
  const sy = (indexTip.y / videoH) * screenH;

  c.indexTrail.push({ x: sx, y: sy, time: c.stateTimer });

  // 只保留最近 2 秒的轨迹
  const cutoff = c.stateTimer - 2.0;
  c.indexTrail = c.indexTrail.filter(p => p.time > cutoff);

  // 检查是否需要进入画圈状态（轨迹足够长）
  if (c.state === GestureState.IDLE && c.indexTrail.length > 30) {
    c.state = GestureState.CIRCLE_DRAW;
    c.stateTimer = 0;
  }
}

function checkCircleComplete(c) {
  if (c.indexTrail.length < 20) return false;

  // 计算轨迹中心
  let cx = 0, cy = 0;
  const pts = c.indexTrail;
  for (const p of pts) { cx += p.x; cy += p.y; }
  cx /= pts.length;
  cy /= pts.length;

  // 计算累积角度
  let totalAngle = 0;
  for (let i = 1; i < pts.length; i++) {
    const a1 = Math.atan2(pts[i - 1].y - cy, pts[i - 1].x - cx);
    const a2 = Math.atan2(pts[i].y - cy, pts[i].x - cx);
    let da = a2 - a1;
    if (da > Math.PI) da -= Math.PI * 2;
    if (da < -Math.PI) da += Math.PI * 2;
    totalAngle += da;
  }

  if (Math.abs(totalAngle) > Math.PI * 1.6) { // > 288°
    c.circleCenter = { x: cx, y: cy };
    c.circleRadius = pts.reduce((s, p) => s + dist(p.x, p.y, cx, cy), 0) / pts.length;
    return true;
  }
  return false;
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/gesture-classifier.js
git commit -m "feat: add gesture classifier with state machine and circle detection"
```

---

### Task 8: 手势触发物理效果

**Files:**
- Create: `d:/bishe/firefly-particles/src/gesture-physics.js`

- [ ] **Step 1: 创建 gesture-physics.js — 涟漪、爆炸、光环三种力**

```javascript
import { applyRadialForce } from './physics.js';
import { GestureState } from './gesture-classifier.js';
import { dist, rand } from './utils.js';

/**
 * 涟漪效果：从手中心向外排斥粒子。
 * 返回涟漪环数据供渲染。
 */
export function applyRipple(positions, engine, handCenter, screenW, screenH) {
  const cx = handCenter.x;
  const cy = handCenter.y;
  applyRadialForce(positions, engine, cx, cy, 1200, 280);
  return { cx, cy, time: 0 };
}

/**
 * 吸附效果：粒子向拳心聚拢。
 */
export function applyAttract(positions, engine, handCenter, screenW, screenH) {
  const cx = handCenter.x;
  const cy = handCenter.y;
  applyRadialForce(positions, engine, cx, cy, -800, 250);
  return { cx, cy };
}

/**
 * 爆炸效果：粒子从拳心径向炸开。
 */
export function applyExplosion(positions, engine, handCenter, screenW, screenH) {
  const { velocities, driven } = engine;
  const cx = handCenter.x;
  const cy = handCenter.y;
  const count = velocities.length / 2;

  for (let i = 0; i < count; i++) {
    const idx2 = i * 2;
    const idx3 = i * 3;
    const d = dist(positions[idx3], positions[idx3 + 1], cx, cy);

    if (d < 300) {
      const angle = Math.atan2(positions[idx3 + 1] - cy, positions[idx3] - cx);
      const speed = rand(200, 600);
      velocities[idx2] = Math.cos(angle) * speed;
      velocities[idx2 + 1] = Math.sin(angle) * speed;
      driven[i] = 1;
    }
  }

  return { cx, cy };
}

/**
 * 光环效果：将周围粒子吸附到环形轨迹上。
 */
export function applyRingAttraction(positions, engine, classifier, screenW, screenH) {
  if (!classifier.circleCenter) return;

  const { velocities, forces, driven } = engine;
  const cx = classifier.circleCenter.x;
  const cy = classifier.circleCenter.y;
  const radius = classifier.circleRadius;
  const count = velocities.length / 2;

  for (let i = 0; i < count; i++) {
    const idx2 = i * 2;
    const idx3 = i * 3;
    const d = dist(positions[idx3], positions[idx3 + 1], cx, cy);

    if (d > radius * 0.5 && d < radius * 1.8) {
      // 径向力：拉向环半径
      const radialDir = (d - radius) > 0 ? -1 : 1;
      const radialStrength = Math.abs(d - radius) * 3;
      const dx = (positions[idx3] - cx) / d;
      const dy = (positions[idx3 + 1] - cy) / d;
      forces[idx2] += dx * radialStrength * radialDir;
      forces[idx2 + 1] += dy * radialStrength * radialDir;

      // 切向力：让粒子沿环运动
      forces[idx2] += -dy * 40;
      forces[idx2 + 1] += dx * 40;

      driven[i] = 1;
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/gesture-physics.js
git commit -m "feat: add gesture physics (ripple, attract, explosion, ring)"
```

---

### Task 9: 音效引擎

**Files:**
- Create: `d:/bishe/firefly-particles/src/audio.js`

- [ ] **Step 1: 创建 audio.js — Web Audio API 合成环境音 + 触发音**

```javascript
export function createAudioEngine() {
  let ctx = null;
  let ambientNodes = null;

  function ensureContext() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  /** 启动环境音：流水 + 微风底噪 */
  function startAmbient() {
    const c = ensureContext();
    if (ambientNodes) return;

    // 流水声：白噪声 → 低通滤波 → LFO 音量调制
    const bufferSize = 2 * c.sampleRate;
    const noiseBuffer = c.createBuffer(1, bufferSize, c.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

    const noiseSource = c.createBufferSource();
    noiseSource.buffer = noiseBuffer;
    noiseSource.loop = true;

    const lowpass = c.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 400;
    lowpass.Q.value = 0.5;

    const lfo = c.createOscillator();
    lfo.frequency.value = 0.3;
    const lfoGain = c.createGain();
    lfoGain.gain.value = 0.3;
    lfo.connect(lfoGain);
    lfoGain.connect(lowpass.frequency);
    lfo.start();

    const waterGain = c.createGain();
    waterGain.gain.value = 0.04;

    noiseSource.connect(lowpass);
    lowpass.connect(waterGain);
    waterGain.connect(c.destination);
    noiseSource.start();

    // 微风：粉噪近似 → 高通
    const windSource = c.createBufferSource();
    windSource.buffer = noiseBuffer;
    windSource.loop = true;

    const highpass = c.createBiquadFilter();
    highpass.type = 'highpass';
    highpass.frequency.value = 2000;

    const windGain = c.createGain();
    windGain.gain.value = 0.015;

    windSource.connect(highpass);
    highpass.connect(windGain);
    windGain.connect(c.destination);
    windSource.start();

    ambientNodes = { noiseSource, windSource, waterGain, windGain, lfo };
  }

  /** 播放单次叮咚音 */
  function playDing(frequency = 800, duration = 0.3, volume = 0.15) {
    const c = ensureContext();
    const osc = c.createOscillator();
    const gain = c.createGain();

    osc.type = 'sine';
    osc.frequency.value = frequency;
    gain.gain.setValueAtTime(volume, c.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + duration);

    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(c.currentTime);
    osc.stop(c.currentTime + duration);
  }

  /** 涟漪触发音 */
  function playRipple() {
    playDing(880, 0.35, 0.12);
    setTimeout(() => playDing(660, 0.25, 0.08), 100);
  }

  /** 爆炸触发音 */
  function playExplosion() {
    const c = ensureContext();
    // 低频嗡
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(120, c.currentTime);
    osc.frequency.linearRampToValueAtTime(40, c.currentTime + 0.3);
    gain.gain.setValueAtTime(0.2, c.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.5);
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(c.currentTime);
    osc.stop(c.currentTime + 0.5);

    // 碎散高频噪声
    const bufferSize = c.sampleRate * 0.2;
    const noiseBuffer = c.createBuffer(1, bufferSize, c.sampleRate);
    const d = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    const noise = c.createBufferSource();
    noise.buffer = noiseBuffer;
    const bp = c.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 3000;
    bp.Q.value = 2;
    const ng = c.createGain();
    ng.gain.setValueAtTime(0.08, c.currentTime);
    ng.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.2);
    noise.connect(bp);
    bp.connect(ng);
    ng.connect(c.destination);
    noise.start(c.currentTime);
  }

  /** 光环触发音：递增音阶 */
  function playRing() {
    const notes = [523, 659, 784, 1047];
    notes.forEach((freq, i) => {
      setTimeout(() => playDing(freq, 0.4, 0.1), i * 120);
    });
  }

  function stop() {
    if (ambientNodes) {
      ambientNodes.noiseSource.stop();
      ambientNodes.windSource.stop();
      ambientNodes.lfo.stop();
      ambientNodes = null;
    }
    if (ctx) { ctx.close(); ctx = null; }
  }

  return { startAmbient, playRipple, playExplosion, playRing, stop, ensureContext };
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/audio.js
git commit -m "feat: add audio engine (water ambience, ding, explosion, ring sounds)"
```

---

### Task 10: 涟漪渲染（Three.js 环）

**Files:**
- Modify: `d:/bishe/firefly-particles/src/scene.js` — 添加涟漪环渲染辅助

 实际上涟漪环在粒子引擎模块中作为独立的 Mesh 管理更合适。我们创建一个新文件：

- Create: `d:/bishe/firefly-particles/src/ripple-renderer.js`

- [ ] **Step 1: 创建 ripple-renderer.js — 涟漪圆环的 Three.js 渲染**

```javascript
import * as THREE from 'three';

/**
 * 管理屏幕上的涟漪圆环视觉效果。
 * 每次触发时创建一个新环，自动淡出消失。
 */
export function createRippleRenderer(scene) {
  const ripples = [];

  function spawn(cx, cy) {
    const segments = 64;
    const geometry = new THREE.RingGeometry(5, 8, segments);
    const material = new THREE.MeshBasicMaterial({
      color: 0xb4ffa0,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.5,
      depthTest: false,
      depthWrite: false
    });
    const ring = new THREE.Mesh(geometry, material);
    ring.position.set(cx, cy, 0.1);
    scene.add(ring);

    ripples.push({
      mesh: ring,
      material,
      age: 0,
      maxAge: 1.5,
      startRadius: 10,
      endRadius: 300
    });
  }

  function update(dt) {
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      r.age += dt;
      const t = r.age / r.maxAge;
      if (t >= 1) {
        scene.remove(r.mesh);
        r.mesh.geometry.dispose();
        r.material.dispose();
        ripples.splice(i, 1);
        continue;
      }

      const radius = r.startRadius + (r.endRadius - r.startRadius) * t;
      r.mesh.geometry.dispose();
      r.mesh.geometry = new THREE.RingGeometry(radius - 3, radius + 3, 64);
      r.material.opacity = 0.5 * (1 - t);
    }
  }

  function clear() {
    for (const r of ripples) {
      scene.remove(r.mesh);
      r.mesh.geometry.dispose();
      r.material.dispose();
    }
    ripples.length = 0;
  }

  return { spawn, update, clear, ripples };
}
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/ripple-renderer.js
git commit -m "feat: add ripple ring renderer for visual feedback"
```

---

### Task 11: 主入口 + 渲染循环

**Files:**
- Create: `d:/bishe/firefly-particles/src/main.js`

- [ ] **Step 1: 创建 main.js — 串联所有模块，主循环**

```javascript
import * as THREE from 'three';
import { isMobile, PARTICLE_COUNT } from './utils.js';
import { initCamera, createVideoElement } from './camera.js';
import { createScene, handleResize } from './scene.js';
import { createParticleSystem, updateParticleWave } from './particle-engine.js';
import { createPhysicsEngine, integrate } from './physics.js';
import { initHandDetector, detectHands } from './hand-detector.js';
import { createGestureClassifier, classifyGesture, GestureState } from './gesture-classifier.js';
import { applyRipple, applyAttract, applyExplosion, applyRingAttraction } from './gesture-physics.js';
import { createAudioEngine } from './audio.js';
import { createRippleRenderer } from './ripple-renderer.js';

async function main() {
  // 1. 摄像头
  const video = createVideoElement();
  await initCamera(video);

  // 2. Three.js 场景
  const { renderer, scene, camera, bgPlane } = createScene(video);

  // 3. 粒子系统
  const particles = createParticleSystem(window.innerWidth, window.innerHeight);
  scene.add(particles.points);

  // 4. 涟漪渲染
  const rippleRenderer = createRippleRenderer(scene);

  // 5. 物理引擎
  const physics = createPhysicsEngine(PARTICLE_COUNT);

  // 6. 手势检测
  const hands = await initHandDetector();

  // 7. 手势分类器
  const classifier = createGestureClassifier();

  // 8. 音效
  const audio = createAudioEngine();

  // 9. UI
  const loadingEl = document.getElementById('loading');
  const guidanceEl = document.getElementById('guidance');
  const statusEl = document.getElementById('status-indicator');
  const statusDot = statusEl.querySelector('.dot');
  const statusLabel = statusEl.querySelector('.label');

  loadingEl.classList.add('hidden');
  guidanceEl.classList.remove('hidden');

  // 首次交互解锁音频
  let audioStarted = false;
  function tryStartAudio() {
    if (!audioStarted) {
      audio.startAmbient();
      audioStarted = true;
    }
  }
  document.addEventListener('click', tryStartAudio, { once: true });
  document.addEventListener('touchstart', tryStartAudio, { once: true });

  // 10. 引导文字定时
  setTimeout(() => guidanceEl.classList.add('hidden'), 5000);

  // 11. 主循环
  let lastTime = performance.now();
  let prevGesture = GestureState.IDLE;

  function loop(now) {
    requestAnimationFrame(loop);

    let dt = (now - lastTime) / 1000;
    if (dt <= 0) dt = 0.016;
    if (dt > 0.1) dt = 0.1; // 防止大帧间隔
    lastTime = now;

    const w = window.innerWidth;
    const h = window.innerHeight;

    // 手势检测
    detectHands(hands, video).then(handData => {
      classifyGesture(classifier, handData, dt, video.videoWidth, video.videoHeight, w, h);

      const state = classifier.state;

      // 状态变化 → 音频触发
      if (state !== prevGesture) {
        if (state === GestureState.PALM) {
          audio.playRipple();
          const ripple = applyRipple(particles.positions, physics, classifier.handCenter, w, h);
          rippleRenderer.spawn(ripple.cx, ripple.cy);
        }
        if (state === GestureState.FIST_EXPLODE) {
          audio.playExplosion();
          applyExplosion(particles.positions, physics, classifier.handCenter, w, h);
        }
        if (state === GestureState.CIRCLE_HOLD) {
          audio.playRing();
        }
      }

      // 持续效果
      if (state === GestureState.PALM) {
        applyRipple(particles.positions, physics, classifier.handCenter, w, h);
      }
      if (state === GestureState.FIST_ATTRACT) {
        applyAttract(particles.positions, physics, classifier.handCenter, w, h);
      }
      if (state === GestureState.CIRCLE_HOLD) {
        applyRingAttraction(particles.positions, physics, classifier, w, h);
      }

      // 状态指示器
      updateStatusIndicator(state, statusEl, statusDot, statusLabel);

      prevGesture = state;
    });

    // 物理积分
    integrate(particles.positions, particles.basePositions, physics, dt, w, h);

    // 波浪更新（未被外力驱动的粒子）
    updateParticleWave(particles, performance.now() / 1000, dt);

    // 涟漪动画
    rippleRenderer.update(dt);

    // 渲染
    renderer.render(scene, camera);
  }

  requestAnimationFrame(loop);

  // 窗口大小调整
  window.addEventListener('resize', () => {
    handleResize({ renderer, camera, bgPlane });
    // 更新粒子 basePositions（缩放映射）
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.basePositions[i * 2] = (particles.basePositions[i * 2] / w) * window.innerWidth;
      particles.basePositions[i * 2 + 1] = (particles.basePositions[i * 2 + 1] / h) * window.innerHeight;
    }
  });
}

function updateStatusIndicator(state, el, dot, label) {
  switch (state) {
    case GestureState.IDLE:
      el.className = '';
      label.textContent = '';
      break;
    case GestureState.PALM:
      el.className = 'active';
      label.textContent = '涟漪';
      break;
    case GestureState.FIST_ATTRACT:
    case GestureState.FIST_EXPLODE:
    case GestureState.FIST_RECOVER:
      el.className = 'active';
      label.textContent = state === GestureState.FIST_ATTRACT ? '聚拢' :
                         state === GestureState.FIST_EXPLODE ? '炸开' : '恢复';
      break;
    case GestureState.CIRCLE_DRAW:
    case GestureState.CIRCLE_HOLD:
      el.className = 'active';
      label.textContent = '光环';
      break;
  }
}

main().catch(err => {
  console.error('启动失败:', err);
  document.getElementById('loading').innerHTML =
    `<p style="color:#ff6b6b;">启动失败: ${err.message}<br><small>请确保已授予摄像头权限并使用 HTTPS</small></p>`;
});
```

- [ ] **Step 2: Commit**

```bash
git add firefly-particles/src/main.js
git commit -m "feat: add main entry point with full render loop integration"
```

---

### Task 12: 移动端适配 + 最终优化

**Files:**
- Modify: `d:/bishe/firefly-particles/index.html` — 添加 iOS Safari 兼容 meta
- Modify: `d:/bishe/firefly-particles/style.css` — 移动端触控优化
- 无需新建文件

- [ ] **Step 1: 更新 index.html — 添加更多兼容性 meta**

在 `<head>` 的 `<meta charset>` 之后插入：

```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#050510">
```

- [ ] **Step 2: 更新 style.css — 移动端安全区 + 触控优化**

在 style.css 末尾追加：

```css
/* 移动端安全区 */
#status-indicator {
  bottom: max(24px, env(safe-area-inset-bottom, 24px));
  right: max(24px, env(safe-area-inset-right, 24px));
}

/* 防止移动端长按菜单 */
canvas {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
}

/* 加载文字移动端缩小 */
@media (max-width: 640px) {
  #guidance { font-size: 18px; }
  #loading p { font-size: 13px; }
  #status-indicator { font-size: 10px; }
}
```

- [ ] **Step 3: Commit**

```bash
git add firefly-particles/index.html firefly-particles/style.css
git commit -m "feat: add mobile optimization (safe area, touch, responsive)"
```

---

### Task 13: 本地测试 + 验证

- [ ] **Step 1: 启动本地 HTTPS 服务器**

```bash
# 使用 Python 生成自签名证书并启动 HTTPS 服务
cd d:/bishe/firefly-particles
npx local-ssl-proxy --source 8443 --target 8080 &
npx http-server -p 8080 -c-1
```

或者直接使用 localhost（浏览器豁免 HTTPS 摄像头权限）：

```bash
cd d:/bishe/firefly-particles
npx http-server -p 8080 -c-1
```

- [ ] **Step 2: 验证清单**

在浏览器打开 `http://localhost:8080`，逐项验证：

- [ ] 加载画面显示 "正在加载手势模型..." 随后消失
- [ ] 引导文字 "试试张开手掌 ✨" 显示并在 5s 后淡出
- [ ] 摄像头画面出现（镜像），粒子在画面中波浪浮动
- [ ] ✋ 张开手掌：粒子被推开，涟漪圆环扩散，叮咚音效
- [ ] ✊ 握拳：粒子聚拢 → 炸开 → 缓缓恢复，爆炸音效
- [ ] 👆 食指画圈：粒子形成光环，递增音阶音效
- [ ] 右下角状态指示器随手势变化
- [ ] 无手势时粒子恢复波浪流动
- [ ] 调整窗口大小后布局正常
- [ ] 手机访问（同一 WiFi 下用 IP + 端口）验证移动端表现

- [ ] **Step 3: Commit 最终版本**

```bash
git add .
git commit -m "feat: complete firefly gesture particle interaction application"
```
