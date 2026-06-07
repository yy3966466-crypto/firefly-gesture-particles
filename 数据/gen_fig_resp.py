"""Generate respiration signal comparison figure - thesis quality."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import scipy.io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Use font that supports Chinese
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# Load processed data
data = scipy.io.loadmat('data/cache/resp_01.mat')
resp = data['resp'][0, 0]

fs = float(resp['fs'][0, 0])
t = resp['t'].flatten()
raw = resp['raw'].flatten()
bandpassed = resp['bandpassed'].flatten()
enhanced = resp['enhanced'].flatten()
peakLocs = resp['peakLocs'].flatten().astype(int) - 1

# Pick a clean 12-second window
window_len = 12
start_time = 25
start_idx = np.searchsorted(t, start_time)
end_idx = min(start_idx + int(window_len * fs), len(t))
idx_range = slice(start_idx, end_idx)

t_win = t[idx_range]
raw_win = raw[idx_range]
bandpassed_win = bandpassed[idx_range]
enhanced_win = enhanced[idx_range]

# Peaks within window
peak_mask = (peakLocs >= start_idx) & (peakLocs < end_idx)
peak_in_win = peakLocs[peak_mask]
peak_times = t[peak_in_win]
peak_vals = enhanced[peak_in_win]

fig, axes = plt.subplots(3, 1, figsize=(8, 5.5), sharex=True)

# (a) Original signal
ax = axes[0]
ax.plot(t_win, raw_win, 'k-', linewidth=0.8)
ax.set_ylabel('幅度', fontsize=10)
ax.set_title('(a) 原始呼吸信号', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(t_win[0], t_win[-1])
y_range = np.ptp(raw_win)
ax.set_ylim(raw_win.min() - 0.05*y_range, raw_win.max() + 0.05*y_range)
ax.tick_params(labelsize=9)

# (b) Bandpassed
ax = axes[1]
ax.plot(t_win, bandpassed_win, 'b-', linewidth=0.8)
ax.set_ylabel('幅度', fontsize=10)
ax.set_title('(b) 带通滤波后 (0.08–0.80 Hz)', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(t_win[0], t_win[-1])
y_range = np.ptp(bandpassed_win)
ax.set_ylim(bandpassed_win.min() - 0.05*y_range, bandpassed_win.max() + 0.05*y_range)
ax.tick_params(labelsize=9)

# (c) ALE-enhanced with peaks
ax = axes[2]
ax.plot(t_win, enhanced_win, 'r-', linewidth=0.9)
ax.plot(peak_times, peak_vals, 'k^', markerfacecolor='k', markersize=5, label='检测波峰')
ax.set_xlabel('时间 (s)', fontsize=10)
ax.set_ylabel('幅度', fontsize=10)
ax.set_title('(c) ALE增强信号与检测波峰', fontsize=11, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(t_win[0], t_win[-1])
y_range = np.ptp(enhanced_win)
ax.set_ylim(enhanced_win.min() - 0.05*y_range, enhanced_win.max() + 0.05*y_range)
ax.tick_params(labelsize=9)
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout(pad=0.8)
plt.savefig('fig_respiration_comparison.png', dpi=300, bbox_inches='tight')
print('Figure saved successfully')
print(f'Window: {start_time}-{start_time+window_len}s, peaks: {len(peak_in_win)}')
plt.close()
