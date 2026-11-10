"""Read-only package checks for this presentation revision."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(root/'deliverables/SmartCampus-progress-12min.pptx') as deck:
    slides=sorted((n for n in deck.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda n:int(re.search(r'(\d+)\.xml',n).group(1)))
    assert len(slides)==13
    text=[' '.join(ET.fromstring(deck.read(n)).itertext()) for n in slides]
    assert 'System Analyst and Document Pre-review Lead' in text[9]
    assert 'Zheyuan Huai' in text[9] and 'Zheyuan Huai' in text[10]
    assert 'System Requirements and Prototype Scope' in text[9]
    assert 'Intelligent Document Pre-review' in text[10]
    assert all('Live Demonstration' not in s for s in text)
    assert len([n for n in deck.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)])==13
timing=json.loads((root/'.build/progress-12min/timing-check.json').read_text(encoding='utf-8'))
assert sum(s['seconds'] for s in timing)==720
assert all(timing[i]['seconds']+timing[i+1]['seconds']==120 for i in range(1,13,2))
notes=(root/'deliverables/SPEAKER_NOTES_12MIN.md').read_text(encoding='utf-8')
sections=re.split(r'^## ',notes,flags=re.M)[2:]
words=[len(s.split('\n',1)[1].split()) for s in sections]
for i in range(0,12,2):
    print(f'Member {i//2+1}: {words[i]+words[i+1]} words across two slides, 120-second rehearsal target')
original=root.parent/'SmartCampus-delivery.zip'
with zipfile.ZipFile(original) as old:
    checked=0
    for file in [*root.glob('app/**/*.py'),*root.glob('static/**/*')]:
        if not file.is_file():continue
        entry='smartcampus/'+file.relative_to(root).as_posix()
        assert hashlib.sha256(old.read(entry)).digest()==hashlib.sha256(file.read_bytes()).digest(), f'Application file changed: {entry}'
        checked+=1
print(f'PASS: 13 slides and notes, 720 seconds, correct Huai section, and {checked} application files unchanged from the original delivery archive.')
