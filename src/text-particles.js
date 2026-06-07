/**
 * 将文字渲染为粒子目标位置。
 * 返回 { x: number, y: number }[] 数组，坐标相对于文字区域中心。
 */
export function textToPositions(text, options = {}) {
  const {
    fontSize = 80,
    fontFamily = 'Arial, sans-serif',
    fontWeight = 'bold',
    particleCount = 300
  } = options;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  // 先测量文字
  ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
  const metrics = ctx.measureText(text);
  const tw = metrics.width;
  const th = fontSize;

  // 加 padding
  canvas.width = Math.ceil(tw + 40);
  canvas.height = Math.ceil(th + 40);

  // 绘制文字
  ctx.fillStyle = '#ffffff';
  ctx.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
  ctx.textBaseline = 'top';
  ctx.textAlign = 'left';
  ctx.fillText(text, 20, 20);

  // 提取像素
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const pixels = imageData.data;
  const brightPixels = [];

  for (let y = 0; y < canvas.height; y++) {
    for (let x = 0; x < canvas.width; x++) {
      const idx = (y * canvas.width + x) * 4;
      if (pixels[idx + 3] > 100) { // alpha > 100
        brightPixels.push({
          x: x - canvas.width / 2,
          y: y - canvas.height / 2
        });
      }
    }
  }

  // 采样到目标数量
  const result = [];
  const step = Math.max(1, Math.floor(brightPixels.length / particleCount));
  for (let i = 0; i < brightPixels.length && result.length < particleCount; i += step) {
    result.push(brightPixels[i]);
  }

  // 如果不够，补随机点
  while (result.length < particleCount) {
    result.push(brightPixels[Math.floor(Math.random() * brightPixels.length)] || { x: 0, y: 0 });
  }

  return result;
}
