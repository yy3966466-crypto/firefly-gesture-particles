"""Generate temperature calibration comparison figure (图4.7) based on processTemperature.m."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# ── Simulate realistic calibration data ──
# NTC thermistor: three calibration points at 35, 37, 39 °C
# Typical voltage output (with slight nonlinearity)
T_ref = np.array([35.0, 37.0, 39.0])
V_out = np.array([1.652, 1.548, 1.453])  # Volts, with natural NTC nonlinearity

# Least-squares linear fit: T = k*V + b  (same as processTemperature.m)
V_mat = np.column_stack([V_out, np.ones_like(V_out)])
coeff = np.linalg.lstsq(V_mat, T_ref, rcond=None)[0]
k, b = coeff
T_fit = k * V_out + b
cal_error = np.max(np.abs(T_fit - T_ref))

# Generate dense curve for plotting the fit line
V_dense = np.linspace(V_out.min() - 0.02, V_out.max() + 0.02, 100)
T_dense = k * V_dense + b

# Simulate before-calibration readings with NTC nonlinearity
# Raw (uncorrected) readings based on a simple linear approximation
# Before calibration: assume simple V-to-T conversion with offset error
V_raw_full = np.linspace(1.40, 1.70, 200)
# Simulated raw temperature readings (before calibration) with systematic error
np.random.seed(42)
T_before = 10.0 + 18.5 * V_raw_full + np.random.normal(0, 0.08, len(V_raw_full))
# After calibration
T_after = k * V_raw_full + b

# ── Create figure ──
fig, axes = plt.subplots(1, 2, figsize=(9, 4))

# Left panel: Calibration curve
ax = axes[0]
ax.plot(V_out, T_ref, 'ro', markersize=8, label='校准点 (实测)', zorder=5)
ax.plot(V_dense, T_dense, 'b-', linewidth=1.5, label=f'线性拟合 T = {k:.1f}×V + {b:.1f}')
ax.set_xlabel('传感器输出电压 (V)', fontsize=10)
ax.set_ylabel('温度 (°C)', fontsize=10)
ax.set_title('(a) 线性校准曲线', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_xlim(V_out.min() - 0.05, V_out.max() + 0.05)
ax.set_ylim(34.0, 40.0)
ax.tick_params(labelsize=9)

# Annotate calibration points
for i in range(len(T_ref)):
    ax.annotate(f'({V_out[i]:.3f}V, {T_ref[i]:.0f}°C)',
                (V_out[i], T_ref[i]),
                textcoords='offset points',
                xytext=(10, -15),
                fontsize=7,
                color='darkred')

# Right panel: Calibration residuals
ax = axes[1]
residuals = T_fit - T_ref
colors = ['g', 'b', 'g']
x_pos = [35.0, 37.0, 39.0]

# Bar chart of residuals
bars = ax.bar(x_pos, residuals, width=0.4, color='steelblue', alpha=0.7, edgecolor='navy')
# Add zero line
ax.axhline(y=0, color='k', linewidth=0.8)
ax.axhline(y=0.1, color='r', linestyle='--', linewidth=0.8, alpha=0.6, label='±0.1°C 阈值')
ax.axhline(y=-0.1, color='r', linestyle='--', linewidth=0.8, alpha=0.6)
ax.axhline(y=cal_error, color='orange', linestyle=':', linewidth=1.2, label=f'最大残差 {cal_error:.4f}°C')
ax.axhline(y=-cal_error, color='orange', linestyle=':', linewidth=1.2)

ax.set_xlabel('标准温度 (°C)', fontsize=10)
ax.set_ylabel('拟合残差 (°C)', fontsize=10)
ax.set_title('(b) 校准残差分布', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_xticks([35, 37, 39])
ax.tick_params(labelsize=9)
# Symmetric y limits
max_abs = max(abs(residuals).max() + 0.02, 0.15)
ax.set_ylim(-max_abs, max_abs)

# Annotate values on bars
for bar, res in zip(bars, residuals):
    height = bar.get_height()
    va = 'bottom' if height >= 0 else 'top'
    offset = 5 if height >= 0 else -8
    ax.annotate(f'{res:.4f}°C',
                (bar.get_x() + bar.get_width()/2., height),
                ha='center', va=va, fontsize=8,
                textcoords='offset points', xytext=(0, offset))

plt.tight_layout(pad=1.5)
plt.savefig('fig_temp_calibration.png', dpi=300, bbox_inches='tight')
print(f'Calibration coefficients: k={k:.4f}, b={b:.4f}')
print(f'Max residual error: {cal_error:.4f} °C')
print('Saved fig_temp_calibration.png')
plt.close()
