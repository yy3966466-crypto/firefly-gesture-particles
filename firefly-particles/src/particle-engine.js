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
