import * as THREE from 'three';

let _bgPlane = null;
let _videoAspect = 16 / 9;

function createBgGeometry(w, h) {
  // cover 模式：保持视频比例，裁剪填满
  const screenAspect = w / h;
  let pw, ph;
  if (screenAspect > _videoAspect) {
    ph = h;
    pw = h * _videoAspect;
  } else {
    pw = w;
    ph = w / _videoAspect;
  }
  const geo = new THREE.PlaneGeometry(pw, ph);
  const uvs = geo.attributes.uv;
  for (let i = 0; i < uvs.count; i++) uvs.setX(i, 1 - uvs.getX(i));
  uvs.needsUpdate = true;
  return { geometry: geo, pw, ph };
}

export function createScene(videoElement) {
  const canvas = document.getElementById('canvas');
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(0, window.innerWidth, window.innerHeight, 0, 0.1, 10);
  camera.position.z = 5;

  const videoTexture = new THREE.VideoTexture(videoElement);
  videoTexture.minFilter = THREE.LinearFilter;
  videoTexture.magFilter = THREE.LinearFilter;

  const { geometry: bgGeometry, pw, ph } = createBgGeometry(window.innerWidth, window.innerHeight);
  const bgMaterial = new THREE.MeshBasicMaterial({ map: videoTexture });
  _bgPlane = new THREE.Mesh(bgGeometry, bgMaterial);
  _bgPlane.position.set(window.innerWidth / 2, window.innerHeight / 2, -1);
  scene.add(_bgPlane);

  return { renderer, scene, camera, videoTexture, bgPlane: _bgPlane, canvas };
}

export function handleResize({ renderer, camera, bgPlane }) {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h);
  camera.right = w;
  camera.bottom = h;
  camera.updateProjectionMatrix();
  bgPlane.geometry.dispose();
  const { geometry, pw, ph } = createBgGeometry(w, h);
  bgPlane.geometry = geometry;
  bgPlane.position.set(w / 2, h / 2, -1);
}

export function setVideoAspect(videoElement) {
  if (videoElement.videoWidth && videoElement.videoHeight) {
    _videoAspect = videoElement.videoWidth / videoElement.videoHeight;
  }
}
