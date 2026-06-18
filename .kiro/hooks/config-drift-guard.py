#!/usr/bin/env python3
# Hook: Block writes to agent config files unless explicitly approved.
# Trigger: preToolUse on fs_write
# Exit 0 = allow, Exit 2 = block (returns STDERR to LLM)
#
# Protected paths: ~/.kiro/steering/, ~/.kiro/skills/, ~/.kiro/agents/
# To allow config writes, set KIRO_ALLOW_CONFIG_WRITES=1 or run the
# flywheel prompt (which should instruct the user to approve changes).

import json
import os
import sys
from pathlib import Path

if os.environ.get('KIRO_ALLOW_CONFIG_WRITES', '') == '1':
    sys.exit(0)

KIRO_DIR = Path.home() / '.kiro'
PROTECTED = [
    str(KIRO_DIR / 'steering'),
    str(KIRO_DIR / 'skills'),
    str(KIRO_DIR / 'agents'),
]

try:
    event = json.loads(sys.stdin.read())
except (json.JSONDecodeError, Exception) as e:
    print(f"Hook error: failed to parse event: {e}", file=sys.stderr)
    sys.exit(1)

inp = event.get('tool_input', {})
ops = inp.get('ops', [inp])

for op in ops:
    path = op.get('path', '')
    if not path:
        continue
    resolved = str(Path(path).expanduser().resolve())
    for protected in PROTECTED:
        protected_resolved = str(Path(protected).resolve())
        if resolved.startswith(protected_resolved + os.sep) or resolved == protected_resolved:
            print("BLOCKED: Writing to Kiro configuration files requires explicit approval.", file=sys.stderr)
            print(f"File: {resolved}", file=sys.stderr)
            print("Ask the user to approve this change before proceeding.", file=sys.stderr)
            sys.exit(2)

sys.exit(0)
