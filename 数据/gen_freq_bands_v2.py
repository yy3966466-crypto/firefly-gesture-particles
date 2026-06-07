#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
Generate ECG 频带成分分布示意图 v2
Clean design: white background, black text, clear boxes, no crowding
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(18, 5.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# --- Frequency axis ---
ax.axhline(y=0, xmin=0, xmax=1, color='black', linewidth=3, zorder=5)
ax.set_xlim(-1, 55)
ax.set_ylim(-2.5, 3.5)
ax.set_xlabel('频率 (Hz)', fontsize=16, fontweight='bold', labelpad=10)

# --- Tick marks ---
for f in range(0, 56, 5):
    ax.plot(f, 0, '|', color='black', markersize=12, mew=2, zorder=6)
    ax.text(f, -0.4, str(f), ha='center', fontsize=11, color='black')

# Minor ticks
for f in range(0, 56):
    if f % 5 != 0:
        ax.plot(f, 0, '|', color='#888888', markersize=6, mew=1, zorder=5)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_position(('data', 0))
ax.set_yticks([])
ax.set_yticklabels([])

# --- Define frequency bands ---
# (start, end, color_top, color_bottom, label, sublabel, freq_label)
bands = [
    (0,    0.7, '#3498DB', '#85C1E9', '基线漂移', '呼吸/电极移动', '< 0.7 Hz'),
    (0.7,  5.0, '#27AE60', '#82E0AA', 'P波 / T波', '心房电活动', '0.7 ~ 5 Hz'),
    (5.0,  18.0,'#E74C3C', '#F1948A', 'QRS 波群 ★', '心室除极（R波）', '5 ~ 18 Hz 核心频段'),
    (18.0, 40.0,'#E67E22', '#F0B27A', '肌电 / 高频噪声', '肌肉收缩干扰', '18 ~ 40 Hz'),
]

# Draw bands as rectangles
for i, (start, end, c_top, c_bot, label, sublabel, freq_lbl) in enumerate(bands):
    y_bottom = -0.05
    height = 1.8
    width = max(end - start, 0.3)

    # Main band rectangle
    rect = mpatches.FancyBboxPatch((start, y_bottom), width, height,
                                     boxstyle=f"round,pad=0.08",
                                     facecolor=c_bot, edgecolor='#333333',
                                     linewidth=1.8, zorder=3)
    ax.add_patch(rect)

    # Top accent stripe
    stripe = mpatches.FancyBboxPatch((start + 0.05, y_bottom + height - 0.35),
                                      width - 0.1, 0.3,
                                      boxstyle=f"round,pad=0.03",
                                      facecolor=c_top, edgecolor='none',
                                      alpha=0.6, zorder=4)
    ax.add_patch(stripe)

    # Band label (inside)
    if width > 2.5:
        ax.text(start + width/2, y_bottom + height/2 + 0.2, label,
                ha='center', va='center', fontsize=14, fontweight='bold', color='#1a1a1a')
        ax.text(start + width/2, y_bottom + height/2 - 0.35, sublabel,
                ha='center', va='center', fontsize=10, color='#444444', style='italic')
        ax.text(start + width/2, y_bottom - 0.6, freq_lbl,
                ha='center', va='top', fontsize=9.5, color='#555555',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FAFAFA',
                          edgecolor='#CCCCCC', linewidth=0.8))
    else:
        # For narrow bands, put label above
        ax.text(start + width/2, y_bottom + height + 0.3, label,
                ha='center', va='center', fontsize=11, fontweight='bold', color=c_top)
        ax.text(start + width/2, y_bottom - 0.6, freq_lbl,
                ha='center', va='top', fontsize=9, color='#555555')

# --- 50 Hz power line interference marker ---
ax.axvline(x=50, ymin=0.03, ymax=0.45, color='#C0392B', linewidth=3,
           linestyle='--', zorder=4)
ax.plot(50, 0.9, 'v', color='#C0392B', markersize=12, zorder=5)
ax.text(50, 1.3, '50 Hz 工频干扰', ha='center', fontsize=12,
        fontweight='bold', color='#C0392B')
# Show 50Hz frequency
ax.text(50, -0.6, '50 Hz', ha='center', fontsize=10, color='#C0392B',
        fontweight='bold')

# --- Divider lines between bands ---
for freq in [0.7, 5, 18]:
    ax.plot([freq, freq], [0, 1.8], color='#666666', linewidth=1, linestyle=':', zorder=2)

# --- Arrow annotations pointing to key bands ---
annotations = [
    (0.3, 2.5, '呼吸运动、电极偏移\n引起的低频波动', '#3498DB'),
    (2.5, 2.5, 'P波：心房除极\nT波：心室复极', '#27AE60'),
    (11,  2.8, '★ R波能量集中区\nQRS波群主要频带', '#E74C3C'),
    (28,  2.5, '肌肉收缩等\n高频干扰成分', '#E67E22'),
]

for x, y, text, color in annotations:
    ax.annotate('', xy=(x, 1.8), xytext=(x, y - 0.2),
                arrowprops=dict(arrowstyle='->', color=color, lw=2.5,
                                connectionstyle='arc3,rad=0'), zorder=3)
    ax.text(x + 2.3, y - 0.35, text, ha='left', va='center', fontsize=10,
            color='#333333', linespacing=1.4,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FAFAFA',
                      edgecolor=color, linewidth=1.2, alpha=0.95))

# --- Title ---
ax.set_title('ECG 心电信号频带成分分布', fontsize=20, fontweight='bold',
             pad=20, color='#1a1a1a', loc='left')

# --- Legend ---
legend_elements = [
    mpatches.Patch(facecolor='#3498DB', edgecolor='#333333', label='基线漂移'),
    mpatches.Patch(facecolor='#27AE60', edgecolor='#333333', label='P波 / T波'),
    mpatches.Patch(facecolor='#E74C3C', edgecolor='#333333', label='QRS 波群 (5~18Hz)'),
    mpatches.Patch(facecolor='#E67E22', edgecolor='#333333', label='肌电 / 高频噪声'),
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10.5,
                    framealpha=0.95, edgecolor='#BBBBBB', ncol=4,
                    columnspacing=1.5)
legend.get_frame().set_linewidth(1.2)

# --- ECG sampling info ---
ax.text(0.99, 0.01, '采样率: 360 Hz  |  检测通带: 5~18 Hz  |  FFT零相位滤波',
        transform=ax.transAxes, fontsize=9.5, color='#777777',
        ha='right', va='bottom', style='italic')

plt.tight_layout()

# Save as RGB (not RGBA) for Word compatibility
output_path = 'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png'
plt.savefig(output_path, dpi=250, bbox_inches='tight', facecolor='white',
            edgecolor='none', format='png')
print(f'Saved: {output_path}')

# Also save for replacing in thesis
plt.savefig('d:/bishe/tech_images/word/media/image6_new.png', dpi=250,
            bbox_inches='tight', facecolor='white', edgecolor='none', format='png')
print('Saved: image6_new.png')

import os
print(f'Size: {os.path.getsize(output_path)/1024:.0f} KB')

plt.close()
