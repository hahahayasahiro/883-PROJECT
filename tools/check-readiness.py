"""Read-only repository, secret and progress-package checks. Never prints secrets."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', help='Optional local JSON report path')
args = parser.parse_args()
failures, warnings = [], []


def check(condition, message):
    if not condition:
        failures.append(message)


result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                        cwd=ROOT, capture_output=True, check=True)
names = sorted(set(result.stdout.decode('utf-8').split('\0')) - {''})
secret_patterns = [rb'sk-[A-Za-z0-9_-]{20,}', rb'gh[pousr]_[A-Za-z0-9]{30,}',
                   rb'github_pat_[A-Za-z0-9_]{30,}', rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
private_key = b''
if (ROOT / '.env').exists():
    for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('DEEPSEEK_API_KEY='):
            private_key = line.split('=', 1)[1].strip().strip('\"\'').encode()


def scan(data, label, depth=0):
    if any(re.search(pattern, data) for pattern in secret_patterns) or (private_key and private_key in data):
        failures.append('Possible private credential in ' + label)
    if depth < 2 and data.startswith(b'PK\x03\x04'):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                check(archive.testzip() is None, 'Corrupt archive: ' + label)
                for entry in archive.infolist():
                    if entry.file_size <= 30 * 1024 * 1024 and not entry.is_dir():
                        scan(archive.read(entry), label + ':' + entry.filename, depth + 1)
        except zipfile.BadZipFile:
            failures.append('Unreadable archive: ' + label)


total_bytes = 0
for name in names:
    file = ROOT / name
    if not file.is_file():
        failures.append('Missing repository candidate: ' + name)
        continue
    parts = Path(name).parts
    check(not any(p in {'.venv', '.build', '.pytest_cache', '__pycache__', 'node_modules', 'data'} for p in parts),
          'Local state included: ' + name)
    check(not (file.name.startswith('.env') and file.name != '.env.example'), 'Private environment file: ' + name)
    check(not re.search(r'\.(sqlite\w*|db|bak|backup|pem|key|p12|pfx)$', name, re.I), 'Private file type: ' + name)
    size = file.stat().st_size
    total_bytes += size
    check(size < 95 * 1024 * 1024, 'File is too large for normal Git upload: ' + name)
    if size > 10 * 1024 * 1024:
        warnings.append('Consider a Release asset for large media: ' + name)
    scan(file.read_bytes(), name)

required = ['README.md', 'START_HERE.md', 'GITHUB_UPLOAD.md', 'CONTRIBUTING.md',
            '.env.example', '.gitignore', '.gitattributes', 'requirements.txt', 'requirements-lock.txt',
            'setup.ps1', 'start.cmd', 'manage.py', '.github/workflows/checks.yml',
            'deliverables/README.md', 'deliverables/COMPLETENESS_REVIEW.md',
            'deliverables/SPEAKER_NOTES_ENHANCED.md', 'deliverables/ENHANCED_GUIDE.md',
            'deliverables/ENHANCED_TEST_REPORT.md', 'deliverables/REQUIREMENTS_AND_SCOPE_ENHANCED.md',
            'deliverables/SmartCampus-enhanced-presentation.pptx',
            'deliverables/SmartCampus_中英文对照使用说明书.docx',
            'deliverables/SmartCampus-enhanced-demo.webm',
            'docs/proposals/CSIT883_SmartCampus_Project_Proposal.docx',
            'docs/proposals/CSIT883_SmartCampus_项目提案_中文版_FINAL.docx']
for name in required:
    check(name in names, 'Required deliverable not in repository candidates: ' + name)
modules = ['assistant', 'learning', 'facilities', 'maintenance', 'reviews', 'applications']
for module in modules:
    for name in [f'app/routers/{module}.py', f'static/modules/{module}.js']:
        check(name in names, 'Module file missing: ' + name)

ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
deck = ROOT / 'deliverables/SmartCampus-enhanced-presentation.pptx'
with zipfile.ZipFile(deck) as archive:
    slides = sorted((n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)),
                    key=lambda n: int(re.search(r'(\d+)\.xml', n).group(1)))
    texts = [' '.join(ET.fromstring(archive.read(n)).findall('.//a:t', ns)[i].text or ''
                      for i in range(len(ET.fromstring(archive.read(n)).findall('.//a:t', ns)))) for n in slides]
    check(len(slides) == 13, 'Current deck must have 13 slides')
    notes_count = sum(bool(re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)) for n in archive.namelist())
    check(notes_count == 13, 'Every slide must have speaker notes')
    if len(texts) == 13:
        check('System Analyst and Document Pre-review Lead' in texts[9], 'Huai role missing on slide 10')
        check('Zheyuan Huai' in texts[9] and 'Zheyuan Huai' in texts[10], 'Huai slide ownership mismatch')
        check('System Requirements and Prototype Scope' in texts[9], 'Requirements slide missing')
        check('Material Upload, Evidence and Review Versions' in texts[10], 'Enhanced review slide missing')
        for n, text in enumerate(texts[1:], 2):
            check(any(word in text.lower() for word in ['next', 'current', 'progress', 'limitations', 'workflow']),
                  f'No progress/next-work content detected on slide {n}')

notes = (ROOT / 'deliverables/SPEAKER_NOTES_ENHANCED.md').read_text(encoding='utf-8')
sections = re.split(r'^## ', notes, flags=re.M)[1:]
check(len(sections) == 13, 'Speaker notes must cover 13 slides')
speakers, word_counts = [], []
for section in sections[1:]:
    heading, _, body = section.partition('\n')
    found = re.search(r'— ([^—]+) — (\d+) seconds', heading)
    check(bool(found), 'Missing speaker/timing in notes heading')
    if found:
        speakers.append((found.group(1).strip(), int(found.group(2))))
        word_counts.append(len(re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", body)))
times = Counter()
for person, seconds in speakers:
    times[person] += seconds
check(len(times) == 6 and all(t == 120 for t in times.values()), 'Each of six speakers must have 120 seconds')
check(sum(times.values()) == 720, 'Planned total must be 720 seconds')

for name in names:
    if not name.endswith('.md'):
        continue
    text = (ROOT / name).read_text(encoding='utf-8-sig')
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        target = target.strip('<>').split('#', 1)[0]
        if not target or re.match(r'[a-zA-Z]+:', target):
            continue
        check(((ROOT / name).parent / unquote(target)).exists(), 'Broken local link in ' + name + ': ' + target)

browser = json.loads((ROOT / 'deliverables/enhanced-browser-results.json').read_text())
check(browser.get('errors') == [], 'Recorded enhanced browser run contains errors')
report = {'status': 'pass' if not failures else 'fail', 'candidate_files': len(names),
          'candidate_bytes': total_bytes, 'slides': len(slides), 'notes': notes_count,
          'speaker_seconds': dict(times), 'speaker_word_counts':
          {speakers[i][0]: sum(word_counts[i:i + 2]) for i in range(0, len(speakers), 2)},
          'deck_sha256': hashlib.sha256(deck.read_bytes()).hexdigest(),
          'warnings': warnings, 'failures': failures,
          'boundaries': ['Secret scanning checks bytes and Office archive contents; it does not OCR images or transcribe video.',
                         'Package checks and recorded browser evidence do not replace live AI or physical classroom rehearsal.']}
if args.output:
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(bool(failures))
