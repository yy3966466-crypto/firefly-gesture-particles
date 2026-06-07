import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 16

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 11.0))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 11)
ax.set_ylim(0, 11.0)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours — 白底黑字
# ---------------------------------------------------------------------------
DARK     = '#000000'
GRAY     = '#222222'
ARR_CLR  = '#000000'
BOX_FILL = '#FFFFFF'
BOX_EDGE = '#333333'
DASH_CLR = '#333333'
LOOP_CLR = '#000000'

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# geometry constants
# ---------------------------------------------------------------------------
OFF = 0.12       # gap between arrow tip and box border

def draw_box(cx, cy, w, h, title='', sub='', t_size=16, s_size=16):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
        boxstyle="round,pad=0.10",
    )
    ax.add_patch(rect)
    if title:
        ax.text(cx, cy + 0.10, title, fontsize=t_size,
                ha='center', va='bottom', color=DARK, fontweight='bold')
    if sub:
        ax.text(cx, cy - 0.10, sub, fontsize=s_size,
                ha='center', va='top', color=GRAY, fontweight='bold')

def v_arrow(cx, y_top, y_bot):
    """Vertical arrow from y_top down to y_bot (top > bot), both outside boxes."""
    ax.annotate('', xy=(cx, y_bot), xytext=(cx, y_top),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=2.0))

# ---------------------------------------------------------------------------
# 1. top row — input signal boxes
# ---------------------------------------------------------------------------
IN_W, IN_H = 2.5, 0.92
x_cx, d_cx = 3.0, 8.0
in_y = 8.60

draw_box(x_cx, in_y, IN_W, IN_H, 'x(n)', '输入信号')
draw_box(d_cx, in_y, IN_W, IN_H, 'd(n)', '期望信号')

# ---------------------------------------------------------------------------
# 2. dashed container
# ---------------------------------------------------------------------------
DB_L = 0.8
DB_R = 10.2
DB_B = 1.80
DB_T = 7.60
DB_CX = (DB_L + DB_R) / 2   # 5.5

dash_rect = mpatches.FancyBboxPatch(
    (DB_L, DB_B), DB_R - DB_L, DB_T - DB_B,
    facecolor='none', edgecolor=DASH_CLR, linewidth=1.5,
    linestyle='--', boxstyle="round,pad=0.12",
)
ax.add_patch(dash_rect)
ax.text(DB_CX, DB_T - 0.10, '自适应滤波核心 (每步迭代)',
        fontsize=16, fontweight='bold', ha='center', va='top', color=DARK)

# ---------------------------------------------------------------------------
# 3. three core modules  (centred at DB_CX, vertically stacked)
# ---------------------------------------------------------------------------
BW = 7.0
BH = 0.80
STEP = 1.50

y1 = DB_T - 0.85                # filter output
y2 = y1 - STEP                  # error
y3 = y2 - STEP                  # weight update

titles = [
    r'$y(n) = \mathbf{w}(n)^{\mathrm{T}} \cdot \mathbf{x}(n)$',
    r'$e(n) = d(n) - y(n)$',
    r'$\mathbf{w}(n+1) = \mathbf{w}(n) + 2\mu \cdot e(n) \cdot \mathbf{x}(n)$',
]
subs = ['滤波输出', '误差计算', '权值更新']

for i in range(3):
    yc = [y1, y2, y3][i]
    draw_box(DB_CX, yc, BW, BH, titles[i], subs[i])

# -- vertical arrows between the three core modules --
v_arrow(DB_CX, y1 - BH/2 - OFF, y2 + BH/2 + OFF)
v_arrow(DB_CX, y2 - BH/2 - OFF, y3 + BH/2 + OFF)

# ---------------------------------------------------------------------------
# 4. input arrows — x(n) → module 1, d(n) → module 1
# ---------------------------------------------------------------------------
v_arrow(x_cx, in_y - IN_H/2 - OFF, y1 + BH/2 + OFF)
ax.text(x_cx, (in_y - IN_H/2 + y1 + BH/2) / 2, 'x(n)',
        fontsize=16, fontweight='bold', ha='center', va='center', color=ARR_CLR, style='italic',
        bbox=dict(boxstyle='round,pad=0.06', facecolor='white', edgecolor='none'))

v_arrow(d_cx, in_y - IN_H/2 - OFF, y1 + BH/2 + OFF)
ax.text(d_cx, (in_y - IN_H/2 + y1 + BH/2) / 2, 'd(n)',
        fontsize=16, fontweight='bold', ha='center', va='center', color=ARR_CLR, style='italic',
        bbox=dict(boxstyle='round,pad=0.06', facecolor='white', edgecolor='none'))

# ---------------------------------------------------------------------------
# 5. feedback loop
#    path: module 3 bottom → down → left → up → right → module 1 left side
# ---------------------------------------------------------------------------
fb_x = DB_CX                                   # 5.5
fb_y_start = y3 - BH/2 - OFF                   # below module 3
fb_y_bot   = DB_B + 0.30                       # near dashed-box bottom

# vertical segment down (no arrowhead; arrowhead at final approach)
ax.plot([fb_x, fb_x], [fb_y_start, fb_y_bot],
        color=LOOP_CLR, linewidth=1.5)

# label on the vertical segment
ax.text(fb_x + 0.35, (fb_y_start + fb_y_bot) / 2, 'w(n+1) 反馈',
        fontsize=16, fontweight='bold', ha='left', va='center', color=LOOP_CLR, style='italic')

# horizontal segment to the left
turn_x = DB_L + 0.30
ax.plot([fb_x, turn_x], [fb_y_bot, fb_y_bot],
        color=LOOP_CLR, linewidth=1.5)

# vertical segment up (to centre of module 1's left edge)
up_y = y1
ax.plot([turn_x, turn_x], [fb_y_bot, up_y],
        color=LOOP_CLR, linewidth=1.5)

# horizontal segment right with arrowhead → pointing toward left side of module 1
module1_left = DB_CX - BW / 2
ax.annotate('', xy=(module1_left - OFF, up_y), xytext=(turn_x, up_y),
            arrowprops=dict(arrowstyle='->', color=LOOP_CLR, lw=1.8))

# "迭代循环" label on the left vertical segment
ax.text(turn_x - 0.15, (fb_y_bot + up_y) / 2, '迭\n代\n循\n环',
        fontsize=16, fontweight='bold', ha='right', va='center', color=DASH_CLR)

# ---------------------------------------------------------------------------
# 6. bottom — LMS three-line core formulas box
# ---------------------------------------------------------------------------
F_L = 1.0
F_R = 10.0
F_B = 0.20
F_H = 1.30
F_CX = (F_L + F_R) / 2

rect_f = mpatches.FancyBboxPatch(
    (F_L, F_B), F_R - F_L, F_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
    boxstyle="round,pad=0.10",
)
ax.add_patch(rect_f)
ax.text(F_CX, F_B + F_H - 0.08, 'LMS 三行核心公式',
        fontsize=16, fontweight='bold', ha='center', va='top', color=DARK)

formulas = [
    (r'$y(n) = \mathbf{w}(n)^{\mathrm{T}} \cdot \mathbf{x}(n)$',
     '滤波输出'),
    (r'$e(n) = d(n) - y(n)$',
     '误差信号'),
    (r'$\mathbf{w}(n+1) = \mathbf{w}(n) + 2\mu \cdot e(n) \cdot \mathbf{x}(n)$',
     '权值更新'),
]

for j, (f, note) in enumerate(formulas):
    fy = F_B + F_H - 0.40 - j * 0.28
    ax.text(F_L + 0.50, fy, f, fontsize=16, fontweight='bold', ha='left', va='top', color=DARK)
    ax.text(F_R - 0.50, fy, note, fontsize=16, fontweight='bold',
            ha='right', va='top', color=GRAY)


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/03_lms_filter.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/lms_filter.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/lms_filter.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → lms_filter.png')
