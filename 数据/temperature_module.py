import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 16

# ---------------------------------------------------------------------------
# figure setup — compact layout
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7.0))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 12)
ax.set_ylim(0, 7.2)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------
TEXT_CLR  = '#000000'
SUB_CLR   = '#222222'
ARR_CLR   = '#000000'
BOX_FILL  = '#FFFFFF'
BOX_EDGE  = '#333333'
LOOP_CLR  = '#000000'

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
OFF = 0.12

def draw_box(cx, cy, w, h, title='', sub='', t_size=16, s_size=16):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
        boxstyle="round,pad=0.10",
    )
    ax.add_patch(rect)
    if title:
        ax.text(cx, cy + 0.10, title, fontsize=t_size,
                ha='center', va='bottom', color=TEXT_CLR, fontweight='bold')
    if sub:
        ax.text(cx, cy - 0.10, sub, fontsize=s_size,
                ha='center', va='top', color=SUB_CLR, fontweight='bold')

def v_arrow(cx, y_top, y_bot):
    ax.annotate('', xy=(cx, y_bot), xytext=(cx, y_top),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=2.0))

# ---------------------------------------------------------------------------
# top row — dual parallel input modules
# ---------------------------------------------------------------------------
IN_W, IN_H = 2.6, 0.80
demo_cx, serial_cx = 3.5, 8.5
in_y = 6.60

draw_box(demo_cx, in_y, IN_W, IN_H,
         'Demo 模式 (默认)', '模拟体温数据生成')
draw_box(serial_cx, in_y, IN_W, IN_H,
         'Serial 串口模式', '传感器读取')

# ---------------------------------------------------------------------------
# middle — TemperatureStream core
# ---------------------------------------------------------------------------
CORE_W = 7.0
CORE_H = 0.90
core_cy = 4.80

draw_box(6.0, core_cy, CORE_W, CORE_H,
         'TemperatureStream 核心', '数据调度与格式统一')

v_arrow(demo_cx,   in_y - IN_H/2 - OFF, core_cy + CORE_H/2 + OFF)
v_arrow(serial_cx, in_y - IN_H/2 - OFF, core_cy + CORE_H/2 + OFF)

ax.text(demo_cx + 0.35, (in_y - IN_H/2 + core_cy + CORE_H/2) / 2,
        'Demo 数据流', fontsize=16, ha='left', va='center',
        color=LOOP_CLR, fontweight='bold')
ax.text(serial_cx - 0.35, (in_y - IN_H/2 + core_cy + CORE_H/2) / 2,
        'Serial 数据流', fontsize=16, ha='right', va='center',
        color=LOOP_CLR, fontweight='bold')

# ---------------------------------------------------------------------------
# output module
# ---------------------------------------------------------------------------
OUT_W, OUT_H = 3.2, 0.75
out_cy = 3.45

draw_box(6.0, out_cy, OUT_W, OUT_H,
         '输出', '温度 / 湿度数据')

v_arrow(6.0, core_cy - CORE_H/2 - OFF, out_cy + OUT_H/2 + OFF)

# ---------------------------------------------------------------------------
# bottom — Demo formulas box (moved up)
# ---------------------------------------------------------------------------
F_L = 1.0
F_R = 11.0
F_W = F_R - F_L
F_B = 0.80
F_H = 1.80
F_CX = (F_L + F_R) / 2

rect_f = mpatches.FancyBboxPatch(
    (F_L, F_B), F_W, F_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
    boxstyle="round,pad=0.10",
)
ax.add_patch(rect_f)
ax.text(F_CX, F_B + F_H - 0.08, 'Demo 模式公式',
        fontsize=16, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

formulas = [
    r'$\mathit{value} = 0.08 * \sin(2\pi * \mathit{t} / 90) + 0.04 * \mathrm{randn} + 37.0$',
    r'$\mathit{base}   = 0.08 * \sin(2\pi * \mathit{t} / 90) + 37.0$',
    r'$\mathit{pin}    = \mathit{base} + 0.02 * \mathrm{randn}$',
]

formula_notes = ['模拟体温值', '基准体温', '引脚采样值']

for j, (f, note) in enumerate(zip(formulas, formula_notes)):
    fy = F_B + F_H - 0.45 - j * 0.36
    ax.text(F_L + 0.50, fy, f, fontsize=16, ha='left', va='top',
            color=TEXT_CLR, fontweight='bold')
    ax.text(F_R - 0.50, fy, note, fontsize=16,
            ha='right', va='top', color=SUB_CLR, fontweight='bold')

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/temperature_module.png',
            dpi=2400, bbox_inches='tight')
plt.savefig('d:/bishe/数据/temperature_module.png',
            dpi=2400, bbox_inches='tight')
plt.close()
print('OK → temperature_module.png')
