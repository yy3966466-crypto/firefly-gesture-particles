import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import scipy.io as sio

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# load cached ECG data  (record 105 — clean normal rhythm)
# ---------------------------------------------------------------------------
data = sio.loadmat('data/cache/ecg_105_lead1.mat')
ecg = data['ecg'][0, 0]

t        = ecg['t'].flatten()
raw      = ecg['raw'].flatten()
filtered = ecg['filtered'].flatten()
diff_env = ecg['diffEnvelope'].flatten()
thresh   = ecg['threshold'].flatten()
r_locs   = ecg['rLocs'].flatten().astype(int) - 1   # MATLAB→0‑indexed
fs       = ecg['fs'][0, 0]
record   = ecg['recordName'][0]

# ---------------------------------------------------------------------------
# pick a representative 10‑second window  (roughly where HR deviates most)
# ---------------------------------------------------------------------------
win_sec = 10
win_samp = int(win_sec * fs)

# pick window 1/3 into the recording (stable region)
start = len(raw) // 3
idx = slice(start, start + win_samp)

t_win    = t[idx]
raw_win  = raw[idx]
filt_win = filtered[idx]
env_win  = diff_env[idx]
thr_win  = thresh[idx]

# R peaks inside window
r_in = r_locs[(r_locs >= idx.start) & (r_locs < idx.stop)]
r_t  = t[r_in]
r_y  = filtered[r_in]

# ---------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5),
                                sharex=True,
                                gridspec_kw=dict(hspace=0.30))
fig.patch.set_facecolor('white')

# ---- top: raw vs filtered ----
ax1.plot(t_win, raw_win,
         color='#999999', linewidth=0.9, label='原始信号')
ax1.plot(t_win, filt_win,
         color='#0055AA', linewidth=1.3, label='滤波后信号')
ax1.scatter(r_t, r_y, s=30, facecolors='#DD2222', edgecolors='none',
            label='R 波位置', zorder=3)
ax1.set_ylabel('幅值 / mV', fontsize=10)
ax1.set_title('ECG 预处理前后波形对比  —  MIT-BIH Record %s' % record,
              fontsize=12, fontweight='bold', pad=8)
ax1.legend(loc='upper right', fontsize=8.5, framealpha=0.85,
           edgecolor='#CCCCCC')
ax1.grid(True, linestyle=':', color='#DDDDDD', linewidth=0.5)
ax1.set_xlim(t_win[0], t_win[-1])

# ---- bottom: diff envelope + threshold ----
ax2.plot(t_win, env_win,
         color='#338833', linewidth=1.1, label='差分包络')
ax2.plot(t_win, thr_win,
         color='#CC3333', linewidth=1.0, linestyle='--', label='自适应阈值')
ax2.set_xlabel('时间 / s', fontsize=10)
ax2.set_ylabel('幅值', fontsize=10)
ax2.legend(loc='upper right', fontsize=8.5, framealpha=0.85,
           edgecolor='#CCCCCC')
ax2.grid(True, linestyle=':', color='#DDDDDD', linewidth=0.5)
ax2.set_xlim(t_win[0], t_win[-1])

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/03_preprocess_comparison.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig('d:/bishe/ecg_preprocess_comparison.png',
            dpi=200, bbox_inches='tight', facecolor='white')
plt.close()
print('OK → ecg_preprocess_comparison.png')
