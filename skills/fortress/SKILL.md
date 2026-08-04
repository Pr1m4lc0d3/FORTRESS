---
name: fortress
description: FORTRESS front door. Build what can't be taken. Use when starting marketing work on a product, setting up brand or claim discipline, protecting marketing assets, or entering the FORTRESS discipline for the first time — runs kickoff once and routes to the six focused sub-skills.
---

# fortress

This is the front door. It holds the doctrine, the gate you run before any outward send, the one-time kickoff that builds a brand pack from the adopter's own product, and the routing table to the six focused skills that do the actual work. Read this once per adoption; route out of it for everything after.

## 1. The doctrine

Build what can't be taken.

Every skill in this plugin, every table below, every gate you're about to be walked through — all downstream of one question: **what can be confiscated, and what can't?**

A platform can take your account. Nobody can take your email list, or your domain. A false claim confiscates your own credibility, and once a lie is indexed you don't get to unpublish it out of the world's memory. A ban is ground seized — not a warning, not a setback, a loss.

FORTRESS is the defensive half of guerrilla marketing for AI agents. It doesn't tell you how to grow — that's the offense skill system. It tells you what to hold on to while you do.

## 2. Motte and bailey

| Motte — survives any platform's decision | Bailey — rented, revocable |
|---|---|
| Your domain | A social account |
| Your email list | A subreddit or forum profile |
| The product itself | A marketplace listing |
| The source code / the repo | A community you don't administer |
| A reputation for accuracy | Follower count on any platform |
| Direct customer relationships | Search ranking on someone else's index |

A real medieval motte-and-bailey castle split its labor by design. The bailey is the enclosed yard at the bottom — workshops, stalls, the daily business of the place. Value gets produced there, and it's the first thing an attacker overruns. The motte is the raised mound and keep above it: small, cramped, unglamorous, and nearly impossible to take. You don't live on the motte. You survive on it.

Marketing splits the same way. **Work in the bailey, retreat to the motte, never confuse the two.**

The classic ruin is building the whole business in the bailey: forty thousand followers, no email list, no channel to reach any of them that the platform doesn't own. Then the platform changes its algorithm, or its terms, or its mind — and on that day you discover you owned nothing. The followers were never yours. You were renting attention, and the rent came due all at once.

One honest caveat: real insurgents don't hold fortresses. A fixed position is exactly what a conventional force wants you to find and besiege — holding ground is a liability against an army that can surround it. That principle inverts here. Nobody can march on a subscriber file. A domain has no garrison to starve out. The asymmetry that makes a fortress a bad idea on a real battlefield is exactly what makes it the right metaphor for the assets that matter in marketing — you can actually hold this ground, because no one can put it under siege.

## 3. The standing gate

Before any outward send — a post, a comment, a submission, a listing, an email, a publish — run this gate in order:

| Check | Skill |
|---|---|
| Does every claim trace to a cleared fact? | `fortress-truth` |
| Has this account earned the standing this action spends? | `fortress-standing` |
| Is the destination motte or bailey — and does the copy point home? | `fortress-bailey` |
| Then send — deliberately, with a human's finger on it. | `fortress-gate` |
| Which tracked number will tell me it built something durable? | `fortress-measure` |

Two of these get skipped constantly, and both are expensive.

**Skipping the standing check** is why "just engage authentically" is malpractice as advice. Reddit and Hacker News don't warn, throttle, or give a second chance — they ban, and a banned account does not come back. The cost isn't one lost post. It's permanent confiscation of the best ground that account had on that platform.

**Skipping the claim check** ships a falsehood in your own copy. For most products that's embarrassing. For a product whose pitch is verifiability, it's disqualifying — and once the copy is indexed, it's unrecoverable. You can edit the page. You can't edit the cached version, the screenshot, or the person who already quoted it.

## 4. Kickoff

Run this once, the first time FORTRESS is adopted into a repo. If `.monkeys/truth.md` already exists, this is not a clean kickoff — stop and use **Retrofit** (section 7) instead.

State this plainly before starting, and mean it: **nothing here is pre-filled.** Every fact, asset, and channel in the generated pack comes from this adopter's own product, gathered by interview and checked against their own canonical source. A generic template with plausible-looking example numbers would be exactly the unsourced-claim problem this plugin exists to prevent — shipping one would make kickoff itself the first violation of the doctrine.

Steps, in order:

1. **Interview the adopter.** Ask, one question at a time:
   - Product name and a one-line description.
   - The canonical source — the URL or document you'd point a fact-checker to for current numbers, pricing, or features.
   - Three to six facts you want to be able to state publicly, and where each one comes from.
   - What you own outright: domain, email list, other properties.
   - Channels you're already using or plan to use, and any you've deliberately ruled out, with why.
   - Any past incidents — a ban, a retraction, a dispute — worth remembering.

2. **Fetch the canonical source.** Use WebFetch for a URL, Read for a local document. Cross-check every fact the adopter gave you against what's actually there. A fact that matches goes to Cleared. A fact that doesn't match, or that can't be verified this way, goes to Uncleared with the reason — never invent the missing verification to make the fact clearable.

3. **Write `.monkeys/truth.md`** from `skills/fortress-truth/assets/truth.template.md`. Fill **Canonical source** with what the adopter gave. Move each verified fact into **Cleared**, each line ending ` — source: <exact source>`. Move everything else into **Uncleared**, each line ending ` — reason: <why>`.

4. **Write `.monkeys/motte.md`** — one bullet per asset the adopter confirmed they own outright. No invented entries. An empty motte is an honest motte, not a placeholder to come back and fill in.

5. **Write `.monkeys/bailey.md`** — two sections, `## Active` and `## Excluded`. Active lists channels in use or planned. Excluded lists channels ruled out, each with its reason — an exclusion recorded without a reason gets re-proposed every session, forever.

6. **Write `.monkeys/scars.md`** — the adopter's own incident log, started empty: a three-column table (Incident / Damage / Rule) plus one sentence noting it gets filled in after something actually happens, never guessed in advance. This is the adopter's own log, separate from FORTRESS's own `scars.md`, which documents this plugin's history, not theirs.

7. **Copy the linter.** `skills/fortress-truth/assets/claim_lint.py` and `skills/fortress-truth/assets/truth.config.json` into the adopter's repo at `tools/monkeys/`.

8. **Add the contract line.** Append to `CLAUDE.md` if it exists, else `AGENTS.md` if that exists, else create `CLAUDE.md`:

   > Before publishing anything, run `python tools/monkeys/claim_lint.py <draft>`; unsourced claims do not ship.

9. **Report back** what was written, and state plainly that every Cleared fact traces to something the adopter said and something that was independently fetched — nothing was invented to fill space.

## 5. Capability report

Read `companions.json` at the plugin root. For each entry, check the filesystem for whether its provider is already available, and report the result **by capability**, not by tool name — "browser automation for one-click publish," never the name of a specific MCP server or package. Offer to install a missing one only when the adopter explicitly consents; never install anything silently.

If `companions.json` has an empty `companions` array — the shipped default — report exactly that: **"No optional capabilities needed — FORTRESS runs entirely on built-in tools."** That is the correct and complete answer for an empty manifest, not a gap to apologize for.

## 6. Routing table

| Moment | Skill |
|---|---|
| About to state a fact, statistic, or comparison publicly, or writing marketing copy | `fortress-truth` |
| Deciding whether an asset is durable, or what to build first | `fortress-motte` |
| Choosing a channel, evaluating a platform, or ruling one out | `fortress-bailey` |
| About to post or comment in a community, or joining a new one | `fortress-standing` |
| About to publish, post, submit, send, or otherwise act outward | `fortress-gate` |
| Reviewing whether marketing worked, or deciding what to stop doing | `fortress-measure` |

## 7. Retrofit

Adopting FORTRESS on a brand that already has published claims is a different job than a clean start. In a clean start, this discipline prevents bad actions before they happen. In a retrofit, the bad claims are already indexed and load-bearing — other pages link to them, a customer may have repeated one, a search engine has cached it. Correcting that carelessly does more damage than leaving it a little longer.

Follow these five steps **in this exact order.** Do not reorder them — each later step is riskier than the one before it, and running them out of order spends standing or attention that hasn't been earned back yet.

1. **Inventory, don't correct.** Find every public claim, everywhere it lives, and check whether each one can be sourced. Produce the full register before producing a single correction.
2. **Stop the bleeding.** Arm the linter before writing anything new. Existing unsourceable claims get recorded as tracked debt, not fixed on the spot — fixing them now, before the inventory is complete, means fixing them out of order and probably twice.
3. **Audit standing per account, not globally.** Standing does not transfer between platforms. A history of good behavior on one account says nothing about another.
4. **Correct quietly, oldest first.** A visible retraction spends standing — it announces the mistake to people who never noticed it. A silent correction of a stale page usually doesn't.
5. **Re-verify before re-publishing.** An old asset carries its old claims, and sometimes an old license. Don't republish it just because it once passed.

## 8. Built-ins only

Every skill in this plugin — this one and all six it routes to — runs on WebSearch, WebFetch, Read/Write/Edit, Glob/Grep, and Bash. Nothing here assumes any other plugin is installed. `fortress-truth`'s linter is Python 3 standard library only. Section 5's capability report exists because some accelerants are worth naming when they happen to be available — not because FORTRESS needs them to function.
