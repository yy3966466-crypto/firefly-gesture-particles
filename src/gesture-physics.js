import { applyRadialForce } from './physics.js';
import { GestureState } from './gesture-classifier.js';
import { dist, rand } from './utils.js';

export function applyRipple(positions, engine, handCenter, screenW, screenH) {
  const cx = handCenter.x;
  const cy = handCenter.y;
  applyRadialForce(positions, engine, cx, cy, 50000, 280);
  return { cx, cy, time: 0 };
}

export function applyAttract(positions, engine, handCenter, screenW, screenH) {
  const cx = handCenter.x;
  const cy = handCenter.y;
  applyRadialForce(positions, engine, cx, cy, -30000, 250);
  return { cx, cy };
}

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
      const radialDir = (d - radius) > 0 ? -1 : 1;
      const radialStrength = Math.abs(d - radius) * 60;
      const dx = (positions[idx3] - cx) / d;
      const dy = (positions[idx3 + 1] - cy) / d;
      forces[idx2] += dx * radialStrength * radialDir;
      forces[idx2 + 1] += dy * radialStrength * radialDir;

      forces[idx2] += -dy * 800;
      forces[idx2 + 1] += dx * 800;

      driven[i] = 1;
    }
  }
}
