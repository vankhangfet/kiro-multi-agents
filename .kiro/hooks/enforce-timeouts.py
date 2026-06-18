#!/usr/bin/env python3
# Hook: Block test/build commands that have no timeout, preventing agent hangs.
# Trigger: preToolUse on execute_bash
# Exit 0 = allow, Exit 2 = block (message returned to LLM so it can retry with timeout)

import json
import re
import sys

# Commands that can run indefinitely and must always have a timeout
LONG_RUNNING_PATTERNS = [
    re.compile(r'\bpytest\b'),
    re.compile(r'\bpython\s+-m\s+pytest\b'),
    re.compile(r'\bnpm\s+(test|run\s+test|run\s+e2e|run\s+integration)\b'),
    re.compile(r'\bnpx\s+jest\b'),
    re.compile(r'\bjest\b'),
    re.compile(r'\bmocha\b'),
    re.compile(r'\bvitest\b'),
    re.compile(r'\bgo\s+test\b'),
    re.compile(r'\bcargo\s+test\b'),
    re.compile(r'\bmvn\s+test\b'),
    re.compile(r'\bgradle\s+test\b'),
    re.compile(r'\brspec\b'),
    re.compile(r'\bphpunit\b'),
    re.compile(r'\bphp\s+artisan\s+test\b'),
    re.compile(r'\bdotnet\s+test\b'),
    re.compile(r'\bdocker\s+build\b'),
    re.compile(r'\bdocker-compose\s+up\b'),
    re.compile(r'\bcdk\s+synth\b'),
    re.compile(r'\bcdk\s+deploy\b'),
    re.compile(r'\bterraform\s+(plan|apply)\b'),
    re.compile(r'\bnpm\s+(install|ci)\b'),
    re.compile(r'\bpip\s+install\b'),
    re.compile(r'\bcargo\s+build\b'),
    re.compile(r'\bgo\s+build\b'),
]

# Patterns that prove a timeout is already present
TIMEOUT_ALREADY_SET = [
    re.compile(r'^timeout\s+\d+'),               # timeout 120 ...
    re.compile(r'--timeout[=\s]\d+'),             # --timeout=60 or --timeout 60
    re.compile(r'--testTimeout[=\s]\d+'),         # jest --testTimeout
    re.compile(r'--forceExit'),                   # jest --forceExit (exits after suite)
    re.compile(r'-p\s+no:timeout'),               # pytest disable timeout plugin
    re.compile(r'PYTEST_TIMEOUT'),                # env var timeout
]

# Suggest a safe re-run for known commands
def suggest(command: str) -> str:
    cmd = command.strip()
    if re.search(r'\bpytest\b', cmd) or re.search(r'python\s+-m\s+pytest', cmd):
        base = re.sub(r'^python\s+-m\s+pytest', 'pytest', cmd)
        base = re.sub(r'^pytest', 'python -m pytest', base)
        if '--timeout' not in base:
            base += ' --timeout=60'
        if '--tb=short' not in base:
            base += ' --tb=short'
        if '-q' not in base:
            base += ' -q'
        return f"timeout 120 {base}"

    if re.search(r'\bnpm\s+test\b', cmd) or re.search(r'\bnpm\s+run\s+test\b', cmd):
        return f"timeout 120 {cmd} -- --forceExit --testTimeout=60000 2>&1 || true"

    if re.search(r'\bnpx\s+jest\b', cmd) or re.search(r'\bjest\b', cmd):
        return f"timeout 120 {cmd} --forceExit --testTimeout=60000"

    if re.search(r'\bgo\s+test\b', cmd):
        if '-timeout' not in cmd:
            return re.sub(r'\bgo\s+test\b', 'go test -timeout 120s', cmd)
        return cmd

    if re.search(r'\bcargo\s+test\b', cmd):
        return f"timeout 120 {cmd}"

    if re.search(r'\bdocker\s+build\b', cmd):
        return f"timeout 120 {cmd}"

    if re.search(r'\bcdk\s+synth\b', cmd):
        return f"timeout 120 {cmd}"

    if re.search(r'\bterraform\s+plan\b', cmd):
        return f"timeout 120 {cmd}"

    if re.search(r'\bnpm\s+(install|ci)\b', cmd):
        return f"timeout 120 {cmd}"

    return f"timeout 120 {cmd}"


try:
    event = json.loads(sys.stdin.read())
except (json.JSONDecodeError, Exception) as e:
    print(f"Hook parse error: {e}", file=sys.stderr)
    sys.exit(0)  # allow on parse failure — don't block agent for hook bugs

inp = event.get('tool_input', {})
command = inp.get('command', '')

if not command:
    sys.exit(0)

# Check if this is a potentially long-running command
is_long_running = any(p.search(command) for p in LONG_RUNNING_PATTERNS)
if not is_long_running:
    sys.exit(0)

# Check if a timeout is already in place
already_timed = any(p.search(command) for p in TIMEOUT_ALREADY_SET)
if already_timed:
    sys.exit(0)

# Block and tell the LLM exactly what to run instead
safe_command = suggest(command)

print("BLOCKED: This command can hang indefinitely and has no timeout.", file=sys.stderr)
print("A hanging command freezes the entire agent session.", file=sys.stderr)
print(f"", file=sys.stderr)
print(f"Run this instead:", file=sys.stderr)
print(f"  {safe_command}", file=sys.stderr)
print(f"", file=sys.stderr)
print(f"If the command exits with code 124 (timeout), mark the task [!] with:", file=sys.stderr)
print(f"  [!] Command timed out: `{command[:100]}`", file=sys.stderr)
print(f"      Stop — do not retry. Report this to the architect.", file=sys.stderr)
sys.exit(2)
