export async function initHandDetector() {
  const hands = new Hands({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`
  });

  hands.setOptions({
    maxNumHands: 2,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.5
  });

  await hands.initialize();
  return hands;
}

/**
 * 从 video 检测手部，返回 landmarks 列表（屏幕坐标，已镜像）。
 * 每个 landmark 为 { x, y } 像素坐标。
 */
export async function detectHands(hands, videoElement) {
  if (!videoElement || videoElement.readyState < 2) return [];

  const results = await hands.send({ image: videoElement });

  if (!results || !results.multiHandLandmarks) return [];

  const width = videoElement.videoWidth;
  const height = videoElement.videoHeight;

  return results.multiHandLandmarks.map((landmarks, idx) => {
    const handedness = results.multiHandedness?.[idx]?.label || 'unknown';
    const points = landmarks.map(l => ({
      x: (1 - l.x) * width,   // 镜像 x
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
