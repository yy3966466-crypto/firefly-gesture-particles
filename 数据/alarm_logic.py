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
fig, ax = plt.subplots(figsize=(9.0, 8.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 9.5)
ax.set_ylim(0, 9.0)
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
CX  = 4.75
OFF = 0.14
LW  = 1.2    # unified linewidth for boxes and arrows

def draw_box(cx, cy, w, h, title='', sub='', t_size=13, s_size=13):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=LW,
        boxstyle="round,pad=0.10",
    )
    ax.add_patch(rect)
    if title:
        ax.text(cx, cy + 0.10, title, fontsize=t_size, fontweight='bold',
                ha='center', va='bottom', color=TEXT_CLR)
    if sub:
        ax.text(cx, cy - 0.10, sub, fontsize=s_size, fontweight='bold',
                ha='center', va='top', color=SUB_CLR)

def v_arr(x, y_from, y_to):
    ax.annotate('', xy=(x, y_to), xytext=(x, y_from),
                arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=LW))

# ---------------------------------------------------------------------------
# Layer 1 — Timer 触发
# ---------------------------------------------------------------------------
t_cy, t_h, t_w = 8.20, 0.75, 6.0
draw_box(CX, t_cy, t_w, t_h,
         'Timer 触发', '定时判断周期', t_size=13, s_size=13)

# ---------------------------------------------------------------------------
# Layer 2 — 基础参数
# ---------------------------------------------------------------------------
p_cy, p_h, p_w = 6.70, 0.75, 2.2
p_cxs = [2.2, 4.75, 7.3]
p_titles = [r'$HR$（心率数据）', r'$RR$（呼吸数据）', r'$\mathit{Temp}$（体温数据）']
p_subs   = ['心率监测', '呼吸监测', '体温监测']

for i in range(3):
    draw_box(p_cxs[i], p_cy, p_w, p_h, p_titles[i], p_subs[i])

# ---------------------------------------------------------------------------
# Layer 3 — 节律 / 趋势判断
# ---------------------------------------------------------------------------
r_cy, r_h, r_w = 5.20, 0.75, 2.3
r_cxs = [2.2, 4.75, 7.3]

for i in range(3):
    draw_box(r_cxs[i], r_cy, r_w, r_h,
             ['ECG 节律异常', 'CV 趋势分析', '体温趋势'][i],
             ['心电节律检测', '变异系数计算', '温度变化检测'][i])

# ---------------------------------------------------------------------------
# Layer 4 — 结果输出
# ---------------------------------------------------------------------------
o_cy, o_h, o_w = 3.70, 0.80, 6.0
draw_box(CX, o_cy, o_w, o_h,
         '结果输出', '正常  |  警告  |  报警', t_size=13, s_size=13)

# ---------------------------------------------------------------------------
# vertical arrows
# ---------------------------------------------------------------------------
# Timer → Parameters
for x in p_cxs:
    v_arr(x, t_cy - t_h / 2 - OFF, p_cy + p_h / 2 + OFF)

# Parameters → Judgment
for x in r_cxs:
    v_arr(x, p_cy - p_h / 2 - OFF, r_cy + r_h / 2 + OFF)

# Judgment → Result
for x in r_cxs:
    v_arr(x, r_cy - r_h / 2 - OFF, o_cy + o_h / 2 + OFF)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/14_alarm_logic.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/flowchart_images_v4/07_alarm_system.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/alarm_logic.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/alarm_logic.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → alarm_logic.png')
