import { useEffect, useRef, useCallback, useState } from 'react';
import { HandLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';

/**
 * React hook: 实时手部检测，返回手指数量 & 食指指尖 3D 位置。
 */
export function useHandDetection(videoRef) {
  const handLandmarkerRef = useRef(null);
  const rafRef = useRef(null);
  const [fingerCount, setFingerCount] = useState(0);
  const [indexTipNDC, setIndexTipNDC] = useState({ x: 0.5, y: 0.5 });
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(null);

  const initDetector = useCallback(async () => {
    try {
      const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
      );
      const handLandmarker = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task',
          delegate: 'GPU'
        },
        runningMode: 'VIDEO',
        numHands: 1,
        minHandDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });
      handLandmarkerRef.current = handLandmarker;
      setReady(true);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => { initDetector(); }, [initDetector]);

  const detectLoop = useCallback(() => {
    const video = videoRef.current;
    const detector = handLandmarkerRef.current;
    if (!video || !detector || video.readyState < 2) {
      rafRef.current = requestAnimationFrame(detectLoop);
      return;
    }

    const results = detector.detectForVideo(video, performance.now());
    if (results.landmarks && results.landmarks.length > 0) {
      const lm = results.landmarks[0];
      // 指尖: 4(拇指), 8(食指), 12(中指), 16(无名指), 20(小指)
      // MCP:  2(拇指), 5(食指), 9(中指), 13(无名指), 17(小指)
      const tips = [4, 8, 12, 16, 20];
      const mcps = [2, 5, 9, 13, 17];
      let count = 0;
      for (let i = 0; i < 5; i++) {
        if (lm[tips[i]].y < lm[mcps[i]].y) count++;
      }
      setFingerCount(count);
      // 食指指尖 NDC (0~1, y 向下)，镜像 x
      const tip = lm[8];
      setIndexTipNDC({ x: 1 - tip.x, y: tip.y });
    } else {
      setFingerCount(0);
    }
    rafRef.current = requestAnimationFrame(detectLoop);
  }, [videoRef]);

  useEffect(() => {
    if (ready) rafRef.current = requestAnimationFrame(detectLoop);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [ready, detectLoop]);

  return { fingerCount, indexTipNDC, ready, error };
}
