import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7.0))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 11)
ax.set_ylim(0, 7.2)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours
# ---------------------------------------------------------------------------
CLR_BOX  = '#F5F5F5'
CLR_EDGE = '#BBBBBB'
CLR_TEXT = '#333333'
CLR_SUB  = '#666666'
CLR_ARROW = '#666666'

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
BOX_W = 2.4
BOX_H = 1.0

# column centres
col_x = [2.2, 5.5, 8.8]
# row y bottoms (3 rows)
row_y = [4.6, 3.0, 1.4]

# column headers
col_labels = ['数据源', '处理管线', '输出存储']
col_header_y = 5.95

# title
ax.text(5.5, 6.80, '系统数据流图',
        fontsize=18, fontweight='bold', ha='center', va='top', color=CLR_TEXT)

# column headers
for c, label in zip(col_x, col_labels):
    ax.text(c, col_header_y, label,
            fontsize=12, fontweight='bold', ha='center', va='bottom', color=CLR_TEXT)

# ---------------------------------------------------------------------------
# box contents  (left, middle, right) × 3 rows
# ---------------------------------------------------------------------------
left_titles  = ['PhysioNet服务器', 'GooDeTek串口', 'GUI实时刷新']
left_bodies  = ['从远程数据库\n读取心电/呼吸/体温数据',
                '接收串口实时\n采集的生理信号',
                '实时波形显示\n与用户交互操作']

mid_titles   = ['数据调度器', '信号处理引擎', '绘图引擎']
mid_bodies   = ['数据格式统一转换\n缓冲队列调度',
                '滤波去噪/特征提取\n逐拍标注计算',
                '信号波形渲染\n图表布局生成']

right_titles = ['.mat缓存', '会话保存', '论文图导出']
right_bodies = ['按记录ID索引\n存储为结构化.mat文件',
                '保存完整会话\n含信号+标注+参数',
                '导出矢量/位图\n供论文排版使用']

# row-connection labels (small decorative text between columns)
flow_hints = [
    ('数据请求', '缓存写入'),
    ('数据流', '保存触发'),
    ('渲染指令', '文件生成'),
]

for i in range(3):
    for j in range(3):
        cx = col_x[j]
        by = row_y[i]

        # pick title & body
        if j == 0:
            title = left_titles[i]
            body  = left_bodies[i]
        elif j == 1:
            title = mid_titles[i]
            body  = mid_bodies[i]
        else:
            title = right_titles[i]
            body  = right_bodies[i]

        # draw box
        left = cx - BOX_W / 2
        rect = mpatches.FancyBboxPatch(
            (left, by), BOX_W, BOX_H,
            facecolor=CLR_BOX, edgecolor=CLR_EDGE, linewidth=1.0,
            boxstyle="round,pad=0.10",
        )
        ax.add_patch(rect)

        # title inside box
        ax.text(cx, by + BOX_H - 0.15, title,
                fontsize=10, fontweight='bold', ha='center', va='top', color=CLR_TEXT)
        # body
        ax.text(cx, by + 0.15, body,
                fontsize=8, ha='center', va='bottom', color=CLR_SUB, linespacing=1.35)

    # ---- horizontal arrows for this row ----
    for j in range(2):
        x_from = col_x[j] + BOX_W / 2 + 0.04
        x_to   = col_x[j + 1] - BOX_W / 2 - 0.04
        y_cent = row_y[i] + BOX_H / 2

        ax.annotate(
            '', xy=(x_to, y_cent), xytext=(x_from, y_cent),
            arrowprops=dict(arrowstyle='->', color=CLR_ARROW, lw=1.3),
        )

        # small hint label above arrow
        ax.text((x_from + x_to) / 2, y_cent + 0.25, flow_hints[i][j],
                fontsize=6.5, ha='center', va='bottom', color='#999999',
                style='italic')

# ---------------------------------------------------------------------------
# decorative vertical guide lines connecting the three rows
# ---------------------------------------------------------------------------
for cx in col_x:
    top_y    = row_y[0] + BOX_H + 0.05
    bottom_y = row_y[2] - 0.05
    ax.plot([cx, cx], [bottom_y, top_y],
            color='#E0E0E0', linewidth=0.5, linestyle=':', zorder=0)

# ---------------------------------------------------------------------------
# total width marker at the very bottom
# ---------------------------------------------------------------------------
mark_y = 0.45
ax.plot([col_x[0] - BOX_W / 2, col_x[2] + BOX_W / 2],
        [mark_y, mark_y], color='#DDDDDD', linewidth=0.8)
ax.text(5.5, mark_y - 0.10, '— 三条并行数据管线 —',
        fontsize=8, ha='center', va='top', color='#AAAAAA')

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/flowchart_images_v4/04_data_flow.png',
            dpi=200, bbox_inches='tight')
plt.savefig('d:/bishe/system_data_flow.png',
            dpi=200, bbox_inches='tight')
plt.close()
print('OK → system_data_flow.png')
