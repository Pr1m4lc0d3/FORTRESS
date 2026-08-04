#!/usr/bin/env python3
"""claim-lint — flag claim-shaped language that is not sourced in the truth register.

The linter flags claim-shaped LANGUAGE. The register ARBITRATES.
No script can know whether "fastest" is true — only whether it is sourced.
"""

import re
from pathlib import Path
from typing import NamedTuple

DEFAULT_CONFIG = {
    "patterns": {
        "number": r"\b\d[\d,]*(?:\.\d+)?%?\b",
        "superlative": (
            r"\b(?:the\s+)?(?:best|worst|fastest|slowest|cheapest|only|first|"
            r"largest|smallest|most|least|leading|number\s+one)\b"
            r"|(?<!\w)#1(?!\w)"
        ),
        "comparative": (
            r"\b(?:better|faster|cheaper|stronger|safer)\s+than\b"
            r"|\bmore\s+\w+\s+than\b|\bunlike\b|\bcompared\s+to\b|\boutperforms\b"
        ),
        "absolute": r"\b(?:never|always|guaranteed|nobody|no\s+one|everyone|zero)\b",
        "testimonial": r"[\"“][^\"”]{20,}[\"”]",
    },
    "severity": {
        "number": "error",
        "superlative": "error",
        "comparative": "error",
        "testimonial": "error",
        "absolute": "warn",
    },
    "ignore": [
        r"\b(?:19|20)\d{2}\b",
    ],
}


class Finding(NamedTuple):
    line: int
    category: str
    span: str
    severity: str


def load_register(path):
    """Return the set of lowercased 'Cleared' lines from a truth register."""
    cleared = set()
    if not Path(path).exists():
        return cleared
    section = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.lower().startswith("## "):
            section = line[3:].strip().lower()
            continue
        if section == "cleared" and line.startswith("- "):
            cleared.add(line[2:].strip().lower())
    return cleared


def strip_noise(text):
    """Blank out fenced code, inline code and URLs, preserving offsets."""

    def blank(match):
        return re.sub(r"\S", " ", match.group(0))

    text = re.sub(r"```.*?```", blank, text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
    return text


def _contains_bounded(haystack, needle):
    """True if needle appears in haystack not flanked by word characters."""
    return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", haystack) is not None


def _is_sourced(text, register):
    """Word-bounded containment: the claim text must appear inside a cleared entry.

    ONE DIRECTION ONLY, and both halves of that are load-bearing:

    - Boundaries are mandatory. Plain substring matching lets an unsourced "49"
      hide inside a cleared "149".
    - The reverse direction is forbidden. If a cleared entry were allowed to
      match inside the claim text, a short cleared fragment would vouch for a
      long line carrying other unsourced claims.

    Both are the same false negative.
    """
    needle = text.strip().lower().rstrip(".")
    if not needle:
        return False
    return any(_contains_bounded(cleared, needle) for cleared in register)


def find_claims(text, config):
    findings = []
    cleaned = strip_noise(text)
    ignores = [re.compile(p, re.IGNORECASE) for p in config.get("ignore", [])]
    for category, pattern in config["patterns"].items():
        severity = config["severity"].get(category, "error")
        for match in re.finditer(pattern, cleaned, flags=re.IGNORECASE):
            span = match.group(0)
            if any(ig.fullmatch(span) for ig in ignores):
                continue
            line = cleaned.count("\n", 0, match.start()) + 1
            findings.append(Finding(line, category, span, severity))
    return findings


def lint_text(text, register, config):
    """Return findings whose containing line is not sourced in the register."""
    lines = text.splitlines()
    out = []
    for finding in find_claims(text, config):
        source_line = lines[finding.line - 1] if finding.line <= len(lines) else ""
        if _is_sourced(source_line, register) or _is_sourced(finding.span, register):
            continue
        out.append(finding)
    return out
