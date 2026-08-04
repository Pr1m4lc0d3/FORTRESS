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
    },
    "severity": {
        "number": "error",
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


def _is_sourced(span, register):
    needle = span.strip().lower()
    return any(needle in cleared for cleared in register)


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
    """Return findings whose span is not sourced in the register."""
    return [f for f in find_claims(text, config) if not _is_sourced(f.span, register)]
