export function createAudioEngine() {
  let ctx = null;
  let ambientNodes = null;

  function ensureContext() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  function startAmbient() {
    const c = ensureContext();
    if (ambientNodes) return;

    const bufferSize = 2 * c.sampleRate;
    const noiseBuffer = c.createBuffer(1, bufferSize, c.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

    const noiseSource = c.createBufferSource();
    noiseSource.buffer = noiseBuffer;
    noiseSource.loop = true;

    const lowpass = c.createBiquadFilter();
    lowpass.type = 'lowpass';
    lowpass.frequency.value = 400;
    lowpass.Q.value = 0.5;

    const lfo = c.createOscillator();
    lfo.frequency.value = 0.3;
    const lfoGain = c.createGain();
    lfoGain.gain.value = 0.3;
    lfo.connect(lfoGain);
    lfoGain.connect(lowpass.frequency);
    lfo.start();

    const waterGain = c.createGain();
    waterGain.gain.value = 0.04;

    noiseSource.connect(lowpass);
    lowpass.connect(waterGain);
    waterGain.connect(c.destination);
    noiseSource.start();

    const windSource = c.createBufferSource();
    windSource.buffer = noiseBuffer;
    windSource.loop = true;

    const highpass = c.createBiquadFilter();
    highpass.type = 'highpass';
    highpass.frequency.value = 2000;

    const windGain = c.createGain();
    windGain.gain.value = 0.015;

    windSource.connect(highpass);
    highpass.connect(windGain);
    windGain.connect(c.destination);
    windSource.start();

    ambientNodes = { noiseSource, windSource, waterGain, windGain, lfo };
  }

  function playDing(frequency = 800, duration = 0.3, volume = 0.15) {
    const c = ensureContext();
    const osc = c.createOscillator();
    const gain = c.createGain();

    osc.type = 'sine';
    osc.frequency.value = frequency;
    gain.gain.setValueAtTime(volume, c.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + duration);

    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(c.currentTime);
    osc.stop(c.currentTime + duration);
  }

  function playRipple() {
    playDing(880, 0.35, 0.12);
    setTimeout(() => playDing(660, 0.25, 0.08), 100);
  }

  function playExplosion() {
    const c = ensureContext();
    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(120, c.currentTime);
    osc.frequency.linearRampToValueAtTime(40, c.currentTime + 0.3);
    gain.gain.setValueAtTime(0.2, c.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.5);
    osc.connect(gain);
    gain.connect(c.destination);
    osc.start(c.currentTime);
    osc.stop(c.currentTime + 0.5);

    const bufferSize = c.sampleRate * 0.2;
    const noiseBuffer = c.createBuffer(1, bufferSize, c.sampleRate);
    const d = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    const noise = c.createBufferSource();
    noise.buffer = noiseBuffer;
    const bp = c.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 3000;
    bp.Q.value = 2;
    const ng = c.createGain();
    ng.gain.setValueAtTime(0.08, c.currentTime);
    ng.gain.exponentialRampToValueAtTime(0.001, c.currentTime + 0.2);
    noise.connect(bp);
    bp.connect(ng);
    ng.connect(c.destination);
    noise.start(c.currentTime);
  }

  function playRing() {
    const notes = [523, 659, 784, 1047];
    notes.forEach((freq, i) => {
      setTimeout(() => playDing(freq, 0.4, 0.1), i * 120);
    });
  }

  function stop() {
    if (ambientNodes) {
      ambientNodes.noiseSource.stop();
      ambientNodes.windSource.stop();
      ambientNodes.lfo.stop();
      ambientNodes = null;
    }
    if (ctx) { ctx.close(); ctx = null; }
  }

  return { startAmbient, playRipple, playExplosion, playRing, stop, ensureContext };
}
