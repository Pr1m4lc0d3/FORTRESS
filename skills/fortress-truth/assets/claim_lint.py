#!/usr/bin/env python3
"""claim-lint — flag claim-shaped language that is not sourced in the truth register.

The linter flags claim-shaped LANGUAGE. The register ARBITRATES.
No script can know whether "fastest" is true — only whether it is sourced.
"""

import argparse
import json
import re
import sys
from datetime import date
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
    # A claim that was true when it was checked is not a claim that is true now.
    # See STALENESS_RULE.
    "staleness": {
        "max_age_days": 90,
        "severity": "warn",
        "require_checked": False,
    },
}


CATCH_ALL_IGNORES = {".*", ".+", "^.*$", "(.*)"}
VALID_SEVERITIES = ("error", "warn")
SOURCE_SUFFIX = " — source:"
CHECKED_SUFFIX = " — checked:"
REASON_SUFFIX = " — reason:"
WINDOW_WORDS = 3

# The two sections that hold claims which USED to be sayable. Both are scanned
# FOR in the draft, which is the opposite direction from Cleared: a cleared
# entry answers "may I say this?", a retracted entry answers "am I still saying
# something I already withdrew?".
#
# 'Uncleared' is deliberately NOT among them. An Uncleared line describes a
# CLASS of claim ("any user or adoption count") rather than the literal words of
# one, so scanning drafts for its text would match nothing useful and would
# train people to write register entries as keyword bait. Changed and
# Contradicted are different in kind: by construction they hold the exact wording
# that used to ship, which is precisely what a stale draft still contains.
RETRACTED_SECTIONS = ("changed", "contradicted")

# Retracted findings are NOT tunable, and that is the point. A Changed entry is
# the register owner's own statement that the wording is no longer true; letting
# a config downgrade it to 'warn' would be a per-claim waiver by the back door,
# and §6 of the skill says there is no per-claim waiver. Staleness IS tunable,
# because how fast a fact rots is genuinely domain-specific — a price moves in
# weeks, a founding date never does.
RETRACTED_SEVERITY = "error"

STALENESS_RULE = (
    "'staleness' may set 'max_age_days' (positive integer), 'severity' "
    "(error|warn) and 'require_checked' (boolean). All three are printed on "
    "every run: a long max_age_days is a weakening and has to be visible in the "
    "same output as the verdict it produced."
)


class ConfigRefused(Exception):
    """A config that oversteps what a config may set (see CONFIG_RULE)."""


class Finding(NamedTuple):
    line: int
    category: str
    span: str
    severity: str
    col: int = 0
    note: str = ""


class RetractedEntry(NamedTuple):
    """A claim the register says is no longer sayable, and why."""

    claim: str
    state: str  # "changed" | "contradicted"
    reason: str
    line: int = 0


class Register:
    """Cleared claims with their check dates, plus the retracted ones.

    ITERABLE OVER THE CLEARED TEXT, so anything that previously received a set
    of cleared strings still works when handed a Register. That compatibility is
    load-bearing rather than cosmetic: console/tests/lint-vectors.json hands
    lint_text() a bare list, and those vectors are the only thing holding this
    file and console/src/lint.js to the same answer.
    """

    def __init__(self, cleared=None, retracted=None):
        # {cleared text (lowercased) -> datetime.date | None}
        self.cleared = dict(cleared or {})
        self.retracted = list(retracted or [])

    def __iter__(self):
        return iter(self.cleared)

    def __len__(self):
        return len(self.cleared)

    def __contains__(self, item):
        return item in self.cleared

    @property
    def undated(self):
        return [text for text, when in self.cleared.items() if when is None]


def _coerce_register(register):
    """Accept a Register, a mapping, or a bare set/list of cleared strings."""
    if isinstance(register, Register):
        return register
    if isinstance(register, dict):
        return Register(cleared=register)
    return Register(cleared={str(entry).lower(): None for entry in (register or [])})


def _split_checked(entry):
    """(entry without its ' — checked:' tail, parsed date or None, raw tail).

    The tail is REMOVED from the text that goes into the cleared set. It has to
    be: sourcing is containment of the draft's words inside a cleared entry, so
    leaving '2026-08-18' in the entry would let any draft mentioning that date
    ride in on a claim that merely happened to be checked that day. The metadata
    about a claim is not part of the claim.
    """
    lowered = entry.lower()
    at = lowered.rfind(CHECKED_SUFFIX.lower())
    if at == -1:
        return entry, None, ""
    head = entry[:at]
    tail = entry[at + len(CHECKED_SUFFIX):].strip()
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})\b", tail)
    if not match:
        return head, None, tail
    try:
        return head, date(*(int(part) for part in match.groups())), tail
    except ValueError:
        return head, None, tail


def _as_date(value):
    """A date from a date, an ISO 'YYYY-MM-DD' string, or None."""
    if value is None or isinstance(value, date):
        return value
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(value).strip())
    if not match:
        raise ValueError(f"expected a YYYY-MM-DD date, got {value!r}")
    return date(*(int(part) for part in match.groups()))


def load_register(path, on_warning=None):
    """Return a Register parsed from a truth register file.

    A Cleared bullet without a ' — source:' suffix is MALFORMED and is excluded.
    An unsourced register entry must not be able to source anything — otherwise
    the register becomes a place to launder a number by writing it down. A
    Changed or Contradicted bullet without a ' — reason:' suffix is malformed for
    the same reason, read the other way round: a retraction that does not say
    what replaced the claim is not a retraction anyone can act on.
    """
    warn = on_warning or (lambda message: print(message, file=sys.stderr))
    register = Register()
    if not Path(path).exists():
        return register
    section = None
    for lineno, raw in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if line.lower().startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.startswith("- "):
            continue
        entry = line[2:].strip()
        if section == "cleared":
            if SOURCE_SUFFIX.lower() not in entry.lower():
                warn(
                    f"claim-lint: WARNING: {Path(path)}:{lineno}: malformed Cleared "
                    "entry, no 'source:' suffix (the template's em-dash form); "
                    f"IGNORED, it sources nothing: {entry!r}"
                )
                continue
            text, checked, tail = _split_checked(entry)
            if tail and checked is None:
                warn(
                    f"claim-lint: WARNING: {Path(path)}:{lineno}: unparseable "
                    f"'checked:' date {tail!r}, expected YYYY-MM-DD; the entry still "
                    "sources, but it is treated as NEVER CHECKED."
                )
            key = text.lower()
            # Duplicates keep the NEWEST date. The oldest would be the safer
            # default for a claim's age, but a register with the same claim
            # written twice has one of them re-verified, and reporting the stale
            # copy would report a line the maintainer already fixed.
            previous = register.cleared.get(key)
            if key not in register.cleared or (
                checked is not None and (previous is None or checked > previous)
            ):
                register.cleared[key] = checked
        elif section in RETRACTED_SECTIONS:
            lowered = entry.lower()
            at = lowered.find(REASON_SUFFIX.lower())
            if at == -1:
                warn(
                    f"claim-lint: WARNING: {Path(path)}:{lineno}: malformed "
                    f"{section.title()} entry, no 'reason:' suffix; IGNORED. A "
                    "retraction that does not say what replaced the claim cannot be "
                    f"acted on: {entry!r}"
                )
                continue
            claim = entry[:at].strip()
            if not claim:
                warn(
                    f"claim-lint: WARNING: {Path(path)}:{lineno}: {section.title()} "
                    "entry has a reason but no claim text before it; IGNORED."
                )
                continue
            register.retracted.append(
                RetractedEntry(
                    claim=claim,
                    state=section,
                    reason=entry[at + len(REASON_SUFFIX):].strip(),
                    line=lineno,
                )
            )
    return register


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


def _flatten(text):
    """(whitespace-collapsed text, index map back into the original).

    Retracted claims are matched against this, NOT line by line. A withdrawn
    sentence that a draft happens to hard-wrap across two lines is still the
    withdrawn sentence, and a line-scoped search would pass it clean — a false
    negative, which is the failure this whole tool exists to prevent. Collapsing
    runs of whitespace to one space and keeping the offsets lets one match span
    a line break and still report the line it started on.
    """
    chars = []
    offsets = []
    previous_was_space = False
    for index, char in enumerate(text):
        if char.isspace():
            if previous_was_space:
                continue
            chars.append(" ")
            previous_was_space = True
        else:
            chars.append(char)
            previous_was_space = False
        offsets.append(index)
    return "".join(chars), offsets


def find_retracted(text, retracted):
    """Findings for draft text that still says something the register withdrew.

    This runs INDEPENDENTLY of claim-shaped detection, and that independence is
    the point. "We serve enterprise customers directly" carries no number, no
    superlative and no quote, so every detector in find_claims() passes it — yet
    if the register's Changed section says that wording was superseded, shipping
    it is a worse failure than any unsourced statistic, because the register
    already knows it is wrong.
    """
    cleaned = strip_noise(text)
    flat, offsets = _flatten(cleaned)
    lowered = flat.lower()
    findings = []
    for entry in retracted:
        needle = " ".join(entry.claim.split()).lower()
        if not needle:
            continue
        pattern = r"(?<!\w)" + re.escape(needle) + r"(?!\w)"
        for match in re.finditer(pattern, lowered):
            origin = offsets[match.start()]
            line = cleaned.count("\n", 0, origin) + 1
            col = origin - (cleaned.rfind("\n", 0, origin) + 1)
            findings.append(
                Finding(
                    line=line,
                    category="retracted",
                    span=flat[match.start():match.end()],
                    severity=RETRACTED_SEVERITY,
                    col=col,
                    note=(
                        f"register marks this {entry.state.upper()} "
                        f"(truth.md:{entry.line}) — {entry.reason}"
                    ),
                )
            )
    return findings


def _staleness_note(checked, settings, today):
    """Why this cleared entry should not be leaned on, or None if it is fine."""
    if checked is None:
        if settings.get("require_checked"):
            return (
                "sourced but NEVER dated; add ' — checked: YYYY-MM-DD' to its "
                "register entry or re-verify it"
            )
        return None
    age = (today - checked).days
    limit = settings.get("max_age_days", DEFAULT_CONFIG["staleness"]["max_age_days"])
    if age > limit:
        return (
            f"last checked {checked.isoformat()}, {age} days ago (limit {limit}); "
            "re-fetch the source before shipping this"
        )
    return None


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
    return _matching_entry(text, register) is not None


def _matching_entry(text, register):
    """The cleared entry that sources this text, or None.

    The same comparison as _is_sourced() and deliberately one function rather
    than two: which entry matched is what tells staleness WHOSE date to read,
    and a second copy of this rule is a second place for it to drift.
    """
    needle = text.strip().lower().rstrip(".")
    if not needle:
        return None
    # LOWERCASED HERE, not left to the caller. load_register() lowercases at
    # load, so the CLI path was fine, but lint_text() is public and a caller
    # handing it a register in original case got silent false positives. The
    # JS twin had exactly this bug on its CLI path. Whoever owns the comparison
    # owns the normalisation.
    for cleared in register:
        if _contains_bounded(str(cleared).lower(), needle):
            return cleared
    return None


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


# Markdown structure is not part of a claim.
#
# FOUND BY RUNNING IT. A claim copied verbatim out of truth.md's Cleared
# section passed as a bare sentence and failed the moment it became a bullet:
#
#       Standard $79, Pro $149, Elite $249, one-time    -> clean
#     - Standard $79, Pro $149, Elite $249, one-time    -> 3 errors
#
# _is_sourced() asks whether the whole LINE sits inside a cleared entry, and
# "- " does not. Table cells broke identically, because the pipes are part of
# the line too. Most marketing copy is bullets and tables, so nearly every
# correctly sourced number in a real draft was being flagged.
#
# WHY THIS DOES NOT OPEN A HOLE. Every context below is a genuine substring of
# the claim as written, never the bare span: a context equal to the span alone
# is refused, for the same reason _span_window() falls back to the whole line
# rather than degrading to the token. Splitting a row into cells is the correct
# reading rather than a loosening: a row holds several independent statements,
# so a sourced price in one cell does not vouch for an invented figure in the
# next.
#
# Mirrored exactly in console/src/lint.js. The vector file holds both to one
# answer.
MD_PREFIX = re.compile(r"^(?:\s*(?:[-*+]|\d+[.)])\s+|\s*>+\s*|\s*#{1,6}\s+)+")


def _strip_markdown_prefix(line):
    """(text, offset) with any list, quote or heading marker removed, or None."""
    match = MD_PREFIX.match(line)
    if not match or not match.group(0):
        return None
    return line[match.end():], match.end()


def _table_cell_at(line, col):
    """(text, offset) of the table cell containing col, or None."""
    if "|" not in line:
        return None
    before = line.rfind("|", 0, max(col, 0))
    after = line.find("|", col)
    start = 0 if before == -1 else before + 1
    end = len(line) if after == -1 else after
    if start >= end:
        return None
    return line[start:end], start


def _sourcing_contexts(line, col, span):
    """Every context a span may be judged in, widest first."""
    contexts = []

    def add(text, offset):
        trimmed = text.strip()
        # A bare span is not evidence of sourcing. Same rule as _span_window().
        if not trimmed or trimmed == span:
            return
        contexts.append(text)
        window = _span_window(text, col - offset, span)
        if window != text:
            contexts.append(window)

    add(line, 0)
    stripped = _strip_markdown_prefix(line)
    if stripped:
        add(stripped[0], stripped[1])

    cell = _table_cell_at(line, col)
    if cell:
        add(cell[0], cell[1])
        cell_stripped = _strip_markdown_prefix(cell[0])
        if cell_stripped:
            add(cell_stripped[0], cell[1] + cell_stripped[1])
    return contexts


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


def lint_text(text, register, config, today=None):
    """Findings for claims that are unsourced, gone stale, or already withdrawn.

    Three questions, asked in that order, because they are three different
    failures and only the first one was ever asked before:

    1. UNSOURCED — nothing in the register backs this. (find_claims)
    2. STALE — something backs it, but nobody has re-verified it recently
       enough to be shipping it today.
    3. RETRACTED — the register itself says this wording was superseded or is
       contradicted. Checked over the whole draft, not just claim-shaped spans.
    """
    register = _coerce_register(register)
    settings = {**DEFAULT_CONFIG["staleness"], **(config.get("staleness") or {})}
    today = _as_date(today) or date.today()
    lines = text.splitlines()
    out = []
    reported_stale = set()
    for finding in find_claims(text, config):
        source_line = lines[finding.line - 1] if finding.line <= len(lines) else ""
        contexts = _sourcing_contexts(source_line, finding.col, finding.span)
        entry = None
        for context in contexts:
            entry = _matching_entry(context, register.cleared)
            if entry is not None:
                break
        if entry is None:
            out.append(finding)
            continue
        note = _staleness_note(register.cleared.get(entry), settings, today)
        # One stale finding per (line, entry). A sentence quoting three numbers
        # from one register line has one problem, not three.
        if note is None or (finding.line, entry) in reported_stale:
            continue
        reported_stale.add((finding.line, entry))
        out.append(
            finding._replace(
                category="stale",
                severity=settings.get("severity", "warn"),
                note=note,
            )
        )
    out.extend(find_retracted(text, register.retracted))
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


PORTABLE_GROUP_PREFIXES = ("(?:", "(?=", "(?!", "(?<=", "(?<!", "(?P<")

NONPORTABLE_RULE = (
    "An ignore pattern must mean the same thing to every implementation of this "
    "linter. console/src/lint.js answers the same question in a browser, and a "
    "pattern the two regex engines read differently would blank a different region "
    "depending on which one ran — two answers to one question, which is the exact "
    "failure this tool exists to prevent."
)

CLASS_ESCAPE_REFUSAL = (
    "\\W, \\D, \\S and \\B inside a character class are not portable between Python "
    "and JavaScript: Python's class escapes are Unicode-aware, JavaScript's are "
    "ASCII-only, and JavaScript cannot negate a class inside a class at all. "
    + NONPORTABLE_RULE
    + " Write the characters out explicitly instead — [A-Za-z_] rather than [^\\W\\d]."
)


def assert_portable_ignore(pattern):
    """Refuse an ignore pattern that Python and JavaScript do not read alike.

    This is the twin of pythonRegexToJs() in console/src/lint.js, and it exists
    because the two implementations must accept the SAME configs. A config the
    CLI takes and the console rejects means the two are not interchangeable, and
    'interchangeable' is the whole claim the shared vector file is making.

    The class-escape case is the dangerous one and the reason this function is
    not merely a nicety: `[^\\W\\d]` COMPILES in both engines and MEANS something
    different in each, so it is the only construct here that fails silently
    rather than loudly. The rest are refused so the accepted set matches.
    """
    in_class = False
    opened_at = -1
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            following = pattern[index + 1] if index + 1 < len(pattern) else ""
            if in_class and following in ("W", "D", "S", "B"):
                raise ConfigRefused(
                    f"ignore pattern {pattern!r} uses \\{following} inside a "
                    f"character class. {CLASS_ESCAPE_REFUSAL}"
                )
            if following in ("p", "P"):
                raise ConfigRefused(
                    f"ignore pattern {pattern!r} uses the Unicode property escape "
                    f"\\{following}{{...}}, which is not portable between Python "
                    f"and JavaScript: JavaScript compiles it and Python's re module "
                    f"cannot. {NONPORTABLE_RULE} Write the characters out explicitly "
                    "instead."
                )
            index += 2
            continue
        if in_class:
            # Python reads a ']' in first position as a literal member.
            first = index == opened_at + 1 or (
                index == opened_at + 2 and pattern[opened_at + 1] == "^"
            )
            if char == "]" and not first:
                in_class = False
            index += 1
            continue
        if char == "[":
            in_class = True
            opened_at = index
            index += 1
            continue
        if pattern.startswith("(?", index) and not pattern.startswith(
            PORTABLE_GROUP_PREFIXES, index
        ):
            raise ConfigRefused(
                f"ignore pattern {pattern!r} uses the group construct "
                f"{pattern[index:index + 4]!r}, which is not portable between "
                f"Python and JavaScript. {NONPORTABLE_RULE} Use (?:...) or one of "
                "the lookaround forms both engines share."
            )
        if char in "*+?}" and pattern[index + 1:index + 2] == "+":
            raise ConfigRefused(
                f"ignore pattern {pattern!r} uses the possessive quantifier "
                f"{pattern[index:index + 2]!r}, which is not portable between "
                f"Python and JavaScript: JavaScript has no possessive quantifiers "
                f"and refuses to compile it. {NONPORTABLE_RULE} Use a plain or lazy "
                "quantifier instead."
            )
        index += 1
    if in_class:
        raise ConfigRefused(
            f"unterminated character class in ignore pattern {pattern!r}"
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
        assert_portable_ignore(pattern)
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
    validate_staleness(config.get("staleness", {}))


def validate_staleness(settings):
    """Refuse a staleness block that is nonsense — but never one that is merely lax.

    A max_age_days of 100000 retires the staleness check as surely as a wide
    ignore retires a category, and it is refused for exactly as long as a wide
    ignore is: not at all. The defence is the same one, and the only honest one
    available — describe_config() prints all three settings on every run, so a
    register nobody re-checks is visible in the same output as its green verdict.
    """
    if not isinstance(settings, dict):
        raise ConfigRefused(f"'staleness' must be an object. {STALENESS_RULE}")
    unknown = set(settings) - {"max_age_days", "severity", "require_checked"}
    if unknown:
        raise ConfigRefused(
            f"unknown staleness key(s) {', '.join(sorted(unknown))}. "
            f"{STALENESS_RULE}"
        )
    if "max_age_days" in settings:
        age = settings["max_age_days"]
        if isinstance(age, bool) or not isinstance(age, int) or age < 1:
            raise ConfigRefused(
                f"staleness.max_age_days must be a positive integer, got {age!r}. "
                f"{STALENESS_RULE}"
            )
    if "severity" in settings and settings["severity"] not in VALID_SEVERITIES:
        raise ConfigRefused(
            f"invalid staleness.severity {settings['severity']!r}; expected one of "
            f"{', '.join(VALID_SEVERITIES)}. {STALENESS_RULE}"
        )
    if "require_checked" in settings and not isinstance(
        settings["require_checked"], bool
    ):
        raise ConfigRefused(
            "staleness.require_checked must be true or false, got "
            f"{settings['require_checked']!r}. {STALENESS_RULE}"
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
    stale = {**DEFAULT_CONFIG["staleness"], **(config.get("staleness") or {})}
    return (
        f"claim-lint: config: {source} | categories: {categories}, "
        f"retracted={RETRACTED_SEVERITY} (fixed) "
        f"| staleness: max_age_days={stale['max_age_days']}, "
        f"severity={stale['severity']}, require_checked={str(stale['require_checked']).lower()} "
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
            if "staleness" in loaded:
                if not isinstance(loaded["staleness"], dict):
                    raise ConfigRefused(
                        f"'staleness' must be an object. {STALENESS_RULE}"
                    )
                merged["staleness"] = {
                    **DEFAULT_CONFIG["staleness"],
                    **loaded["staleness"],
                }
            validate_config(merged)
            return merged, str(candidate)
    validate_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG, "built-in defaults"


def lint_path(target, register, config, today=None):
    """Lint a file or, for a directory, every markdown/text file beneath it."""
    target = Path(target)
    files = [target] if target.is_file() else sorted(
        p for p in target.rglob("*") if p.suffix.lower() in SCAN_SUFFIXES
    )
    results = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for finding in lint_text(text, register, config, today=today):
            results.append((path, finding))
    return results


def describe_register(register, settings, today):
    """One line naming what the register actually holds, printed on every run.

    A register is not a static asset — it rots. A run that says nothing about
    how much of the register is undated or overdue lets a green verdict stand in
    for a register nobody has touched in a year.
    """
    register = _coerce_register(register)
    undated = len(register.undated)
    overdue = sum(
        1
        for when in register.cleared.values()
        if when is not None and (today - when).days > settings["max_age_days"]
    )
    return (
        f"claim-lint: register: {len(register.cleared)} cleared "
        f"({undated} undated, {overdue} past {settings['max_age_days']}d), "
        f"{len(register.retracted)} retracted"
    )


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
    parser.add_argument(
        "--today",
        default=None,
        metavar="YYYY-MM-DD",
        help="Treat this as today's date when ageing the register (default: today)",
    )
    args = parser.parse_args(argv)

    try:
        today = _as_date(args.today) or date.today()
    except ValueError as exc:
        print(f"claim-lint: {exc}", file=sys.stderr)
        return 2

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
    settings = {**DEFAULT_CONFIG["staleness"], **(config.get("staleness") or {})}
    print(describe_register(register, settings, today), file=sys.stderr)
    results = lint_path(target, register, config, today=today)

    errors = 0
    for path, finding in results:
        if finding.severity == "error":
            errors += 1
        if finding.category == "retracted":
            headline = f"RETRACTED claim still in the copy: {finding.span!r}"
        elif finding.category == "stale":
            headline = f"stale source for: {finding.span!r}"
        else:
            headline = f"unsourced {finding.category}: {finding.span!r}"
        detail = f" — {finding.note}" if finding.note else ""
        print(f"{path}:{finding.line}: {finding.severity}: {headline}{detail}")

    if not results:
        print("claim-lint: no unsourced, stale or retracted claims found.")
    elif errors:
        retracted = sum(1 for _, f in results if f.category == "retracted")
        tail = (
            f" {retracted} of them "
            f"{'is' if retracted == 1 else 'are'} RETRACTED — the register already "
            "says that wording is superseded or contradicted, so the fix is the "
            "copy, not the register."
            if retracted
            else ""
        )
        print(
            f"\nclaim-lint: {errors} claim(s) failed. "
            "Source them in .monkeys/truth.md or cut them. There is no per-finding "
            "waiver flag; an 'ignore' pattern silences by shape, and every one in "
            f"effect is printed in the config line above.{tail}",
            file=sys.stderr,
        )

    if args.report:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
