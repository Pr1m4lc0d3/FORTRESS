#!/usr/bin/env python3
"""claim-lint — flag claim-shaped language that is not sourced in the truth register.

The linter flags claim-shaped LANGUAGE. The register ARBITRATES.
No script can know whether "fastest" is true — only whether it is sourced.
"""

import argparse
import json
import re
import sys
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


SCAN_SUFFIXES = {".md", ".markdown", ".txt"}


def load_config(explicit=None):
    """Load config from an explicit path, else tools/monkeys/truth.config.json, else defaults."""
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(Path("tools") / "monkeys" / "truth.config.json")
    for candidate in candidates:
        if candidate.exists():
            loaded = json.loads(candidate.read_text(encoding="utf-8"))
            merged = {**DEFAULT_CONFIG, **loaded}
            for key in ("patterns", "severity"):
                if key in loaded:
                    merged[key] = {**DEFAULT_CONFIG[key], **loaded[key]}
            return merged
    return DEFAULT_CONFIG


def lint_path(target, register, config):
    """Lint a file or, for a directory, every markdown/text file beneath it."""
    target = Path(target)
    files = [target] if target.is_file() else sorted(
        p for p in target.rglob("*") if p.suffix.lower() in SCAN_SUFFIXES
    )
    results = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for finding in lint_text(text, register, config):
            results.append((path, finding))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="claim-lint",
        description="Flag claim-shaped language not sourced in the truth register.",
    )
    parser.add_argument("target", help="File or directory to scan")
    parser.add_argument(
        "--register",
        default=".monkeys/truth.md",
        help="Path to the truth register (default: .monkeys/truth.md)",
    )
    parser.add_argument("--config", default=None, help="Path to truth.config.json")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print findings without failing (always exits 0)",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print(f"claim-lint: target not found: {target}", file=sys.stderr)
        return 2
    register_path = Path(args.register)
    if not register_path.exists():
        print(
            f"claim-lint: register not found: {register_path}\n"
            "Run the fortress kickoff to generate .monkeys/truth.md",
            file=sys.stderr,
        )
        return 2

    register = load_register(register_path)
    config = load_config(args.config)
    results = lint_path(target, register, config)

    errors = 0
    for path, finding in results:
        if finding.severity == "error":
            errors += 1
        print(
            f"{path}:{finding.line}: {finding.severity}: "
            f"unsourced {finding.category}: {finding.span!r}"
        )

    if not results:
        print("claim-lint: no unsourced claims found.")
    elif errors:
        print(
            f"\nclaim-lint: {errors} unsourced claim(s). "
            "Source them in .monkeys/truth.md or remove them. There are no waivers.",
            file=sys.stderr,
        )

    if args.report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
