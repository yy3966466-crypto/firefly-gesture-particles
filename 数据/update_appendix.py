import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = Document('我的论文_v6_revised.docx')

def replace_appendix_code(paragraphs, start_idx, code_lines):
    """Replace code paragraphs starting at start_idx with actual code lines."""
    # Find how many consecutive code paragraphs exist (until next heading)
    end_idx = start_idx
    for i in range(start_idx, len(doc.paragraphs)):
        p = doc.paragraphs[i]
        text = p.text.strip()
        style_name = p.style.name if p.style else ''
        # Stop at next heading or empty para or new section
        if 'heading' in style_name.lower() and i > start_idx:
            break
        if text.startswith('附录') or text.startswith('图B.') or text.startswith('function') or text.startswith('%') or text == '':
            if i > start_idx:
                # Check if this is the next section header
                next_is_header = False
                for j in range(i, min(i+3, len(doc.paragraphs))):
                    s = doc.paragraphs[j].style.name if doc.paragraphs[j].style else ''
                    if 'heading' in s.lower():
                        next_is_header = True
                        break
                if next_is_header:
                    end_idx = i
                    break
        end_idx = i + 1

    # Remove old code paragraphs (keep the heading)
    paras_to_remove = []
    for i in range(start_idx, end_idx):
        style_name = doc.paragraphs[i].style.name if doc.paragraphs[i].style else ''
        if 'heading' not in style_name.lower():
            paras_to_remove.append(doc.paragraphs[i])

    for p in paras_to_remove:
        p._element.getparent().remove(p._element)

    # Insert new code paragraphs after the heading
    heading_para = doc.paragraphs[start_idx - 1]  # The heading is just before start_idx
    # Actually the heading is at start_idx - 1, but we need to find it
    # Find the heading paragraph element
    insert_after = doc.paragraphs[start_idx - 1]._element

    for line in code_lines:
        new_p = OxmlElement('w:p')
        new_r = OxmlElement('w:r')
        new_t = OxmlElement('w:t')
        new_t.text = line
        new_t.set(qn('xml:space'), 'preserve')
        new_r.append(new_t)
        new_p.append(new_r)
        insert_after.addnext(new_p)
        insert_after = new_p


# Read actual source files
with open('src/+bioalg/bandpassSignal.m', 'r', encoding='utf-8') as f:
    bp_lines = [l.rstrip() for l in f.readlines()]

with open('src/+bioalg/processEcg.m', 'r', encoding='utf-8') as f:
    ecg_lines = [l.rstrip() for l in f.readlines()]

with open('src/+bioalg/processRespiration.m', 'r', encoding='utf-8') as f:
    resp_lines = [l.rstrip() for l in f.readlines()]

# A.1 — bandpassSignal.m (replace P266-P270)
# Find the start of actual code after the heading
for i, line in enumerate(bp_lines):
    if line.startswith('function'):
        a1_code = bp_lines[i:]
        break

replace_appendix_code(doc.paragraphs, 266, a1_code)
print('A.1 updated: bandpassSignal.m')

# A.2 — processEcg.m (replace P271-P277)
for i, line in enumerate(ecg_lines):
    if line.startswith('function'):
        a2_code = ecg_lines[i:]
        break

replace_appendix_code(doc.paragraphs, 271, a2_code)
print('A.2 updated: processEcg.m')

# A.3 — processRespiration.m (replace P278-P287)
for i, line in enumerate(resp_lines):
    if line.startswith('function'):
        a3_code = resp_lines[i:]
        break

replace_appendix_code(doc.paragraphs, 278, a3_code)
print('A.3 updated: processRespiration.m')

# Save
doc.save('我的论文_v6_revised.docx')
print('\nDone → 我的论文_v6_revised.docx')
