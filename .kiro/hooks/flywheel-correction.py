#!/usr/bin/env python3
# Hook: Detect correction signals in user prompts and log them for flywheel analysis.
# Trigger: userPromptSubmit
# Writes filtered JSONL entries to ~/.kiro/flywheel-corrections.jsonl
# Outputs nothing to stdout — side-channel logger only.

import json
import os
import re
import sys
import time
from pathlib import Path

LOG_PATH = Path.home() / '.kiro' / 'flywheel-corrections.jsonl'
MAX_LOG_BYTES = 5 * 1024 * 1024
MAX_PROMPT_CHARS = 500

SIGNALS = [
    ('explicit_correction', re.compile(r"\b(no|nope),?\s+(i\s+)?(meant|said|wanted|asked)\b", re.I)),
    ('explicit_correction', re.compile(r"\bthat'?s\s+(wrong|not\s+(right|correct|what))\b", re.I)),
    ('explicit_correction', re.compile(r"\b(don'?t|do\s+not)\s+(do|use|run|create|delete|change)\b", re.I)),
    ('explicit_correction', re.compile(r"\bi\s+said\b.*\bnot\b", re.I | re.DOTALL)),
    ('explicit_correction', re.compile(r"\b(actually|wait),?\s", re.I)),
    ('redirect', re.compile(r"\binstead\s+(of|do|use|try)\b", re.I)),
    ('redirect', re.compile(r"\b(cancel|stop|abort)\s+(that|this)\b", re.I)),
    ('redirect', re.compile(r"\btry\s+again\b", re.I)),
    ('redirect', re.compile(r"\b(start|do)\s+over\b", re.I)),
    ('repeat', re.compile(r"\bi\s+(already|just)\s+(said|told|asked)\b", re.I)),
    ('repeat', re.compile(r"\b(again|once\s+more),?\s+(but|with|please)\b", re.I)),
    ('repeat', re.compile(r"^(why|why\s+(did|are)).{0,80}\?", re.I)),
    ('quality', re.compile(r"\b(too\s+(verbose|long|short|much|many))\b", re.I)),
    ('quality', re.compile(r"\b(stop|don'?t)\s+(making|creating|adding|using)\b", re.I)),
    ('quality', re.compile(r"\byou\s+(forgot|missed|skipped|ignored)\b", re.I)),
    ('quality', re.compile(r"\b(read|check)\s+(the|my|this)\s+\w+\s+(again|first)\b", re.I)),
    ('tool_redirect', re.compile(r"\buse\s+(\w+)\s+(instead|not)\b", re.I)),
    ('tool_redirect', re.compile(r"\b(don'?t|do\s+not)\s+(use|run|call)\b", re.I)),
]

try:
    event = json.loads(sys.stdin.read())
except (json.JSONDecodeError, Exception) as e:
    print(f"Hook error: failed to parse event: {e}", file=sys.stderr)
    sys.exit(0)

prompt = event.get('prompt', '')
cwd = event.get('cwd', '')

if not prompt or not prompt.strip():
    sys.exit(0)

user_text = prompt
if '--- USER MESSAGE BEGIN' in prompt:
    start = prompt.find('USER MESSAGE BEGIN ---')
    end = prompt.find('--- USER MESSAGE END')
    if start >= 0 and end > start:
        user_text = prompt[start + len('USER MESSAGE BEGIN ---'):end].strip()

if len(user_text) > 2000:
    sys.exit(0)

matches = []
for label, pattern in SIGNALS:
    if pattern.search(user_text):
        matches.append(label)

is_terse = len(user_text.strip()) < 60
is_short_question = is_terse and user_text.strip().endswith('?')

if not matches and not is_terse:
    sys.exit(0)

if is_terse and not matches:
    matches.append('terse')
if is_short_question:
    matches.append('short_question')

matches = sorted(set(matches))

entry = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'cwd': cwd,
    'signals': matches,
    'prompt': user_text[:MAX_PROMPT_CHARS],
    'prompt_len': len(user_text),
}

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

try:
    if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_LOG_BYTES:
        rotated = LOG_PATH.with_suffix('.jsonl.old')
        if rotated.exists():
            rotated.unlink()
        LOG_PATH.rename(rotated)
except OSError:
    pass

try:
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(str(LOG_PATH), flags, 0o600)
    try:
        os.chmod(str(LOG_PATH), 0o600)
    except OSError:
        pass
    with os.fdopen(fd, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
except OSError:
    pass

sys.exit(0)
