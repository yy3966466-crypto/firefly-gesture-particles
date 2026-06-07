import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 13

# ---------------------------------------------------------------------------
# figure setup — white background
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 8.0))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 11)
ax.set_ylim(0, 8.5)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours — 白底黑字
# ---------------------------------------------------------------------------
TEXT_CLR  = '#000000'
SUB_CLR   = '#222222'
ARR_CLR   = '#000000'
BOX_FILL  = '#FFFFFF'
BOX_EDGE  = '#333333'

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
OFF = 0.12       # gap between arrow tip and box border
CX  = 5.5        # global centre x

def draw_box(cx, cy, w, h, title='', sub='', t_size=13, s_size=13):
    """White rounded rectangle with centred two-line black text."""
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.2,
        boxstyle="round,pad=0.10",
    )
    ax.add_patch(rect)
    if title:
        ax.text(cx, cy + 0.10, title, fontsize=t_size, fontweight='bold',
                ha='center', va='bottom', color=TEXT_CLR)
    if sub:
        ax.text(cx, cy - 0.10, sub, fontsize=s_size, fontweight='bold',
                ha='center', va='top', color=SUB_CLR)

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Top — MATLAB Timer (centred)
# ---------------------------------------------------------------------------
timer_cy = 7.30
timer_h = 0.80
draw_box(CX, timer_cy, 3.2, timer_h,
         'MATLAB Timer', '定时调度核心', t_size=13, s_size=13)

# ---------------------------------------------------------------------------
# Middle row — three parallel modules
# ---------------------------------------------------------------------------
mod_cy = 5.00
mod_h = 0.80
mod_w = 2.6
mod_cxs = [2.2, 5.5, 8.8]
mod_titles = ['波形刷新', '数值更新', '算法分析']
mod_subs = ['GUI 绘图引擎', '数据显示刷新', '心电算法处理']

for i in range(3):
    draw_box(mod_cxs[i], mod_cy, mod_w, mod_h, mod_titles[i], mod_subs[i])

# ---------------------------------------------------------------------------
# Arrows — Timer fans out to the three modules
# gap OFF on both ends, arrows stay clear of box borders
# ---------------------------------------------------------------------------
timer_bot = timer_cy - timer_h / 2
mod_top   = mod_cy + mod_h / 2

for x in mod_cxs:
    ax.annotate('', xy=(x, mod_top + OFF), xytext=(CX, timer_bot - OFF),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=1.2))

# ---------------------------------------------------------------------------
# Descriptions below each module
# ---------------------------------------------------------------------------
descs = [
    ['实时波形显示刷新', '绘图引擎调用'],
    ['心率 / 体温数值更新', '数据显示面板刷新'],
    ['QRS 检测与定位', 'HRV 时域 / 频域分析'],
]

for i, lines in enumerate(descs):
    for j, line in enumerate(lines):
        yy = mod_cy - mod_h / 2 - 0.22 - j * 0.24
        ax.text(mod_cxs[i], yy, line, fontsize=13, fontweight='bold',
                ha='center', va='top', color=SUB_CLR)

# ---------------------------------------------------------------------------
# Bottom — summary box "三层刷新"
# ---------------------------------------------------------------------------
BOX_CX = CX
BOX_CY = 3.00
BOX_W  = 9.0
BOX_H  = 1.20

rect_b = mpatches.FancyBboxPatch(
    (BOX_CX - BOX_W / 2, BOX_CY - BOX_H / 2), BOX_W, BOX_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.0,
    boxstyle="round,pad=0.10",
)
ax.add_patch(rect_b)

ax.text(BOX_CX, BOX_CY + BOX_H / 2 - 0.10, '三层刷新',
        fontsize=13, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

ax.text(BOX_CX, BOX_CY + 0.08,
        '波形刷新 (0.5 s)  |  数值更新 (1 s)  |  算法分析 (2 s)',
        fontsize=13, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

ax.text(BOX_CX, BOX_CY - 0.28,
        'BusyMode = drop',
        fontsize=13, fontweight='bold', ha='center', va='top', color=SUB_CLR)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/09_event_loop.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/flowchart_images_v4/09_timer_event_loop.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/event_loop.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/event_loop.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → event_loop.png')
