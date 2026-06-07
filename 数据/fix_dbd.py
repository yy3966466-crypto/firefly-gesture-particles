"""Fix the 'dB dB' duplication in para 212."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document('d:/bishe/我的论文.docx')
p = doc.paragraphs[212]
for run in p.runs:
    if '约7.3 dB dB' in run.text:
        run.text = run.text.replace('约7.3 dB dB', '约7.3 dB')
        print(f'Fixed: "{run.text[:50]}"')
doc.save('d:/bishe/我的论文.docx')
print('Saved.')
