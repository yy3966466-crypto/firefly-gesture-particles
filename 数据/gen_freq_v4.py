#!/c/Users/杨竣程/AppData/Local/Programs/Python/Python312/python.exe
# -*- coding: utf-8 -*-
"""
ECG频带成分分布示意图 v4
Clear, no overlapping text, no compression artifacts
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['font.size'] = 13
plt.rcParams['axes.unicode_minus'] = False

# --- Larger figure for better clarity ---
fig, ax = plt.subplots(1, 1, figsize=(20, 5.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.set_xlim(-1, 56)
ax.set_ylim(-1.8, 4.5)

for s in ax.spines.values():
    s.set_visible(False)
ax.set_yticks([])
ax.set_yticklabels([])
ax.tick_params(axis='x', length=0)

# --- Frequency axis ---
ax.axhline(y=0, color='black', linewidth=2.5, zorder=5)
ax.set_xlabel('频率 (Hz)', fontsize=15, fontweight='bold', labelpad=15, color='#1a1a1a')

for f in range(0, 56, 5):
    ax.plot(f, 0, '|', color='black', markersize=12, mew=2, zorder=6)
    ax.text(f, -0.35, str(f), ha='center', va='top', fontsize=11, color='black')
for f in range(0, 56):
    if f % 5 != 0:
        ax.plot(f, 0, '|', color='#AAAAAA', markersize=6, mew=1, zorder=5)

# --- Frequency bands with generous spacing ---
y0 = 0.1
h = 1.5

bands = [
    (0,   0.7, '#5DADE2', '#D6EAF8', '基线漂移', '< 0.7 Hz', '呼吸运动、电极移动引起的低频波动'),
    (0.7, 5,   '#58D68D', '#D5F5E3', 'P波 / T波', '0.7 ~ 5 Hz', '心房除极(P波)与心室复极(T波)'),
    (5,   18,  '#E74C3C', '#FADBD8', 'QRS 波群', '5 ~ 18 Hz', '心室除极·R波核心频段★'),
    (18,  40,  '#F39C12', '#FDEBD0', '肌电/高频噪声', '18 ~ 40 Hz', '肌肉收缩等高频干扰'),
]

for start, end, color, light_c, label, freq_s, desc in bands:
    w = max(end - start, 0.3)

    # Light background
    bg = mpatches.FancyBboxPatch((start, y0), w, h,
                                   boxstyle="round,pad=0.06",
                                   facecolor=light_c, edgecolor='none', alpha=0.5, zorder=1)
    ax.add_patch(bg)

    # Colored band bar (only top portion)
    bar_h = h * 0.55
    rect = mpatches.FancyBboxPatch((start + 0.05, y0 + h - bar_h), w - 0.1, bar_h,
                                     boxstyle="round,pad=0.04",
                                     facecolor=color, edgecolor='#333333', linewidth=1.5, zorder=3)
    ax.add_patch(rect)

    # Band label INSIDE bar (for wide enough bands)
    txt_color = 'white' if label == 'QRS 波群' else '#1a1a1a'
    if w >= 4:
        ax.text(start + w/2, y0 + h - bar_h/2, label,
                ha='center', va='center', fontsize=15, fontweight='bold', color=txt_color)
    else:
        ax.text(start + w/2, y0 + h + 0.25, label,
                ha='center', va='bottom', fontsize=12, fontweight='bold', color=color)

    # Frequency label BELOW band (not on band)
    ax.text(start + w/2, y0 - 0.05, freq_s, ha='center', va='top',
            fontsize=11, color='#444444', fontweight='bold')

# --- Annotation arrows ABOVE the bands ---
# Each annotation is placed ABOVE the bands, with a clear arrow pointing down
annot_y = 3.0
annot_data = [
    (0.3,  '基线漂移源', '呼吸运动、电极偏移\n引起的低频基线变化', '#5DADE2'),
    (2.5,  'P/T波源', '心房除极与复极\n产生的低频电活动', '#58D68D'),
    (11.0, '★ R波源', '心室除极过程\nQRS波群能量最集中', '#E74C3C'),
    (28.0, '噪声源', '肌肉收缩/外部电磁\n产生的高频干扰', '#F39C12'),
]

for x, title, desc, c in annot_data:
    # Vertical arrow from top down to the band
    ax.annotate('', xy=(x, y0 + h + 0.1), xytext=(x, annot_y - 0.2),
                arrowprops=dict(arrowstyle='->', color=c, lw=2.5,
                                connectionstyle='arc3,rad=0'), zorder=3)

    # Annotation box ABOVE the arrow
    ax.text(x, annot_y + 0.15, f'【{title}】', ha='center', va='bottom',
            fontsize=12, fontweight='bold', color=c)
    ax.text(x, annot_y + 0.15, f'【{title}】', ha='center', va='bottom',
            fontsize=12, fontweight='bold', color=c)

    # Description text next to the arrow, slightly offset to avoid overlap
    if x < 3:
        tx = x + 5.5
        ha = 'left'
    elif x > 20:
        tx = x - 5.5
        ha = 'right'
    else:
        tx = x + 6
        ha = 'left'

    ax.text(tx, annot_y - 0.35, desc, ha=ha, va='center', fontsize=10.5,
            color='#333333', linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=c, linewidth=1.2, alpha=0.95))

    # Connecting line from arrow to text box
    ax.annotate('', xy=(x, annot_y - 0.4), xytext=(tx if ha == 'left' else tx, annot_y - 0.4),
                arrowprops=dict(arrowstyle='-', color=c, lw=1.2, linestyle='dotted'),
                zorder=2)

# --- 50 Hz marker ---
ax.axvline(x=50, ymin=0.05, ymax=0.55, color='#C0392B', linewidth=2.5, linestyle='--', zorder=4)
ax.plot(50, 1.0, 'v', color='#C0392B', markersize=12, zorder=5)
ax.text(50, 1.4, '50 Hz 工频干扰', ha='center', fontsize=11,
        fontweight='bold', color='#C0392B',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FDEDEC',
                  edgecolor='#C0392B', linewidth=1))

# --- Boundary markers at band edges ---
for freq in [0.7, 5, 18]:
    ax.plot([freq, freq], [0, y0+h], color='#999999', linewidth=1, linestyle=':', zorder=2)
    ax.text(freq, -0.7, f'{freq}Hz', ha='center', fontsize=8.5, color='#888888')

# --- Vertical frequency range zones (top markers) ---
# These are small labeled tags on top indicating the range names
zone_y = 4.2
zones = [
    (0, 0.7, '低频区', '#5DADE2'),
    (0.7, 5, '中低频区', '#58D68D'),
    (5, 18, '中频区 ★', '#E74C3C'),
    (18, 40, '高频区', '#F39C12'),
]
for start, end, name, c in zones:
    mid = (start + end) / 2
    ax.text(mid, zone_y, name, ha='center', va='center', fontsize=10,
            fontweight='bold', color=c,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor=c, linewidth=1.2))

# --- Title ---
ax.set_title('ECG 心电信号频带成分分布', fontsize=20, fontweight='bold',
             pad=18, color='#1a1a1a', loc='left', x=0.01)

# --- Legend ---
legend_elements = [
    mpatches.Patch(facecolor='#5DADE2', edgecolor='#333333', label='基线漂移 (<0.7Hz)'),
    mpatches.Patch(facecolor='#58D68D', edgecolor='#333333', label='P波/T波 (0.7~5Hz)'),
    mpatches.Patch(facecolor='#E74C3C', edgecolor='#333333', label='QRS波群 (5~18Hz)'),
    mpatches.Patch(facecolor='#F39C12', edgecolor='#333333', label='肌电/噪声 (>18Hz)'),
]
legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10,
                    framealpha=0.95, edgecolor='#BBBBBB', ncol=4,
                    columnspacing=1.5, handletextpad=0.5)
legend.get_frame().set_linewidth(1)

# --- Bottom info ---
ax.text(0.98, -0.9, 'ECG采样率: 360 Hz  |  R波检测通带: 5~18 Hz  |  FFT零相位滤波',
        transform=ax.transAxes, fontsize=9, color='#888888',
        ha='right', va='center', style='italic')

plt.tight_layout()

out = 'd:/bishe/flowchart_images_v4/11_ecg_frequency_bands.png'
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='white',
            edgecolor='none', format='png', transparent=False)
print(f'Saved: {out}')

import os
print(f'Size: {os.path.getsize(out)/1024:.0f} KB')

# Analyze content
from PIL import Image
img = Image.open(out)
w, h = img.size
print(f'Dimensions: {w}x{h}')
pixels = list(img.getdata())
non_white = sum(1 for p in pixels if p[0] < 230 or p[1] < 230 or p[2] < 230)
print(f'Content: {non_white/len(pixels)*100:.1f}% non-white')

plt.close()
