/**
 * 将文字渲染为 2D 点阵。
 * 返回 { x, y }[] 数组，坐标以文字区域中心为原点，范围已归一化。
 */
export function textToPoints(text, targetCount = 4000) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const fontSize = 100;

  ctx.font = `bold ${fontSize}px "Segoe UI", "PingFang SC", Arial, sans-serif`;
  const metrics = ctx.measureText(text);
  const tw = metrics.width;
  const th = fontSize;

  canvas.width = Math.ceil(tw + 60);
  canvas.height = Math.ceil(th + 60);
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${fontSize}px "Segoe UI", "PingFang SC", Arial, sans-serif`;
  ctx.textBaseline = 'top';
  ctx.textAlign = 'left';
  ctx.fillText(text, 30, 30);

  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const bright = [];
  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      if (img.data[(y * canvas.width + x) * 4 + 3] > 80) {
        bright.push({
          x: (x - canvas.width / 2) / (canvas.width / 2),
          y: (y - canvas.height / 2) / (canvas.height / 2)
        });
      }
    }
  }

  if (bright.length === 0) return [];

  const result = [];
  const step = Math.max(1, Math.floor(bright.length / targetCount));
  for (let i = 0; i < bright.length && result.length < targetCount; i += step) {
    result.push(bright[i]);
  }
  while (result.length < targetCount) {
    result.push(bright[Math.floor(Math.random() * bright.length)]);
  }
  return result;
}
