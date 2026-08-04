---
name: fortress-truth
description: Use before stating any fact, statistic, or comparison publicly, before writing marketing copy, before verifying a claim, or when setting up claim discipline for a repo. Installs and runs a linter that blocks unsourced claim-shaped language.
---

# fortress-truth

FORTRESS doctrine: **Build what can't be taken.** A claim you cannot source is a claim that can be taken apart — by a competitor, a reviewer, or reality. If you have bullshit inside of it, bullshit comes out of it. This skill is how the bullshit stays out.

## 1. The rule

Every public claim traces to a line under **Cleared** in the truth register, or it does not ship.

- Never invent a stat, a testimonial, or a user count. Not as a placeholder, not "to be confirmed later" — copy with an invented number in it does not go out, ever.
- Before every batch of public-facing copy, re-fetch the canonical source. Never write from memory of a site, a dashboard, or a document you read last week. Numbers move; your memory of them doesn't.
- If a fact is not in **Cleared**, it is either moved there with a source, or it is cut from the copy. There is no third option.

## 2. The register format

The register lives at `.monkeys/truth.md` by default. The linter parses it — the format below is not a suggestion, it is the grammar the parser reads.

```markdown
# Truth Register

Every public claim traces to a line under **Cleared**, or it does not ship.
The linter parses this file. Keep the format exactly.

## Cleared

<!-- One bullet per fact, in this exact shape. A bullet without the " — source:" -->
<!-- suffix is malformed: the linter ignores it, and it sources nothing. -->
<!-- - <the claim, exactly as it will appear in copy> — source: <where this was verified> -->

## Uncleared

<!-- Facts that may NOT be stated publicly without re-verification. -->
<!-- - <the fact> — reason: <why it is not cleared> -->

## Canonical source

<!-- The URL or location to re-fetch before every copy batch. Never write from memory of it. -->
```

Copy this file to `.monkeys/truth.md` in the adopter's repo (create the `.monkeys/` directory if it doesn't exist) and start filling in **Cleared** as facts get sourced. Each bullet the linter reads is matched word-bounded against your draft text — write the fact in full, not a keyword fragment.

The ` — source:` suffix is **enforced, not decorative.** A **Cleared** bullet without it is treated as malformed: the linter drops it from the cleared set and prints a warning naming the line. An unsourced register entry cannot source anything — otherwise the register would be a place to launder a number by writing it down.

Two more things the linter will not let a register do:

- **A bare number does not clear itself in another context.** A cleared entry vouches for a matched span only together with the **next three words** that follow it in the draft. Cleared `97 downloads all-time — source: …` sources the sentence "We have 97 downloads all-time." and does **not** source "Our platform serves 97 million requests a day." The digits are not the claim; the phrase is.
- **Write the claim as it will appear in copy.** The consequence of the rule above is that re-phrasing needs re-clearing: a cleared phrase followed by unfamiliar words in the draft flags. That is the safe direction of error — a noisy flag costs you one line of register, an unsourced number costs you your credibility. Fragments make the register weaker, not more flexible.

## 3. The banned move

The motte-and-bailey fallacy is banned outright: never advertise the bold claim and retreat to the modest one when challenged.

Example of the fallacy: advertise **"AI-powered"** (the bailey — bold, attractive, hard to defend), and when someone asks what that means, retreat to **"it has autocomplete"** (the motte — narrow, defensible, true but not what was advertised). The reader who saw the ad never sees the retreat. They bought the bailey.

FORTRESS is named for the honest version of this structure: a motte worth defending, advertised as exactly what it is. **Use the castle, never the fallacy.** If a claim needs a retreat position to survive a challenge, the claim itself is wrong — narrow it before it ships, don't narrow it after someone calls it out.

## 4. What it installs

Two different roots are in play, and confusing them is why a cold run fails. **Sources** live inside the installed plugin, addressed with `${CLAUDE_PLUGIN_ROOT}`. **Destinations** are relative to the **adopter's repo root** — the directory the agent is working in.

| Read from (plugin root) | Write to (adopter's repo root) |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/claim_lint.py` | `tools/monkeys/claim_lint.py` |
| `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/truth.config.json` | `tools/monkeys/truth.config.json` |
| `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/truth.template.md` | `.monkeys/truth.md` (only if the adopter has no register yet — never overwrite an existing one) |

A bare `skills/fortress-truth/assets/...` path resolves against the adopter's working directory, where the plugin is not checked out, so it will not be found.

`tools/monkeys/` is a plain directory of committed files, not a package. No install step, no dependency resolution — the linter is Python 3 standard library only.

## 5. Running it

```bash
python tools/monkeys/claim_lint.py <draft-or-dir>
```

`<draft-or-dir>` is a single file or a directory; a directory is scanned recursively for `.md`, `.markdown`, `.mdx`, `.txt`, `.rst`, `.html`, and `.htm` files. A store listing or a landing page is copy like any other, and it does not get a green pass for being HTML. `.json` is deliberately **not** scanned: it is rarely prose, and scanning it produced findings on keys and ids rather than on claims.

Flags:

| Flag | Effect |
|---|---|
| `--register <path>` | Path to the truth register. Default: `.monkeys/truth.md`. |
| `--config <path>` | Path to `truth.config.json`. Default: `tools/monkeys/truth.config.json` if present, else built-in defaults. |
| `--report` | Print findings without failing — always exits 0. Use for a survey pass, not a gate. |

Exit codes:

| Code | Meaning |
|---|---|
| `0` | No error-severity findings, or `--report` was passed. |
| `1` | At least one error-severity finding (`number`, `magnitude`, `superlative`, `comparative`, `testimonial`). |
| `2` | The target path or the register file does not exist, **or the config was refused** (see §6). |

Every run prints one line to stderr naming the active config before it scans anything:

```
claim-lint: config: tools/monkeys/truth.config.json | categories: absolute=warn, comparative=error, magnitude=error, number=error, superlative=error, testimonial=error | ignore patterns: 1: \b\d{4}-\d{2}-\d{2}\b|\b(?:\d{1,2}\s+)?(?:January|February|…|Dec)\.?\s+(?:\d{1,2},?\s+)?\d{4}\b
```

(The month alternation is elided here for width. It is printed in full on every real run — the whole point of the line is that nothing about the tuning is abbreviated where it matters.)

Every ignore pattern in effect is printed **in full**, not counted. That is deliberate and it is load-bearing: an ignore regex can retire a whole category — `\d+` silences every number as surely as `.*` silences everything — and no validator can judge for you whether a given regex is too broad. Printing them is the defence, because the weakening then appears in the same output as the verdict it produced.

A gate that can be tuned has to say how it is currently tuned. Read that line before trusting a green run — an all-clear from a config you have not read is not evidence of anything.

### The detection categories

| Category | Severity | Detects |
|---|---|---|
| `number` | `error` | Digits and percentages: `4200`, `40,000`, `4.5`, `18%`. **A bare year is included** — see below. |
| `magnitude` | `error` | Quantities written as words: `forty thousand`, `one million`, `hundreds of`, `millions of`, `dozens of`, `scores of`, `a handful of`, `countless`, `numerous`, and a number word quantifying a plural noun (`forty paying customers`). |
| `superlative` | `error` | `best`, `worst`, `fastest`, `only`, `first`, `largest`, `most`, `leading`, `number one`, `#1`. |
| `comparative` | `error` | `better than`, `more X than`, `unlike`, `compared to`, `outperforms`. |
| `testimonial` | `error` | Quote-shaped spans of 20+ characters: straight or curly **double** quotes, **single** quotes, and a markdown **blockquote** line. |
| `absolute` | `warn` | `never`, `always`, `guaranteed`, `nobody`, `no one`, `everyone`, `zero`. |

`absolute` findings are `warn` severity — they print but never fail the run. Every other category is `error` severity and fails the run when unsourced.

**A bare year is a claim.** `Founded in 2024` is a factual assertion about a company and belongs in the register like any other. Only genuine **date formats** are exempt: ISO (`2026-08-04`) and written (`January 2024`, `12 March 2026`, `March 12, 2026`). The exemption used to be `\b(?:19|20)\d{2}\b`, which was meant to silence dates and in fact exempted every integer from 1900 to 2099 — so `Over 2000 people signed up.` and `We processed 1999 orders.` passed clean. Round numbers in that range are exactly the shape an invented stat takes.

**A stat does not stop being a stat when it is spelled out.** That is what `magnitude` is for. It is deliberately narrower than every number word in English: `one` and `two` are matched only in front of an explicit magnitude word (`one million users` flags; `one place to look` does not), because a linter that fires on ordinary prose gets switched off, and a switched-off linter is itself a false negative.

Run it before any copy goes public: PR checks on marketing content, a pre-publish hook, or by hand before pasting into a post.

## 6. No per-claim waivers — and exactly what the config can still do

There is **no per-finding waiver.** No `--waive` flag, no expiry date, no "fix it next sprint" for a claim. A size-budget guard can permit an expiring waiver, because size debt is negotiable — a slightly-too-long file still works. A factual claim is not negotiable in the same way: an unsourced "fastest" doesn't get temporarily worse if you ship it; it's either true and sourced, or it's a lie with a deadline attached. **Sourced or cut.**

`truth.config.json` is the one place that could quietly become a waiver anyway, so be precise about what is enforced and what is not. **The code enforces exactly this, and nothing more:**

| Enforced | How |
|---|---|
| Detection patterns cannot be edited | a `patterns` key in a config **exits 2**. Otherwise a regex that can never match (`$^`) would switch a category off while the output still said `number=error`. |
| The run cannot be made incapable of failing | a `severity` map with every category `warn` **exits 2**. |
| A severity typo cannot silently downgrade | any value other than `error`/`warn` (`"eror"`) **exits 2**. |
| The obvious blanket ignores are rejected | `.*`, `.+`, `^.*$`, `(.*)`, and any pattern matching the empty string **exit 2**; so does an ignore that is not a valid regex. |
| Every weakening is visible | all ignore patterns in effect are **printed in full on every run**. |

**Not enforced, stated plainly — this list is the honest half of the guarantee:**

- An ignore pattern can narrow detection. That is what it is for, and a broad one narrows a category to nothing: `{"ignore": ["\\d+"]}` retires the whole `number` category and the run exits 0.
- The blanket-ignore check catches the shapes people actually type, **not every possible equivalent.** `[\s\S]+` suppresses every category and is not rejected, because it does not match the empty string. Deciding in general whether a regex is "too broad" is not something a checker can do, and one that claimed to would be making a claim it cannot source — the exact move this skill exists to stop.

So the check is a guard against the careless config, not a defence against a determined one. The real defence is the printed line: **an ignore you can see is an ignore someone can question.** Read it before you trust a green run.

So the honest statement of the guarantee is: **patterns are fixed, severities are constrained, ignores are your responsibility and are printed in every run.** If a run is green, read the config line before you believe it. If someone widened an ignore, it is in the output — that is the protection, not a promise that nobody can widen one.

## 7. The honest caveat

The linter flags claim-shaped language; the register arbitrates. No script can know whether "fastest" is **true** — only whether it is **sourced**. Regex matches a shape, not a fact. A finding means "this looks like a claim and nothing in the register backs it" — it is not a verdict on truth, and it is not proof of falsehood either. The human (or the agent doing the sourcing work) still has to go verify the number and write it into **Cleared** with a real source.

A guard that implied otherwise — that a clean lint run means the copy is true — would itself be the exact overclaiming this skill exists to stop. Don't market this tool, or describe it to a user, as verifying truth. It verifies sourcing. Say that plainly.

## 8. Tuning

False positives happen: a build number, a SKU that looks like a bare number, an issue id. Fix these by adding a pattern to `ignore` in `truth.config.json`. The detection patterns themselves are not editable — a `patterns` key exits 2 — so the ignore list is the whole tuning surface, and **how tight you keep it is the whole of the discipline.** Write the narrowest pattern that clears the specific false positive: `\b4471\b`, not `\d+`. A lazy-wide ignore reopens the exact hole this skill exists to close, and the only thing standing between that and a false all-clear is that the pattern is printed on every run for someone to notice.

**An ignore pattern blanks the region of text it matches, before detection runs.** It also drops any finding whose span it fullmatches, so a pattern written against a span still works. Blanking the region is what makes a **multi-token** exemption expressible at all: the number detector splits `2026-08-04` into the three spans `2026`, `08` and `04`, so a span-only check could never silence a date with one pattern no matter how it was written. That is why the shipped date exemption works and why the old year ignore never covered ISO dates.

The practical consequence is that an ignore is **wider than it looks** — it removes text from the scan, not just one finding. Check what the span actually is before writing the pattern; the finding prints it:

```
draft.md:1: error: unsourced number: '4471'
```

That finding is silenced by `"\\b4471\\b"`, which blanks exactly those four characters. A pattern describing the surrounding sentence would blank the sentence — including any other claim in it.

The shipped `ignore` list contains one entry: an alternation matching **genuine date formats only**, ISO (`\d{4}-\d{2}-\d{2}`) and written (a month name adjacent to a year). Two things it deliberately does **not** cover:

- **Bare years are not ignored.** `Founded in 2024` flags, by design — it is a factual assertion and it belongs in the register. The previous entry, `\b(?:19|20)\d{2}\b`, was written to silence dates and instead exempted every integer from 1900 to 2099.
- **Version strings are not ignored.** In `v2.3.1` the detector matches the span `3.1`, so no `v`-prefixed pattern can ever fire on it, and a pattern loose enough to catch `3.1` (`\d+\.\d+`) would also swallow `4.5 stars` and every other decimal claim in your copy. That trade is a false negative, which is the failure this tool exists to prevent — so the honest options are to source the version string in the register or to accept the finding, not to bolt on an ignore that costs more than it saves.

One known noise source, stated rather than hidden: the double-quote testimonial pattern is not line-bounded, so a single unpaired `"` in a document can produce one very large span running to the next quote character. It is left that way on purpose — bounding it to a single line would miss a testimonial that is hard-wrapped across two, and a missed testimonial is the failure mode this tool exists to prevent. Noise you can see is the safer side of that trade.
