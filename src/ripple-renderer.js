import * as THREE from 'three';

export function createRippleRenderer(scene) {
  const ripples = [];

  function spawn(cx, cy) {
    const segments = 64;
    const geometry = new THREE.RingGeometry(5, 8, segments);
    const material = new THREE.MeshBasicMaterial({
      color: 0x22d3ee,
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
