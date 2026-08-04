---
name: fortress-bailey
description: Use when choosing a channel, evaluating a platform, deciding where to post, or recording why a channel was ruled out. Tracks rented ground and why some ground was refused.
---

# fortress-bailey

FORTRESS doctrine: build what can't be taken. This skill is the bailey side of that question — the rented ground where work actually happens, and the discipline for using it without losing anything permanent to it.

## 1. What the bailey is

The bailey is where value is produced and where it is lost. It's useful — social accounts, communities, directory listings, published content all live here, and this is genuinely where most of the day-to-day work of marketing happens. It's also revocable — every square foot of it sits inside someone else's terms of service, and can be taken back at any time, for any reason, with no appeal.

Work in the bailey. Don't mistake it for somewhere you can afford to lose everything by living exclusively inside.

## 2. The rule: rented ground is an on-ramp, never a destination

Every piece of bailey content points home to the motte (see `fortress-motte`). A post, a comment, a profile bio, a directory listing — each one exists to move someone one step closer to something the adopter actually owns: the email list, the domain, the product itself.

Content that dead-ends in the bailey — a post with no link home, an account bio with no way off the platform — produces engagement the platform keeps and the adopter never gets to convert. It's activity, not asset-building. Check every piece of outward content for a path home before it ships.

## 3. The exclusion register

When a channel is ruled out, record the reason in `.monkeys/bailey.md`. An exclusion without a recorded reason gets re-proposed every session, forever — the next session, or the next agent, has no way to know the channel was already considered and rejected, so it comes back up as if it were new. Writing the reason down once is cheaper than re-litigating the same channel indefinitely.

A good exclusion reason is specific enough to survive being reread cold months later: "audience skews to a different buyer persona" is useful; "not a good fit" is not — it will get re-proposed anyway because it doesn't actually say what was wrong.

## 4. Register shape

`.monkeys/bailey.md`, written by FORTRESS kickoff:

```markdown
# Bailey — rented ground

## Active
- <channel> — account: <handle> — joined: <YYYY-MM-DD> — standing: <cold|warming|established> — links allowed: <yes|no>

## Excluded
- <channel> — reason: <why this was ruled out>
```

`standing:` and `links allowed:` live on the **Active** line itself because `fortress-standing` reads and updates those exact fields per account — this skill doesn't own the standing values, it only reads the channel-level facts (which platform, which handle, when it started) around them. Don't hand-edit `standing:` or `links allowed:` from here; that's `fortress-standing`'s job.

## 5. Per-channel cost

Before adding a channel to **Active**, weigh what it costs to maintain, not just what it might return:

| Cost dimension | Question |
|---|---|
| Time | Does this channel need daily presence to matter, or can it be checked weekly? |
| Standing to build | Is this a platform (Reddit, Hacker News) where trust has to be earned before any link is allowed — see `fortress-standing`? |
| Reversibility | If this account is banned, does the adopter lose only that account, or also content, followers, or history that mattered elsewhere? |
| Redundancy | Does this channel reach an audience already reached through an existing Active channel? |

A channel that costs more standing-building and daily attention than it returns in traffic toward the motte is a candidate for **Excluded**, not **Active** — move it, and write the reason down.
