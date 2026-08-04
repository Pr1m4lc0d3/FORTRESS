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

MONTH_NAMES = (
    "January February March April May June July August September October "
    "November December Jan Feb Mar Apr Jun Jul Aug Sept Sep Oct Nov Dec"
).split()

# Number words, longest first so the alternation prefers "seventeen" over "seven".
NUMBER_WORDS = sorted(
    (
        "one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty "
        "thirty forty fifty sixty seventy eighty ninety"
    ).split(),
    key=len,
    reverse=True,
)

# "one" and "two" are ordinary prose words ("one place", "two halves") and are
# excluded from the bare-count branch below, which would otherwise fire on most
# English sentences. They are still matched in front of an explicit magnitude
# word, where "one million users" is unambiguously a quantity claim.
AMBIGUOUS_NUMBER_WORDS = ("one", "two")
COUNTABLE_NUMBER_WORDS = [w for w in NUMBER_WORDS if w not in AMBIGUOUS_NUMBER_WORDS]

MAGNITUDE_WORDS = ["hundred", "thousand", "million", "billion", "trillion"]

_MONTHS = "|".join(MONTH_NAMES)
_NUMS = "|".join(NUMBER_WORDS)
_COUNTABLE_NUMS = "|".join(COUNTABLE_NUMBER_WORDS)
_MAGS = "|".join(MAGNITUDE_WORDS)

# Genuine DATE FORMATS only. A bare year is a claim ("Founded in 2024" is a
# factual assertion about a company) and is deliberately NOT ignored: the old
# \b(?:19|20)\d{2}\b exempted every integer from 1900 to 2099, so "Over 2000
# people signed up" passed clean — exactly the shape an invented stat takes.
DATE_FORMS = (
    r"\b\d{4}-\d{2}-\d{2}\b"
    rf"|\b(?:\d{{1,2}}\s+)?(?:{_MONTHS})\.?\s+(?:\d{{1,2}},?\s+)?\d{{4}}\b"
)

MAGNITUDE_PATTERN = (
    # "forty thousand", "one million", "twenty-five thousand" — one span.
    rf"\b(?:{_NUMS})(?:[\s-]+(?:{_NUMS}))?\s+(?:{_MAGS})s?\b"
    # "hundreds of teams", "millions of requests", "thousands rely on us".
    rf"|\b(?:{_MAGS})s(?:\s+of)?\b"
    # Vague magnitude quantifiers.
    r"|\bdozens(?:\s+of)?\b|\ba\s+dozen\b|\bscores\s+of\b"
    r"|\ba\s+handful\s+of\b"
    r"|\b(?:countless|numerous)\b"
    # A number word quantifying a plural noun within a couple of words:
    # "forty paying customers".
    rf"|\b(?:{_COUNTABLE_NUMS})\s+(?:\w+\s+){{0,1}}\w{{3,}}s\b"
)

TESTIMONIAL_PATTERN = (
    # Straight or curly double quotes.
    r"[\"“][^\"”]{20,}[\"”]"
    # A markdown blockquote line with 20+ characters of text.
    r"|(?m:^[ \t]{0,3}>[ \t]*\S.{19,})"
    # Single-quoted spans. The lookaround keeps an apostrophe inside a word
    # ("doesn't ... you're") from being read as an opening quote.
    r"|(?<![\w'’])'[^'’\n]{20,}'(?!\w)"
    r"|(?<![\w'’])‘[^’\n]{20,}’(?!\w)"
)

DEFAULT_CONFIG = {
    "patterns": {
        "number": r"\b\d[\d,]*(?:\.\d+)?%?\b",
        "magnitude": MAGNITUDE_PATTERN,
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
        "testimonial": TESTIMONIAL_PATTERN,
    },
    "severity": {
        "number": "error",
        "magnitude": "error",
        "superlative": "error",
        "comparative": "error",
        "testimonial": "error",
        "absolute": "warn",
    },
    "ignore": [
        DATE_FORMS,
    ],
}


CATCH_ALL_IGNORES = {".*", ".+", "^.*$", "(.*)"}
VALID_SEVERITIES = ("error", "warn")
SOURCE_SUFFIX = " — source:"
WINDOW_WORDS = 3


class ConfigRefused(Exception):
    """A config that oversteps what a config may set (see CONFIG_RULE)."""


class Finding(NamedTuple):
    line: int
    category: str
    span: str
    severity: str
    col: int = 0


def load_register(path):
    """Return the set of lowercased 'Cleared' lines from a truth register.

    A Cleared bullet without a ' — source:' suffix is MALFORMED and is excluded.
    An unsourced register entry must not be able to source anything — otherwise
    the register becomes a place to launder a number by writing it down.
    """
    cleared = set()
    if not Path(path).exists():
        return cleared
    section = None
    for lineno, raw in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if line.lower().startswith("## "):
            section = line[3:].strip().lower()
            continue
        if section == "cleared" and line.startswith("- "):
            entry = line[2:].strip()
            if SOURCE_SUFFIX.lower() not in entry.lower():
                print(
                    f"claim-lint: WARNING: {Path(path)}:{lineno}: malformed Cleared "
                    "entry, no 'source:' suffix (the template's em-dash form); "
                    f"IGNORED, it sources nothing: {entry!r}",
                    file=sys.stderr,
                )
                continue
            cleared.add(entry.lower())
    return cleared


def strip_noise(text):
    """Blank out fenced code, inline code and URLs, preserving offsets.

    Fences are paired EXPLICITLY. An unterminated fence must not blank the rest
    of the document: a single typo would otherwise switch the gate off for
    everything after it and still report all-clear.
    """

    def blank_span(chunk):
        return re.sub(r"\S", " ", chunk)

    def blank(match):
        return blank_span(match.group(0))

    markers = list(re.finditer(r"```", text))
    if len(markers) % 2:
        unterminated = markers[-1]
        line = text.count("\n", 0, unterminated.start()) + 1
        print(
            f"claim-lint: WARNING: unterminated code fence at line {line}; "
            "the text after it is being SCANNED, not treated as code.",
            file=sys.stderr,
        )
    chunks = []
    cursor = 0
    for index in range(len(markers) // 2):
        start = markers[2 * index].start()
        end = markers[2 * index + 1].end()
        chunks.append(text[cursor:start])
        chunks.append(blank_span(text[start:end]))
        cursor = end
    chunks.append(text[cursor:])
    text = "".join(chunks)
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


def _span_window(line, col, span):
    """The span plus the next few words on its line, whitespace-normalised.

    A BARE span is not evidence of sourcing. The token "97" sits inside a cleared
    "97 downloads all-time" no matter what the draft says next to it, so checking
    the token alone lets "97 million requests a day" ride in on it. Only the span
    IN CONTEXT may vouch for itself.

    THE INVARIANT: the window is only ever NARROWER THAN THE LINE and WIDER THAN
    THE SPAN. When it cannot be both — the offset does not line up, or the span
    is the last token on its line and no word follows it — the fallback is the
    WHOLE LINE, the strict check. Never the bare span: a number ending a line, a
    heading, or a list item is ordinary copy, and degrading to the token there
    would reopen exactly the hole this function exists to close.
    """
    if col < 0 or line[col:col + len(span)] != span:
        return line
    following = line[col + len(span):].split()[:WINDOW_WORDS]
    if not following:
        return line
    return " ".join(span.split() + following)


def _blank_ignored(text, ignores):
    """Blank every region matching an ignore pattern, preserving offsets.

    An ignore is applied to the TEXT, not only to a finished span. A span-only
    check cannot express a multi-token exemption: the number detector splits
    '2026-08-04' into the three spans '2026', '08' and '04', so no pattern
    fullmatching the whole date could ever silence it. Blanking the region does.
    The span-level fullmatch is kept as well, so an anchored pattern that only
    makes sense against a span still works.
    """
    for ignore in ignores:
        text = ignore.sub(lambda m: re.sub(r"\S", " ", m.group(0)), text)
    return text


def find_claims(text, config):
    findings = []
    ignores = [re.compile(p, re.IGNORECASE) for p in config.get("ignore", [])]
    cleaned = _blank_ignored(strip_noise(text), ignores)
    for category, pattern in config["patterns"].items():
        severity = config["severity"].get(category, "error")
        for match in re.finditer(pattern, cleaned, flags=re.IGNORECASE):
            span = match.group(0)
            if any(ig.fullmatch(span) for ig in ignores):
                continue
            line = cleaned.count("\n", 0, match.start()) + 1
            col = match.start() - (cleaned.rfind("\n", 0, match.start()) + 1)
            findings.append(Finding(line, category, span, severity, col))
    return findings


def lint_text(text, register, config):
    """Return findings whose containing line is not sourced in the register."""
    lines = text.splitlines()
    out = []
    for finding in find_claims(text, config):
        source_line = lines[finding.line - 1] if finding.line <= len(lines) else ""
        window = _span_window(source_line, finding.col, finding.span)
        if _is_sourced(source_line, register) or _is_sourced(window, register):
            continue
        out.append(finding)
    return out


SCAN_SUFFIXES = {
    ".md",
    ".markdown",
    ".mdx",
    ".txt",
    ".rst",
    ".html",
    ".htm",
}


CONFIG_RULE = (
    "A config may set 'severity' and 'ignore' only. Detection patterns are fixed. "
    "Ignore patterns are printed on every run, so a broad one is visible in the "
    "output rather than hidden in a file."
)


def validate_config(config):
    """Refuse the config shapes that turn the gate off outright.

    Scope, stated honestly because the alternative is a false claim inside a tool
    about false claims: this refuses a config that can never fail and a severity
    map that is nonsense. It does NOT — and cannot — decide whether a given
    ignore REGEX is too broad. `\\d+` silences the number category as surely as
    `.*` silences everything. That is why every ignore pattern is echoed on every
    run: the defence against a too-broad ignore is that you can SEE it, not that
    the linter second-guessed it.
    """
    for pattern in config.get("ignore", []):
        try:
            matches_empty = re.compile(pattern).fullmatch("") is not None
        except re.error as exc:
            raise ConfigRefused(f"invalid ignore pattern {pattern!r}: {exc}")
        if pattern.strip() in CATCH_ALL_IGNORES or matches_empty:
            raise ConfigRefused(
                f"catch-all ignore pattern {pattern!r} would suppress every "
                f"finding. {CONFIG_RULE}"
            )
    severity = config.get("severity", {})
    for category, value in severity.items():
        if value not in VALID_SEVERITIES:
            raise ConfigRefused(
                f"invalid severity {value!r} for category {category!r}; expected "
                f"one of {', '.join(VALID_SEVERITIES)}. {CONFIG_RULE}"
            )
    if severity and all(value == "warn" for value in severity.values()):
        raise ConfigRefused(
            "every category is set to 'warn', so the run can never fail. "
            + CONFIG_RULE
        )


def describe_config(config, source):
    """One line naming what the gate is actually set to for this run.

    The ignore patterns are printed IN FULL, not counted. An ignore regex can
    silence an entire category — `\\d+` retires every number — and no validator
    can judge that for you. Printing the patterns is the only honest defence:
    the weakening is visible in the same output as the verdict it produced.
    """
    categories = ", ".join(
        f"{name}={config['severity'].get(name, 'error')}"
        for name in sorted(config["patterns"])
    )
    ignores = list(config.get("ignore", []))
    shown = "; ".join(ignores) if ignores else "(none)"
    return (
        f"claim-lint: config: {source} | categories: {categories} "
        f"| ignore patterns: {len(ignores)}: {shown}"
    )


def load_config(explicit=None):
    """Return (config, source-label).

    Loads an explicit path, else tools/monkeys/truth.config.json, else defaults.
    Raises ConfigRefused for a config that oversteps what a config may set.
    """
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(Path("tools") / "monkeys" / "truth.config.json")
    for candidate in candidates:
        if candidate.exists():
            loaded = json.loads(candidate.read_text(encoding="utf-8"))
            if "patterns" in loaded:
                raise ConfigRefused(
                    "'patterns' is not user-overridable: a config that could "
                    "rewrite a detection pattern could switch a category off with "
                    "a regex that never matches, such as '$^'. A config may set "
                    "'severity' and 'ignore' only."
                )
            merged = {**DEFAULT_CONFIG, **loaded}
            if "severity" in loaded:
                merged["severity"] = {**DEFAULT_CONFIG["severity"], **loaded["severity"]}
            validate_config(merged)
            return merged, str(candidate)
    validate_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG, "built-in defaults"


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

    try:
        config, config_source = load_config(args.config)
    except ConfigRefused as exc:
        print(f"claim-lint: refusing config: {exc}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, OSError) as exc:
        print(f"claim-lint: unreadable config: {exc}", file=sys.stderr)
        return 2
    print(describe_config(config, config_source), file=sys.stderr)

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
            "Source them in .monkeys/truth.md or cut them. There is no per-finding "
            "waiver flag; an 'ignore' pattern silences by shape, and every one in "
            "effect is printed in the config line above.",
            file=sys.stderr,
        )

    if args.report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
