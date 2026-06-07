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
fig, ax = plt.subplots(figsize=(9, 10))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 9)
ax.set_ylim(0, 10)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours — 白底黑字
# ---------------------------------------------------------------------------
BOX_FILL  = '#FFFFFF'
BOX_EDGE  = '#333333'
TEXT_CLR  = '#000000'
DESC_CLR  = '#222222'
ARR_CLR   = '#000000'

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
BOX_W = 2.8
BOX_H = 0.75

BOX_CX = 2.5               # box centre x
DESC_X = 4.8               # description left-aligned x

# 6 steps, evenly spaced vertically
N = 6
SPACING = 1.4
y_top   = 8.5
y_centers = [y_top - i * SPACING for i in range(N)]

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# step data
# ---------------------------------------------------------------------------
step_nums  = ['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5', 'Step 6']
step_names = ['原始信号采集', '预处理去噪', '基线漂移校正',
              'R 波检测定位', '特征提取计算', '结果输出与可视化']
descs = [
    'PhysioNet 数据库 / 传感器读取心电数据',
    '带通滤波去除噪声与高频干扰',
    '高通滤波器去除呼吸引起的基线漂移',
    '自适应阈值法检测 QRS 波群位置',
    '计算 RR 间期、HRV 时域 / 频域指标',
    '波形可视化、心拍分类、会话保存与导出',
]

# ---------------------------------------------------------------------------
# draw boxes + descriptions
# ---------------------------------------------------------------------------
OFF = 0.10   # gap between arrow tip and box border

for i in range(N):
    yc   = y_centers[i]
    by   = yc - BOX_H / 2
    left = BOX_CX - BOX_W / 2

    # ---- box (white fill, black border) ----
    rect = mpatches.FancyBboxPatch(
        (left, by), BOX_W, BOX_H,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.0,
        boxstyle="round,pad=0.08",
    )
    ax.add_patch(rect)

    # step number (bold)
    ax.text(BOX_CX, yc + 0.12, step_nums[i],
            fontsize=13, fontweight='bold', ha='center', va='bottom', color=TEXT_CLR)
    # step name
    ax.text(BOX_CX, yc - 0.12, step_names[i],
            fontsize=13, fontweight='bold', ha='center', va='top', color=TEXT_CLR)

    # ---- description (right side) ----
    ax.text(DESC_X, yc, descs[i],
            fontsize=13, fontweight='bold', ha='left', va='center', color=DESC_CLR)

    # ---- arrow to next step (gap OFF on both ends) ----
    if i < N - 1:
        y_next = y_centers[i + 1]
        y_from = yc - BOX_H / 2 - OFF
        y_to   = y_next + BOX_H / 2 + OFF

        ax.annotate(
            '', xy=(BOX_CX, y_to), xytext=(BOX_CX, y_from),
            arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=1.8),
        )

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/02_ecg_processing.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/ecg_processing_flow.png',
            dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/ecg_processing_flow.png',
            dpi=1200, bbox_inches='tight')
plt.close()
print('OK → ecg_processing_flow.png')
