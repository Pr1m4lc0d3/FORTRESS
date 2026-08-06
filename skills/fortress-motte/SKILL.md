---
name: fortress-motte
description: Use when deciding what to build first, evaluating whether an asset is durable, growing an owned audience, or reducing platform dependence. Sorts assets by whether they can be confiscated.
---

# fortress-motte

FORTRESS doctrine: **Build what can't be taken.** This skill is the motte side of that question — what an adopter owns outright, and what still needs building.

## 1. What qualifies as motte

Motte is owned outright and survives any platform decision made against you. Nobody but the adopter can revoke it.

- The domain.
- The email list.
- The product itself — the repo, the source, the thing that runs without anyone's permission.
- A reputation for accuracy, built claim by sourced claim (see `fortress-truth`).
- A direct customer relationship — a name, an email, a way to reach one specific person that no platform sits between.

None of these have a landlord. That's the entire test.

## 2. The growth rule: motte first

Build the motte before spending effort growing the bailey. Bailey traffic with no motte to send it to is traffic you rent and then lose — a spike of visitors who arrive, look around a rented room, and leave no trace behind because there was nowhere for them to leave one.

An email list turns a one-time visitor into someone reachable again next week regardless of what any platform does between now and then. A domain turns "content that lives on someone else's site" into "content you can move." Build the receiving end before you build the funnel that feeds it.

## 3. The test

For any asset, ask one question: **if this platform banned me tomorrow, would I still have it?**

- Yes, unconditionally → motte.
- Yes, but degraded (a scraped export, a stale cache) → probably bailey wearing a motte costume; be honest about the degradation.
- No → bailey. See `fortress-bailey`.

Run this test per asset, not once for the whole business. A product can have a motte-solid domain and a bailey-fragile support channel at the same time.

## 4. The anti-pattern

Forty thousand followers and no email list is a business with no keep. The followers were never owned — they were attention on loan from a platform that can change the terms, the algorithm, or its mind, with no notice and no appeal. On the day it does, the number goes to zero and there was never a way to reach any of those people directly.

A large audience is not evidence of a motte. It's evidence of a well-stocked bailey. That's still valuable — the bailey is where value gets produced — but it is not defensible, and treating it as if it were is the mistake this skill exists to catch.

## 5. Reading and writing `.monkeys/motte.md`

The register lives at `.monkeys/motte.md`, written by FORTRESS kickoff:

```markdown
# Motte — what cannot be confiscated

## Held
- <asset> — control: <full|partial> — grows by: <what moves it>

## Wanted
- <asset not yet built> — why: <what it would let you do>
```

Read **Held** to see what's already owned and how it grows — the `grows by` field is the lever, not decoration; it's the answer to "what should I actually go do." Read **Wanted** to see what's missing and why it matters before proposing new build work — don't invent a Wanted entry that isn't grounded in something the adopter actually said mattered.

When an asset moves from aspiration to reality — a list gets started, a domain gets bought — move the line from **Wanted** to **Held** and fill in `control` and `grows by`. An empty **Held** section is an honest starting point, not a gap to paper over.
