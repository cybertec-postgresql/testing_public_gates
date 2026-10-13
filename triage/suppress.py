"""In-source suppressions. A `nosemgrep` comment on the finding's line or the
line above it is how a reviewer accepts a finding in a pull request; the reason
stands next to it and in SUPPRESSIONS.md. Semgrep drops such results, and the
pull request path skips them, but GitHub's code scanning alert list keeps them
open, so the reconciliation of main reads the source itself."""

import re

_NOSEMGREP = re.compile(r"nosemgrep(?::\s*([^\n]*))?")


def suppressed_in_source(repo_dir: str, path: str, line, rule_id: str | None) -> bool:
    if not line:
        return False
    try:
        with open(f"{repo_dir}/{path}", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return False
    for n in (line, line - 1):
        if 1 <= n <= len(lines):
            m = _NOSEMGREP.search(lines[n - 1])
            if not m:
                continue
            named = [r.strip() for r in (m.group(1) or "").split(",") if r.strip()]
            if not named or (rule_id and rule_id in named):
                return True
    return False
