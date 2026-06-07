import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 13

# ---------------------------------------------------------------------------
# figure setup — compact layout
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5.8))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.set_xlim(0, 12)
ax.set_ylim(0, 6.2)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------
BOX_FILL   = '#FFFFFF'
BOX_EDGE   = '#333333'
TEXT_CLR   = '#000000'
SUB_CLR    = '#222222'
ARR_CLR    = '#000000'
GUIDE_CLR  = '#AAAAAA'
ADV_FILL   = '#FAFAFA'

# ---------------------------------------------------------------------------
# geometry constants
# ---------------------------------------------------------------------------
BOX_W = 2.8
BOX_H = 1.5
GAP   = 0.12

cx1, cx2, cx3 = 2.6, 6.0, 9.4

BOX_Y_BOTTOM = 3.9
BOX_Y_TOP    = BOX_Y_BOTTOM + BOX_H   # 5.4
BOX_Y_CENTER = BOX_Y_BOTTOM + BOX_H / 2

# ---------------------------------------------------------------------------
# three step boxes
# ---------------------------------------------------------------------------
step_titles = ['Step 1', 'Step 2', 'Step 3']
step_bodies = ['FFT 变换', '频域滤波', 'IFFT 变换']

for i, (cx, title, body) in enumerate(zip([cx1, cx2, cx3], step_titles, step_bodies)):
    left = cx - BOX_W / 2
    rect = mpatches.FancyBboxPatch(
        (left, BOX_Y_BOTTOM), BOX_W, BOX_H,
        facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
        boxstyle="round,pad=0.12",
    )
    ax.add_patch(rect)

    # box title — bold
    ax.text(cx, BOX_Y_TOP - 0.30, title,
            fontsize=14, fontweight='bold', ha='center', va='top', color=TEXT_CLR)
    # box body — bold
    ax.text(cx, BOX_Y_BOTTOM + 0.30, body,
            fontsize=14, fontweight='bold', ha='center', va='bottom', color=TEXT_CLR)

    # description text — bold
    desc_y = BOX_Y_BOTTOM - 0.45
    desc_texts = [
        '① 将信号从时域变换至频域',
        '② 乘以滤波器传输函数',
        '③ 将信号从频域变换回时域',
    ]
    ax.text(cx, desc_y, desc_texts[i],
            fontsize=13, fontweight='bold', ha='center', va='top', color=SUB_CLR)

# ---------------------------------------------------------------------------
# horizontal arrows between boxes
# ---------------------------------------------------------------------------
for x_from, x_to in [(cx1 + BOX_W / 2 + GAP, cx2 - BOX_W / 2 - GAP),
                      (cx2 + BOX_W / 2 + GAP, cx3 - BOX_W / 2 - GAP)]:
    ax.annotate(
        '', xy=(x_to, BOX_Y_CENTER), xytext=(x_from, BOX_Y_CENTER),
        arrowprops=dict(arrowstyle='->', color=ARR_CLR, lw=2.0),
    )

# ---------------------------------------------------------------------------
# advantage box — moved upward, no vertical guide lines
# ---------------------------------------------------------------------------
ADV_LEFT   = cx1 - BOX_W / 2
ADV_RIGHT  = cx3 + BOX_W / 2
ADV_W      = ADV_RIGHT - ADV_LEFT
ADV_BOTTOM = 1.3
ADV_H      = 1.2
ADV_TOP    = ADV_BOTTOM + ADV_H   # 2.5

rect_adv = mpatches.FancyBboxPatch(
    (ADV_LEFT, ADV_BOTTOM), ADV_W, ADV_H,
    facecolor=ADV_FILL, edgecolor=BOX_EDGE, linewidth=1.5,
    boxstyle="round,pad=0.12",
)
ax.add_patch(rect_adv)

ax.text(6.0, ADV_BOTTOM + ADV_H / 2,
        '优点：零相位偏移，无相位失真，不改变信号时域特征',
        fontsize=14, fontweight='bold', ha='center', va='center', color=TEXT_CLR)

# label above advantage box — bold
ax.text(6.0, ADV_TOP + GAP + 0.08, '▼ 算法特点',
        fontsize=14, fontweight='bold', ha='center', va='bottom', color=SUB_CLR)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/fft_zerophase_filter.png', dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/数据/fft_zerophase_filter.png', dpi=1200, bbox_inches='tight')
plt.savefig('d:/bishe/flowchart_images_v4/06_fft_filtering.png', dpi=1200, bbox_inches='tight')
plt.close()
print('OK → fft_zerophase_filter.png')
