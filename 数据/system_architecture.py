import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# figure setup — original spacing
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 9.5))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 11)
ax.set_ylim(0, 9.5)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours — white background, black text
# ---------------------------------------------------------------------------
DARK     = '#000000'
GRAY     = '#444444'
ARR_CLR  = '#000000'
BOX_FILL = '#FFFFFF'
BOX_EDGE = '#333333'

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
OFF   = 0.12
CX    = 5.5
BOX_W = 6.5

def draw_box(cy, title, lines, box_h=1.15, t_size=12, l_size=11):
    left = CX - BOX_W / 2
    rect = mpatches.FancyBboxPatch(
        (left, cy - box_h / 2), BOX_W, box_h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
        boxstyle="round,pad=0.10",
    )
    ax.add_patch(rect)

    ax.text(CX, cy + box_h / 2 - 0.15, title,
            fontsize=t_size, fontweight='bold',
            ha='center', va='top', color=DARK)

    ax.text(CX, cy - 0.08, lines,
            fontsize=l_size, fontweight='bold', ha='center', va='top', color=DARK,
            linespacing=1.5)

def v_arrow(cy_top, cy_bot, h_top=1.15, h_bot=1.15):
    y_from = cy_top - h_top / 2 - OFF
    y_to   = cy_bot + h_bot / 2 + OFF
    ax.annotate('', xy=(CX, y_to), xytext=(CX, y_from),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=2.0))

# ---------------------------------------------------------------------------
# four layers — original spacing
# ---------------------------------------------------------------------------
y_list = [7.80, 6.00, 4.20, 2.40]

layers = [
    ('UI层（用户界面）',
     'App Designer  |  实时波形显示  |  用户交互操作'),
    ('逻辑层（业务逻辑）',
     'BioMonitorApp Controller\n数据调度与指令分发'),
    ('信号层（信号处理）',
     '滤波去噪（FFT / 零相位）\nQRS 检测（5-18Hz）\n特征提取（RR间期 / HRV）'),
    ('数据层（数据存取）',
     'PhysioNet / .mat 缓存\nGooDeTek 串口（9600baud）\n会话保存与导出'),
]

left_labels = ['展示', '调度', '处理', '存取']
box_heights = [1.15, 1.15, 1.15, 1.15]

for i, (title, lines) in enumerate(layers):
    cy = y_list[i]
    bh = box_heights[i]
    draw_box(cy, title, lines, box_h=bh)

    ax.text(0.30, cy, left_labels[i],
            fontsize=10, fontweight='bold', ha='left', va='center', color=GRAY)

    if i < len(layers) - 1:
        v_arrow(cy, y_list[i + 1], h_top=bh, h_bot=box_heights[i + 1])

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/system_architecture.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/system_architecture.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → system_architecture.png')
