import { useRef, useMemo, useCallback, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import {
  getParticleCount, createInitialParticles,
  updateFloat, lerpToTargets, applyExplosion, applyRipple
} from '../utils/particleUtils.js';
import { textToPoints } from '../utils/textToPoints.js';

const COUNT = getParticleCount();

// ══════════════ 粒子 Shader ══════════════
const vertShader = `
  attribute float size;
  varying float vAlpha;
  uniform float uAlpha;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = size * (300.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
    vAlpha = uAlpha;
  }
`;

const fragShader = `
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float glow = exp(-d * 3.8);
    if (glow * vAlpha < 0.02) discard;
    gl_FragColor = vec4(1.0, 1.0, 1.0, glow * vAlpha);
  }
`;

// ══════════════ 涟漪环 Mesh ══════════════
function RippleRing({ cx, cy, cz, id }) {
  const ref = useRef();
  const ageRef = useRef(0);

  useFrame((_, dt) => {
    if (!ref.current) return;
    ageRef.current += dt;
    const t = ageRef.current / 2.5;
    if (t >= 1) { ref.current.visible = false; return; }
    const s = 0.05 + 3.5 * t;
    ref.current.scale.setScalar(s);
    ref.current.material.opacity = 0.5 * (1 - t);
  });

  return (
    <mesh ref={ref} position={[cx, cy, cz]}>
      <ringGeometry args={[0.08, 0.1, 48]} />
      <meshBasicMaterial color="white" side={2} transparent opacity={0.5} depthTest={false} depthWrite={false} />
    </mesh>
  );
}

// ══════════════ 粒子系统 ══════════════
function Particles({ animState, handPos, ripplePos, onAnimComplete }) {
  const pointsRef = useRef();
  const { positions, sizes, targets, phases } = useMemo(createInitialParticles, []);
  const textTargets = useMemo(() => ({
    claude: textToPoints('claude code', COUNT),
    love: textToPoints('love life', COUNT)
  }), []);
  const stateRef = useRef({ state: 'idle', timer: 0, prevFingers: 0 });
  const posAttr = useRef(null);

  // 设置文字目标
  const setTextTargets = useCallback((textKey, scale = 3) => {
    const pts = textTargets[textKey];
    if (!pts) return;
    for (let i = 0; i < COUNT; i++) {
      const p = pts[i] || pts[Math.floor(Math.random() * pts.length)] || { x: 0, y: 0 };
      targets[i * 3] = p.x * scale;
      targets[i * 3 + 1] = p.y * scale * 0.5;
      targets[i * 3 + 2] = 0;
    }
  }, [targets, textTargets]);

  // 设置指尖目标
  const setFingertipTargets = useCallback((ndcX, ndcY) => {
    for (let i = 0; i < COUNT; i++) {
      const angle = Math.random() * Math.PI * 2;
      const r = Math.random() * 0.3;
      targets[i * 3] = (ndcX - 0.5) * 8;
      targets[i * 3 + 1] = (0.5 - ndcY) * 6;
      targets[i * 3 + 2] = (Math.random() - 0.5) * 0.5;
    }
  }, [targets]);

  // 状态机
  useEffect(() => {
    const s = stateRef.current;
    const prev = s.state;

    if (animState === 'explode') {
      if (prev !== 'explode') {
        s.state = 'explode'; s.timer = 0;
        setFingertipTargets(handPos.x, handPos.y);
        // 立即聚拢
        for (let i = 0; i < COUNT; i++) {
          positions[i * 3] = targets[i * 3];
          positions[i * 3 + 1] = targets[i * 3 + 1];
          positions[i * 3 + 2] = targets[i * 3 + 2];
        }
        applyExplosion(positions, targets,
          (handPos.x - 0.5) * 8, (0.5 - handPos.y) * 6, 0);
      }
    } else if (animState === 'textClaude') {
      if (prev !== 'textClaude' && prev !== 'holdClaude') {
        s.state = 'textClaude'; s.timer = 0;
        setTextTargets('claude', 3);
      }
    } else if (animState === 'textLove') {
      if (prev !== 'textLove' && prev !== 'holdLove') {
        s.state = 'textLove'; s.timer = 0;
        setTextTargets('love', 3.2);
      }
    } else if (animState === 'idle') {
      if (prev === 'holdClaude' || prev === 'holdLove') {
        // 散开
        for (let i = 0; i < COUNT; i++) {
          targets[i * 3] = (Math.random() - 0.5) * 10;
          targets[i * 3 + 1] = (Math.random() - 0.5) * 8;
          targets[i * 3 + 2] = (Math.random() - 0.5) * 3;
        }
      }
      s.state = 'idle'; s.timer = 0;
    }
    stateRef.current = s;
  }, [animState, handPos, setFingertipTargets, setTextTargets, positions, targets]);

  useFrame((st, dt) => {
    if (!posAttr.current) return;
    const s = stateRef.current;
    s.timer += dt;

    // 状态转换
    if (s.state === 'explode' && s.timer > 2.5) {
      s.state = 'idle'; s.timer = 0;
      for (let i = 0; i < COUNT; i++) {
        targets[i * 3] = (Math.random() - 0.5) * 10;
        targets[i * 3 + 1] = (Math.random() - 0.5) * 8;
        targets[i * 3 + 2] = (Math.random() - 0.5) * 3;
      }
      onAnimComplete && onAnimComplete('idle');
    }
    if (s.state === 'textClaude' && s.timer > 1.5) {
      s.state = 'holdClaude'; s.timer = 0;
      onAnimComplete && onAnimComplete('holdClaude');
    }
    if (s.state === 'holdClaude' && s.timer > 5.0) {
      s.state = 'idle'; s.timer = 0;
      for (let i = 0; i < COUNT; i++) {
        targets[i * 3] = (Math.random() - 0.5) * 10;
        targets[i * 3 + 1] = (Math.random() - 0.5) * 8;
        targets[i * 3 + 2] = (Math.random() - 0.5) * 3;
      }
      onAnimComplete && onAnimComplete('idle');
    }
    if (s.state === 'textLove' && s.timer > 1.5) {
      s.state = 'holdLove'; s.timer = 0;
      onAnimComplete && onAnimComplete('holdLove');
    }
    if (s.state === 'holdLove' && s.timer > 6.0) {
      s.state = 'idle'; s.timer = 0;
      for (let i = 0; i < COUNT; i++) {
        targets[i * 3] = (Math.random() - 0.5) * 10;
        targets[i * 3 + 1] = (Math.random() - 0.5) * 8;
        targets[i * 3 + 2] = (Math.random() - 0.5) * 3;
      }
      onAnimComplete && onAnimComplete('idle');
    }

    // 更新粒子
    if (s.state === 'idle') {
      updateFloat(positions, targets, phases, st.clock.elapsedTime, dt);
    } else {
      lerpToTargets(positions, targets, 0.06);
    }

    // 涟漪
    if (ripplePos) {
      applyRipple(positions, targets, ripplePos.x, ripplePos.y, ripplePos.z, 2.5, 0.3);
    }

    posAttr.current.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute ref={posAttr} attach="attributes-position" count={COUNT} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-size" count={COUNT} array={sizes} itemSize={1} />
      </bufferGeometry>
      <shaderMaterial
        vertexShader={vertShader}
        fragmentShader={fragShader}
        uniforms={{ uAlpha: { value: 0.75 } }}
        transparent
        blending={THREE.AdditiveBlending}
        depthWrite={false}
        depthTest={false}
      />
    </points>
  );
}

// ══════════════ 摄像头背景 ══════════════
function VideoBackground({ videoRef }) {
  const matRef = useRef();

  useEffect(() => {
    const video = videoRef?.current;
    if (!video) return;
    const tex = new THREE.VideoTexture(video);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    if (matRef.current) matRef.current.map = tex;
  }, [videoRef]);

  return (
    <mesh position={[0, 0, -4]}>
      <planeGeometry args={[16, 9]} />
      <meshBasicMaterial ref={matRef} color="#0a0a1e" depthTest={false} depthWrite={false} />
    </mesh>
  );
}

// ══════════════ 场景容器 ══════════════
function SceneContent({ videoRef, animState, handPos, ripplePos, onAnimComplete }) {
  return (
    <>
      <ambientLight intensity={0.1} />
      <VideoBackground videoRef={videoRef} />
      {/* 半透明水面 */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2.5, 0]}>
        <planeGeometry args={[16, 12]} />
        <meshStandardMaterial color="#1a1a3e" transparent opacity={0.1} depthWrite={false} />
      </mesh>
      <Particles animState={animState} handPos={handPos} ripplePos={ripplePos} onAnimComplete={onAnimComplete} />
      {ripplePos && <RippleRing cx={ripplePos.x} cy={ripplePos.y} cz={ripplePos.z} id={ripplePos.id} />}
    </>
  );
}

export default function ParticleScene({ videoRef, animState, handPos, ripplePos, onAnimComplete }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 55, near: 0.1, far: 50 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: false }}
      style={{ position: 'fixed', inset: 0 }}
    >
      <color attach="background" args={['#050510']} />
      <SceneContent videoRef={videoRef} animState={animState} handPos={handPos} ripplePos={ripplePos} onAnimComplete={onAnimComplete} />
    </Canvas>
  );
}
