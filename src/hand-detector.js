export async function initHandDetector(videoElement, onProgress) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('手势模型加载超时'));
    }, 30000);

    const hands = new Hands({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    const camera = new Camera(videoElement, {
      onFrame: async () => {
        try { await hands.send({ image: videoElement }); } catch (e) {}
      },
      width: 640,
      height: 480
    });

    hands.onResults((results) => {
      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        window.__lastResults = {
          multiHandLandmarks: results.multiHandLandmarks,
          multiHandedness: results.multiHandedness,
          width: 640, height: 480
        };
      } else {
        window.__lastResults = null;
      }
    });

    if (onProgress) onProgress('初始化中...');
    hands.initialize()
      .then(() => {
        clearTimeout(timeout);
        if (onProgress) onProgress('启动摄像头...');
        camera.start().then(() => {
          if (onProgress) onProgress('就绪');
          resolve({ hands, camera });
        }).catch(err => reject(new Error('摄像头启动失败: ' + err.message)));
      })
      .catch(err => {
        clearTimeout(timeout);
        reject(new Error('模型加载失败: ' + err.message));
      });
  });
}

export function detectHands() {
  const r = window.__lastResults;
  if (!r || !r.multiHandLandmarks || r.multiHandLandmarks.length === 0) return [];
  return r.multiHandLandmarks.map((landmarks, idx) => ({
    points: landmarks.map(l => ({
      x: (1 - l.x) * r.width,
      y: l.y * r.height
    })),
    handedness: r.multiHandedness?.[idx]?.label || 'unknown'
  }));
}

export const LANDMARK = {
  WRIST: 0, THUMB_TIP: 4, INDEX_TIP: 8, MIDDLE_TIP: 12,
  RING_TIP: 16, PINKY_TIP: 20, INDEX_MCP: 5, MIDDLE_MCP: 9,
  RING_MCP: 13, PINKY_MCP: 17
};
