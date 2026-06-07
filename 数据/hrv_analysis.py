import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.8))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.8)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------
RED      = '#E74C3C'
DARK     = '#222222'
WAVE_CLR = '#444444'
ARR_CLR  = '#666666'
BOX_FILL = '#F5F5F5'
BOX_EDGE = '#BBBBBB'

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
ax.text(5, 5.55, 'RR间期与HRV分析',
        fontsize=18, fontweight='bold', ha='center', va='top', color=DARK)

# ---------------------------------------------------------------------------
# generate synthetic ECG signal
# ---------------------------------------------------------------------------
t = np.linspace(0, 10, 4000)
ecg = np.zeros_like(t)

r_peaks = np.array([0.6, 1.5, 2.4, 3.3, 4.2, 5.15, 6.1, 7.05, 8.0, 8.9])

for r in r_peaks:
    # R wave
    ecg += 1.0   * np.exp(-((t - r) / 0.018)**2)
    # Q wave
    ecg += -0.08 * np.exp(-((t - r + 0.04) / 0.015)**2)
    # S wave
    ecg += -0.05 * np.exp(-((t - r - 0.04) / 0.020)**2)
    # P wave
    ecg += 0.08  * np.exp(-((t - r + 0.22) / 0.040)**2)
    # T wave
    ecg += 0.12  * np.exp(-((t - r + 0.35) / 0.060)**2)

# scale into drawing y-range
WAVE_BOT = 3.0
WAVE_TOP = 5.1
ecg_scaled = WAVE_BOT + (ecg - ecg.min()) / (ecg.max() - ecg.min()) * (WAVE_TOP - WAVE_BOT)

ax.plot(t, ecg_scaled, color=WAVE_CLR, linewidth=1.2, zorder=2)

# ---------------------------------------------------------------------------
# R-peak red dots (exact positions)
# ---------------------------------------------------------------------------
r_idx = [np.searchsorted(t, r) for r in r_peaks]
r_y   = ecg_scaled[r_idx]
ax.scatter(r_peaks, r_y, color=RED, s=40, zorder=5, edgecolors='none')

# ---------------------------------------------------------------------------
# RR-interval horizontal arrows below waveform
# ---------------------------------------------------------------------------
ARR_Y    = 2.60          # arrow vertical position
OFF_R    = 0.14          # gap from red dot centre to arrow tip
LBL_OFF  = 0.20          # label vertical offset above arrow

# label a representative subset so it's not too crowded
label_idx = {0, 1, 2, 5, 7}

for i in range(len(r_peaks) - 1):
    x1 = r_peaks[i]   + OFF_R
    x2 = r_peaks[i+1] - OFF_R

    # bidirectional horizontal arrow
    ax.annotate(
        '', xy=(x2, ARR_Y), xytext=(x1, ARR_Y),
        arrowprops=dict(arrowstyle='<->', color=ARR_CLR, lw=1.3),
    )

    # RR-value label (only a few to avoid clutter)
    if i in label_idx:
        rr_val = r_peaks[i+1] - r_peaks[i]
        ax.text((x1 + x2) / 2, ARR_Y + LBL_OFF, f'{rr_val:.2f}s',
                fontsize=8.5, ha='center', va='bottom', color=DARK)

# small "RR间期" indicator below the arrow line
ax.text(5, ARR_Y - 0.22, 'RR 间期',
        fontsize=8, ha='center', va='top', color='#888888', style='italic')

# ---------------------------------------------------------------------------
# vertical dashed lines from each R peak down toward the arrow
# start below the red dot, end before the arrow
# ---------------------------------------------------------------------------
dot_r = 0.055   # approximate red-dot radius in data coords
for i, r in enumerate(r_peaks):
    top_y = r_y[i] - dot_r - 0.03     # start below red dot
    bot_y = ARR_Y + 0.05              # end above arrow
    ax.plot([r, r], [top_y, bot_y],
            color='#CCCCCC', linewidth=0.5, linestyle=':', zorder=1)

# ---------------------------------------------------------------------------
# bottom: HRV key metrics text box
# ---------------------------------------------------------------------------
BOX_L = 1.0
BOX_R = 9.0
BOX_B = 0.08
BOX_H = 1.57
BOX_CX = (BOX_L + BOX_R) / 2
BOX_CY = BOX_B + BOX_H / 2

rect = mpatches.FancyBboxPatch(
    (BOX_L, BOX_B), BOX_R - BOX_L, BOX_H,
    facecolor=BOX_FILL, edgecolor=BOX_EDGE, linewidth=1.0,
    boxstyle="round,pad=0.08",
)
ax.add_patch(rect)

# box title
ax.text(BOX_CX, BOX_B + BOX_H - 0.12, 'HRV 关键指标',
        fontsize=11, fontweight='bold', ha='center', va='top', color=DARK)

# metrics table (aligned left with fixed-width columns)
metrics = [
    ('SDNN',   'NN 间期的标准差',                     '衡量整体心率变异性'),
    ('RMSSD',  '相邻 NN 间期差值的均方根',             '衡量短期心率变异性'),
    ('LF/HF',  '低频功率 / 高频功率比值',              '衡量交感/副交感平衡'),
]

col1_x = BOX_L + 0.40
col2_x = BOX_L + 2.60
col3_x = BOX_L + 5.80
y0     = BOX_B + BOX_H - 0.52

ax.text(col1_x, y0, '指标',   fontsize=8.5, fontweight='bold', ha='left', va='top', color=DARK)
ax.text(col2_x, y0, '定义',   fontsize=8.5, fontweight='bold', ha='left', va='top', color=DARK)
ax.text(col3_x, y0, '生理意义', fontsize=8.5, fontweight='bold', ha='left', va='top', color=DARK)

for j, (name, defn, meaning) in enumerate(metrics):
    yy = y0 - 0.32 - j * 0.30
    ax.text(col1_x, yy, name,   fontsize=8.5, ha='left', va='top', color=DARK)
    ax.text(col2_x, yy, defn,   fontsize=8.5, ha='left', va='top', color=DARK)
    ax.text(col3_x, yy, meaning, fontsize=8.5, ha='left', va='top', color=DARK)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/10_hrv_analysis.png',
            dpi=200, bbox_inches='tight')
plt.savefig('d:/bishe/hrv_analysis.png',
            dpi=200, bbox_inches='tight')
plt.close()
print('OK → hrv_analysis.png')
