import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12

# ---------------------------------------------------------------------------
# figure setup — white background
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.2))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(0, 7.0)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours — 白底黑字
# ---------------------------------------------------------------------------
BOX_FILL   = '#FFFFFF'
BOX_EDGE   = '#333333'
TEXT_CLR   = '#000000'
SUB_CLR    = '#222222'
GUIDE_CLR  = '#AAAAAA'
GAP        = 0.12          # gap between lines and box borders

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# top row: two database boxes — white fill, black border
# ---------------------------------------------------------------------------
BOX_W_L = 4.5
BOX_W_R = 4.5
BOX_H   = 2.3
BOX_YB  = 4.0             # box bottom y
BOX_YT  = BOX_YB + BOX_H  # box top y

cxL, cxR = 2.5, 7.5
leftL = cxL - BOX_W_L / 2   # 0.5
leftR = cxR - BOX_W_R / 2   # 5.0

# ---- left box: MIT-BIH 心律失常数据库 ----
rect_l = mpatches.FancyBboxPatch(
    (leftL, BOX_YB), BOX_W_L, BOX_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.2,
    boxstyle="round,pad=0.12",
)
ax.add_patch(rect_l)

ax.text(cxL, BOX_YT - 0.25, 'MIT-BIH 心律失常数据库',
        fontsize=12, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

left_lines = [
    '来源：MIT-BIH Arrhythmia Database',
    '48 条心电记录，每条约 30 分钟',
    '2 导联 ECG 信号，采样率 360 Hz',
    '11 位 ADC 分辨率，范围 ±5 mV',
    '包含 100+ 万心搏标注',
    '广泛应用于心律失常检测研究',
]
for j, line in enumerate(left_lines):
    ax.text(cxL, BOX_YT - 0.55 - j * 0.30, line,
            fontsize=12, fontweight='bold', ha='center', va='top', color=SUB_CLR)

# ---- right box: BIDMC PPG 与呼吸数据库 ----
rect_r = mpatches.FancyBboxPatch(
    (leftR, BOX_YB), BOX_W_R, BOX_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.2,
    boxstyle="round,pad=0.12",
)
ax.add_patch(rect_r)

ax.text(cxR, BOX_YT - 0.25, 'BIDMC PPG 与呼吸数据库',
        fontsize=12, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

right_lines = [
    '来源：BIDMC PPG and Respiration Database',
    '53 例 ICU 患者记录',
    '同步 PPG、呼吸、ECG 三通道信号',
    '采样率 125 Hz',
    '包含逐拍心搏标注',
    '用于心肺功能监测研究',
]
for j, line in enumerate(right_lines):
    ax.text(cxR, BOX_YT - 0.55 - j * 0.30, line,
            fontsize=12, fontweight='bold', ha='center', va='top', color=SUB_CLR)

# ---------------------------------------------------------------------------
# bottom box: 随机抽样策略 — white fill, black border
# ---------------------------------------------------------------------------
ADV_L  = leftL                          # 0.5
ADV_R  = leftR + BOX_W_R                # 10.0
ADV_W  = ADV_R - ADV_L                  # 9.5
ADV_B  = 2.0
ADV_H  = 1.55
ADV_T  = ADV_B + ADV_H                  # 3.55
ADV_CY = ADV_B + ADV_H / 2              # box vertical center

rect_b = mpatches.FancyBboxPatch(
    (ADV_L, ADV_B), ADV_W, ADV_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.2,
    boxstyle="round,pad=0.12",
)
ax.add_patch(rect_b)

ax.text(5.0, ADV_CY + 0.56, '随机抽样策略',
        fontsize=12, fontweight='bold', ha='center', va='center', color=TEXT_CLR)

bottom_lines = [
    '从 MIT-BIH 与 BIDMC 两个数据库中按比例随机抽取样本',
    '保证训练集 / 验证集 / 测试集分布均衡',
    '按患者 ID 划分，避免同一患者数据出现在不同集合中',
    '默认划分比例：训练集 70% ｜ 验证集 15% ｜ 测试集 15%',
]
for j, line in enumerate(bottom_lines):
    ax.text(5.0, ADV_CY + 0.28 - j * 0.28, line,
            fontsize=12, fontweight='bold', ha='center', va='center', color=SUB_CLR)

# ---------------------------------------------------------------------------
# vertical guide lines — start below top boxes, end above bottom box
# both ends have GAP to avoid crossing box borders
# ---------------------------------------------------------------------------
guide_top = BOX_YB - GAP          # 4.0 - 0.12 = 3.88
guide_bot = ADV_T + GAP            # 2.9 + 0.12 = 3.02

for cx in [cxL, cxR]:
    ax.plot([cx, cx], [guide_top, guide_bot],
            color=GUIDE_CLR, linewidth=0.6, linestyle=':', zorder=0)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/12_datasets_and_sampling.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/datasets_sampling.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/datasets_sampling.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → datasets_sampling.png')
