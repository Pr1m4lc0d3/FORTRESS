---
name: fortress-standing
description: Use when about to post or comment in a community, joining a new platform, or assessing whether an account can safely share a link. Checks and updates per-account trust before it gets spent.
---

# fortress-standing

FORTRESS doctrine: build what can't be taken. This is the highest-consequence skill in the plugin. Everything else in FORTRESS is recoverable — a bad line of copy gets edited, an excluded channel gets reconsidered later. A ban is not recoverable.

## 1. Why this is the highest-consequence skill

Reddit and Hacker News do not warn, throttle, or forgive. Other platforms slow you down, hide your posts, or send a warning email. These two ban outright, on a moderator's judgment, often with no appeal — and a banned account does not come back. The cost of getting this wrong isn't one bad post. It's permanent confiscation of every bit of standing that account had built on that platform, gone in the same action that tried to spend it.

Treat every check in this skill as a check against an irreversible loss, not an inconvenience to route around.

## 2. The rules

- **No drop-and-run.** Never post a link and disappear. A first appearance in a community that is only ever a promotional drop reads as exactly what it is, and it burns the account's first impression — often its only chance to make one.
- **No links on a cold account.** An account with no history, or one that hasn't contributed anything the community found useful, does not get to post a link. Establish the account by being useful first; earn the right to link second.
- **Answer the pain, don't pitch.** When engaging in a community, respond to what the person actually asked or struggled with. A genuine answer that happens to be relevant to the adopter's product builds standing. A pitch dressed as an answer burns it — communities that ban aggressively are specifically tuned to detect this pattern.

## 3. Standing does not transfer

Karma, reputation, or trust built on one platform is worth nothing on the next. A well-regarded account on one forum starts at zero credibility on a different one — there is no import, no reputation passport, no shortcut.

Standing also decays. A dormant account — one with old history but no recent activity — may be worth less than a brand-new account, not more. Old contributions don't vouch for present behavior in a community's eyes, and a sudden reappearance after a long silence, followed immediately by a link, reads exactly like a sock puppet even when it isn't one. Re-establish presence before spending standing on a dormant account, the same as a new one.

Audit standing per account, never globally. A pattern of good behavior on one account says nothing about another, even for the same adopter, even on the same platform.

## 4. The per-account record

Standing lives on the **Active** lines of `.monkeys/bailey.md`, in the shape `fortress-bailey` defines and reads:

```markdown
## Active
- <channel> — account: <handle> — joined: <YYYY-MM-DD> — standing: <cold|warming|established> — links allowed: <yes|no>
```

This skill owns the `standing:` and `links allowed:` fields specifically — read them before any post or comment, and update them after one:

| Field | Meaning |
|---|---|
| `standing: cold` | New or unproven account. No links. Contribute only. |
| `standing: warming` | Has posted useful, non-promotional content and it landed without pushback. Still no links unless the community's own norms clearly allow them. |
| `standing: established` | Sustained history of contribution the community has responded well to. |
| `links allowed: yes` | Set only once `standing` has reached a point where a link would read as a natural part of a genuine answer, not a drop. Never set this to unblock a specific post — set it because the account earned it before that post was ever drafted. |

`joined:` and `account:` are read-only from this skill's side — they're `fortress-bailey`'s facts about the channel, not standing facts. Update only `standing:` and `links allowed:`, and only based on what actually happened on the platform, never on how badly the current task needs a link to go out.

## 5. The check this skill runs

Before any post or comment, in order:

1. Look up the account's line in `.monkeys/bailey.md` under **Active**. No line, or the channel is only in **Excluded** → stop; this account has no standing here, full stop.
2. Read `standing:`. If `cold`, the only allowed action is a genuine, non-promotional contribution — no link, no product mention.
3. If a link is part of the plan, check `links allowed:`. `no` means no, regardless of how relevant or how well-worded the link would be.
4. After the action lands and the community's response is known, update `standing:` to reflect what actually happened — a well-received contribution moves `cold` toward `warming`; a downvoted or removed post does not, and may move it backward.

This is the check `fortress-gate` calls before any outward send that targets a community platform. `fortress-gate` will not send past a `cold` account with a link in the draft.
