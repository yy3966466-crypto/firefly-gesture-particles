export async function initHandDetector(onProgress) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('手势模型加载超时，请检查网络连接后刷新页面'));
    }, 30000);

    const hands = new Hands({
      locateFile: (file) => {
        if (onProgress) onProgress('正在下载模型...');
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`;
      }
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.3,
      minTrackingConfidence: 0.3
    });

    if (onProgress) onProgress('正在初始化手势识别...');
    hands.initialize()
      .then(() => {
        clearTimeout(timeout);
        resolve(hands);
      })
      .catch(err => {
        clearTimeout(timeout);
        reject(new Error(`手势模型加载失败: ${err.message}`));
      });
  });
}

/**
 * 从 video 检测手部，返回 landmarks 列表（屏幕坐标，已镜像）。
 * 每个 landmark 为 { x, y } 像素坐标。
 */
let _debugCanvas = null;

export async function detectHands(hands, videoElement) {
  if (!videoElement) { window.__handDebug = 'no_video'; return []; }
  if (videoElement.readyState < 2) {
    window.__handDebug = 'ready:' + videoElement.readyState + ' ' + videoElement.videoWidth + 'x' + videoElement.videoHeight;
    return [];
  }

  // 通过 canvas 中转，确保 MediaPipe 能稳定读取视频帧
  if (!_debugCanvas) {
    _debugCanvas = document.createElement('canvas');
    _debugCanvas.width = videoElement.videoWidth || 640;
    _debugCanvas.height = videoElement.videoHeight || 480;
    _debugCanvas.style.cssText = 'position:fixed;top:0;left:320px;width:160px;height:120px;opacity:0.3;z-index:999;border:1px solid red;';
    document.body.appendChild(_debugCanvas);
  }
  const ctx = _debugCanvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0, _debugCanvas.width, _debugCanvas.height);

  let results;
  try {
    results = await hands.send({ image: _debugCanvas });
  } catch (e) {
    window.__handDebug = 'send_err:' + e.message;
    return [];
  }

  if (!results || !results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
    window.__handDebug = 'empty:' + (results ? 'has_results' : 'no_results');
    return [];
  }

  window.__handDebug = 'OK:' + results.multiHandLandmarks.length;
  const width = _debugCanvas.width;
  const height = _debugCanvas.height;

  return results.multiHandLandmarks.map((landmarks, idx) => {
    const handedness = results.multiHandedness?.[idx]?.label || 'unknown';
    const points = landmarks.map(l => ({
      x: (1 - l.x) * width,
      y: l.y * height
    }));
    return { points, handedness };
  });
}

/** MediaPipe 手部关键点索引 */
export const LANDMARK = {
  WRIST: 0,
  THUMB_TIP: 4,
  INDEX_TIP: 8,
  MIDDLE_TIP: 12,
  RING_TIP: 16,
  PINKY_TIP: 20,
  INDEX_MCP: 5,
  MIDDLE_MCP: 9,
  RING_MCP: 13,
  PINKY_MCP: 17
};
