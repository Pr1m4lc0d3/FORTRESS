# Scars — what this plugin's doctrine was learned from

This is FORTRESS's own incident log, not an adopter's. It documents what the doctrine in this
plugin cost to learn, before it was doctrine. Each entry is written generically — no product,
company, or domain is named — because the lesson has to survive leaving this specific incident
behind. **The lesson generalizes even though the incident does not.**

This file is separate from the adopter's own `.monkeys/scars.md`, generated empty at kickoff and
filled in as the adopter's own incidents happen. Don't confuse the two.

---

## 1. A permissive licence does not prevent a claim against your content

**Incident.** A music track was sourced under a licence explicitly marked safe for commercial use,
no attribution required. It was used as the background bed for a video that was cut into nine
separate shipped versions across different edits and platforms. Every one of those nine versions
was independently flagged and demonetised by an automated content-matching system, because the
original uploader of the track had separately registered it with a content-identification
distributor — a registration that operates independently of, and is not disclosed by, the licence
terms a downstream user actually reads.

**Damage.** Revenue on all nine versions redirected to the rights claimant. The dispute process
for each one required proving licence terms after the fact, per video, with no guarantee of
reversal — for something that should never have been claimable in the first place.

**Rule.** A licence tells you what you're *allowed* to do. It says nothing about whether the same
asset has been *registered* somewhere that a platform checks automatically. Verify the provenance
— has this exact file, or the work it derives from, been registered with any automated matching
system — not just the licence label attached to where you got it. A licence and a registration are
two different questions, and only one of them is visible in the download terms.

---

## 2. "Sites that pay for AI articles" runs backward

**Incident.** A channel was evaluated as a plausible revenue source under the premise that certain
publishing venues pay contributors for AI-assisted or AI-written articles. Research to actually
place content there surfaced the opposite arrangement at every venue checked: the site charged the
submitter for placement, review, or a "contributor programme" fee — the payment flowed from
creator to platform, not the reverse. Two multi-hundred-dollar "developer programmes" that were
assumed to still be running had also quietly closed.

**Damage.** Hours spent building a content pipeline against a revenue channel that never existed in
the direction assumed. The mistake wasn't a bad estimate of *how much* a channel would pay — it was
building on a channel that was never going to pay at all, and might have cost money to use.

**Rule.** Before treating any channel as a revenue source, verify the *direction* payment actually
flows — who pays whom — not just that money is mentioned near the channel's name. A channel
description that uses the word "pay" is not evidence you get paid.

---

## 3. Positioning and quality-audit scores are noisy, not measurements

**Incident.** A piece of marketing copy was run through a scoring-style critique pass more than
once, with no changes made to the copy between runs. The score swung by several points each run —
sometimes on the same copy, back to back, from the same instructions. Treating any single run's
score as a fixed measurement of quality led to chasing the score itself: rewriting copy in response
to a number that would have moved just as much on a re-run with nothing changed.

**Damage.** Editing cycles spent optimizing for a number that carried several points of run-to-run
noise on unchanged input — motion that looked like progress and wasn't, and copy that got reworked
away from a version that had tested fine, chasing a swing that had nothing to do with the words on
the page.

**Rule.** Treat a scoring-style audit as a source of *criticisms to read*, not a *score to chase*.
A single-run number on this kind of audit is not a stable measurement — read what it flagged, judge
whether the flag is real, and ignore the number's movement between otherwise-identical runs.

---

## 4. A correction written into the draft dies with the draft

**Incident.** A claims register was built, filled with sourced entries, and used to gate public
copy. It worked. Over the following months the underlying facts moved: a capability that had been
unproven was demonstrated and signed, a ratio that had barred a claim turned out to measure the
wrong population, and the reasoning behind one entry was found to be circular and was reversed by
the owner. Every one of those corrections was made — in a chat, in a commit message, in the
paragraph being edited at the time. None of them was made *in the register*. The register still
held the superseded reasoning, with no date on any line to suggest it might have aged, and every
later run read it as current.

**Damage.** The gate kept passing copy against a version of the truth its own owner had already
abandoned, and barred a claim that had since been cleared. Worse than a gate that fails: a gate
that confidently approves the wrong thing while looking green. The corrections were not lost
because anyone forgot them — they were written down somewhere that nothing reads twice.

**Rule.** When a check is wrong, fix **the thing the check reads**, not the artefact you happened
to be editing when you noticed. A miss means the watchlist, the register, or the source list is
incomplete. A false alarm means the rule is too broad. A number nobody re-verified means the
checking rhythm is too slow. Editing the draft fixes one draft; editing the rule fixes every run
after it. And a register with no dates on it cannot tell you which of its lines you are relying on
were last confirmed a year ago — so date the entries, and keep what *changed* rather than
overwriting it, because a claim you merely stopped writing down is one you can walk back into.
