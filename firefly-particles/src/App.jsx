import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import ParticleScene from './components/ParticleScene';
import StatusDisplay from './components/StatusDisplay';
import { useHandDetection } from './hooks/useHandDetection';

export default function App() {
  const videoRef = useRef(null);
  const { fingerCount, indexTipNDC, ready, error } = useHandDetection(videoRef);
  const [animState, setAnimState] = useState('idle'); // idle|explode|textClaude|holdClaude|textLove|holdLove
  const [rippleKey, setRippleKey] = useState(0);
  const [ripplePos, setRipplePos] = useState(null);
  const prevFingersRef = useRef(0);

  // 手势 → 动画状态
  useEffect(() => {
    const prev = prevFingersRef.current;
    if (fingerCount === 1 && prev !== 1 && animState === 'idle') {
      setAnimState('explode');
    } else if (fingerCount === 2 && (animState === 'idle' || animState === 'explode')) {
      setAnimState('textClaude');
    } else if (fingerCount === 3 && (animState === 'idle' || animState === 'explode')) {
      setAnimState('textLove');
    }
    prevFingersRef.current = fingerCount;
  }, [fingerCount, animState]);

  const onAnimComplete = useCallback((newState) => {
    setAnimState(newState);
  }, []);

  // 点击涟漪
  const handleClick = useCallback((e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = -(e.clientY / window.innerHeight) * 2 + 1;
    setRipplePos({
      x: x * 6,
      y: y * 4.5,
      z: 0,
      id: Date.now()
    });
    setRippleKey(k => k + 1);
    // 涟漪 2s 后消失
    setTimeout(() => setRipplePos(null), 2500);
  }, []);

  // 启动摄像头
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
    }).then(stream => {
      video.srcObject = stream;
      video.play();
    }).catch(() => {});
  }, []);

  return (
    <div className="w-full h-full bg-transparent" onClick={handleClick}>
      <video ref={videoRef} style={{ position:'fixed',top:0,left:0,width:'320px',height:'240px',opacity:0.01,pointerEvents:'none',zIndex:-1 }} playsInline autoPlay muted />

      {error && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <p className="text-red-400 text-sm text-center px-6">
            启动失败: {error}<br />
            <span className="text-white/50 text-xs">请使用 HTTPS 并允许摄像头权限</span>
          </p>
        </div>
      )}

      {!error && (
        <>
          <ParticleScene
            key={ready ? 'ready' : 'loading'}
            videoRef={videoRef}
            animState={animState}
            handPos={indexTipNDC}
            ripplePos={ripplePos}
            onAnimComplete={onAnimComplete}
          />
          <StatusDisplay fingerCount={fingerCount} animState={animState} />

          {/* 加载/引导 */}
          {!ready && (
            <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 pointer-events-none">
              <p className="text-white/70 text-sm animate-pulse">正在加载手势模型...</p>
            </div>
          )}
          {ready && (
            <div className="guide-fade fixed inset-0 z-30 flex items-center justify-center pointer-events-none">
              <p className="text-white/60 text-sm sm:text-base text-center px-4">
                ☝️ 1指炸开 &nbsp; ✌️ 2指 claude code &nbsp; 🤟 3指 love life<br />
                <span className="text-white/30 text-xs">轻点水面泛起涟漪</span>
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
