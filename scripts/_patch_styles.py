import re

p = r'c:/Users/HEMANTH/Desktop/project-3/scripts/generate_submission_docs.py'
txt = open(p, encoding='utf-8').read()

for old, new in [
    ('DocTitle',    'AGDocTitle'),
    ('DocSubtitle', 'AGDocSubtitle'),
    ('SectionHead', 'AGSectionHead'),
    ('SubHead',     'AGSubHead'),
    ('Body',        'AGBody'),
    ('Bullet',      'AGBullet'),
    ('Code',        'AGCode'),
    ('TableHead',   'AGTableHead'),
    ('TableCell',   'AGTableCell'),
]:
    txt = txt.replace(f'S["{old}"]', f'S["{new}"]')

open(p, 'w', encoding='utf-8').write(txt)
print('Style references updated OK')
