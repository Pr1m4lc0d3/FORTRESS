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

| Motte | Bailey |
|---|---|
| domain · email list · the product itself · a reputation for accuracy | social accounts · communities · directory listings · published content |
| small, boring, cannot be confiscated | where the traffic actually is, revocable at any moment |

Further examples, same sorting: a direct customer relationship and the source code / the repo are motte — nobody can revoke them. A marketplace listing and follower count on any platform are bailey — both live inside someone else's terms of service.

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

Two roots are in play throughout these steps, and mixing them up is why kickoff fails cold:

- **Plugin root** — where this plugin is installed. Address it with `${CLAUDE_PLUGIN_ROOT}`; everything you *read* from FORTRESS lives under it.
- **Adopter's repo root** — the directory you are working in. Every path you *write* (`.monkeys/…`, `tools/monkeys/…`, `CLAUDE.md`) is relative to it.

A bare `skills/…` path is neither: it resolves against the adopter's working directory, where this plugin is not checked out, and the Read fails.

Steps, in order:

1. **Ask whether there is a Sell-Kit, and read it if there is.** Ask one question and wait for the answer: *"Do you have a Sell-Kit from Idea Forge Pro?"*

   If the answer is no, skip the rest of this step. Nothing else in kickoff changes — the interview below is the whole of it, exactly as it was before this step existed. **A Sell-Kit is never required.** Idea Forge Pro (ideaforgepro.com) is a separate, free, bring-your-own-API-key tool that runs a startup idea through seven gates and exports a Sell-Kit: `<name>-sell-kit.md`, plus a `<name>-forge.json` holding the same data typed. It is optional in exactly the way section 5's companions are optional — FORTRESS runs with no Sell-Kit, no Idea Forge Pro, and no internet beyond the built-in WebSearch and WebFetch.

   If the answer is yes, ask for the path. Where both files exist, read the **`-forge.json`** — it is typed, so nothing is lost to formatting — and fall back to the `-sell-kit.md` where that is the only one. A kit may carry any subset of its fields; an absent field is absent.

   Before a single field moves anywhere, the rule that governs the whole import:

   > **A Sell-Kit field never enters `## Cleared` unless its evidence grade earns it.**

   A Sell-Kit is largely written by a model from what a founder typed into it. Importing that prose into a truth register as fact would inject model-written claims into the exact place that exists to keep them out — and `claim_lint.py` would then pass them forever, because a line that *looks* sourced is all a script can check. **The default for anything without a grade is Uncleared.**

   The kit's claim register carries one line per claim with an evidence grade: **A** attested · **B** observed · **C** public principle · **D** analogy · **E** founder assertion · **F** generated. Its own rule is that anything generated is F and **cannot be raised** — not by argument, not by the founder wanting it, and not by this import.

   Map it exactly. Nothing here creates a file; hold the mapped lines and write them when steps 4, 5 and 6 write the files themselves.

   | From the kit | Goes to | Carrying |
   |---|---|---|
   | `What is known` | `truth.md` `## Cleared` | the source the kit names, as ` — source: <exact source>` |
   | `What is hypothesized` | `truth.md` `## Uncleared` | ` — reason: hypothesis, not established` |
   | claim register, graded **A/B/C/D** | `truth.md` `## Cleared` | ` — source: <the source the register names>` |
   | claim register, graded **E** | `truth.md` `## Uncleared` | ` — reason: founder assertion, no source` |
   | claim register, graded **F** | `truth.md` `## Uncleared` | ` — reason: model-written, cannot be raised` |
   | `Channel` | `bailey.md` `## Active` | `standing: cold` — `links allowed: no` |
   | `Value artifact` | `motte.md` `## Wanted` | why it matters, in the kit's own words |
   | **every other field** | `truth.md` `## Uncleared` | ` — reason: from a Sell-Kit, ungraded` |

   Four things about that table are the whole of it, and each one is where the import goes wrong if it is softened:

   - **`What is known` is the only field that arrives already eligible for Cleared**, because that is its own definition inside the kit: facts directly supplied by the founder or independently supported, nothing generated. It still needs a ` — source:` suffix like every other Cleared line. Where the kit doesn't name one, **ask the adopter**; if they can't name one either, it goes to **Uncleared** instead — ` — reason: no source named`. A Cleared bullet without that suffix sources nothing and the linter ignores it.
   - **Every other field goes to Uncleared unless the claim register grades it A–D.** `Buyer`, `Problem`, `Why now`, `Offer`, `Price`, `Intent signal`, `Value artifact`, and all eight pre-build-test fields — all of it. **A price a model proposed is not a fact about the world.**
   - **The `Channel` entry is a candidate, not a channel in use.** A channel named in a kit has no account behind it yet, which is why it lands `standing: cold` with `links allowed: no` — the two fields `fortress-standing` reads — and `account: none yet` with `joined: n/a`, because inventing a handle or a date would fabricate the account itself. If the adopter says they already have an account there, that is the interview's answer, not the kit's.
   - **The `Value artifact` goes to `## Wanted`, never `## Held`.** It is a thing to build. Writing it under **Held** would claim an asset the adopter does not have.

   Ignore the kit's builder spec entirely — `Acceptance criteria`, `Must nail`, `Out of scope (v1)`. Those describe what to build, not what may be claimed, and nothing in FORTRESS reads them.

   **Never fabricate a field the kit lacks.** An absent field is absent: ask for it in the interview, or leave it out. Then run the interview below asking only for what the kit did not answer, and confirming — not re-asking — what it did.

2. **Interview the adopter.** Ask, one question at a time:
   - Product name and a one-line description.
   - The canonical source — the URL or document you'd point a fact-checker to for current numbers, pricing, or features.
   - Three to six facts you want to be able to state publicly, and where each one comes from.
   - What you own outright: domain, email list, other properties.
   - Channels you're already using or plan to use, and any you've deliberately ruled out, with why.
   - Any past incidents — a ban, a retraction, a dispute — worth remembering.

3. **Fetch the canonical source.** Use WebFetch for a URL, Read for a local document. Cross-check every fact the adopter gave you against what's actually there. A fact that matches goes to Cleared. A fact that doesn't match, or that can't be verified this way, goes to Uncleared with the reason — never invent the missing verification to make the fact clearable.

4. **Write `.monkeys/truth.md`** (adopter's repo root) from `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/truth.template.md`. The template ships placeholders only — no example numbers to leave behind by accident, and any bullet you write under **Cleared** without a ` — source:` suffix is ignored by the linter. Fill **Canonical source** with what the adopter gave. Move each verified fact into **Cleared**, each line ending ` — source: <exact source>`. Move everything else into **Uncleared**, each line ending ` — reason: <why>`.

5. **Write `.monkeys/motte.md`** — one bullet per asset the adopter confirmed they own outright, in exactly this shape. No invented entries. An empty **Held** section is an honest motte, not a placeholder to come back and fill in.

   ```markdown
   # Motte — what cannot be confiscated

   ## Held
   - <asset> — control: <full|partial> — grows by: <what moves it>

   ## Wanted
   - <asset not yet built> — why it matters
   ```

6. **Write `.monkeys/bailey.md`** — channels in use or planned under **Active**, channels ruled out under **Excluded**, in exactly this shape. An exclusion recorded without a reason gets re-proposed every session, forever — that's why **Excluded** entries require one.

   ```markdown
   # Bailey — rented ground

   ## Active
   - <channel> — account: <handle> — joined: <YYYY-MM-DD> — standing: <cold|warming|established> — links allowed: <yes|no>

   ## Excluded
   - <channel> — reason: <why this was ruled out>
   ```

   These two shapes are a contract, not a suggestion: `fortress-motte` reads **Held**/**Wanted**, `fortress-bailey` reads **Active**/**Excluded**, and `fortress-standing` reads the `standing:` and `links allowed:` fields on each **Active** line — that's why those fields live on the channel line itself rather than in a separate file. A skill that changes either shape breaks its siblings.

7. **Write `.monkeys/scars.md`** — the adopter's own incident log, started empty: a three-column table (Incident / Damage / Rule) plus one sentence noting it gets filled in after something actually happens, never guessed in advance. This is the adopter's own log, separate from FORTRESS's own `scars.md`, which documents this plugin's history, not theirs.

8. **Copy the linter.** Read `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/claim_lint.py` and `${CLAUDE_PLUGIN_ROOT}/skills/fortress-truth/assets/truth.config.json`, then Write each verbatim into the adopter's repo at `tools/monkeys/claim_lint.py` and `tools/monkeys/truth.config.json` (both relative to the adopter's repo root). Read+Write, not a shell copy — this step works even where Bash is unavailable. Write the config **verbatim**: the linter refuses a `patterns` key, an all-`warn` severity map, an unrecognised severity value and a catch-all `ignore` (exit 2), and it prints every active `ignore` pattern on each run — so a hand-edit either fails loudly or shows up in the output.

9. **Add the contract line.** Append to `CLAUDE.md` if it exists, else `AGENTS.md` if that exists, else create `CLAUDE.md`:

   > Before publishing anything, run `python tools/monkeys/claim_lint.py <draft>`; unsourced claims do not ship.

10. **Report back** what was written, and state plainly that every Cleared fact traces to something the adopter said and something that was independently fetched — nothing was invented to fill space. Where a Sell-Kit was imported, report it in the same breath: what was imported, what was placed under **Uncleared** and the reason for each, and what still needs verification before it can move.

## 5. Capability report

Read `companions.json` at the plugin root. For each entry, check the filesystem for whether its provider is already available, and report the result **by capability**, not by tool name — "browser automation for one-click publish," never the name of a specific MCP server or package. Offer to install a missing one only when the adopter explicitly consents; never install anything silently.

As shipped, `companions.json` holds **one** entry: browser automation, which lets `fortress-gate` execute the copy-paste step of a send a human has already approved. It is optional — every FORTRESS skill produces its full deliverable without it — so report it as an available accelerant, never as a missing requirement.

If a `companions.json` ever has an **empty** `companions` array, that is not a defect either: report exactly **"No optional capabilities needed — FORTRESS runs entirely on built-in tools."** An empty manifest is a complete answer, not a gap to apologize for.

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
