#!/usr/bin/env python3
# Hook: Lightweight turn index for flywheel analysis.
# Trigger: stop (fires after each assistant response)
# Writes one minimal JSONL entry per turn to ~/.kiro/flywheel-log.jsonl

import json
import os
import sys
import time
from pathlib import Path

LOG_PATH = Path.home() / '.kiro' / 'flywheel-log.jsonl'
MAX_LOG_BYTES = 5 * 1024 * 1024
PREVIEW_CHARS = 200

try:
    event = json.loads(sys.stdin.read())
except (json.JSONDecodeError, Exception) as e:
    print(f"Hook error: failed to parse event: {e}", file=sys.stderr)
    sys.exit(0)

response = event.get('assistant_response', '')
cwd = event.get('cwd', '')

if not response.strip():
    sys.exit(0)

head = response[:PREVIEW_CHARS].replace('\n', ' ').strip()
tail = response[-PREVIEW_CHARS:].replace('\n', ' ').strip() if len(response) > PREVIEW_CHARS * 2 else ''

entry = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    'cwd': cwd,
    'len': len(response),
    'head': head,
}
if tail:
    entry['tail'] = tail

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
    # 0o600 is ignored on Windows but harmless
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
