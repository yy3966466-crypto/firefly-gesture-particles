import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 16

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(16, 6.5))
fig.patch.set_facecolor('white')

ax.set_xlim(-1.2, 61)
ax.set_ylim(0, 7.5)
ax.set_xlabel('频率 (Hz)', fontsize=16, fontweight='bold', labelpad=8)

# major ticks (labelled)
ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
ax.set_xticklabels(['0', '10', '20', '30', '40', '50', '60'],
                    fontsize=16, fontweight='bold')
# minor ticks at band boundaries (unlabelled)
ax.set_xticks([0.7, 5, 18], minor=True)
ax.tick_params(axis='x', which='minor', length=6, width=1.2, color='#555555')

ax.tick_params(axis='y', left=False, labelleft=False)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_position(('data', 0))

# ---------------------------------------------------------------------------
# coloured frequency bands
# ---------------------------------------------------------------------------
band_cen_y = 1.5
band_h    = 1.0          # band spans [1.0, 2.0]

bands = [
    (0,    0.7, '#1A5FCC'),   # blue   – baseline drift
    (0.7,  5,   '#1D9E4A'),   # green  – P/T wave
    (5,   18,   '#C0392B'),   # red    – QRS
    (18,  60,   '#D68910'),   # orange – EMG / noise
]

for start, end, color in bands:
    rect = mpatches.FancyBboxPatch(
        (start, band_cen_y - band_h / 2),
        end - start, band_h,
        facecolor=color, edgecolor='gray', linewidth=0.8,
        alpha=0.85, boxstyle="round,pad=0.02",
    )
    ax.add_patch(rect)

# ---------------------------------------------------------------------------
# band annotation text boxes  (staggered y-levels, straight vertical arrows)
# ---------------------------------------------------------------------------
annotations = [
    (0, 0.7,   '#1A5FCC', '来源：呼吸\n影响：使心电信号产生基线漂移'),
    (0.7, 5,   '#1D9E4A', '来源：心房除极、心室复极\n频带：0.7~5Hz 低频成分'),
    (5,   18,  '#C0392B', '来源：心室除极\n频带：5~18Hz 中高频成分，R波能量最集中频段'),
    (18,  60,  '#D68910', '来源：肌肉收缩、外部电磁干扰\n频带：>18Hz 高频干扰成分'),
]

# staggered y positions so nearby text boxes don't overlap
txt_ys = [3.6, 5.8, 4.6, 5.2]   # blue low, green high, red mid, orange upper-mid
arr_top = 2.0                    # arrow tip = top of bands

band_centers = [(s + e) / 2 for (s, e, _, _) in annotations]

# blue text box vertical span (for green arrow split)
BLUE_BOT = txt_ys[0] - 0.12   # ~3.48
BLUE_TOP = txt_ys[0] + 0.60   # ~4.20

for i, ((start, end, color, text), cx, ty) in enumerate(zip(annotations, band_centers, txt_ys)):
    if i == 1:  # green arrow — split to avoid blue text box
        ax.plot([cx, cx], [ty - 0.15, BLUE_TOP + 0.08],
                color=color, lw=2.0)
        ax.annotate(
            '', xy=(cx, arr_top), xytext=(cx, BLUE_BOT - 0.08),
            arrowprops=dict(arrowstyle='->', color=color, lw=2.0),
        )
    else:
        ax.annotate(
            '', xy=(cx, arr_top), xytext=(cx, ty - 0.15),
            arrowprops=dict(arrowstyle='->', color=color, lw=2.0),
        )
    # text box — green uses original pad; blue shifted right, tighter pad
    if i == 0:
        pad_val = '0.15'
    elif i == 1:
        pad_val = '0.40'
    else:
        pad_val = '0.50'
    tx = cx + 1.8 if i == 0 else cx
    ax.text(
        tx, ty, text, fontsize=16, ha='center', va='bottom',
        fontweight='bold', color='#1a1a1a',
        bbox=dict(boxstyle=f'round,pad={pad_val}', facecolor='white',
                  edgecolor=color, linewidth=1.6, alpha=0.95),
    )

# ---------------------------------------------------------------------------
# 50 Hz power-line interference  (between bands & annotation boxes)
# ---------------------------------------------------------------------------
ax.annotate(
    '', xy=(50, 0.05), xytext=(50, 3.2),
    arrowprops=dict(arrowstyle='->', color='#C0392B', lw=2.5, ls='--'),
)
ax.text(
    50, 3.3, '50Hz工频干扰',
    fontsize=16, ha='center', va='bottom', color='black',
    fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
              edgecolor='black', linewidth=1.5, alpha=1.0),
)

# ---------------------------------------------------------------------------
# title & legend
# ---------------------------------------------------------------------------
legend_elements = [
    mpatches.Patch(facecolor='#1A5FCC', edgecolor='gray', alpha=0.85, label='基线漂移(<0.7Hz)'),
    mpatches.Patch(facecolor='#1D9E4A', edgecolor='gray', alpha=0.85, label='P波/T波(0.7~5Hz)'),
    mpatches.Patch(facecolor='#C0392B', edgecolor='gray', alpha=0.85, label='QRS波群(5~18Hz)'),
    mpatches.Patch(facecolor='#D68910', edgecolor='gray', alpha=0.85, label='肌电/高频噪声(>18Hz)'),
]
leg = ax.legend(
    handles=legend_elements, loc='upper right',
    fontsize=16, framealpha=0.95, edgecolor='#aaaaaa',
    title='频段说明', title_fontsize=16,
    bbox_to_anchor=(0.995, 1.01),
    prop=dict(weight='bold'),
)
leg.get_title().set_fontweight('bold')

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.tight_layout()
plt.savefig('d:/bishe/ecg_spectrum.png', dpi=2400, bbox_inches='tight')
plt.savefig('d:/bishe/数据/ecg_spectrum.png', dpi=2400, bbox_inches='tight')
plt.close()
print('OK → ecg_spectrum.png')
