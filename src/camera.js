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
  video.setAttribute('playsinline', '');
  video.setAttribute('autoplay', '');
  video.setAttribute('muted', '');
  // 不能用 display:none，MediaPipe 访问不到视频帧
  video.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0.01;pointer-events:none;z-index:-1;';
  document.body.appendChild(video);
  return video;
}
