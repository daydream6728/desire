can we simplify this? feels bloated https://github.com/toumix/desire/pull/136

what i had in mind is just for each codex session to listen to the PRs it opens and reply to comments until they are merged, apparently that’s not possible with webhook so I thought about the “timed self check in” trick that Claude sometimes used, i.e. when it’s done it
just sets a timer for checking the PR after a certain time

[WIP] @codex-2026-09-02  Replace the custom scheduler and registry with a native thread heartbeat.
[ ] Keep only the instructions needed to check feedback, act on it, and stop after merge or close.
[ ] Update the repository rule, documentation, and changelog to describe the simpler design.
[ ] Validate the reduced skill and review the final diff.
