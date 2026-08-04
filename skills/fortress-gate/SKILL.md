---
name: fortress-gate
description: Use before publishing, posting, submitting, or sending anything outward-facing. Runs the pre-send checklist and defaults to a human-approved paste block rather than an automated send.
---

# fortress-gate

FORTRESS doctrine: build what can't be taken. Staging a draft costs nothing and can be redone infinitely. Sending it does not — an outward action, once taken, is hard or impossible to reverse, and this skill exists to put a real check between the two.

## 1. Staging is free, sending is not

Write, revise, and re-draft as much as needed — none of that spends anything. The moment content leaves the workspace and lands on a platform, in an inbox, or in front of a stranger, it's spent: a post can be deleted but the cached copy and the people who already read it can't be un-shown it; a submission to a community counts against that account's standing whether or not it's later removed; an email is read the instant it's opened.

Treat drafting as free and treat every send as a decision with a cost, because those are the actual economics of the two actions — even when the tooling makes them feel equally easy.

## 2. The default deliverable is a paste block for a human

This is doctrine, not a limitation of what's available. Given a finished, gate-cleared draft, the default output of this skill is the exact text, formatted and ready, for a human to read once more and paste in themselves — not an automated publish action, even where one is technically possible.

A human reading the text immediately before it goes out is the last check between a mistake and a public mistake. That check is worth keeping even when it would be faster to skip it — speed is not the scarce resource an irreversible outward action should be optimized for.

## 3. The pre-send checklist

Before handing over anything outward-facing, run this in order:

| Check | Skill | Stops the send if |
|---|---|---|
| Does every claim in the draft trace to a cleared fact? | `fortress-truth` | Any claim-shaped language is unsourced. Run the linter; a failing exit code means the draft doesn't go out as-is. |
| Has this account earned the standing this action spends? | `fortress-standing` | The target account is `cold` and the draft contains a link, or the community norms this account hasn't earned yet. |
| Does the copy point home? | `fortress-bailey` | The draft is bailey content with no path back to anything the adopter owns. |

All three pass → produce the paste block. Any one fails → report which check failed and why, and don't produce the paste block until it's fixed. Don't soften this into a warning that still hands over the text — a failed check means no deliverable, not a deliverable with a caveat attached.

## 4. Browser automation still needs a human per send

Where browser automation for one-click publishing happens to be available in the environment, it does not replace this checklist or the human approval step — it only removes the manual copy-paste after approval is given. Every individual send still gets explicit human sign-off before it fires, one at a time. Never chain automated sends across multiple pieces of content on the strength of one earlier approval; approval is per-send, not per-batch.

## 5. Zero add-ons required

This skill is fully functional with nothing beyond the built-in tools. A paste block for a human requires no browser automation, no publishing API, no external service — just the checklist above and a place to put the finished text. Any automation capability that exists is an accelerant for the copy-paste step, never a requirement for the skill to work at all.
