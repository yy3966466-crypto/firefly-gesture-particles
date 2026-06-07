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
  video.style.display = 'none';
  document.body.appendChild(video);
  return video;
}
