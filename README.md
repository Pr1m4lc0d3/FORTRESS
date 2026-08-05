# FORTRESS

### `RAID` takes ground · `FORTRESS` builds what can't be taken

FORTRESS is the defensive half of **THE MAVERICK'S MONKEYS** — a pair of Claude Code plugins
that together make an agent competent at marketing a product with no budget. The taijitu splits
across the two: `RAID` is yang, light and initiating; `FORTRESS` is yin, dark and holding. Side by
side the two halves close into one circle — a raiding party with nowhere to fall back gets hunted
down, and a fortress that never raids starves. Neither half is complete alone, and neither half is
pure: `RAID` carries restraint, `FORTRESS` carries aggression.

**`RAID` is released.** This repository ships `FORTRESS`; `RAID` ships separately. Each is fully
functional alone — every skill below runs standalone — but each is one half of the doctrine, not
the whole of it. Installed together, `FORTRESS` governs what may be claimed and `RAID` governs
where to fight.

Both halves answer to the same domain: guerrilla marketing, as Levinson defined it in 1984 —
imagination, energy, and time substituted for money. `FORTRESS` specifically descends from Mao's
concept of *base areas* in **On Guerrilla Warfare**: territory an insurgency actually controls, as
distinct from the contested ground it operates in — renamed here in castle terms because they are
more legible to read cold. One honest caveat belongs up front: real insurgents do not hold
fortresses. A fixed position is exactly what a conventional force wants you to find and besiege.
That principle **inverts** in marketing. Nobody can march on a subscriber file, and a domain has no
garrison to starve out — the asymmetry that makes a fortress a liability on a real battlefield is
exactly what makes it the right metaphor for the assets that matter here. You can actually hold
this ground.

---

## The doctrine

> **Build what can't be taken.**

Every skill in this plugin, every gate, every table below — all downstream of one question:
**what can be confiscated, and what can't?** A platform can take your account. Nobody can take
your email list or your domain. A false claim confiscates your own credibility, and once a lie is
indexed you don't get to unpublish it out of the world's memory. A ban is ground seized — not a
warning, a loss.

## The thesis

> **"If you have bullshit inside of it, bullshit comes out of it."**

This is the line the whole plugin is built to make true in the negative. A marketing tool that can
hallucinate — invent a user count, fabricate a testimonial, round up a percentage that was never
measured — is not a productivity aid. It is a **liability generator**: every unsourced sentence it
produces is a claim your name is now attached to, indexed, screenshottable, and quotable back at
you the moment someone checks it against reality. Marketing content is disproportionately exposed
to this failure mode, because its entire job is to state things about a real product in public,
permanently, for an audience actively motivated to catch it wrong.

`fortress-truth` is the answer: a cleared/uncleared claim register plus a real linter,
`claim_lint.py`, that fails the build on unsourced claim-shaped language. It doesn't verify truth
— no script can know whether "fastest" is *true*. It verifies **sourcing**, which is the thing a
script actually can check. That distinction is stated plainly in the tool's own skill doc and
restated here so it is never overclaimed.

## Motte and bailey — the castle and the banned fallacy

**As architecture**, motte-and-bailey sorts every marketing asset into two piles:

| Motte | Bailey |
|---|---|
| domain · email list · the product itself · a reputation for accuracy | social accounts · communities · directory listings · published content |
| small, boring, cannot be confiscated | where the traffic actually is, revocable at any moment |

Work in the bailey — that's where value gets produced. Retreat to the motte — that's what
survives a platform changing its mind. Never confuse the two, and never let a large bailey (forty
thousand followers, no email list) stand in for a motte that was never built.

**As rhetoric, the same shape names the thing this plugin forbids.** The motte-and-bailey
fallacy: advertise the bold, attractive, hard-to-defend claim (the bailey — "AI-powered"), and
when challenged, retreat to the narrow, defensible, technically-true one (the motte — "it has
autocomplete"). The reader who saw the ad never sees the retreat; they bought the bailey.
`fortress-truth` bans this move outright. If a claim needs a fallback position to survive a
challenge, the claim was wrong from the start — narrow it before it ships, not after someone calls
it out.

**Use the castle, never the fallacy.** Same words, same shape, one is the architecture you build
and the other is the sentence you're never allowed to write.

## The skills

| Skill | Job |
|---|---|
| **`fortress`** | Front door: doctrine, the standing gate, one-time kickoff that generates a `.monkeys/` brand pack from the adopter's own product, capability report, routing to the six skills below. |
| **`fortress-truth`** | The cleared/uncleared claim register. Installs and runs `claim_lint.py`, which fails on unsourced claim-shaped language: bare numbers/percentages, spelled-out magnitudes (`forty thousand`, `hundreds of`), superlatives, comparatives, absolutes, testimonial-shaped quotes. Bans the motte-and-bailey rhetorical move outright. No per-finding waiver: detection patterns are fixed and not user-overridable, severities are constrained, and every `ignore` pattern in effect is printed on every run. |
| **`fortress-motte`** | The un-takeable core: what an adopter owns outright, and the rule that it gets built before the bailey does. |
| **`fortress-bailey`** | The productive, exposed, rented ground — and the exclusion register, so a channel that was already ruled out doesn't get re-proposed every session forever. |
| **`fortress-standing`** | Per-account trust, tracked per platform, never globally. The highest-consequence skill in the plugin: a ban is the one failure mode nothing else here can undo. |
| **`fortress-gate`** | The human gate before any outward send. Runs the truth/standing/bailey checklist, then defaults to a paste block for a human to send — not an automated publish, even where automation is technically available. |
| **`fortress-measure`** | A small number of honestly-read metrics, sorted by whether they measure something durable (a motte number) or something on loan from a platform (a bailey number). |

## Install

```
/plugin marketplace add ./FORTRESS
/plugin install fortress@fortress
```

Or point the marketplace command at wherever this repository is checked out locally
(`.claude-plugin/marketplace.json` at the repo root). Then, on the target repo, invoke `fortress`
to run kickoff — it interviews the adopter about their own product and generates the `.monkeys/`
brand pack from scratch. Nothing ships pre-filled; a generic template with plausible example
numbers would be exactly the unsourced-claim problem this plugin exists to prevent.

Every skill here runs on built-in tools alone — WebSearch, WebFetch, Read/Write/Edit,
Glob/Grep, Bash — and `claim_lint.py` is Python 3 standard library only, no dependencies. See
`companions.json` for the one optional accelerant currently verified (browser automation, to let
`fortress-gate` execute the copy-paste step of an already-human-approved send); every FORTRESS
skill produces its full deliverable without it.

## Arriving with a Sell-Kit

Optional, and it changes nothing for an adopter who doesn't have one. **Idea Forge Pro**
(ideaforgepro.com) is a separate, free, bring-your-own-API-key tool that runs an idea through seven
gates and exports a *Sell-Kit*. Its fields map closely onto the `.monkeys/` pack, so a founder who
arrives with one isn't re-interviewed for what they already wrote down:

```
An idea → Idea Forge Pro (free, your own key) → a Sell-Kit
        → FORTRESS kickoff reads it → your .monkeys/ pack
        → fortress-truth decides what may be claimed
        → fortress-gate → a human sends it
```

**Reading a Sell-Kit is not clearance.** Idea Forge Pro deliberately refuses to say "clear to
build" — craft, demand, and a critic conceding are three different axes there — and importing a kit
into this pack is not permission to market either. A kit changes where the interview starts, not
what may be said: a field enters `truth.md`'s **Cleared** section only if its own evidence grade
earns it, and anything a model wrote lands in **Uncleared**, which is exactly where `claim_lint.py`
keeps it out of copy. FORTRESS runs with no Sell-Kit, no Idea Forge Pro, and no internet beyond the
built-in search and fetch.

## Honest proof — read this before trusting anything above

`scars.md` in this repository is real. Every entry in it documents a concrete incident with
measurable damage — a demonetised video, a revenue channel that never existed, editing cycles
spent chasing a noisy score — and states the rule the incident forced into existence. Nothing in
that file is hypothetical.

**The system as a whole is unproven.** FORTRESS has not produced a sale, and it has no case study
of a product it grew. This is stated here, in the README, deliberately and up front — not buried,
not softened — because a marketing plugin that claimed results it had not produced would violate
`fortress-truth`'s own rule on line one of its own documentation. A tool whose entire pitch is
claim discipline cannot afford to be the first place that discipline quietly doesn't apply.

The honest pitch is narrower than "this will get you customers," and it's this instead: **this
encodes what the failures cost, so you can skip paying for them.** The doctrine, the gates, and the
linter exist because specific mistakes were expensive to learn once. Adopting FORTRESS doesn't
promise growth — it removes the cost of relearning `scars.md` the hard way.
