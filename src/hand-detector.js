export async function initHandDetector(videoElement, onProgress) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('模型加载超时')), 30000);

    const hands = new Hands({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`
    });

    hands.setOptions({
      maxNumHands: 1,
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
          landmarks: results.multiHandLandmarks[0],
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

/** 计算伸出的手指数量 */
export function countFingers() {
  const r = window.__lastResults;
  if (!r) return 0;

  const lm = r.landmarks;
  // 指尖: 4(拇指), 8(食指), 12(中指), 16(无名指), 20(小指)
  // MCP:  2(拇指), 5(食指), 9(中指),  13(无名指), 17(小指)
  const tips = [4, 8, 12, 16, 20];
  const mcps = [2, 5, 9, 13, 17];
  let count = 0;

  for (let i = 0; i < 5; i++) {
    const tip = lm[tips[i]];
    const mcp = lm[mcps[i]];
    // 指尖 y < MCP y 表示手指伸出（MediaPipe 坐标系 y 向下）
    if (tip.y < mcp.y) count++;
  }
  return count;
}

/** 获取食指指尖屏幕坐标 */
export function getIndexTip(screenW, screenH) {
  const r = window.__lastResults;
  if (!r) return null;
  const tip = r.landmarks[8]; // 食指指尖
  return {
    x: (1 - tip.x) * screenW,
    y: tip.y * screenH
  };
}
