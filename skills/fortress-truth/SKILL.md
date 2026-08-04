---
name: fortress-truth
description: Use before stating any fact, statistic, or comparison publicly, before writing marketing copy, before verifying a claim, or when setting up claim discipline for a repo. Installs and runs a linter that blocks unsourced claim-shaped language.
---

# fortress-truth

FORTRESS doctrine: build what can't be taken. A claim you cannot source is a claim that can be taken apart — by a competitor, a reviewer, or reality. If you have bullshit inside of it, bullshit comes out of it. This skill is how the bullshit stays out.

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

<!-- One bullet per fact. Must end with " — source: <where it came from>". -->
<!-- Example: - 97 downloads all-time — source: analytics dashboard, 2026-08-04 -->

## Uncleared

<!-- Facts that may NOT be stated publicly without re-verification. -->
<!-- Must end with " — reason: <why it is not cleared>". -->
<!-- Example: - community member counts — reason: third-party, conflicting figures -->

## Canonical source

<!-- The URL or location to re-fetch before every copy batch. Never write from memory of it. -->
```

Copy this file to `.monkeys/truth.md` in the adopter's repo (create the `.monkeys/` directory if it doesn't exist) and start filling in **Cleared** as facts get sourced. Each bullet the linter reads is matched word-bounded against your draft text — write the fact in full, not a keyword fragment.

## 3. The banned move

The motte-and-bailey fallacy is banned outright: never advertise the bold claim and retreat to the modest one when challenged.

Example of the fallacy: advertise **"AI-powered"** (the bailey — bold, attractive, hard to defend), and when someone asks what that means, retreat to **"it has autocomplete"** (the motte — narrow, defensible, true but not what was advertised). The reader who saw the ad never sees the retreat. They bought the bailey.

FORTRESS is named for the honest version of this structure: a motte worth defending, advertised as exactly what it is. **Use the castle, never the fallacy.** If a claim needs a retreat position to survive a challenge, the claim itself is wrong — narrow it before it ships, don't narrow it after someone calls it out.

## 4. What it installs

Copy from this skill's `assets/` into the adopter's repo:

- `assets/claim_lint.py` → `tools/monkeys/claim_lint.py`
- `assets/truth.config.json` → `tools/monkeys/truth.config.json`
- `assets/truth.template.md` → `.monkeys/truth.md` (only if the adopter has no register yet — never overwrite an existing one)

`tools/monkeys/` is a plain directory of committed files, not a package. No install step, no dependency resolution — the linter is Python 3 standard library only.

## 5. Running it

```bash
python tools/monkeys/claim_lint.py <draft-or-dir>
```

`<draft-or-dir>` is a single file or a directory; a directory is scanned recursively for `.md`, `.markdown`, and `.txt` files.

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
| `1` | At least one error-severity finding (`number`, `superlative`, `comparative`, `testimonial`). |
| `2` | The target path or the register file does not exist. |

`absolute` findings (`never`, `always`, `guaranteed`, `nobody`, `no one`, `everyone`, `zero`) are `warn` severity — they print but never fail the run. Every other category is `error` severity and fails the run when unsourced.

Run it before any copy goes public: PR checks on marketing content, a pre-publish hook, or by hand before pasting into a post.

## 6. No waivers

A size-budget guard can permit an expiring waiver — size debt is negotiable, a slightly-too-long file still works. A factual claim is not negotiable in the same way. An unsourced "fastest" doesn't get temporarily worse if you ship it; it's either true and sourced, or it's a lie with a deadline attached. There is no `--waive` flag, no expiry date, no "fix it next sprint" for a claim. **Sourced or blocked.** Cut the claim or source it — those are the only two moves.

## 7. The honest caveat

The linter flags claim-shaped language; the register arbitrates. No script can know whether "fastest" is **true** — only whether it is **sourced**. Regex matches a shape, not a fact. A finding means "this looks like a claim and nothing in the register backs it" — it is not a verdict on truth, and it is not proof of falsehood either. The human (or the agent doing the sourcing work) still has to go verify the number and write it into **Cleared** with a real source.

A guard that implied otherwise — that a clean lint run means the copy is true — would itself be the exact overclaiming this skill exists to stop. Don't market this tool, or describe it to a user, as verifying truth. It verifies sourcing. Say that plainly.

## 8. Tuning

False positives happen: a version string like `v2.3.1`, a year in running prose, a SKU that looks like a bare number. Fix these by adding a pattern to `ignore` in `truth.config.json` — never by deleting or weakening a detection category (`number`, `superlative`, `comparative`, `absolute`, `testimonial`). Loosening a category to quiet noise reopens the exact hole this skill exists to close. Narrow the ignore list instead; keep it project-specific and as tight as the false positive requires.
