import * as THREE from 'three';
import { isMobile, PARTICLE_COUNT } from './utils.js';
import { createVideoElement } from './camera.js';
import { createScene, handleResize } from './scene.js';
import { createParticleSystem, updateParticleWave } from './particle-engine.js';
import { createPhysicsEngine, integrate } from './physics.js';
import { initHandDetector, detectHands } from './hand-detector.js';
import { createGestureClassifier, classifyGesture, GestureState } from './gesture-classifier.js';
import { applyRipple, applyAttract, applyExplosion, applyRingAttraction } from './gesture-physics.js';
import { createAudioEngine } from './audio.js';
import { createRippleRenderer } from './ripple-renderer.js';

async function main() {
  // 1. 创建 video 元素（MediaPipe Camera 会管理摄像头）
  const video = createVideoElement();

  // 2. Three.js 场景
  const { renderer, scene, camera, bgPlane } = createScene(video);

  // 3. 粒子系统
  const particles = createParticleSystem(window.innerWidth, window.innerHeight);
  scene.add(particles.points);

  // 4. 涟漪渲染
  const rippleRenderer = createRippleRenderer(scene);

  // 5. 物理引擎
  const physics = createPhysicsEngine(PARTICLE_COUNT);

  // 6-8. UI 元素
  const loadingEl = document.getElementById('loading');
  const loadingText = loadingEl.querySelector('p');
  const guidanceEl = document.getElementById('guidance');
  const statusEl = document.getElementById('status-indicator');
  const statusDot = statusEl.querySelector('.dot');
  const statusLabel = statusEl.querySelector('.label');

  // 更新加载文字
  loadingText.textContent = '正在加载手势模型...';

  // 手势检测（MediaPipe Camera 管理视频帧推送）
  const { hands } = await initHandDetector(video, (msg) => {
    loadingText.textContent = msg;
  });

  // 手势分类器
  const classifier = createGestureClassifier();

  // 音效
  const audio = createAudioEngine();

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
    if (dt > 0.1) dt = 0.1;
    lastTime = now;

    const w = window.innerWidth;
    const h = window.innerHeight;

    // 手势检测（同步读取 MediaPipe 结果）
    const handData = detectHands();
    classifyGesture(classifier, handData, dt, 640, 480, w, h);

    const state = classifier.state;

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

    if (state === GestureState.PALM) {
      applyRipple(particles.positions, physics, classifier.handCenter, w, h);
    }
    if (state === GestureState.FIST_ATTRACT) {
      applyAttract(particles.positions, physics, classifier.handCenter, w, h);
    }
    if (state === GestureState.CIRCLE_HOLD) {
      applyRingAttraction(particles.positions, physics, classifier, w, h);
    }

    updateStatusIndicator(state, statusEl, statusDot, statusLabel);
    statusLabel.textContent = (window.__handDebug || '?') + ' ' + state;

    prevGesture = state;

    // 物理积分
    integrate(particles.positions, particles.basePositions, physics, dt, w, h);

    // 波浪更新（未被外力驱动的粒子）
    updateParticleWave(particles, performance.now() / 1000, dt, physics.driven);

    // 涟漪动画
    rippleRenderer.update(dt);

    // 渲染
    renderer.render(scene, camera);
  }

  requestAnimationFrame(loop);

  // 窗口大小调整
  window.addEventListener('resize', () => {
    handleResize({ renderer, camera, bgPlane });
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
  const loadingEl = document.getElementById('loading');
  const msg = err.message || String(err);
  if (msg.includes('not allowed') || msg.includes('Permission')) {
    loadingEl.innerHTML = `<p style="color:#ff6b6b;">摄像头权限被拒绝<br><small>请允许摄像头访问后刷新页面</small></p>`;
  } else if (msg.includes('超时')) {
    loadingEl.innerHTML = `<p style="color:#ffb060;">${msg}<br><small>请检查网络后刷新页面重试</small></p>`;
  } else {
    loadingEl.innerHTML = `<p style="color:#ff6b6b;">启动失败: ${msg}<br><small>请确保使用 HTTPS 并授予摄像头权限</small></p>`;
  }
});
