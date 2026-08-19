# Truth Register

Every public claim traces to a line under **Cleared**, or it does not ship.
The linter parses this file. Keep the format exactly.

## Cleared

<!-- One bullet per fact, in this exact shape. A bullet without the " — source:" -->
<!-- suffix is malformed: the linter ignores it, and it sources nothing. -->
<!-- - <the claim, exactly as it will appear in copy> — source: <where this was verified> — checked: <YYYY-MM-DD> -->
<!--                                                                                                             -->
<!-- " — checked:" is OPTIONAL and dates the last time somebody actually re-fetched -->
<!-- the source. Past the configured max_age_days the entry still sources, but the -->
<!-- run says so: sourced-once is not the same question as true-today. -->

## Uncleared

<!-- Facts that may NOT be stated publicly without re-verification. -->
<!-- - <the fact> — reason: <why it is not cleared> -->

## Changed

<!-- Claims that WERE cleared, until the world moved. The old wording stays here -->
<!-- so a draft still carrying it gets caught; it is not deleted, because a claim -->
<!-- you merely stopped writing down is one you can walk back into. -->
<!-- - <the old claim, in the words that used to ship> — reason: <what is true now> -->

## Contradicted

<!-- Claims where credible sources disagree. Neither side ships until someone -->
<!-- resolves it. Keeping both visible is the point — the conflict is the finding. -->
<!-- - <the claim> — reason: <what disagrees with what> -->

## Canonical source

<!-- The URL or location to re-fetch before every copy batch. Never write from memory of it. -->
