#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate white-background, black-text professional diagrams for sections 2.5, 3.11, 4.3.
Strict rules: white background, black text, arrows never penetrate text boxes."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Rectangle
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = r'd:/bishe/diagrams'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── colour palette: white + greyscale only ──
WHITE  = '#FFFFFF'
BLACK  = '#000000'
DGRAY  = '#333333'
GRAY   = '#666666'
LGRAY  = '#999999'
BORDER = '#444444'
STRIPE = '#F5F5F5'  # subtle alternating row tint (still reads as white)


# ============================================================
# Diagram 1: System Data Flow (Section 2.5)
# 4-layer vertical architecture. Arrows on the RIGHT side,
# never crossing text boxes.
# ============================================================
def draw_data_flow():
    fig, ax = plt.subplots(1, 1, figsize=(13, 9))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 13)
    ax.axis('off')
    ax.set_facecolor(WHITE)
    fig.patch.set_facecolor(WHITE)

    ax.text(6.5, 12.3, '系统数据流总览', fontsize=20, fontweight='bold',
            ha='center', va='center', fontfamily='SimHei', color=BLACK)

    # ── Layer geometry ──
    layer_left  = 0.4
    layer_width = 10.8
    arrow_x     = 11.8   # arrows run down this x-position, outside boxes
    layer_h     = 2.3

    layers = [
        {
            'title': '数据采集层',
            'y': 9.2,
            'items': [
                'MIT-BIH ECG 数据库\n.dat / .hea / .atr 格式',
                'BIDMC 呼吸数据库\nCSV 格式',
                '串口体温采集\nType-C 红外，COM 口',
            ],
            'stripe': False,
        },
        {
            'title': '信号处理层',
            'y': 6.5,
            'items': [
                'ECG 处理流水线\n基线校正→FFT带通→\n差分阈值→R波检测→心率',
                '呼吸处理流水线\n基线去除→FFT带通→\nALE/LMS→峰值检测→呼吸率',
                '体温处理流水线\nFIR低通→零相位滤波\n→最小二乘校准→体温值',
            ],
            'stripe': True,
        },
        {
            'title': '应用功能层',
            'y': 3.8,
            'items': [
                '实时参数刷新\n阈值报警\nCV 节律分析',
                '心-呼相关性分析\n体温趋势监测\n异常事件记录',
                '会话保存(.mat+CSV)\n报警日志导出\n可视化报告',
            ],
            'stripe': False,
        },
        {
            'title': '人机交互层',
            'y': 1.1,
            'items': [
                'App Designer GUI\n实时波形显示\n数字参数面板',
                '报警提示灯\n运行日志窗口\n状态指示器',
                '数据回放\n图表导出\n参数配置',
            ],
            'stripe': True,
        },
    ]

    for layer in layers:
        y = layer['y']
        bg = STRIPE if layer['stripe'] else WHITE

        # Main layer box
        rect = FancyBboxPatch((layer_left, y), layer_width, layer_h,
                              boxstyle='round,pad=0.12',
                              facecolor=bg, edgecolor=BORDER, linewidth=1.8)
        ax.add_patch(rect)

        # Title — vertical on the left
        ax.text(0.9, y + layer_h / 2, layer['title'], fontsize=13,
                fontweight='bold', color=BLACK, va='center', ha='center',
                fontfamily='SimHei')

        # Vertical separator line after title
        ax.plot([1.85, 1.85], [y + 0.35, y + layer_h - 0.35],
                color=GRAY, linewidth=1.0, linestyle='-')

        # Three item columns
        n = len(layer['items'])
        item_w = 2.8
        gap = 0.3
        total_w = n * item_w + (n - 1) * gap
        start_x = 2.2 + (layer_width - 2.0 - total_w) / 2

        for ci, text in enumerate(layer['items']):
            ix = start_x + ci * (item_w + gap)
            item_rect = FancyBboxPatch((ix, y + 0.45), item_w, layer_h - 0.9,
                                      boxstyle='round,pad=0.08',
                                      facecolor=WHITE, edgecolor=LGRAY, linewidth=1.0)
            ax.add_patch(item_rect)
            ax.text(ix + item_w / 2, y + layer_h / 2, text, fontsize=8.5,
                    ha='center', va='center', fontfamily='SimHei', color=BLACK,
                    linespacing=1.35)

    # ── Arrows — on the RIGHT side only, between layers ──
    arrow_y_pairs = [(9.2 + layer_h, 9.2), (6.5 + layer_h, 6.5),
                     (3.8 + layer_h, 3.8)]
    for y_top, y_bot in arrow_y_pairs:
        mid = (y_top + y_bot) / 2
        # Thick arrow
        ax.annotate('', xy=(arrow_x, y_bot + 0.15), xytext=(arrow_x, y_top - 0.15),
                    arrowprops=dict(arrowstyle='->', color=BLACK, lw=2.5,
                                   connectionstyle='arc3,rad=0'))
        # "数据流" label next to arrow
        ax.text(arrow_x + 0.25, mid, '↓', fontsize=12, color=DGRAY,
                ha='center', va='center')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, '01_data_flow.png'), dpi=200,
                bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print('Generated: 01_data_flow.png')


# ============================================================
# Diagram 2: Folder Hierarchy & Call Relations (Section 3.11)
# Tree layout with orthogonal edges. All nodes white with black
# border. Edges route AROUND intermediate nodes.
# ============================================================
def draw_folder_hierarchy():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 14)
    ax.axis('off')
    ax.set_facecolor(WHITE)
    fig.patch.set_facecolor(WHITE)

    ax.text(7.0, 13.5, '项目文件夹层级关联与调用关系', fontsize=18,
            fontweight='bold', ha='center', va='center', fontfamily='SimHei',
            color=BLACK)

    # ── Node definitions (x, y, label, w, h, style) ──
    # style: 'dark' = black bg white text, 'light' = white bg black text
    #         'green' = outlined only
    nodes = {}

    def add_node(key, x, y, label, w, h, style='light'):
        nodes[key] = (x, y, label, w, h, style)

    # Level 0 — entry points (y ≈ 11.5)
    add_node('main',   2.0, 11.8, 'main.m\n(程序入口)',            1.6, 0.70, 'dark')
    add_node('smoke',  5.2, 11.8, 'smoke_test.m\n(链路验证)',      1.8, 0.70, 'green')
    add_node('tempui', 8.5, 11.8, 'temperature_sensor_ui.m\n(体温UI入口)', 2.4, 0.70, 'green')
    add_node('eval',  12.0, 11.8, 'evaluateEcgDetection.m\n(R波检测评估)', 2.2, 0.70, 'green')

    # Level 1 — core app (y ≈ 9.8)
    add_node('app',      2.0, 10.0, 'BioMonitorApp.m\n(主程序核心)',      2.2, 0.70, 'dark')
    add_node('tempapp',  8.5, 10.0, 'TemperatureSensorReaderApp\n(独立体温App)', 2.6, 0.70, 'light')

    # Level 2 — io / alg / source packages (y ≈ 8.0)
    add_node('plan',     1.5, 8.2, 'getRandomDatasetPlan\n(随机抽样)',    2.1, 0.65, 'light')
    add_node('loadprep', 5.2, 8.2, 'loadPreparedMonitoringData\n(数据加载总调度)', 2.7, 0.65, 'light')
    add_node('temp',    10.5, 8.2, 'TemperatureStream\n(体温数据源)',    2.0, 0.65, 'light')
    add_node('export',  10.5, 6.8, 'exportAnalysisReport\n(可视化导出)',  2.0, 0.65, 'light')

    # Level 3 — io sub-functions (y ≈ 6.2)
    add_node('ensure',   1.5, 6.5, 'ensurePublicDatasets\n(检查/下载公共库)', 2.3, 0.65, 'light')
    add_node('mitdb',    5.2, 6.5, 'loadMitdbRecord\n(ECG 记录解析)',    2.0, 0.65, 'light')
    add_node('bidmc',    5.2, 5.0, 'loadBidmcResp\n(呼吸数据加载)',      2.0, 0.65, 'light')

    # Level 4 — leaf functions (y ≈ 4.5)
    add_node('download', 1.5, 4.8, 'downloadPhysioNetFile\n(单文件下载)',  2.1, 0.65, 'light')
    add_node('parse',    1.5, 3.2, 'parseMitdbHeader\n(头文件解析)',      1.9, 0.65, 'light')

    # ECG algorithm chain (right side)
    add_node('ecgalg',  8.8, 6.5, 'processEcg\n(ECG 算法)',          1.7, 0.65, 'light')
    add_node('respalgo',8.8, 5.0, 'processResp\n(呼吸算法)',          1.7, 0.65, 'light')
    add_node('bandpass',8.8, 3.8, 'bandpassSignal\n(FFT 带通滤波)',   1.7, 0.60, 'light')
    add_node('select',  8.8, 2.5, 'selectPeaks\n(不应期选峰)',        1.7, 0.60, 'light')
    add_node('snr',    11.2, 2.5, 'estimateSnr\n(SNR 估计)',         1.5, 0.60, 'light')

    # ── Edges: (src, dst) pairs ──
    edges = [
        ('main', 'app'),
        ('app', 'plan'), ('app', 'loadprep'),
        ('loadprep', 'ensure'), ('loadprep', 'mitdb'), ('loadprep', 'bidmc'),
        ('loadprep', 'ecgalg'), ('loadprep', 'respalgo'),
        ('ensure', 'download'),
        ('mitdb', 'parse'),
        ('ecgalg', 'bandpass'), ('ecgalg', 'select'), ('ecgalg', 'snr'),
        ('respalgo', 'bandpass'), ('respalgo', 'select'), ('respalgo', 'snr'),
        ('tempui', 'tempapp'),
        ('app', 'temp'), ('app', 'export'),
    ]

    # Draw edges first (below nodes)
    for src, dst in edges:
        sx, sy = nodes[src][0], nodes[src][1]
        dx, dy = nodes[dst][0], nodes[dst][1]
        _, _, _, sw, sh, _ = nodes[src]
        _, _, _, dw, dh, _ = nodes[dst]

        # Route: exit bottom of src, enter top of dst
        y_start = sy - sh / 2
        y_end   = dy + dh / 2

        # Use orthogonal routing: go down from src, then horizontally, then down to dst
        if abs(sx - dx) < 0.3:
            # Direct vertical
            ax.plot([sx, dx], [y_start, y_end], color=GRAY, linewidth=1.2, zorder=1)
        else:
            # L-shaped route: vertical from src to midpoint, horizontal, vertical to dst
            mid_y = (y_start + y_end) / 2
            ax.plot([sx, sx, dx, dx], [y_start, mid_y, mid_y, y_end],
                    color=GRAY, linewidth=1.2, zorder=1)

        # Arrow head
        ax.annotate('', xy=(dx, y_end), xytext=(dx, y_end - 0.15),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5))

    # Draw nodes
    for key, (x, y, label, w, h, style) in nodes.items():
        if style == 'dark':
            fc, ec, tc = DGRAY, BLACK, WHITE
            lw = 1.5
        elif style == 'green':
            fc, ec, tc = WHITE, GRAY, DGRAY
            lw = 1.5
        else:
            fc, ec, tc = WHITE, BORDER, BLACK
            lw = 1.2

        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle='round,pad=0.08',
                              facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2)
        ax.add_patch(rect)
        fs = 6.8 if '\n' in label else 7.5
        ax.text(x, y, label, fontsize=fs, ha='center', va='center',
                color=tc, fontweight='bold', fontfamily='SimHei', zorder=3,
                linespacing=1.15)

    # ── Legend ──
    legend_y = 0.8
    for i, (lbl, fc, ec, tc) in enumerate([
        ('程序入口 / 核心', DGRAY, BLACK, WHITE),
        ('功能模块', WHITE, BORDER, BLACK),
        ('独立入口 / 脚本', WHITE, GRAY, DGRAY),
    ]):
        lx = 2.0 + i * 4.2
        rect = FancyBboxPatch((lx - 0.25, legend_y - 0.15), 0.5, 0.3,
                              boxstyle='round,pad=0.04',
                              facecolor=fc, edgecolor=ec, linewidth=1.2)
        ax.add_patch(rect)
        ax.text(lx + 0.45, legend_y, lbl, fontsize=8.5, va='center',
                fontfamily='SimHei', color=BLACK)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, '02_folder_hierarchy.png'), dpi=200,
                bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print('Generated: 02_folder_hierarchy.png')


# ============================================================
# Diagram 3: Subroutine Call Dependency Graph (Section 4.3)
# Three-tier layered boxes. Arrows on the SIDE, not through
# function boxes. Clean monochrome style.
# ============================================================
def draw_call_dependency():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 12)
    ax.axis('off')
    ax.set_facecolor(WHITE)
    fig.patch.set_facecolor(WHITE)

    ax.text(6.0, 11.3, '子程序互相调用依赖关系图', fontsize=18,
            fontweight='bold', ha='center', va='center', fontfamily='SimHei',
            color=BLACK)

    # ── Three tiers ──
    tier_w = 10.2
    tier_x = 0.6
    arrow_x = 11.4  # arrows go here, outside tier boxes

    tiers = [
        {
            'title': '一级（核心调度层）',
            'y': 8.2,
            'h': 2.4,
            'files': [
                'BioMonitorApp.m', 'processEcg.m',
                'processRespiration.m', 'processTemperature.m',
                'loadPreparedMonitoringData.m',
                'exportAnalysisReport.m', 'TemperatureStream.m',
            ],
            'stripe': False,
        },
        {
            'title': '二级（算法支撑层）',
            'y': 5.0,
            'h': 2.4,
            'files': [
                'bandpassSignal.m', 'estimateSnr.m', 'selectPeaks.m',
                'getRandomDatasetPlan.m', 'ensurePublicDatasets.m',
                'loadMitdbRecord.m', 'loadBidmcRespiration.m',
                'loadMitdbAnnotations.m',
            ],
            'stripe': True,
        },
        {
            'title': '三级（基础工具层）',
            'y': 1.8,
            'h': 2.4,
            'files': [
                'parseMitdbHeader.m', 'downloadPhysioNetFile.m',
            ],
            'stripe': False,
        },
    ]

    for tier in tiers:
        y = tier['y']
        h = tier['h']
        bg = STRIPE if tier['stripe'] else WHITE

        # Tier background
        rect = FancyBboxPatch((tier_x, y), tier_w, h,
                              boxstyle='round,pad=0.1',
                              facecolor=bg, edgecolor=BORDER, linewidth=1.8)
        ax.add_patch(rect)

        # Tier label on the left
        ax.text(1.0, y + h / 2, tier['title'], fontsize=12, fontweight='bold',
                color=BLACK, va='center', ha='center', fontfamily='SimHei',
                rotation=90)

        # Vertical separator
        ax.plot([1.6, 1.6], [y + 0.35, y + h - 0.35],
                color=GRAY, linewidth=1.0)

        # File boxes — flow in rows
        files = tier['files']
        box_w = 1.30
        box_h = 0.60
        gap_x = 0.12
        gap_y = 0.15
        max_per_row = 6
        n = len(files)
        n_rows = (n + max_per_row - 1) // max_per_row

        for fi, fname in enumerate(files):
            row = fi // max_per_row
            col = fi % max_per_row
            items_in_row = min(max_per_row, n - row * max_per_row)
            row_w = items_in_row * box_w + (items_in_row - 1) * gap_x
            start_x = 2.0 + (tier_w - 2.5 - row_w) / 2

            bx = start_x + col * (box_w + gap_x)
            by = y + h - 0.55 - row * (box_h + gap_y)

            file_rect = FancyBboxPatch((bx, by), box_w, box_h,
                                      boxstyle='round,pad=0.05',
                                      facecolor=WHITE, edgecolor=GRAY,
                                      linewidth=1.0)
            ax.add_patch(file_rect)

            fs = 6.3 if len(fname) > 22 else (6.8 if len(fname) > 16 else 7.5)
            ax.text(bx + box_w/2, by + box_h/2, fname, fontsize=fs,
                    ha='center', va='center', fontfamily='SimHei', color=BLACK,
                    fontweight='bold', linespacing=1.0)

    # ── Arrows on the RIGHT side between tiers ──
    arrow_pairs = [(8.2 + 2.4, 8.2), (5.0 + 2.4, 5.0)]
    for y_top, y_bot in arrow_pairs:
        ax.annotate('', xy=(arrow_x, y_bot + 0.2), xytext=(arrow_x, y_top - 0.2),
                    arrowprops=dict(arrowstyle='->', color=BLACK, lw=2.8))
        mid = (y_top + y_bot) / 2
        ax.text(arrow_x + 0.30, mid, '调用', fontsize=10, color=DGRAY,
                va='center', fontfamily='SimHei')

    # ── Legend for packages ──
    legend_y = 0.7
    for i, (lbl, lc) in enumerate([
        ('bioio.*  数据 IO 包', BORDER),
        ('bioalg.*  算法包', BORDER),
        ('bioout.*  输出包', BORDER),
        ('tempsrc.*  体温源', BORDER),
    ]):
        lx = 1.5 + i * 2.8
        ax.plot([lx, lx + 0.4], [legend_y, legend_y], color=lc, linewidth=2.5,
                solid_capstyle='round')
        ax.text(lx + 0.55, legend_y, lbl, fontsize=8.5, va='center',
                fontfamily='SimHei', color=BLACK)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, '03_call_dependency.png'), dpi=200,
                bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print('Generated: 03_call_dependency.png')


if __name__ == '__main__':
    draw_data_flow()
    draw_folder_hierarchy()
    draw_call_dependency()
    print('All diagrams regenerated — white background, black text, clean arrows.')
