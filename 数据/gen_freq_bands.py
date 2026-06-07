#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
Generate ECG 频带成分分布示意图
White background, black text, clear arrows, proper sizing
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image

# Use Chinese font
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.unicode_minus'] = False

# Create figure with white background
fig, ax = plt.subplots(1, 1, figsize=(16, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Frequency range: 0 to 55 Hz
freq_max = 55

# Define frequency bands as (start, end, color, label, sublabel)
bands = [
    (0, 0.7,   '#4A90D9', '基线漂移', '呼吸运动、电极移动'),
    (0.7, 5,   '#2ECC71', 'P波 / T波', '心房除极与复极'),
    (5, 18,    '#E74C3C', 'QRS 波群 ★', '心室除极（R波核心频段）'),
    (18, 40,   '#F39C12', '肌电噪声', '肌肉收缩干扰'),
]

# Draw the frequency axis
ax.axhline(y=1.5, xmin=0, xmax=freq_max/freq_max, color='black', linewidth=2.5, zorder=1)

# Draw frequency bands as rectangles with rounded corners
band_height = 1.2
band_y = 1.5 - band_height/2

for i, (start, end, color, label, sublabel) in enumerate(bands):
    width = end - start
    if width < 0.3:
        width = 0.3  # minimum width for visibility
    rect = FancyBboxPatch((start, band_y), width, band_height,
                           boxstyle=f"round,pad=0.08",
                           facecolor=color, edgecolor='#333333',
                           linewidth=1.5, alpha=0.85, zorder=2)
    ax.add_patch(rect)

    # Label inside the band (if width is enough)
    if width > 2:
        ax.text(start + width/2, 1.5, label, ha='center', va='center',
                fontsize=13, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.15', facecolor=color, edgecolor='none', alpha=0.0))
        ax.text(start + width/2, 1.5 - 0.35, sublabel, ha='center', va='center',
                fontsize=8.5, color='white', alpha=0.9, style='italic')
    else:
        # Label above for narrow bands
        ax.annotate(label, xy=(start + width/2, 1.5 + band_height/2),
                    xytext=(start + width/2, 1.5 + band_height/2 + 0.4),
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color=color,
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

# Draw 50Hz power line interference marker
ax.axvline(x=50, ymin=0.05, ymax=0.35, color='#E74C3C', linewidth=2.5, linestyle='--', zorder=3)
ax.text(50, 1.5 + band_height/2 + 0.5, '← 50Hz 工频干扰', ha='center', fontsize=12,
        fontweight='bold', color='#E74C3C')

# Draw amplitude waveform hint (simplified ECG-like wave above)
wave_x = np.linspace(0, 50, 1000)
# Simulate a simplified ECG spectrum energy curve
wave_y = np.zeros_like(wave_x)
# Baseline drift peak
wave_y += 0.3 * np.exp(-((wave_x - 0.3)/0.2)**2)
# P/T wave peak
wave_y += 0.5 * np.exp(-((wave_x - 2.5)/1.2)**2)
# QRS peak (main)
wave_y += 1.8 * np.exp(-((wave_x - 10)/3.5)**2)
# QRS secondary peak
wave_y += 0.8 * np.exp(-((wave_x - 15)/2.0)**2)
# EMG noise
wave_y += 0.15 * np.sin(wave_x * 0.5) * (1 - np.exp(-(wave_x - 20)/5))
wave_y[wave_x > 20] += 0.1 * np.sin(wave_x[wave_x > 20] * 0.8)

# Normalize and shift to upper area
wave_y = wave_y * 0.6 / wave_y.max()
ax.fill_between(wave_x, 2.8, 2.8 + wave_y, color='#2C3E50', alpha=0.12, zorder=0)
ax.plot(wave_x, 2.8 + wave_y, color='#2C3E50', linewidth=1.2, alpha=0.3, zorder=0)

# Annotations - text descriptions
annotations = [
    (0.3, 2.4, '呼吸/电极移动', '0.3~0.5 Hz'),
    (2.5, 2.4, '心房电活动', '0.7~5 Hz'),
    (11, 2.6, 'R波能量集中区', '5~18 Hz ★'),
    (30, 2.4, '高频干扰', '>30 Hz'),
]

for x, y, text, detail in annotations:
    ax.plot(x, y, 'o', color='#555555', markersize=4, zorder=3)
    ax.annotate(f'{text}\n({detail})', xy=(x, y),
                xytext=(x + 3.5, y - 0.3), fontsize=9.5, color='#333333',
                ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FAFAFA',
                          edgecolor='#CCCCCC', linewidth=0.8),
                arrowprops=dict(arrowstyle='->', color='#555555', lw=1.2))

# Axis labels and ticks
ax.set_xlabel('频率 (Hz)', fontsize=15, fontweight='bold', labelpad=8)
ax.set_ylabel('信号能量', fontsize=15, fontweight='bold', labelpad=8)

# X-axis ticks
ax.set_xticks(np.arange(0, 56, 5))
ax.set_xticks(np.arange(0, 56, 1), minor=True)
ax.set_xlim(-1, 55)
ax.set_ylim(0.5, 3.8)

# Add vertical grid lines as visual guides
for freq in [0.7, 5, 18]:
    ax.axvline(x=freq, ymin=0.3, ymax=0.42, color='#888888', linewidth=0.8, linestyle=':', zorder=0)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)

# Add a legend for the bands
legend_elements = [
    mpatches.Patch(facecolor='#4A90D9', edgecolor='#333333', label='基线漂移 (<0.7Hz)'),
    mpatches.Patch(facecolor='#2ECC71', edgecolor='#333333', label='P波/T波 (0.7~5Hz)'),
    mpatches.Patch(facecolor='#E74C3C', edgecolor='#333333', label='QRS波群 (5~18Hz)'),
    mpatches.Patch(facecolor='#F39C12', edgecolor='#333333', label='肌电噪声 (>18Hz)'),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10,
          framealpha=0.9, edgecolor='#CCCCCC', ncol=2)

# Title
ax.set_title('ECG 心电信号频带成分分布', fontsize=18, fontweight='bold',
             pad=15, color='#1a1a1a')

# Additional annotation for ECG sampling
ax.text(0.98, 0.02, 'ECG采样频率: 360 Hz  |  通带设计: 5~18 Hz (R波检测)',
        transform=ax.transAxes, fontsize=9, color='#666666',
        ha='right', va='bottom', style='italic')

plt.tight_layout()

# Save with high DPI
output_path = 'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f'Saved: {output_path}')

# Also save a version that matches the tech doc naming
plt.savefig('d:/bishe/tech_images/word/media/image6_new.png', dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
print('Saved: image6_new.png')

# Show file size
import os
size = os.path.getsize(output_path)
print(f'File size: {size/1024:.1f} KB')

plt.close()
