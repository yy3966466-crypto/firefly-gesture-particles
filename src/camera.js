export function createVideoElement() {
  const video = document.createElement('video');
  video.setAttribute('playsinline', '');
  video.style.cssText = 'position:fixed;top:0;left:0;width:320px;height:240px;opacity:0.01;pointer-events:none;z-index:-1;';
  document.body.appendChild(video);
  return video;
}
