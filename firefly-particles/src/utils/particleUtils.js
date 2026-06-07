const PARTICLE_COUNT = 4000;

export function getParticleCount() { return PARTICLE_COUNT; }

/** 粒子初始位置 & 属性 */
export function createInitialParticles() {
  const count = PARTICLE_COUNT;
  const positions = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const targets = new Float32Array(count * 3);
  const phases = new Float32Array(count);

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 10;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 8;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 3;
    targets[i * 3] = positions[i * 3];
    targets[i * 3 + 1] = positions[i * 3 + 1];
    targets[i * 3 + 2] = positions[i * 3 + 2];
    sizes[i] = 0.015 + Math.random() * 0.035;
    phases[i] = Math.random() * Math.PI * 2;
  }
  return { positions, sizes, targets, phases };
}

/** 波浪漂浮更新 */
export function updateFloat(positions, targets, phases, time, dt) {
  const count = positions.length / 3;
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const ox = targets[i3];
    const oy = targets[i3 + 1];
    const oz = targets[i3 + 2];
    const p = phases[i];
    positions[i3] = ox + 0.4 * Math.sin(time * 0.7 + p);
    positions[i3 + 1] = oy + 0.3 * Math.cos(time * 0.9 + p + 1);
    positions[i3 + 2] = oz + 0.15 * Math.sin(time * 0.5 + p + 2);
  }
}

/** Lerp 粒子到目标位置（文字/指尖） */
export function lerpToTargets(positions, targets, factor = 0.08) {
  const count = positions.length / 3;
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    positions[i3] += (targets[i3] - positions[i3]) * factor;
    positions[i3 + 1] += (targets[i3 + 1] - positions[i3 + 1]) * factor;
    positions[i3 + 2] += (targets[i3 + 2] - positions[i3 + 2]) * factor;
  }
}

/** 爆炸速度 */
export function applyExplosion(positions, targets, centerX, centerY, centerZ) {
  const count = positions.length / 3;
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const dx = positions[i3] - centerX;
    const dy = positions[i3 + 1] - centerY;
    const dz = positions[i3 + 2] - centerZ;
    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 0.01;
    const force = 0.5 + Math.random() * 1.5;
    positions[i3] += (dx / dist) * force;
    positions[i3 + 1] += (dy / dist) * force;
    positions[i3 + 2] += (dz / dist) * force;
    targets[i3] = positions[i3];
    targets[i3 + 1] = positions[i3 + 1];
    targets[i3 + 2] = positions[i3 + 2];
  }
}

/** 涟漪推开 */
export function applyRipple(positions, targets, cx, cy, cz, radius = 2.5, strength = 0.4) {
  const count = positions.length / 3;
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const dx = positions[i3] - cx;
    const dy = positions[i3 + 1] - cy;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d < radius && d > 0.01) {
      const f = strength * (1 - d / radius);
      positions[i3] += (dx / d) * f;
      positions[i3 + 1] += (dy / d) * f;
      targets[i3] = positions[i3];
      targets[i3 + 1] = positions[i3 + 1];
    }
  }
}
