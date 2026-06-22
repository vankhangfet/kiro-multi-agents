#!/usr/bin/env python3
# Hook: Inject git status summary into agent context.
# Trigger: userPromptSubmit
# Outputs one-line git summary to stdout. Silent no-op outside git repos.

import json
import os
import subprocess
import sys


def run(cmd, cwd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def count_lines(text):
    return len([l for l in text.splitlines() if l.strip()])


try:
    event = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

cwd = event.get("cwd", "")
if not cwd:
    sys.exit(0)

if not os.path.isdir(cwd):
    sys.exit(0)

# Check if inside a git repo
check = run(["git", "rev-parse", "--git-dir"], cwd)
if not check:
    sys.exit(0)

branch = run(["git", "branch", "--show-current"], cwd) or "detached"
staged = count_lines(run(["git", "diff", "--cached", "--numstat"], cwd))
modified = count_lines(run(["git", "diff", "--numstat"], cwd))
untracked = count_lines(run(["git", "ls-files", "--others", "--exclude-standard"], cwd))
last = run(["git", "log", "-1", "--format=%s (%cr)"], cwd) or "no commits"

print(f'[git] branch: {branch} | staged:{staged} modified:{modified} untracked:{untracked} | last: "{last}"')
