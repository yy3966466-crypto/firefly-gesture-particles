#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
ECG频带成分分布示意图 v6
Fix aspect ratio, use fig.subplots_adjust for proper spacing
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 13
plt.rcParams['axes.unicode_minus'] = False

# Use a more square aspect ratio
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Use subplots_adjust to set margins manually (not tight_layout)
fig.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.12)

ax.set_xlim(-2, 58)
ax.set_ylim(-2.0, 6.5)

for s in ax.spines.values():
    s.set_visible(False)
ax.set_yticks([])
ax.set_yticklabels([])
ax.tick_params(axis='x', length=0)

# ============================================================
# Frequency axis
# ============================================================
ax.axhline(y=3.0, color='black', linewidth=3, zorder=8)
ax.set_xlabel('频率 (Hz)', fontsize=16, fontweight='bold', labelpad=8, color='#1a1a1a')

for f in range(0, 56, 5):
    ax.plot(f, 3.0, '|', color='black', markersize=14, mew=2.5, zorder=9)
    ax.text(f, 2.55, str(f), ha='center', va='top', fontsize=13, color='black', fontweight='bold')

for f in range(0, 56):
    if f % 5 != 0:
        ax.plot(f, 3.0, '|', color='#BBBBBB', markersize=7, mew=1, zorder=8)

# ============================================================
# Colored bands (below axis)
# ============================================================
band_top = 3.15
band_h = 2.0

bands = [
    (0,   0.7, '#1A6DB5', '#A9CCE3', '基线漂移', '呼吸运动、电极移动\n引起的低频波动', '<0.7Hz'),
    (0.7, 5,   '#1D9E4A', '#A9DFBF', 'P波 / T波', '心房除极与复极\n产生的电活动', '0.7~5Hz'),
    (5,   18,  '#C0392B', '#F0B8B5', 'QRS 波群 ★', '心室除极过程\nR波能量最集中频段', '5~18Hz'),
    (18,  45,  '#D68910', '#FAD7A1', '肌电 / 高频噪声', '肌肉收缩、外部电磁\n等干扰成分', '>18Hz'),
]

for start, end, color, light_c, label, desc, freq_s in bands:
    w = max(end - start, 0.5)

    # Background box
    bg = mpatches.FancyBboxPatch((start, band_top), w, band_h,
                                   boxstyle="round,pad=0.08",
                                   facecolor=light_c, edgecolor='none', zorder=2)
    ax.add_patch(bg)

    # Colored rectangle
    rect_h = band_h * 0.7
    rect = mpatches.FancyBboxPatch((start + 0.1, band_top + band_h - rect_h),
                                     w - 0.2, rect_h,
                                     boxstyle="round,pad=0.05",
                                     facecolor=color, edgecolor='#222222',
                                     linewidth=1.8, zorder=4)
    ax.add_patch(rect)

    # Label inside colored rect
    if w > 3:
        ax.text(start + w/2, band_top + band_h - rect_h/2, label,
                ha='center', va='center', fontsize=17, fontweight='bold',
                color='white')
        # Description below the colored bar
        ax.text(start + w/2, band_top + band_h * 0.25, desc,
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='#333333', linespacing=1.3)
    else:
        ax.text(start + w/2, band_top + band_h + 0.3, label,
                ha='center', va='bottom', fontsize=13, fontweight='bold',
                color=color)

    # Frequency label
    ax.text(start + w/2, band_top - 0.2, freq_s, ha='center', va='top',
            fontsize=13, color='#444444', fontweight='bold')

# ============================================================
# Band boundaries
# ============================================================
for freq in [0.7, 5, 18]:
    ax.plot([freq, freq], [3.0, band_top + band_h], color='#777777',
            linewidth=1.2, linestyle=':', zorder=3)
    ax.text(freq, band_top - 0.8, f'{freq}Hz', ha='center', fontsize=10,
            color='#666666', fontweight='bold')

# ============================================================
# 50 Hz marker
# ============================================================
ax.axvline(x=50, ymin=0.08, ymax=0.48, color='#C0392B', linewidth=3,
           linestyle='--', zorder=5)
ax.plot(50, 1.0, 'v', color='#C0392B', markersize=14, zorder=6)
ax.text(50, 1.5, '50 Hz 工频干扰', ha='center', fontsize=13,
        fontweight='bold', color='#C0392B',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FDEDEC',
                  edgecolor='#C0392B', linewidth=1.2))

# ============================================================
# Top annotations with arrows pointing to each band
# ============================================================
anno_y = 5.8
annotations = [
    (0.35, '基线漂移', '来源：呼吸运动、电极缓慢偏移\n影响：使心电信号偏离基线', '#1A6DB5'),
    (2.8,  'P波 / T波', '来源：心房除极、心室复极\n频带：0.7~5 Hz 低频成分', '#1D9E4A'),
    (11.5, '★ QRS 波群', '来源：心室除极过程\n频带：5~18 Hz 能量最集中', '#C0392B'),
    (29,   '肌电 / 高频噪声', '来源：肌肉收缩、外部电磁干扰\n频带：>18 Hz', '#D68910'),
]

for x, title, desc, c in annotations:
    # Arrow from annotation to band
    ax.annotate('', xy=(x, band_top + band_h + 0.2),
                xytext=(x, anno_y - 0.3),
                arrowprops=dict(arrowstyle='->', color=c, lw=3,
                                connectionstyle='arc3,rad=0'),
                zorder=5)

    # Title
    ax.text(x, anno_y + 0.1, title, ha='center', va='bottom',
            fontsize=14, fontweight='bold', color=c)

    # Description box - offset horizontally to avoid stacking
    if x < 1:
        dx = 5
        ha = 'left'
    elif x > 20:
        dx = -5
        ha = 'right'
    else:
        dx = 6
        ha = 'left'

    ax.text(x + dx, anno_y - 0.3, desc, ha=ha, va='center',
            fontsize=11, fontweight='bold', color='#333333', linespacing=1.4,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=c, linewidth=1.5, alpha=0.95))

    # Dotted line connecting arrow to description box
    ax.annotate('', xy=(x, anno_y - 0.4), xytext=(x + (dx * 0.7), anno_y - 0.4),
                arrowprops=dict(arrowstyle='-', color=c, lw=1,
                                linestyle='dotted'), zorder=2)

# ============================================================
# Zone labels at top
# ============================================================
zone_y = 6.3
zones = [
    (0, 0.7, '低频区', '#1A6DB5'),
    (0.7, 5, '中低频区', '#1D9E4A'),
    (5, 18, '中频区', '#C0392B'),
    (18, 45, '高频区', '#D68910'),
]
for start, end, name, c in zones:
    mid = (start + end) / 2
    ax.text(mid, zone_y, name, ha='center', va='center', fontsize=13,
            fontweight='bold', color=c,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                      edgecolor=c, linewidth=1.5))

# ============================================================
# Title and Legend
# ============================================================
ax.set_title('ECG 心电信号频带成分分布', fontsize=22, fontweight='bold',
             pad=8, color='#1a1a1a', loc='left')

legend_elements = [
    mpatches.Patch(facecolor='#1A6DB5', edgecolor='#222222', label='基线漂移 (<0.7Hz)'),
    mpatches.Patch(facecolor='#1D9E4A', edgecolor='#222222', label='P波/T波 (0.7~5Hz)'),
    mpatches.Patch(facecolor='#C0392B', edgecolor='#222222', label='QRS波群 (5~18Hz) ★'),
    mpatches.Patch(facecolor='#D68910', edgecolor='#222222', label='肌电/高频噪声 (>18Hz)'),
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=12,
                    framealpha=0.95, edgecolor='#BBBBBB', ncol=4,
                    columnspacing=1.5, handletextpad=0.5,
                    prop=dict(weight='bold'))
legend.get_frame().set_linewidth(1.2)

# Info
ax.text(0.97, -0.6, 'ECG采样率: 360 Hz  |  R波检测通带: 5~18 Hz  |  FFT零相位滤波',
        transform=ax.transAxes, fontsize=11, fontweight='bold', color='#777777',
        ha='right', va='center', style='italic')

# Save
for out in [
    'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png',
    'd:/bishe/ecg_frequency_bands.png',
    'd:/bishe/数据/ecg_frequency_bands.png',
]:
    plt.savefig(out, dpi=1200, facecolor='white', edgecolor='none', bbox_inches='tight')
    print(f'Saved: {out}')

plt.close()
