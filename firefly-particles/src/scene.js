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
