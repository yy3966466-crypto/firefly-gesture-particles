import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC']
plt.rcParams['axes.unicode_minus'] = False

# ---------------------------------------------------------------------------
# figure setup
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.5))
fig.patch.set_facecolor('white')
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.5)
ax.set_axis_off()

# ---------------------------------------------------------------------------
# colours (white / gray only)
# ---------------------------------------------------------------------------
CLR_CELL      = '#F5F5F5'
CLR_BYTE1_L   = '#EDEDED'   # left half  (bits 7-4)
CLR_BYTE1_R   = '#E0E0E0'   # right half (bits 3-0)
CLR_EDGE      = '#AAAAAA'
CLR_TEXT      = '#333333'
CLR_TEXT_SUB  = '#666666'
CLR_ARROW     = '#666666'
CLR_BG_BOTTOM = '#F5F5F5'

# ---------------------------------------------------------------------------
# layout constants
# ---------------------------------------------------------------------------
TITLE_Y   = 6.15

BYTE_W    = 2.8               # width of each byte box
BIT_W     = BYTE_W / 8        # width of one bit cell
BOX_H     = 1.2               # box height
BOX_Y_BTM = 3.8               # box bottom y

# three byte-box centres  (equally spaced)
cx = [2.4, 5.5, 8.6]
lx = [c - BYTE_W / 2 for c in cx]   # left edges

# ---------------------------------------------------------------------------
# title
# ---------------------------------------------------------------------------
ax.text(5.5, TITLE_Y, 'MIT-BIH 212格式: 3字节存2个12-bit采样',
        fontsize=17, fontweight='bold', ha='center', va='top', color=CLR_TEXT)

# ---------------------------------------------------------------------------
# labels above each byte box
# ---------------------------------------------------------------------------
for c, label in zip(cx, ['导联1低8位', '混合', '导联2低8位']):
    ax.text(c, BOX_Y_BTM + BOX_H + 0.20, label,
            fontsize=11, ha='center', va='bottom', color=CLR_TEXT)

# ---------------------------------------------------------------------------
# draw the three byte boxes (each with 8 bit cells)
# ---------------------------------------------------------------------------
for i, (c, l) in enumerate(zip(cx, lx)):
    for b in range(8):                     # b=0 → leftmost cell (bit 7)
        bit_x = l + b * BIT_W

        if i == 1:                         # Byte 1 — two halves
            face = CLR_BYTE1_L if b < 4 else CLR_BYTE1_R
        else:
            face = CLR_CELL

        cell = mpatches.FancyBboxPatch(
            (bit_x, BOX_Y_BTM), BIT_W, BOX_H,
            facecolor=face, edgecolor=CLR_EDGE, linewidth=0.6,
            boxstyle="round,pad=0.01",
        )
        ax.add_patch(cell)

        # bit number  (7 … 0 left → right)
        ax.text(bit_x + BIT_W / 2, BOX_Y_BTM + BOX_H / 2, str(7 - b),
                fontsize=8, ha='center', va='center', color=CLR_TEXT_SUB)

# ---------------------------------------------------------------------------
# vertical divider in Byte 1  (between bit 4 and bit 3)
# ---------------------------------------------------------------------------
div_x = lx[1] + 4 * BIT_W
ax.plot([div_x, div_x], [BOX_Y_BTM, BOX_Y_BTM + BOX_H],
        color='#777777', linewidth=1.6, solid_capstyle='round')


# ---------------------------------------------------------------------------
#  "字节0/1/2"  label below each box
# ---------------------------------------------------------------------------
for i, c in enumerate(cx):
    ax.text(c, BOX_Y_BTM - 0.15, f'字节{i}',
            fontsize=10, ha='center', va='top', color=CLR_TEXT_SUB)

# ---------------------------------------------------------------------------
# arrows from Byte 1 down to the two description texts
# ---------------------------------------------------------------------------
DESC_Y = 2.55                               # y of description text (centre)
DESC1_X = cx[0]                              # left description  (bit 0-3)
DESC2_X = cx[2]                              # right description (bit 4-7)

# Arrow origins: from the bottom of Byte 1, diverging straight to descriptions
arrow_L_start_x = cx[1] - BIT_W
arrow_R_start_x = cx[1] + BIT_W

# Left arrow   →  "bit 0-3 = 导联1高4位"   (arrow stops just above text)
ax.annotate(
    '', xy=(DESC1_X, DESC_Y + 0.28), xytext=(arrow_L_start_x, BOX_Y_BTM - 0.10),
    arrowprops=dict(arrowstyle='->', color=CLR_ARROW, lw=1.5),
)

# Right arrow  →  "bit 4-7 = 导联2高4位"
ax.annotate(
    '', xy=(DESC2_X, DESC_Y + 0.28), xytext=(arrow_R_start_x, BOX_Y_BTM - 0.10),
    arrowprops=dict(arrowstyle='->', color=CLR_ARROW, lw=1.5),
)

# description text (no background box — arrow tip stops beside text)
ax.text(DESC1_X, DESC_Y, 'bit 0-3 = 导联1高4位',
        fontsize=10.5, ha='center', va='center', color=CLR_TEXT)
ax.text(DESC2_X, DESC_Y, 'bit 4-7 = 导联2高4位',
        fontsize=10.5, ha='center', va='center', color=CLR_TEXT)


# ---------------------------------------------------------------------------
# bottom MATLAB extraction box  (width = full 3-byte span)
# ---------------------------------------------------------------------------
ADV_L  = lx[0]
ADV_R  = lx[2] + BYTE_W
ADV_W  = ADV_R - ADV_L
ADV_B  = 0.55
ADV_H  = 1.35

bottom_box = mpatches.FancyBboxPatch(
    (ADV_L, ADV_B), ADV_W, ADV_H,
    facecolor=CLR_BG_BOTTOM, edgecolor=CLR_EDGE, linewidth=1.0,
    boxstyle="round,pad=0.10",
)
ax.add_patch(bottom_box)

matlab_lines = (
    'sample1 = byte0 + bitand(byte1, 15) * 256;\n'
    'sample2 = byte2 + bitshift(bitand(byte1, 240), 4);\n'
    '有符号: 值>=2048则减去4096'
)
ax.text(5.5, ADV_B + ADV_H / 2, matlab_lines,
        fontsize=8.5, ha='center', va='center', color=CLR_TEXT_SUB,
        linespacing=1.5)

# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------
plt.savefig('d:/bishe/mit212_format.png', dpi=200, bbox_inches='tight')
plt.close()
print('OK → mit212_format.png')
