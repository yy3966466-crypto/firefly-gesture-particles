import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 13

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8.8))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 10)
ax.set_ylim(0, 9.0)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------
TEXT_CLR  = '#000000'
ARR_CLR   = '#000000'
BOX_FILL  = '#FFFFFF'
BOX_EDGE  = '#333333'

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
OFF = 0.12
CX  = 5.0
LW  = 1.2    # unified linewidth

def draw_box(cx, cy, w, h, title='', sub='', t_size=13, s_size=13):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=LW,
        boxstyle="round,pad=0.08",
    )
    ax.add_patch(rect)
    if title:
        ax.text(cx, cy + 0.12, title, fontsize=t_size, fontweight='bold',
                ha='center', va='bottom', color=TEXT_CLR)
    if sub:
        ax.text(cx, cy - 0.08, sub, fontsize=s_size, fontweight='bold',
                ha='center', va='top', color=TEXT_CLR)

# ---------------------------------------------------------------------------
# 6 steps (vertical pipeline)
# ---------------------------------------------------------------------------
box_w = 5.0
box_h = 0.70

steps = [
    (r'原始信号输入', r'$x(n)$ --- 原始生理信号'),
    (r'预处理滤波',   r'带通滤波 (0.5~45Hz) + 去基线漂移'),
    (r'自适应噪声对消', r'$y(n) = \mathbf{w}^{\mathrm{T}}(n) * \mathbf{x}(n)$'),
    (r'残差信号提取',  r'$e(n) = x(n) - y(n)$'),
    (r'SNR 计算',     r'$\mathrm{SNR} = 10 * \log_{10}(E[y^{2}] / E[e^{2}])$'),
    (r'结果输出',     r'$\mathrm{SNR}$ 值 (dB)'),
]

N = len(steps)
y_top = 8.20
spacing = 1.35
centers = [y_top - i * spacing for i in range(N)]

for i, (title, sub) in enumerate(steps):
    draw_box(CX, centers[i], box_w, box_h, title, sub, t_size=13, s_size=13)

# vertical arrows
for i in range(N - 1):
    y_from = centers[i] - box_h / 2 - OFF
    y_to   = centers[i + 1] + box_h / 2 + OFF
    ax.annotate('', xy=(CX, y_to), xytext=(CX, y_from),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=LW))

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/snr_estimation.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/snr_estimation.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → snr_estimation.png')
