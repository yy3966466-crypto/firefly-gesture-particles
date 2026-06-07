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
      if (positions[idx3 + 1] < 0) { positions[idx3 + 1] = 0; velocities[idx2 + 1] *= -0.3; }
      if (positions[idx3 + 1] > height) { positions[idx3 + 1] = height; velocities[idx2 + 1] *= -0.3; }

      // 速度很小时退出驱动模式
      if (Math.abs(velocities[idx2]) < 0.5 && Math.abs(velocities[idx2 + 1]) < 0.5) {
        velocities[idx2] = 0;
        velocities[idx2 + 1] = 0;
        driven[i] = 0;
        // 更新 basePositions 为当前位置，让粒子从新位置开始波浪
        basePositions[idx2] = positions[idx3];
        basePositions[idx2 + 1] = positions[idx3 + 1];
      }
    }

    // 清零力累加器
    forces[idx2] = 0;
    forces[idx2 + 1] = 0;
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
