#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
Generate ECG 频带成分分布示意图 v3
Optimized for clear viewing, better space utilization
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 13
plt.rcParams['axes.unicode_minus'] = False

# --- Create figure with optimized dimensions ---
fig, ax = plt.subplots(1, 1, figsize=(16, 4.2))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# --- Axis setup ---
ax.set_xlim(-1, 55)
ax.set_ylim(-1.0, 3.0)

# Hide default spines and ticks
for s in ax.spines.values():
    s.set_visible(False)
ax.set_yticks([])
ax.set_yticklabels([])
ax.tick_params(axis='x', length=0)

# --- Frequency axis at y=0 ---
ax.axhline(y=0, xmin=0, xmax=1, color='black', linewidth=2.5, zorder=5)

# Frequency labels and ticks along axis
for f in range(0, 56, 5):
    ax.plot(f, 0, '|', color='black', markersize=10, mew=2, zorder=6)
    offset = -0.3 if f % 10 == 0 else -0.22
    ax.text(f, offset, str(f), ha='center', va='top', fontsize=10, color='black')

# Minor ticks
for f in range(0, 56):
    if f % 5 != 0:
        ax.plot(f, 0, '|', color='#999999', markersize=5, mew=1, zorder=5)

ax.set_xlabel('频率 (Hz)', fontsize=14, fontweight='bold', labelpad=8, color='#1a1a1a')

# --- Band definitions: (start, end, color, label, sublabel, freq_str) ---
bands = [
    (0.0,  0.7, '#5DADE2', '#A9CCE3', '基线漂移', '呼吸/电极移动', '< 0.7 Hz'),
    (0.7,  5.0, '#58D68D', '#A9DFBF', 'P波 / T波', '心房电活动', '0.7 ~ 5 Hz'),
    (5.0,  18.0,'#E74C3C', '#F5B7B1', 'QRS 波群 ★', '心室除极 · R波核心频段', '5 ~ 18 Hz'),
    (18.0, 40.0,'#F39C12', '#F9E79F', '肌电噪声', '高频干扰', '18 ~ 40 Hz'),
]

# --- Draw bands ---
y0, h = 0.03, 1.6
for i, (start, end, color, light_c, label, sublabel, freq_s) in enumerate(bands):
    w = max(end - start, 0.3)

    # Light background rectangle
    bg_rect = mpatches.FancyBboxPatch((start, y0), w, h,
                                        boxstyle="round,pad=0.05",
                                        facecolor=light_c, edgecolor='none',
                                        alpha=0.4, zorder=1)
    ax.add_patch(bg_rect)

    # Top colored band
    band_h = h * 0.7
    rect = mpatches.FancyBboxPatch((start, y0 + h - band_h), w, band_h,
                                     boxstyle="round,pad=0.04",
                                     facecolor=color, edgecolor='#222222',
                                     linewidth=1.5, zorder=3)
    ax.add_patch(rect)

    # Label inside band
    if w > 3:
        ax.text(start + w/2, y0 + h - band_h/2, label,
                ha='center', va='center', fontsize=13, fontweight='bold',
                color='white' if label.startswith('QRS') else '#1a1a1a')
        ax.text(start + w/2, y0 + band_h * 0.3, sublabel,
                ha='center', va='center', fontsize=8.5, color='#444444')
    else:
        ax.text(start + w/2, y0 + h + 0.2, label,
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)

    # Frequency label below band
    ax.text(start + w/2, y0 - 0.08, freq_s, ha='center', va='top',
            fontsize=8.5, color='#555555', style='italic')

# --- 50 Hz interference marker ---
ax.axvline(x=50, ymin=0.05, ymax=0.55, color='#C0392B', linewidth=2.5,
           linestyle='--', zorder=4)
ax.plot(50, 0.85, 'v', color='#C0392B', markersize=10, zorder=5)
ax.text(50, 1.15, '50 Hz 工频干扰', ha='center', fontsize=10,
        fontweight='bold', color='#C0392B')

# --- Vertical guide lines at band boundaries ---
for freq, label in [(0.7, '0.7'), (5, '5'), (18, '18')]:
    ax.plot([freq, freq], [0, y0+h], color='#888888', linewidth=0.8, linestyle=':', zorder=2)

# --- Direct annotation arrows from top ---
annotations = [
    (0.3,  2.6, '呼吸运动引起的\n低频基线漂移', '#5DADE2'),
    (2.5,  2.6, 'P波：心房除极电活动\nT波：心室复极过程', '#58D68D'),
    (10.5, 2.8, '★ R波检测核心频段\nQRS波群能量最集中区域', '#E74C3C'),
    (28,   2.5, '肌肉收缩产生的\n高频噪声干扰', '#F39C12'),
]

for x, y, txt, c in annotations:
    ax.annotate('', xy=(x, y0+h), xytext=(x, y - 0.15),
                arrowprops=dict(arrowstyle='->', color=c, lw=2.2,
                                connectionstyle='arc3,rad=0'), zorder=3)
    # Text box
    ax.text(x + 2.8, y - 0.35, txt, ha='left', va='center', fontsize=9.5,
            color='#222222', linespacing=1.3,
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white',
                      edgecolor=c, linewidth=1.5, alpha=0.95))

# --- Title ---
ax.set_title('ECG 心电信号频带成分分布', fontsize=18, fontweight='bold',
             pad=12, color='#1a1a1a', loc='left', x=0.02)

# --- Legend at bottom-right of figure ---
legend_elements = [
    mpatches.Patch(facecolor='#5DADE2', edgecolor='#333333', label='基线漂移 (<0.7Hz)'),
    mpatches.Patch(facecolor='#58D68D', edgecolor='#333333', label='P/T波 (0.7~5Hz)'),
    mpatches.Patch(facecolor='#E74C3C', edgecolor='#333333', label='QRS波群 (5~18Hz) ★'),
    mpatches.Patch(facecolor='#F39C12', edgecolor='#333333', label='肌电/噪声 (>18Hz)'),
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
                    framealpha=0.95, edgecolor='#CCCCCC', ncol=2,
                    columnspacing=1.2, handletextpad=0.5)
legend.get_frame().set_linewidth(1)

# --- Info line ---
ax.text(0.98, -0.55, 'ECG采样率: 360 Hz  |  R波检测通带: 5~18 Hz  |  FFT零相位滤波',
        transform=ax.transAxes, fontsize=8.5, color='#888888',
        ha='right', va='center', style='italic')

plt.tight_layout()

# Save
out = 'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png'
plt.savefig(out, dpi=250, bbox_inches='tight', facecolor='white',
            edgecolor='none', format='png', transparent=False)
print(f'Saved: {out}')

# Also save for tech doc replacement
plt.savefig('d:/bishe/tech_images/word/media/image6_new.png', dpi=250,
            bbox_inches='tight', facecolor='white', edgecolor='none', format='png')
print('Saved: image6_new.png')

import os
print(f'File size: {os.path.getsize(out)/1024:.0f} KB')
plt.close()
