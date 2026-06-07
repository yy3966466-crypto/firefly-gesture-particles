#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
ECG频带成分分布示意图 v5
Clean design: no text overlap, clear fonts, proper spacing
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 13
plt.rcParams['axes.unicode_minus'] = False

# Better aspect ratio: wider but taller to give room for annotations
fig, ax = plt.subplots(1, 1, figsize=(18, 7))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.set_xlim(-1, 56)
ax.set_ylim(-2.5, 5.5)

for s in ax.spines.values():
    s.set_visible(False)
ax.set_yticks([])
ax.set_yticklabels([])
ax.tick_params(axis='x', length=0)

# ============================================================
# Top section: Frequency zone indicators
# ============================================================
zone_y = 5.0
zones = [
    (0, 0.7,   '低频区', '#5DADE2', '基线漂移'),
    (0.7, 5,   '中低频区', '#58D68D', 'P波/T波'),
    (5,   18,  '中频区 ★', '#E74C3C', 'QRS波群'),
    (18,  40,  '高频区', '#F39C12', '肌电噪声'),
]

for start, end, zone_name, c, band_name in zones:
    mid = (start + end) / 2
    ax.annotate('', xy=(mid, zone_y - 0.3), xytext=(mid, 3.2),
                arrowprops=dict(arrowstyle='->', color=c, lw=2.5, connectionstyle='arc3,rad=0'),
                zorder=3)
    # Zone name tag
    ax.text(mid, zone_y, zone_name, ha='center', va='center', fontsize=12,
            fontweight='bold', color=c,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                      edgecolor=c, linewidth=1.5))

# ============================================================
# Main frequency axis at y=2.5
# ============================================================
axis_y = 2.5
ax.axhline(y=axis_y, xmin=0, xmax=1, color='black', linewidth=2.5, zorder=5)
ax.set_xlabel('频率 (Hz)', fontsize=15, fontweight='bold', labelpad=5, color='#1a1a1a')

for f in range(0, 56, 5):
    ax.plot(f, axis_y, '|', color='black', markersize=12, mew=2, zorder=6)
    ax.text(f, axis_y - 0.4, str(f), ha='center', va='top', fontsize=12, color='black')
for f in range(0, 56):
    if f % 5 != 0:
        ax.plot(f, axis_y, '|', color='#AAAAAA', markersize=6, mew=1, zorder=5)

# ============================================================
# Frequency bands (below the axis)
# ============================================================
y0 = axis_y + 0.15
h = 1.6

bands = [
    (0,   0.7, '#5DADE2', '#EBF5FB', '基线漂移', '呼吸/电极移动', '< 0.7 Hz'),
    (0.7, 5,   '#58D68D', '#EAF2E3', 'P波 / T波', '心房电活动', '0.7 ~ 5 Hz'),
    (5,   18,  '#E74C3C', '#FDEDEC', 'QRS 波群', '心室除极·R波核心', '5 ~ 18 Hz'),
    (18,  40,  '#F39C12', '#FEF5E7', '肌电/高频噪声', '肌肉收缩干扰', '18 ~ 40 Hz'),
]

for start, end, color, light_c, label, desc, freq_s in bands:
    w = max(end - start, 0.3)

    # Light background box
    bg = mpatches.FancyBboxPatch((start, y0), w, h,
                                   boxstyle="round,pad=0.08",
                                   facecolor=light_c, edgecolor='#DDDDDD',
                                   linewidth=0.5, zorder=1)
    ax.add_patch(bg)

    # Colored top bar
    bar_h = h * 0.65
    rect = mpatches.FancyBboxPatch((start + 0.08, y0 + h - bar_h), w - 0.16, bar_h,
                                     boxstyle="round,pad=0.04",
                                     facecolor=color, edgecolor='#333333',
                                     linewidth=1.5, zorder=3)
    ax.add_patch(rect)

    # Label INSIDE bar
    txt_color = 'white'
    if w >= 4:
        ax.text(start + w/2, y0 + h - bar_h/2, label,
                ha='center', va='center', fontsize=16, fontweight='bold',
                color=txt_color)
        # Description below bar
        ax.text(start + w/2, y0 + bar_h * 0.2, desc,
                ha='center', va='center', fontsize=10, color='#444444')
    else:
        ax.text(start + w/2, y0 + h + 0.3, label,
                ha='center', va='bottom', fontsize=12, fontweight='bold',
                color=color)

    # Frequency range label below band
    ax.text(start + w/2, y0 - 0.15, freq_s, ha='center', va='top',
            fontsize=11, color='#555555', fontweight='bold')

# ============================================================
# Band boundary markers
# ============================================================
for freq, lbl in [(0.7, '0.7Hz'), (5, '5Hz'), (18, '18Hz')]:
    ax.plot([freq, freq], [axis_y, y0+h], color='#999999', linewidth=1, linestyle=':', zorder=2)
    ax.text(freq, y0-0.8, lbl, ha='center', fontsize=9, color='#888888')

# ============================================================
# 50 Hz interference
# ============================================================
ax.axvline(x=50, ymin=0.1, ymax=0.46, color='#C0392B', linewidth=2.5,
           linestyle='--', zorder=4)
ax.plot(50, 0.9, 'v', color='#C0392B', markersize=12, zorder=5)
ax.text(50, 1.3, '50 Hz 工频干扰', ha='center', fontsize=11,
        fontweight='bold', color='#C0392B',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#F5EEF8',
                  edgecolor='#C0392B', linewidth=1.2))

# ============================================================
# Top annotation boxes
# ============================================================
# Place annotation descriptions in the space ABOVE zone tags
# Each has: a colored arrow pointing down, then a short description
descriptions = [
    (0.35, '呼吸运动及电极移动\n产生的低频基线漂移', '#5DADE2'),
    (2.8,  'P波（心房除极）和\nT波（心室复极）的低频电活动', '#58D68D'),
    (11.5, '★ R波能量最集中频段\nQRS波群主体成分', '#E74C3C'),
    (29,   '肌肉收缩、电磁干扰\n等高频噪声成分', '#F39C12'),
]

for x, txt, c in descriptions:
    # Small arrow pointing down
    ax.annotate('', xy=(x, zone_y - 0.3), xytext=(x, y0 + h + 0.5),
                arrowprops=dict(arrowstyle='->', color=c, lw=1.5,
                                connectionstyle='arc3,rad=0'),
                zorder=2)

    # Text box above zones
    ax.text(x, zone_y + 0.4, txt, ha='center', va='bottom', fontsize=10,
            color='#333333', linespacing=1.4,
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                      edgecolor=c, linewidth=1.5, alpha=0.95))

# ============================================================
# Sampling info at bottom
# ============================================================
ax.text(0.98, -1.0, 'ECG采样率: 360 Hz  |  R波检测通带: 5~18 Hz  |  FFT零相位滤波',
        transform=ax.transAxes, fontsize=9.5, color='#888888',
        ha='right', va='center', style='italic')

# ============================================================
# Title and Legend
# ============================================================
ax.set_title('ECG 心电信号频带成分分布', fontsize=20, fontweight='bold',
             pad=15, color='#1a1a1a', loc='left', x=0.01)

legend_elements = [
    mpatches.Patch(facecolor='#5DADE2', edgecolor='#333333', label='基线漂移 (<0.7Hz)'),
    mpatches.Patch(facecolor='#58D68D', edgecolor='#333333', label='P波/T波 (0.7~5Hz)'),
    mpatches.Patch(facecolor='#E74C3C', edgecolor='#333333', label='QRS波群 (5~18Hz) ★'),
    mpatches.Patch(facecolor='#F39C12', edgecolor='#333333', label='肌电/噪声 (>18Hz)'),
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10.5,
                    framealpha=0.95, edgecolor='#CCCCCC', ncol=4,
                    columnspacing=1.5, handletextpad=0.5)
legend.get_frame().set_linewidth(1.2)

plt.tight_layout()

out = 'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png'
plt.savefig(out, dpi=250, bbox_inches='tight', facecolor='white',
            edgecolor='none', format='png', transparent=False)
print(f'Saved: {out}')

import os
from PIL import Image
sz = os.path.getsize(out)
img = Image.open(out)
w, h = img.size
pixels = list(img.getdata())
non_white = sum(1 for p in pixels if p[0] < 230 or p[1] < 230 or p[2] < 230)
print(f'Size: {w}x{h}, {sz/1024:.0f} KB, Content: {non_white/len(pixels)*100:.1f}%')
plt.close()
