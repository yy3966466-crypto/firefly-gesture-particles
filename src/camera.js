export async function initCamera() {
  const video = document.createElement('video');
  video.setAttribute('playsinline', '');
  video.style.cssText = 'position:fixed;top:0;left:0;width:320px;height:240px;opacity:0.01;pointer-events:none;z-index:-1;';
  document.body.appendChild(video);

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
  });
  video.srcObject = stream;
  await video.play();

  return { stream, video };
}
