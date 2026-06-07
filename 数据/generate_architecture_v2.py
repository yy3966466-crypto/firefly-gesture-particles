import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 11

fig, ax = plt.subplots(figsize=(6, 7.5))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 6)
ax.set_ylim(0, 7.0)
ax.set_axis_off()

BOX_W = 4.4
BOX_H = 1.05
CX = 3.0

layers = [
    {'title': '人机交互层', 'y': 5.85,
     'items': ['MATLAB GUI 界面 / 实时波形显示', '数字体温显示 / 用户控制面板']},
    {'title': '应用功能层',  'y': 4.30,
     'items': ['数据存储（.mat 导出）/ 历史回放', '异常报警（声光+日志）/ TTS 语音']},
    {'title': '信号处理层',  'y': 2.75,
     'items': ['FIR 带通滤波 / 差分阈值 R 波检测', 'LMS 自适应呼吸增强 / 体温校准']},
    {'title': '数据采集层',  'y': 1.20,
     'items': ['MIT-BIH 心电数据库 / BIDMC 呼吸库', 'NTC 热敏电阻串口（9600）/ USB 驱动']},
]

for layer in layers:
    cy = layer['y']
    left = CX - BOX_W / 2

    rect = mpatches.FancyBboxPatch(
        (left, cy - BOX_H / 2), BOX_W, BOX_H,
        facecolor='white', edgecolor='black', linewidth=1.0,
        boxstyle="round,pad=0.05",
        zorder=1
    )
    ax.add_patch(rect)

    # Title at top of box
    ax.text(left + 0.22, cy + BOX_H / 2 - 0.16, layer['title'],
            fontsize=12, fontweight='bold',
            ha='left', va='top', color='black', zorder=3)

    # Items centered below title
    text = '\n'.join(layer['items'])
    ax.text(CX, cy - 0.08, text,
            fontsize=11, fontweight='bold', ha='center', va='top', color='black',
            linespacing=1.7, zorder=3)

# Arrows — clearly visible with ~0.65 unit gap between boxes
for i in range(len(layers) - 1):
    y_from = layers[i]['y'] - BOX_H / 2
    y_to = layers[i + 1]['y'] + BOX_H / 2
    ax.annotate('', xy=(CX, y_to + 0.08), xytext=(CX, y_from - 0.08),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.2),
                zorder=0)

plt.tight_layout()
plt.savefig('d:/bishe/fig_architecture_v2.png', dpi=2400, bbox_inches='tight')
plt.savefig('d:/bishe/数据/fig_architecture_v2.png', dpi=2400, bbox_inches='tight')
print('Saved fig_architecture_v2.png')
plt.close()
