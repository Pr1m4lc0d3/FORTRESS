# FORTRESS worked example

**This is fictional. Every number, claim, name, and channel below was invented for this
example. "Backlot Hot Sauce" does not exist. Nobody ferments anything for it, nobody has
bought a bottle, and `backlothotsauce.example` is not a real domain — `.example` is the
reserved TLD for exactly this purpose (RFC 2606), chosen on purpose so nobody mistakes it
for a live site. If any of the numbers below look plausible, that is the point: a worked
example that could pass for a real company's real data is the exact defect `fortress-truth`
exists to prevent, so this file says so before anything else.**

Read the files in this order — it's the order an adopter would actually produce them, and
the order that makes the payoff at the end make sense.

## 1. `.monkeys/truth.md` — the claim register

Three facts that trace to a source (`## Cleared`), and three that don't yet (`## Uncleared`,
each with a reason). Notice the two "sales figure" lines: one is checked against the real
fulfillment log (412 bottles, Cleared), and the other is a rounder, more flattering number
someone almost used instead (over a thousand, Uncleared — "does not match the fulfillment
spreadsheet"). That's the register doing its job before a draft ever gets written: catching
the gap between what sounds better and what's actually true.

## 2. `.monkeys/motte.md` — what can't be taken

Two owned assets (a domain, a mailing list), each with a `control:` and a `grows by:` —
the lever, not decoration. One `## Wanted` entry: a batch-notes archive page, not yet built.

## 3. `.monkeys/bailey.md` — rented ground, including a refusal

Two `## Active` channels, one still `cold`. And a `## Excluded` section with two real
reasons — not "not a good fit," which would just get re-proposed next session, but specific
ones: no capacity to sustain a weekly video channel, and a subscription box that would
directly contradict the one-time-purchase claim already sitting in `truth.md`. That second
one is the motte-and-bailey discipline reaching outside the linter: a channel gets excluded
not because it's a bad channel in general, but because running it would make an existing
Cleared claim false.

## 4. `draft-social-post.md` — the failure

A two-sentence social post for r/hotsauce's Saturday self-promo thread. One sentence
restates the sourced fermentation claim. The other calls the sauce "the best hot sauce on
the market" — nothing in `truth.md` clears that, and it's exactly the kind of sentence that
feels harmless to write and is genuinely a liability once it's indexed.

## 5. `lint-run-1-failing.txt` — the linter catching it, for real

This is not hand-written output. It's the literal stdout/stderr of:

```
python tools/monkeys/claim_lint.py draft-social-post.md
```

run from this directory, with `tools/monkeys/claim_lint.py` and `truth.config.json` the
same verbatim copies FORTRESS kickoff installs into a real adopter's repo. The result:

```
claim-lint: config: tools\monkeys\truth.config.json | categories: absolute=warn, comparative=error, magnitude=error, number=error, superlative=error, testimonial=error | ignore patterns: 1: \b\d{4}-\d{2}-\d{2}\b|\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?\s+(?:\d{1,2},?\s+)?\d{4}\b

claim-lint: 1 unsourced claim(s). Source them in .monkeys/truth.md or cut them. There is no per-finding waiver flag; an 'ignore' pattern silences by shape, and every one in effect is printed in the config line above.
draft-social-post.md:3: error: unsourced superlative: 'the best'

EXIT CODE: 1
```

Notice what it *didn't* flag: the $9 price, the 5oz size, and the 21-day ferment claim all
appear in the draft too, and all three are sourced in `truth.md` — the linter matched them
against the register and let them through silently. Only the one sentence with nothing
behind it failed, and the run exited non-zero because of it. That's the whole mechanism in
one real run: it isn't guessing at truth, it's checking sourcing, and it checked correctly.

## 6. `draft-social-post-fixed.md` — the fix

The fix is not a softer version of the same claim, and it is not a new `ignore` pattern in
`truth.config.json` that would make "best" stop matching. Both of those would be the
motte-and-bailey move in miniature: say the bold thing, then quietly make the checker stop
looking. What actually changed: the unsourced sentence was **cut**, and replaced with
another already-Cleared fact (the 412-bottles figure) that does the same persuasive job
truthfully.

## 7. `lint-run-2-passing.txt` — the same command, genuinely clean

```
python tools/monkeys/claim_lint.py draft-social-post-fixed.md
```

```
claim-lint: config: tools\monkeys\truth.config.json | categories: absolute=warn, comparative=error, magnitude=error, number=error, superlative=error, testimonial=error | ignore patterns: 1: \b\d{4}-\d{2}-\d{2}\b|\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\.?\s+(?:\d{1,2},?\s+)?\d{4}\b
claim-lint: no unsourced claims found.

EXIT CODE: 0
```

## Format verification

`.monkeys/truth.md`, `.monkeys/motte.md`, and `.monkeys/bailey.md` above were loaded through
the real parser at `console/src/pack.js` (`parsePack`), not eyeballed for plausibility. Result:

```
=== FORTRESS/examples/.monkeys ===
files provided: [ 'bailey.md', 'motte.md', 'truth.md' ]
missing: [ 'recon.md', 'asymmetry.md', 'campaign.md', 'numbers.md', 'sell-kit.md', 'scars.md' ]
malformed: []
unrecognised: []
```

Zero malformed entries, zero unrecognised headings. The six `missing` files are the ones
this example doesn't need to make its point (recon/asymmetry/campaign/numbers/sell-kit/
scars belong to the RAID side of the same story, or to a campaign this example doesn't run)
— `missing` is never an error in this format, only an honest statement of what isn't there.

## What this is not

This is not a claim that Backlot Hot Sauce could be a real business, and it is not a
template — copying these exact numbers into a real `truth.md` would be exactly the
invented-evidence problem this whole plugin exists to prevent. It's one run of the actual
tool, on an invented product, showing a real catch and a real fix.

See `RAID/examples/` for the same product's offensive half: recon, asymmetry, a campaign
stage, and a drafted post that never needed the claim above in the first place.
