#!/usr/bin/env python3
# Hook: Validate required tools are installed and print versions.
# Trigger: agentSpawn
# Exits non-zero only if critical tools (python, git) are missing.

import subprocess
import sys

# Consume stdin (hook event)
sys.stdin.read()

TOOLS = [
    ("python",  ["python", "--version"],  True),
    ("git",     ["git", "--version"],     True),
    ("node",    ["node", "--version"],    False),
    ("aws",     ["aws", "--version"],     False),
    ("docker",  ["docker", "--version"],  False),
    ("cargo",   ["cargo", "--version"],   False),
]

missing_critical = False

for name, cmd, critical in TOOLS:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = (result.stdout or result.stderr or "").splitlines()
        version = output[0].strip() if output else "(no output)"
        print(f"[env] {name}: {version}")
    except FileNotFoundError:
        print(f"[env] {name}: [MISSING]")
        if critical:
            missing_critical = True
    except Exception as e:
        print(f"[env] {name}: [ERROR: {e}]")
        if critical:
            missing_critical = True

sys.exit(1 if missing_critical else 0)
