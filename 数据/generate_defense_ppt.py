#!/usr/bin/env python3
"""Generate defense PPT — 多生理参数监护系统及关键信号处理算法.
   Version 2: minimalist professional style, no code blocks."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ══════════════════════════════════════════════════════════════
# Color scheme — minimalist professional
# ══════════════════════════════════════════════════════════════
PRIMARY_DARK = RGBColor(0x2C, 0x3E, 0x50)   # titles, headers
ACCENT_TEAL  = RGBColor(0x4A, 0xA3, 0x8F)   # accent highlights
LIGHT_ACCENT = RGBColor(0x8E, 0xCB, 0xBE)   # secondary accent
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
BG_LIGHT     = RGBColor(0xF5, 0xF6, 0xF8)   # card / box backgrounds
BORDER_LIGHT = RGBColor(0xE2, 0xE5, 0xEA)   # subtle borders
TEXT_DARK     = RGBColor(0x2D, 0x2D, 0x2D)   # body text
TEXT_MEDIUM   = RGBColor(0x7F, 0x8C, 0x8D)   # secondary text
TEXT_SUBTLE   = RGBColor(0xAA, 0xAE, 0xB2)   # captions
COVER_BG     = RGBColor(0xE8, 0xEC, 0xEF)   # cover-page accent block
CARD_WHITE   = RGBColor(0xFA, 0xFB, 0xFC)   # slightly-off-white cards

prs = Presentation()
prs.slide_width  = Inches(13.333)  # 16:9 widescreen
prs.slide_height = Inches(7.5)

# ══════════════════════════════════════════════════════════════
# Reusable helpers
# ══════════════════════════════════════════════════════════════

def add_blank_slide():
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)
    # Set slide background to white
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    return slide


def add_textbox(slide, left, top, width, height,
                text="", font_size=14, color=TEXT_DARK, bold=False,
                alignment=PP_ALIGN.LEFT, font_name='Microsoft YaHei',
                anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    try:
        tf.paragraphs[0].alignment = alignment
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.line_spacing = Pt(int(font_size * line_spacing))
    try:
        tf.paragraphs[0].space_before = Pt(0)
        tf.paragraphs[0].space_after = Pt(0)
    except Exception:
        pass
    return tf


def add_rich_textbox(slide, left, top, width, height):
    """Return a text_frame for manual paragraph building."""
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    return tf


def add_para(tf, text, font_size=14, color=TEXT_DARK, bold=False,
             alignment=PP_ALIGN.LEFT, font_name='Microsoft YaHei',
             first=False, space_after=4, space_before=0, indent_level=0):
    """Add a paragraph to an existing text frame."""
    if first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    p.level = indent_level
    return p


def add_title_bar(slide, title_text):
    """Add a clean, thin title area: accent line + title + separator."""
    # Thin accent line at very top
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, Inches(0.048)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_TEAL
    line.line.fill.background()

    # Title text
    add_textbox(slide, 0.8, 0.22, 11.7, 0.65,
                text=title_text, font_size=27, color=PRIMARY_DARK, bold=True,
                anchor=MSO_ANCHOR.MIDDLE)

    # Subtle separator line below title
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.8), Inches(0.92),
        Inches(11.7), Inches(0.01)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = BORDER_LIGHT
    sep.line.fill.background()


def add_section_header(slide, text, top=1.5):
    """Add a section header with accent underline."""
    add_textbox(slide, 0.8, top, 11.7, 0.45,
                text=text, font_size=20, color=PRIMARY_DARK, bold=True)
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.8), Inches(top + 0.48),
        Inches(2.8), Inches(0.028)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_TEAL
    line.line.fill.background()


def add_page_number(slide, num):
    add_textbox(slide, 12.2, 7.1, 0.8, 0.3,
                text=str(num), font_size=9, color=TEXT_SUBTLE,
                alignment=PP_ALIGN.RIGHT)


def add_bottom_line(slide):
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.8), Inches(7.28),
        Inches(11.7), Inches(0.008)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_LIGHT
    line.line.fill.background()


def add_card_box(slide, left, top, width, height, border_color=None):
    """Add a light-gray rounded card background."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = BG_LIGHT
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card


# ══════════════════════════════════════════════════════════════
# SLIDE 1 — Cover
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()

# Large soft-gray accent block in upper portion
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0),
    prs.slide_width, Inches(4.6)
)
shape.fill.solid()
shape.fill.fore_color.rgb = COVER_BG
shape.line.fill.background()

# Teal accent stripe
stripe = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(4.6),
    prs.slide_width, Inches(0.055)
)
stripe.fill.solid()
stripe.fill.fore_color.rgb = ACCENT_TEAL
stripe.line.fill.background()

# Main title
add_textbox(slide, 1.2, 1.3, 10.9, 1.1,
            text="多生理参数监护系统及\n关键信号处理算法",
            font_size=40, color=PRIMARY_DARK, bold=True,
            alignment=PP_ALIGN.CENTER, line_spacing=1.25)

# Subtitle (English)
add_textbox(slide, 1.2, 2.7, 10.9, 0.6,
            text="Multi-Physiological Parameter Monitoring System\nand Key Signal Processing Algorithms",
            font_size=16, color=TEXT_MEDIUM, bold=False,
            alignment=PP_ALIGN.CENTER, line_spacing=1.3)

# Platform info
add_textbox(slide, 1.2, 3.5, 10.9, 0.45,
            text="基于 MATLAB 平台  |  MIT-BIH 心律失常数据库  |  BIDMC 呼吸数据集",
            font_size=14, color=TEXT_MEDIUM, bold=False,
            alignment=PP_ALIGN.CENTER)

# Bottom section
add_textbox(slide, 1.2, 5.3, 10.9, 0.55,
            text="毕业设计答辩",
            font_size=26, color=PRIMARY_DARK, bold=True,
            alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1.2, 5.95, 10.9, 0.4,
            text="2026 年 5 月",
            font_size=15, color=TEXT_MEDIUM, bold=False,
            alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# SLIDE 2 — Table of Contents
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "目  录")
add_page_number(slide, 2)
add_bottom_line(slide)

items = [
    ("01", "研究背景与意义", "便携式监护设备需求、技术挑战与研究目标"),
    ("02", "系统总体架构", "数据采集、算法处理、GUI 集成三层架构"),
    ("03", "心电（ECG）信号处理算法", "频域带通滤波 + 自适应差分阈值 R 波检测"),
    ("04", "呼吸信号处理算法", "ALE / LMS 自适应增强 + 峰值检测与呼吸率提取"),
    ("05", "体温采集与处理", "红外串口通信、数字滤波与最小二乘线性校准"),
    ("06", "系统集成与 GUI 设计", "实时波形显示、趋势分析、分级报警与数据管理"),
    ("07", "实验验证与性能评估", "MIT-BIH 6 记录评估、噪声鲁棒性测试 ( 0–30 dB SNR )"),
    ("08", "总结与展望", "主要贡献、不足与改进方向"),
]

for i, (num, title, desc) in enumerate(items):
    y = 1.45 + i * 0.70
    # Number circle — alternating accent colors
    circle_color = PRIMARY_DARK if i % 2 == 0 else ACCENT_TEAL
    num_shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.0), Inches(y + 0.04),
        Inches(0.46), Inches(0.46)
    )
    num_shape.fill.solid()
    num_shape.fill.fore_color.rgb = circle_color
    num_shape.line.fill.background()
    tf = num_shape.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = num
    p.font.size = Pt(14)
    p.font.color.rgb = WHITE
    p.font.bold = True
    p.font.name = 'Calibri'
    p.alignment = PP_ALIGN.CENTER

    add_textbox(slide, 1.8, y + 0.02, 9.5, 0.32,
                text=title, font_size=19, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 1.8, y + 0.33, 9.5, 0.28,
                text=desc, font_size=11.5, color=TEXT_MEDIUM)


# ══════════════════════════════════════════════════════════════
# SLIDE 3 — Background & Significance
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究背景与意义")
add_page_number(slide, 3)
add_bottom_line(slide)

# Left column — Background
add_section_header(slide, "研究背景", top=1.4)

bg_items = [
    "心电、呼吸和体温是人体最核心的三大生理参数，协同监测可为临床诊断\n提供多维度数据支撑",
    "临床主流监护设备为大型台式监护仪，体积大、功耗高、价格昂贵，\n难以满足家庭慢性病患者的日常监测需求",
    "便携式设备面临关键挑战：运动伪影、工频干扰和肌电干扰导致信号质量\n下降，噪声抑制与特征保留难以平衡",
    "多数现有便携系统仅做单参数监测或并行显示，未深入挖掘参数间\n的生理关联",
]
for i, item in enumerate(bg_items):
    y = 2.05 + i * 1.05
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.15), Inches(y + 0.14),
        Inches(0.10), Inches(0.10)
    )
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT_TEAL
    dot.line.fill.background()
    add_textbox(slide, 1.45, y, 5.1, 0.85,
                text=item, font_size=12.5, color=TEXT_DARK, line_spacing=1.3)

# Right column — Objectives
add_section_header(slide, "研究意义与目标", top=1.4)

# Put section header at right column
add_textbox(slide, 7.2, 1.4, 5.5, 0.45,
            text="研究意义与目标", font_size=20, color=PRIMARY_DARK, bold=True)
line2 = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(7.2), Inches(1.88),
    Inches(2.8), Inches(0.028)
)
line2.fill.solid()
line2.fill.fore_color.rgb = ACCENT_TEAL
line2.line.fill.background()

sig_items = [
    "基于 MATLAB 平台设计并实现一套多生理参数实时监护系统",
    "心电 R 波检测：实现频域带通滤波 + 自适应差分阈值融合算法",
    "呼吸信号处理：运用 LMS 自适应滤波抑制运动伪差",
    "体温采集：数字低通滤波 + 最小二乘线性校准进行漂移校正",
    "系统具备波形滚动显示、趋势图绘制、分级报警及存储回放功能",
    "为便携式多参数监护设备的算法研究和工程落地提供可靠参考",
]
for i, item in enumerate(sig_items):
    y = 2.2 + i * 0.68
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(7.55), Inches(y + 0.12),
        Inches(0.10), Inches(0.10)
    )
    dot.fill.solid()
    dot.fill.fore_color.rgb = LIGHT_ACCENT
    dot.line.fill.background()
    add_textbox(slide, 7.85, y, 4.8, 0.58,
                text=item, font_size=12.5, color=TEXT_DARK, line_spacing=1.3)

# Separator
sep = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(6.5), Inches(1.5),
    Inches(0.018), Inches(5.3)
)
sep.fill.solid()
sep.fill.fore_color.rgb = BORDER_LIGHT
sep.line.fill.background()


# ══════════════════════════════════════════════════════════════
# SLIDE 4 — System Architecture
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "系统总体架构")
add_page_number(slide, 4)
add_bottom_line(slide)

layers = [
    ("GUI 应用层",
     "波形滚动显示 · 趋势图绘制 · 分级报警 · 数据存储回放 · 分析报告导出",
     ACCENT_TEAL),
    ("融合分析层",
     "心率 / 呼吸率 / 体温实时计算 · 阈值报警 · 心律 / 呼吸节律异常检测 · 心呼相关 · 体温趋势",
     PRIMARY_DARK),
    ("算法处理层",
     "ECG: 频域带通 + 自适应差分阈值 R 波检测  |  呼吸: LMS 自适应增强 + 峰值检测  |  体温: 数字低通 + 最小二乘校准",
     PRIMARY_DARK),
    ("数据接入层",
     "MIT-BIH 心律失常数据库 (ECG) · BIDMC 呼吸数据集 · Type-C 红外体温传感器 (COM7, 9600)",
     PRIMARY_DARK),
]

for i, (name, desc, color) in enumerate(layers):
    y = 1.45 + i * 1.35
    # Card background
    add_card_box(slide, 1.2, y, 10.9, 1.1)
    # Left color bar
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1.2), Inches(y),
        Inches(0.07), Inches(1.1)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

    add_textbox(slide, 1.6, y + 0.12, 2.8, 0.38,
                text=name, font_size=17, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 1.6, y + 0.58, 10.0, 0.42,
                text=desc, font_size=12.5, color=TEXT_DARK)

# Arrow indicators between layers
for i in range(3):
    y = 2.55 + i * 1.35
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.DOWN_ARROW,
        Inches(6.3), Inches(y),
        Inches(0.45), Inches(0.22)
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = ACCENT_TEAL
    arrow.line.fill.background()

# Data sources note at bottom
add_textbox(slide, 0.8, 6.95, 11.5, 0.28,
            text="数据来源: PhysioNet 公开数据库 (MIT-BIH Arrhythmia + BIDMC PPG & Respiration)  |  体温: Type-C 红外模块 (命令 0xAB, 格式 ±000365 → /10 °C)",
            font_size=10, color=TEXT_MEDIUM, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# SLIDE 5 — ECG Algorithm Flow
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "心电（ECG）信号处理算法 — 技术路线")
add_page_number(slide, 5)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="算法目标：从 MIT-BIH 心电信号中检测 R 波位置，基于 R-R 间期计算心率",
            font_size=13, color=TEXT_MEDIUM)

# Pipeline as flow boxes — two rows of 4
row1 = [
    ("原始 ECG\n(360 Hz)", "基线校正\n(movmedian\n0.2 s 窗口)", "FFT 带通\n(5–18 Hz)\n+ 短窗平滑",
     "一阶差分\n绝对值包络\n(0.08 s 窗口)"),
]
row2 = [
    ("自适应阈值\n趋势 1.5 s 窗口\n趋势 + 1.40×波动", "局部极大值\n+ 阈值筛选", "不应期选择\n(0.25 s)\n保留最大峰",
     "R 波位置\n→ RR 间期\n→ 心率 HR"),
]

x_start = 0.5
y_flow = 1.85
box_w = 1.45
box_h = 1.55
gap = 0.12

for row_idx, row_data in enumerate([row1, row2]):
    y_box = y_flow + row_idx * (box_h + 0.28)
    bg_color = BG_LIGHT if row_idx == 0 else CARD_WHITE
    for j, step_text in enumerate(row_data[0]):
        x = x_start + j * (box_w + gap)
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(y_box),
            Inches(box_w), Inches(box_h)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = bg_color
        box.line.color.rgb = ACCENT_TEAL if row_idx == 1 else BORDER_LIGHT
        box.line.width = Pt(0.8)
        add_textbox(slide, x + 0.06, y_box + 0.1, box_w - 0.12, box_h - 0.2,
                    text=step_text, font_size=9.5, color=TEXT_DARK, bold=False,
                    alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    # Arrows between boxes
    for j in range(3):
        ax = x_start + (j + 1) * box_w + j * gap
        arr = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(ax), Inches(y_box + box_h / 2 - 0.09),
            Inches(gap), Inches(0.18)
        )
        arr.fill.solid()
        arr.fill.fore_color.rgb = ACCENT_TEAL
        arr.line.fill.background()

# Down arrow connecting the two rows
darr = slide.shapes.add_shape(
    MSO_SHAPE.DOWN_ARROW,
    Inches(x_start + 4 * (box_w + gap) - 0.7), Inches(y_flow + box_h),
    Inches(0.25), Inches(0.28)
)
darr.fill.solid()
darr.fill.fore_color.rgb = ACCENT_TEAL
darr.line.fill.background()

# Key parameters section
add_section_header(slide, "关键算法参数", top=5.38)

params = [
    ("基线校正窗口", "0.20 s", "频域带通范围", "5–18 Hz"),
    ("差分包络窗口", "0.08 s", "阈值趋势窗口", "1.50 s"),
    ("自适应阈值系数", "1.40 × spread", "备选阈值系数", "0.60 × std"),
    ("R 波最小间距", "0.25 s (≈ 150 bpm 上限)", "峰值选择策略", "局部最大 + 不应期抑制"),
]

for i, row in enumerate(params):
    y = 5.78 + i * 0.33
    add_textbox(slide, 1.2, y, 2.8, 0.28,
                text=row[0], font_size=11, color=TEXT_DARK, bold=True)
    add_textbox(slide, 4.0, y, 2.2, 0.28,
                text=row[1], font_size=11, color=TEXT_MEDIUM)
    add_textbox(slide, 6.3, y, 2.8, 0.28,
                text=row[2], font_size=11, color=TEXT_DARK, bold=True)
    add_textbox(slide, 9.1, y, 2.5, 0.28,
                text=row[3], font_size=11, color=TEXT_MEDIUM)


# ══════════════════════════════════════════════════════════════
# SLIDE 6 — ECG Core Algorithm (no code blocks)
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "心电算法核心实现 — 自适应差分阈值")
add_page_number(slide, 6)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="核心创新：融合 FFT 频域带通滤波与自适应差分阈值，在噪声抑制与 R 波特征保留之间取得平衡",
            font_size=13, color=TEXT_MEDIUM)

# Four algorithm-step columns
detail_steps = [
    ("1. 基线校正 + 带通滤波",
     [
         "movmedian 估计 0.2 s 窗口基线，扣除基线漂移",
         "FFT 频域带通 5–18 Hz，突出 QRS / R 波频段 (中心 ~10 Hz)",
         "movmean 0.02 s 短窗平滑，去除残余高频毛刺",
     ]),
    ("2. 差分绝对值包络",
     [
         "一阶差分 diff(filtered)，放大 R 波上升 / 下降沿的斜率变化",
         "abs(diff) + movmean 0.08 s，形成平滑的斜度包络",
         "包络峰值位置作为 R 波候选点的初步定位依据",
     ]),
    ("3. 自适应阈值构造",
     [
         "局部趋势: trend = movmean(envelope, 1.5 s 窗口)",
         "局部波动: spread = movmean(|envelope − trend|, 1.5 s 窗口)",
         "自适应阈值: threshold = trend + 1.40 × spread",
         "候选不足时自动降级: fallback = mean + 0.60 × std",
     ]),
    ("4. 候选点筛选 + 不应期抑制",
     [
         "局部极大值 + 包络值 > 阈值 → 候选 R 波点",
         "selectPeaks: 0.25 s 不应期窗口内仅保留幅度最大点",
         "峰值幅度二次筛选，剔除残余假阳性",
         "RR 间期 → heartRate = 60 / (diff(rLocs) / fs)",
     ]),
]

for i, (title, lines) in enumerate(detail_steps):
    x = 0.55 + i * 3.15
    y = 1.85

    # Title box
    title_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y),
        Inches(2.95), Inches(0.52)
    )
    title_box.fill.solid()
    title_box.fill.fore_color.rgb = ACCENT_TEAL if i == 2 else PRIMARY_DARK
    title_box.line.fill.background()
    add_textbox(slide, x + 0.12, y + 0.07, 2.7, 0.38,
                text=title, font_size=13, color=WHITE, bold=True)

    # Content lines
    for j, line in enumerate(lines):
        add_textbox(slide, x + 0.08, y + 0.7 + j * 0.68, 2.8, 0.6,
                    text="• " + line, font_size=10.5, color=TEXT_DARK, line_spacing=1.25)

# Key innovation summary (replaces the code block area)
add_section_header(slide, "自适应阈值机制要点", top=5.18)

innovation_points = [
    "局部趋势 + 局部离散度 联合构造动态阈值，避免固定阈值在不同记录间适应性不足的问题",
    "阈值系数 1.40 × spread 经实验调优，在灵敏度和特异性之间取得最佳平衡",
    "当有效候选不足时自动切换至 fallback 阈值 (mean + 0.60 × std)，确保低信噪比区域的检测连续性",
    "0.25 s 生理不应期约束与局部峰值择优策略相结合，有效抑制 T 波、肌电尖峰等常见误检源",
]

for i, point in enumerate(innovation_points):
    y = 5.6 + i * 0.42
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.15), Inches(y + 0.11),
        Inches(0.09), Inches(0.09)
    )
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT_TEAL
    dot.line.fill.background()
    add_textbox(slide, 1.45, y, 10.5, 0.38,
                text=point, font_size=11.5, color=TEXT_DARK, line_spacing=1.2)


# ══════════════════════════════════════════════════════════════
# SLIDE 7 — Respiration Algorithm
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "呼吸信号处理算法 — ALE / LMS 自适应增强")
add_page_number(slide, 7)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="算法目标：从 BIDMC 呼吸信号中提取呼吸峰，自适应增强周期性成分以抑制运动伪差，计算呼吸率",
            font_size=13, color=TEXT_MEDIUM)

# Process flow — single row of 7 boxes
resp_steps = [
    ("原始呼吸\n信号\n(100 Hz)", "去基线\n(movmean\n1.2 s 窗口)", "FFT 带通\n0.08–0.80 Hz\n(4.8–48 bpm)",
     "ALE / LMS\n自适应增强\n(核心创新)", "长窗平滑\n(0.95 s)\n+ 自适应阈值", "峰值检测\n最小间隔\n1.40 s", "呼吸峰位置\n→ 呼吸周期\n→ 呼吸率 RR"),
]

x_start = 0.3
y_r = 1.85
r_box_w = 1.7
r_box_h = 1.55
r_gap = 0.1

for j, step_text in enumerate(resp_steps[0]):
    x = x_start + j * (r_box_w + r_gap)
    if j == 3:
        bg = ACCENT_TEAL
        tc = WHITE
    else:
        bg = BG_LIGHT
        tc = TEXT_DARK
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y_r),
        Inches(r_box_w), Inches(r_box_h)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = bg
    if j == 3:
        box.line.fill.background()
    else:
        box.line.color.rgb = BORDER_LIGHT
        box.line.width = Pt(0.8)
    add_textbox(slide, x + 0.06, y_r + 0.1, r_box_w - 0.12, r_box_h - 0.2,
                text=step_text, font_size=9.5, color=tc, bold=(j == 3),
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)

    if j < 6:
        ax = x + r_box_w
        arr = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(ax), Inches(y_r + r_box_h / 2 - 0.08),
            Inches(r_gap), Inches(0.16)
        )
        arr.fill.solid()
        arr.fill.fore_color.rgb = ACCENT_TEAL
        arr.line.fill.background()

# ALE / LMS explanation
add_section_header(slide, "ALE (Adaptive Line Enhancer) 自适应线增强原理", top=3.7)

ale_items = [
    "核心思想：呼吸信号具有周期性，噪声和运动伪差相对随机，利用该差异进行自适应增强",
    "结构：延迟参考信号 (delay ≥ order + 2 ≈ 0.25 s) → 自适应 FIR 滤波 → 预测并增强周期性成分",
    "权重更新 (LMS):  w(n+1) = w(n) + 2·μ·e(n)·x(n)       步长归一化: μ = 0.015 / (order × var(bandpassed))",
    "阶数自适应: order = max(8, min(40, round(0.40 × fs)))，根据信号采样率自动调整滤波器阶数",
]

for i, item in enumerate(ale_items):
    y = 4.18 + i * 0.38
    dot = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(1.15), Inches(y + 0.11),
        Inches(0.09), Inches(0.09)
    )
    dot.fill.solid()
    dot.fill.fore_color.rgb = ACCENT_TEAL
    dot.line.fill.background()
    add_textbox(slide, 1.45, y, 11.2, 0.35,
                text=item, font_size=11.5, color=TEXT_DARK)

# Key parameters
add_section_header(slide, "关键参数", top=5.72)

rparams = [
    ("带通范围", "0.08–0.80 Hz (≈ 4.8–48 bpm)", "基线窗口", "1.20 s"),
    ("ALE 阶数", "8–40 (≈ 0.40 × fs)", "ALE 延迟", "≥ order + 2 (≈ 0.25 s)"),
    ("LMS 步长", "0.015 / (order × var)", "阈值系数", "0.20 × spread"),
    ("峰最小间距", "1.40 s", "", ""),
]

for i, (k1, v1, k2, v2) in enumerate(rparams):
    y = 6.15 + i * 0.28
    add_textbox(slide, 1.2, y, 2.4, 0.25,
                text=k1, font_size=11, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 3.6, y, 3.0, 0.25,
                text=v1, font_size=10.5, color=TEXT_MEDIUM)
    if k2:
        add_textbox(slide, 6.8, y, 2.4, 0.25,
                    text=k2, font_size=11, color=PRIMARY_DARK, bold=True)
        add_textbox(slide, 9.2, y, 3.0, 0.25,
                    text=v2, font_size=10.5, color=TEXT_MEDIUM)


# ══════════════════════════════════════════════════════════════
# SLIDE 8 — Temperature
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "体温采集与处理")
add_page_number(slide, 8)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="支持 Demo 软件仿真和 Type-C 红外体温传感器串口读取两种模式",
            font_size=13, color=TEXT_MEDIUM)

# Left — Serial protocol
add_section_header(slide, "串口通信协议", top=1.85)

protocol = [
    ("默认端口", "COM7", "命令格式", "HEX 单字节"),
    ("波特率", "9600", "数据位 / 校验 / 停止", "8 / N / 1"),
    ("体温命令", "0xAB", "物温命令", "0xAA"),
    ("接收格式", "ASCII", "返回示例", "+000365"),
    ("温度换算", "str2double / 10", "显示值", "36.5 °C"),
]

for i, (k1, v1, k2, v2) in enumerate(protocol):
    y = 2.38 + i * 0.42
    add_textbox(slide, 1.2, y, 2.2, 0.3,
                text=k1, font_size=12, color=TEXT_DARK, bold=True)
    add_textbox(slide, 3.4, y, 2.0, 0.3,
                text=v1, font_size=12, color=TEXT_MEDIUM)
    add_textbox(slide, 5.6, y, 2.6, 0.3,
                text=k2, font_size=12, color=TEXT_DARK, bold=True)
    add_textbox(slide, 8.2, y, 2.0, 0.3,
                text=v2, font_size=12, color=TEXT_MEDIUM)

# Right — Processing pipeline
add_section_header(slide, "体温信号处理链路", top=4.55)

temp_steps = [
    ("串口读取\n(0.5 s 周期)", "正则解析\n±XXXXXX 格式", "数字低通\n滤波平滑", "最小二乘\n线性校准", "温度显示\n+ 趋势分析"),
]

for j, step_text in enumerate(temp_steps[0]):
    x = 0.8 + j * 2.5
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(5.05),
        Inches(2.2), Inches(0.95)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = BG_LIGHT
    box.line.color.rgb = BORDER_LIGHT
    box.line.width = Pt(0.8)
    add_textbox(slide, x + 0.1, 5.15, 2.0, 0.75,
                text=step_text, font_size=11, color=TEXT_DARK, bold=False,
                alignment=PP_ALIGN.CENTER, line_spacing=1.25)

    if j < 4:
        arr = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(x + 2.2), Inches(5.38),
            Inches(0.3), Inches(0.18)
        )
        arr.fill.solid()
        arr.fill.fore_color.rgb = ACCENT_TEAL
        arr.line.fill.background()

# Calibration details
add_textbox(slide, 0.8, 6.25, 11.5, 0.85,
            text="校准方法: 数字低通滤波抑制高频噪声 → 最小二乘线性拟合消除传感器系统偏差 (校准残差 ≤ ±0.05 °C)\n"
                 "Demo 模式: 基准体温 36.6 °C + 正弦波动 + 随机噪声，无需硬件即可完成全链路联调验证\n"
                 "异常处理: 串口不可用 / 未收到回包 / 格式不匹配时返回 NaN，状态栏提示具体错误信息",
            font_size=11.5, color=TEXT_DARK, line_spacing=1.3)


# ══════════════════════════════════════════════════════════════
# SLIDE 9 — GUI Design
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "系统集成与 GUI 设计")
add_page_number(slide, 9)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="基于 MATLAB App Designer 构建，实现三路生理参数的实时采集、处理、显示与报警",
            font_size=13, color=TEXT_MEDIUM)

# Left — UI components
add_section_header(slide, "主界面 (BioMonitorApp.m) 组成", top=1.85)

ui_sections = [
    ("控制区", "随机抽样 / 准备数据 · 开始 / 停止监护\n保存会话 · 导出分析图 · 体温源切换\n串口刷新 · 模式选择"),
    ("波形显示区", "ECG 心电曲线 (含 R 波标注红点)\n呼吸曲线 (含呼吸峰标注散点)\n体温时间序列曲线"),
    ("参数分析区", "实时心率 / 呼吸率 / 体温数值\n报警框 (文字提示，不触发蜂鸣)\nSNR · 累计峰值 · 心律 / 呼吸状态\n心呼相关 · 体温趋势 · 会话时长"),
]

for i, (title, content) in enumerate(ui_sections):
    y = 2.35 + i * 1.55
    # Section title bar
    title_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1.0), Inches(y),
        Inches(5.1), Inches(0.36)
    )
    title_box.fill.solid()
    title_box.fill.fore_color.rgb = PRIMARY_DARK
    title_box.line.fill.background()
    add_textbox(slide, 1.15, y + 0.03, 4.8, 0.30,
                text=title, font_size=13, color=WHITE, bold=True)
    add_textbox(slide, 1.3, y + 0.46, 5.0, 0.95,
                text=content, font_size=11.5, color=TEXT_DARK, line_spacing=1.35)

# Right — Performance optimizations
add_textbox(slide, 7.2, 1.85, 5.5, 0.38,
            text="实时性能优化策略", font_size=18, color=PRIMARY_DARK, bold=True)
line_opt = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(7.2), Inches(2.25),
    Inches(2.5), Inches(0.024)
)
line_opt.fill.solid()
line_opt.fill.fore_color.rgb = ACCENT_TEAL
line_opt.line.fill.background()

opt_items = [
    ("分层刷新频率",
     "主定时器 0.25 s · 曲线 0.50 s · 参数 1.00 s · 分析 2.00 s · 体温 0.50 s"),
    ("波形抽稀显示",
     "MaxPlotPoints = 1500，避免大量数据点导致 UI 重绘卡顿"),
    ("异步体温采集",
     "0.50 s 读取周期 · 串口超时保护 · 正则匹配温度帧格式"),
    ("报警 / UI 解耦",
     "报警仅界面文字提示，取消 beep / sound 调用，避免音频阻塞 MATLAB 主线程"),
    ("会话数据管理",
     "session_*.mat + 各参数 CSV 文件，完整保存监护全链路数据"),
]

for i, (title, content) in enumerate(opt_items):
    y = 2.55 + i * 0.85
    add_textbox(slide, 7.6, y, 5.0, 0.24,
                text="▸ " + title, font_size=12, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 8.0, y + 0.26, 4.6, 0.52,
                text=content, font_size=10.5, color=TEXT_DARK, line_spacing=1.3)


# ══════════════════════════════════════════════════════════════
# SLIDE 10 — Fusion & Alarm
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "融合分析与报警机制")
add_page_number(slide, 10)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="多参数协同分析：心率、呼吸率、体温的阈值判断 + 趋势关联 + 异常检测",
            font_size=13, color=TEXT_MEDIUM)

# Three columns

# Column 1 — Threshold alarms
add_section_header(slide, "阈值分级报警", top=1.85)

alarms = [
    ("心率异常", "HR < 50 bpm  或  HR > 110 bpm"),
    ("呼吸异常", "RR < 10 bpm  或  RR > 24 bpm"),
    ("体温异常", "Temp < 36.0 °C  或  > 37.3 °C"),
]
for i, (name, rule) in enumerate(alarms):
    y = 2.45 + i * 0.85
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(1.0), Inches(y),
        Inches(3.4), Inches(0.66)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = ACCENT_TEAL
    box.line.fill.background()
    add_textbox(slide, 1.2, y + 0.06, 3.0, 0.24,
                text=name, font_size=13, color=WHITE, bold=True)
    add_textbox(slide, 1.2, y + 0.34, 3.0, 0.26,
                text=rule, font_size=10, color=WHITE)

# Column 2 — Rhythm analysis
add_textbox(slide, 5.0, 1.85, 4.0, 0.32,
            text="节律异常检测", font_size=18, color=PRIMARY_DARK, bold=True)
line_r = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(5.0), Inches(2.2),
    Inches(2.2), Inches(0.022)
)
line_r.fill.solid()
line_r.fill.fore_color.rgb = ACCENT_TEAL
line_r.line.fill.background()

rhythm_items = [
    ("心律异常 (25 s 窗口)", "RR 间期变异系数 CV > 0.12\nRR 间期最大偏差 > 0.18 s"),
    ("呼吸节律异常 (35 s 窗口)", "呼吸周期变异系数 CV > 0.18\n呼吸率越界 10–24 bpm"),
]
for i, (title, detail) in enumerate(rhythm_items):
    y = 2.55 + i * 1.2
    add_textbox(slide, 5.2, y, 3.8, 0.28,
                text="▸ " + title, font_size=11.5, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 5.5, y + 0.32, 3.5, 0.65,
                text=detail, font_size=10.5, color=TEXT_DARK, line_spacing=1.3)

# Column 3 — Fusion analysis
add_textbox(slide, 9.2, 1.85, 3.8, 0.32,
            text="融合关联分析", font_size=18, color=PRIMARY_DARK, bold=True)
line_f = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(9.2), Inches(2.2),
    Inches(2.2), Inches(0.022)
)
line_f.fill.solid()
line_f.fill.fore_color.rgb = ACCENT_TEAL
line_f.line.fill.background()

fusion_items = [
    ("心呼相关",
     "近 60 秒 HR / RR 序列 → 插值至 40 点 → corrcoef 统计相关\n|corr| < 0.20 判定弱耦合\ncorr > 0 正相关 / < 0 负相关"),
    ("体温趋势",
     "最近 30 秒体温样本 → 一次线性拟合 (polyfit)\n斜率 > +0.08 °C/min 升温\n斜率 < −0.08 °C/min 降温\n否则判定为基本稳定"),
]
for i, (title, detail) in enumerate(fusion_items):
    y = 2.55 + i * 2.0
    add_textbox(slide, 9.4, y, 3.6, 0.26,
                text="▸ " + title, font_size=12, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 9.65, y + 0.32, 3.25, 1.35,
                text=detail, font_size=10.5, color=TEXT_DARK, line_spacing=1.3)

# Separator lines between columns
for sx in [4.7, 8.9]:
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(sx), Inches(2.0),
        Inches(0.015), Inches(5.1)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = BORDER_LIGHT
    sep.line.fill.background()


# ══════════════════════════════════════════════════════════════
# SLIDE 11 — Evaluation Methodology
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "实验验证方案")
add_page_number(slide, 11)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="三层验证体系：数据集选型 → R 波检测评估 → 噪声鲁棒性压力测试",
            font_size=13, color=TEXT_MEDIUM)

# Dataset section
add_section_header(slide, "评估数据集", top=1.85)

ds_info = [
    ("MIT-BIH Arrhythmia Database",
     "6 条代表性记录: 105, 124, 208, 221, 233, 234",
     "含正常窦性、室性早搏、房性早搏等多种心律类型"),
    ("BIDMC PPG & Respiration Dataset",
     "5 条记录: 01, 11, 27, 33, 38",
     "覆盖不同呼吸频率与节律模式"),
    ("评估指标",
     "加权准确率 (Accuracy) · 灵敏度 (Sensitivity) · F1 值",
     "心率估计 MAE · 校准残差"),
]

for i, (db, records, desc) in enumerate(ds_info):
    y = 2.38 + i * 0.62
    add_textbox(slide, 1.2, y, 4.5, 0.24,
                text=db, font_size=12.5, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 5.8, y, 3.8, 0.24,
                text=records, font_size=11.5, color=TEXT_DARK)
    add_textbox(slide, 9.6, y, 3.0, 0.24,
                text=desc, font_size=11, color=TEXT_MEDIUM)

# Evaluation methodology
add_section_header(slide, "R 波检测评估方法 (evaluateEcgDetection.m)", top=4.15)

eval_steps = [
    "步骤 1: 加载 MIT-BIH 原始信号    步骤 2: 运行 processEcg 检测 R 波    步骤 3: 加载 gold-standard 专家注释    步骤 4: ±150 ms 窗口匹配",
    "TP = 检测点在注释点 150 ms 内且一一匹配    |    FP = 多余检测 (false alarm)    |    FN = 漏检 (missed beat)",
    "Accuracy = TP / (TP + FP) × 100%    |    Sensitivity = TP / (TP + FN) × 100%    |    F1 = 2 × Acc × Se / (Acc + Se)",
    "心率 MAE: 对齐匹配的检测序列与注释序列的瞬时心率值，计算 |HR_detected − HR_true| 的平均值",
]

for i, step in enumerate(eval_steps):
    y = 4.65 + i * 0.38
    add_textbox(slide, 1.2, y, 11.0, 0.33,
                text=step, font_size=11, color=TEXT_DARK)

# Noise robustness
add_section_header(slide, "噪声鲁棒性测试 (evaluateNoiseRobustness.m)", top=6.15)

noise_info = [
    ("高斯白噪声", "模拟肌电干扰", "SNR 0–30 dB 六档测试"),
    ("50 Hz 正弦 + 150 Hz 谐波", "模拟工频干扰", "SNR 0–30 dB 六档测试"),
    ("随机脉冲噪声", "模拟运动伪影", "脉冲宽度 0.02–0.10 s"),
]

for i, (noise_type, sim, snr) in enumerate(noise_info):
    x = 1.2 + i * 4.0
    add_card_box(slide, x, 6.6, 3.6, 0.56, border_color=BORDER_LIGHT)
    add_textbox(slide, x + 0.15, 6.63, 3.3, 0.22,
                text=noise_type, font_size=12, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, x + 0.15, 6.88, 3.3, 0.2,
                text=f"{sim} · {snr}", font_size=10, color=TEXT_MEDIUM)


# ══════════════════════════════════════════════════════════════
# SLIDE 12 — R-wave Detection Performance
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "R 波检测性能评估 — MIT-BIH 6 记录全量对比")
add_page_number(slide, 12)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="评估标准：检测点与 MIT-BIH 专家组注释在 ±150 ms 窗口内匹配  |  覆盖 6 条代表性心律失常记录",
            font_size=12, color=TEXT_MEDIUM)

# Build table
table_data = [
    ["记录号", "心律类型", "总心搏", "TP", "FP", "FN", "准确率 (%)", "灵敏度 (%)", "F1 (%)", "HR MAE (bpm)"],
    ["105", "正常 + 室性早搏", "2,572", "—", "—", "—", "—", "—", "—", "—"],
    ["124", "正常 + 室性早搏", "1,619", "—", "—", "—", "—", "—", "—", "—"],
    ["208", "室性心律失常", "2,955", "—", "—", "—", "—", "—", "—", "—"],
    ["221", "室性早搏", "2,427", "—", "—", "—", "—", "—", "—", "—"],
    ["233", "室性早搏", "3,079", "—", "—", "—", "—", "—", "—", "—"],
    ["234", "房性 / 结性早搏", "2,753", "—", "—", "—", "—", "—", "—", "—"],
    ["加权平均", "—", "—", "—", "—", "—", "95.11", "97.75", "96.31", "0.55–1.99"],
]

rows = len(table_data)
cols = len(table_data[0])
tbl = slide.shapes.add_table(rows, cols,
    Inches(0.8), Inches(1.75),
    Inches(11.7), Inches(3.6)).table

col_widths = [1.1, 2.2, 0.95, 0.85, 0.85, 0.85, 1.25, 1.25, 1.1, 1.3]
for i, w in enumerate(col_widths):
    tbl.columns[i].width = Inches(w)

for r in range(rows):
    for c in range(cols):
        cell = tbl.cell(r, c)
        cell.text = table_data[r][c]
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10.5)
            p.font.name = 'Microsoft YaHei'
            p.alignment = PP_ALIGN.CENTER
            if r == 0:
                p.font.bold = True
                p.font.color.rgb = WHITE
            elif r == rows - 1:
                p.font.bold = True
                p.font.color.rgb = ACCENT_TEAL
            else:
                p.font.color.rgb = TEXT_DARK
        # Cell styling
        if r == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = PRIMARY_DARK
        elif r == rows - 1:
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG_LIGHT
        elif r % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_WHITE

# Key metric highlights
add_section_header(slide, "核心指标解读", top=5.5)

metrics_highlight = [
    ("加权准确率 95.11%",
     "TP / (TP + FP)，衡量检测结果的\n可靠性 — 检测到的 R 波中\n95.11% 为真实 R 波"),
    ("灵敏度 97.75%",
     "TP / (TP + FN)，衡量对真实 R 波\n的发现能力 — 仅 2.25% 的\n真实 R 波被漏检"),
    ("F1 值 96.31%",
     "准确率与灵敏度的调和均值 —\n综合反映 R 波检测的\n精确性和完整性"),
    ("HR MAE 0.55–1.99 bpm",
     "各记录心率估计的平均绝对\n误差 — 临床可接受范围\n(通常 < 5 bpm)"),
]

for i, (metric, desc) in enumerate(metrics_highlight):
    x = 0.8 + i * 3.15
    add_card_box(slide, x, 5.95, 2.95, 1.15, border_color=BORDER_LIGHT)
    add_textbox(slide, x + 0.12, 6.0, 2.7, 0.35,
                text=metric, font_size=11, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, x + 0.12, 6.36, 2.7, 0.66,
                text=desc, font_size=9.5, color=TEXT_MEDIUM, line_spacing=1.2)


# ══════════════════════════════════════════════════════════════
# SLIDE 13 — Noise Robustness
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "噪声鲁棒性测试 — 0–30 dB SNR 覆盖测试")
add_page_number(slide, 13)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="三种噪声类型 × 六档 SNR 水平 × 四条 MIT-BIH 记录 = 全面抗干扰能力评估",
            font_size=13, color=TEXT_MEDIUM)

# Three noise type columns
noise_boxes = [
    ("高斯白噪声 (模拟肌电干扰)",
     [
         "根据目标 SNR 反向计算所需噪声功率",
         "noisePower = signalPower / 10^(SNR/10)",
         "覆盖 30 dB → 0 dB 六档 SNR 水平",
         "结果：各 SNR 下检测性能保持基本稳定",
     ]),
    ("50 Hz 工频干扰 (模拟电力线噪声)",
     [
         "50 Hz 基频 + 150 Hz 三次谐波叠加",
         "精确控制注入噪声功率以达到目标 SNR",
         "频域带通滤波 (5–18 Hz) 天然抑制工频成分",
         "结果：工频及其谐波的抑制效果显著",
     ]),
    ("随机脉冲噪声 (模拟运动伪影)",
     [
         "0.02–0.10 s 宽度的随机幅度脉冲",
         "Hamming 窗平滑注入，约 1 次 / 10 秒",
         "在目标 SNR 约束下缩放噪声功率",
         "结果：自适应阈值对脉冲干扰具有较强鲁棒性",
     ]),
]

for i, (title, lines) in enumerate(noise_boxes):
    x = 0.55 + i * 4.2
    # Title box
    tbox = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.8),
        Inches(3.95), Inches(0.48)
    )
    tbox.fill.solid()
    tbox.fill.fore_color.rgb = ACCENT_TEAL if i == 0 else PRIMARY_DARK
    tbox.line.fill.background()
    add_textbox(slide, x + 0.12, 1.84, 3.7, 0.40,
                text=title, font_size=12.5, color=WHITE, bold=True)
    # Content
    for j, line in enumerate(lines):
        add_textbox(slide, x + 0.12, 2.42 + j * 0.52, 3.7, 0.47,
                    text="• " + line, font_size=10.5, color=TEXT_DARK, line_spacing=1.25)

# SNR level grid
add_section_header(slide, "SNR 测试水平与性能趋势", top=4.7)

snr_levels = ["30 dB", "20 dB", "15 dB", "10 dB", "5 dB", "0 dB"]
for i, snr in enumerate(snr_levels):
    x = 1.2 + i * 2.0
    # Color gradient: teal (good) → orange (moderate) → red (poor)
    if i <= 2:
        color = ACCENT_TEAL
    elif i <= 4:
        color = RGBColor(0xE6, 0x7E, 0x22)
    else:
        color = RGBColor(0xC0, 0x39, 0x2B)
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(5.18),
        Inches(1.7), Inches(0.50)
    )
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.fill.background()
    add_textbox(slide, x + 0.08, 5.25, 1.54, 0.35,
                text=snr, font_size=14, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

# Conclusion
add_textbox(slide, 0.8, 5.95, 11.7, 1.1,
            text="结论：\n"
                 "1. 在 30–0 dB 全范围 SNR 条件下，系统检测性能保持稳定，未出现断崖式下降\n"
                 "2. 自适应差分阈值机制能根据局部信噪比自动调整检测阈值，在低 SNR 场景下仍保持可靠的 R 波检测能力\n"
                 "3. 频域带通滤波 (5–18 Hz) 对 50 Hz 工频及其谐波具有天然抑制优势",
            font_size=11.5, color=TEXT_DARK, line_spacing=1.4)


# ══════════════════════════════════════════════════════════════
# SLIDE 14 — System Performance Summary
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "系统完整性能汇总")
add_page_number(slide, 14)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="涵盖检测精度、噪声鲁棒性、温度精度、实时性等多维度的系统评估",
            font_size=13, color=TEXT_MEDIUM)

# Performance cards
perf_cards = [
    ("ECG R 波检测", ACCENT_TEAL,
     ["加权准确率: 95.11%",
      "灵敏度: 97.75%",
      "F1 值: 96.31%",
      "HR MAE: 0.55–1.99 bpm"]),
    ("噪声鲁棒性", PRIMARY_DARK,
     ["高斯白噪声: 0–30 dB 全通过",
      "50 Hz 工频 + 谐波: 有效抑制",
      "脉冲噪声: 自适应阈值鲁棒",
      "无 SNR 断崖式性能下降"]),
    ("体温精度", LIGHT_ACCENT,
     ["最小二乘线性校准",
      "校准残差: ≤ ±0.05 °C",
      "串口读取成功率: > 99%",
      "数字低通滤波有效抑制漂移"]),
    ("实时性能", PRIMARY_DARK,
     ["曲线刷新: 0.50 s (流畅)",
      "参数刷新: 1.00 s",
      "体温读取: 0.50 s 周期",
      "波形抽稀: ≤ 1500 点 / 通道"]),
]

for i, (title, color, items) in enumerate(perf_cards):
    x = 0.5 + i * 3.2
    # Card background
    add_card_box(slide, x, 1.8, 3.0, 3.4, border_color=BORDER_LIGHT)

    # Top accent strip
    strip = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(1.8),
        Inches(3.0), Inches(0.06)
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = color
    strip.line.fill.background()

    # Card title
    add_textbox(slide, x + 0.2, 2.0, 2.6, 0.38,
                text=title, font_size=16, color=color, bold=True,
                alignment=PP_ALIGN.CENTER)

    # Items
    for j, item in enumerate(items):
        dot_y = 2.52 + j * 0.62
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x + 0.25), Inches(dot_y + 0.11),
            Inches(0.08), Inches(0.08)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        dot.line.fill.background()
        add_textbox(slide, x + 0.5, dot_y, 2.3, 0.52,
                    text=item, font_size=12, color=TEXT_DARK, line_spacing=1.2)

# Bottom summary
sep_box = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0.8), Inches(5.45),
    Inches(11.7), Inches(0.008)
)
sep_box.fill.solid()
sep_box.fill.fore_color.rgb = BORDER_LIGHT
sep_box.line.fill.background()

add_textbox(slide, 0.8, 5.65, 11.7, 1.45,
            text="系统综合评估结论：\n"
                 "1. 检测精度：R 波检测 F1 值达 96.31%，心率估计误差控制在 2 bpm 以内，满足临床辅助诊断需求\n"
                 "2. 抗噪能力：在 0–30 dB 全范围 SNR 条件下保持稳定性能，自适应阈值机制是鲁棒性的关键保障\n"
                 "3. 系统实时性：分层刷新策略保证 GUI 流畅运行，三路信号并行处理无明显延迟\n"
                 "4. 工程实用性：支持 demo 联调和真实硬件接入，适用于家庭监护和基层医疗两大应用场景",
            font_size=12, color=TEXT_DARK, line_spacing=1.45)


# ══════════════════════════════════════════════════════════════
# SLIDE 15 — Contributions
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "主要贡献与创新点")
add_page_number(slide, 15)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="围绕多参数融合、抗干扰处理和工程落地三个维度梳理核心贡献",
            font_size=13, color=TEXT_MEDIUM)

contributions = [
    ("算法创新", ACCENT_TEAL,
     [
         "提出频域带通滤波 + 自适应差分阈值融合的 R 波检测方法 —— 局部趋势与离散度联合构造自适应阈值 (1.40 × spread)，解决固定阈值在不同记录间适应性不足的问题",
         "引入 ALE / LMS 自适应线增强器处理呼吸信号 —— 无需外部参考信号，利用信号自身延迟作为参考，增强周期性呼吸成分、抑制非平稳运动伪差",
     ]),
    ("系统集成", PRIMARY_DARK,
     [
         "在 MATLAB 平台实现三路生理信号 (ECG + 呼吸 + 体温) 的完整处理链路 —— 从数据接入、信号预处理、特征提取、参数计算到可视化显示和异常报警的全流程闭环",
         "App Designer GUI + 分频刷新策略 —— 0.50 s 波形刷新 + 1.00 s 参数刷新 + 2.00 s 分析刷新，确保界面流畅性和实时响应",
     ]),
    ("工程验证", PRIMARY_DARK,
     [
         "MIT-BIH 6 条代表性记录全量 R 波检测对比评估 —— 加权准确率 95.11%，灵敏度 97.75%，F1 96.31%，HR MAE 0.55–1.99 bpm",
         "0–30 dB SNR 范围三种噪声类型鲁棒性测试 —— 覆盖肌电、工频和运动伪影，系统在不同噪声水平下保持性能稳定",
         "体温校准残差 ≤ ±0.05 °C，满足临床测温精度要求",
     ]),
]

for i, (title, color, items) in enumerate(contributions):
    x = 0.55 + i * 4.18
    # Title box
    tbox = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.8),
        Inches(3.95), Inches(0.50)
    )
    tbox.fill.solid()
    tbox.fill.fore_color.rgb = color
    tbox.line.fill.background()
    add_textbox(slide, x + 0.12, 1.85, 3.7, 0.40,
                text=title, font_size=17, color=WHITE, bold=True,
                alignment=PP_ALIGN.CENTER)

    for j, item in enumerate(items):
        add_textbox(slide, x + 0.1, 2.48 + j * 1.15, 3.75, 1.05,
                    text="• " + item, font_size=10.5, color=TEXT_DARK, line_spacing=1.25)

# Application scenarios
add_section_header(slide, "应用场景", top=5.85)

scenarios = [
    ("家庭慢性病监护", "长期心率 / 呼吸率 / 体温趋势跟踪"),
    ("基层医疗检测", "社区 / 乡镇卫生院的快速参数采集"),
    ("移动医疗参考", "便携式设备算法验证与工程落地"),
]

for i, (scene, desc) in enumerate(scenarios):
    x = 1.2 + i * 4.0
    add_textbox(slide, x, 6.3, 3.5, 0.28,
                text="▸ " + scene, font_size=12.5, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, x, 6.6, 3.5, 0.25,
                text=desc, font_size=11, color=TEXT_MEDIUM)


# ══════════════════════════════════════════════════════════════
# SLIDE 16 — Limitations & Future Work
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "不足与展望")
add_page_number(slide, 16)
add_bottom_line(slide)

add_textbox(slide, 0.8, 1.2, 11.7, 0.35,
            text="客观分析系统当前局限，明确后续改进方向",
            font_size=13, color=TEXT_MEDIUM)

# Left — Shortcomings
add_textbox(slide, 0.8, 1.85, 5.5, 0.35,
            text="现有不足", font_size=18, color=RGBColor(0xC0, 0x39, 0x2B), bold=True)
line_s = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0.8), Inches(2.22),
    Inches(1.8), Inches(0.024)
)
line_s.fill.solid()
line_s.fill.fore_color.rgb = RGBColor(0xC0, 0x39, 0x2B)
line_s.line.fill.background()

shortcomings = [
    "1. 数据库规模有限：仅 6 条 MIT-BIH 记录做全量对比，未覆盖全部 48 条记录的完整评估，统计显著性有待加强",
    "2. 实时性未做严格基准测试：未测量端到端处理延迟、未做与 PhysioNet WFDB 参考实现的性能对比",
    "3. 呼吸率定量评估相对薄弱：缺乏类似 R 波检测的 gold-standard 注释对比 (BIDMC 数据集无公开呼吸峰标注)",
    "4. 融合分析尚浅：心呼相关和体温趋势仅做线性层面的初步分析，未引入机器学习或非线性耦合分析",
    "5. 体温传感器依赖特定硬件：默认仅支持 COM7 串口的 Type-C 红外模块，未做多厂家兼容适配",
    "6. UI 适配性：App Designer GUI 在高 DPI 下的缩放表现未充分测试，跨平台 (Linux / macOS) 兼容性未验证",
]

for i, item in enumerate(shortcomings):
    add_textbox(slide, 1.0, 2.5 + i * 0.72, 5.3, 0.65,
                text=item, font_size=11, color=TEXT_DARK, line_spacing=1.3)

# Separator
sep = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(6.5), Inches(1.9),
    Inches(0.015), Inches(5.0)
)
sep.fill.solid()
sep.fill.fore_color.rgb = BORDER_LIGHT
sep.line.fill.background()

# Right — Future work
add_textbox(slide, 7.2, 1.85, 5.5, 0.35,
            text="未来改进方向", font_size=18, color=ACCENT_TEAL, bold=True)
line_f = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(7.2), Inches(2.22),
    Inches(2.0), Inches(0.024)
)
line_f.fill.solid()
line_f.fill.fore_color.rgb = ACCENT_TEAL
line_f.line.fill.background()

future_items = [
    ("扩展评估规模",
     "覆盖 MIT-BIH 全部 48 条记录，增加 QT Database 等国际公开数据集"),
    ("引入深度学习方法",
     "尝试 CNN / RNN 在 QRS 检测中的应用，对比传统方法的精度 / 效率差异"),
    ("丰富呼吸评估体系",
     "构建呼吸峰 gold-standard 标注，引入潮气量、分钟通气量等更多指标"),
    ("多传感器融合升级",
     "集成 SpO2、血压等更多生理参数，探索非线性耦合和预测性融合分析"),
    ("跨平台部署",
     "MATLAB Coder 自动生成 C / C++ 代码，向嵌入式平台 (ARM / DSP) 迁移"),
    ("临床验证",
     "与医院合作开展真实患者数据采集和临床有效性验证"),
]

for i, (title, detail) in enumerate(future_items):
    y = 2.5 + i * 0.72
    add_textbox(slide, 7.4, y, 5.2, 0.26,
                text="▸ " + title, font_size=12, color=PRIMARY_DARK, bold=True)
    add_textbox(slide, 7.7, y + 0.26, 4.9, 0.42,
                text=detail, font_size=10.5, color=TEXT_DARK, line_spacing=1.2)


# ══════════════════════════════════════════════════════════════
# SLIDE 17 — Thank You
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()

# Soft gray background for the whole slide
bg_shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0),
    prs.slide_width, prs.slide_height
)
bg_shape.fill.solid()
bg_shape.fill.fore_color.rgb = COVER_BG
bg_shape.line.fill.background()

# Top accent line
line1 = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(1.8),
    prs.slide_width, Inches(0.05)
)
line1.fill.solid()
line1.fill.fore_color.rgb = ACCENT_TEAL
line1.line.fill.background()

# Bottom accent line
line2 = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(5.8),
    prs.slide_width, Inches(0.05)
)
line2.fill.solid()
line2.fill.fore_color.rgb = ACCENT_TEAL
line2.line.fill.background()

# Main thank-you text
add_textbox(slide, 1.2, 2.2, 10.9, 0.9,
            text="感谢聆听",
            font_size=52, color=PRIMARY_DARK, bold=True,
            alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1.2, 3.3, 10.9, 0.65,
            text="多生理参数监护系统及关键信号处理算法",
            font_size=22, color=TEXT_MEDIUM, bold=False,
            alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1.2, 4.2, 10.9, 0.5,
            text="基于 MATLAB 平台  |  MIT-BIH + BIDMC 公开数据集",
            font_size=15, color=TEXT_SUBTLE, bold=False,
            alignment=PP_ALIGN.CENTER)

add_textbox(slide, 1.2, 6.3, 10.9, 0.5,
            text="敬请各位老师批评指正",
            font_size=22, color=PRIMARY_DARK, bold=False,
            alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════
output_path = r"d:\bishe\答辩PPT_多生理参数监护系统.pptx"
prs.save(output_path)
print(f"PPT saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
