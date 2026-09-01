# The board

State only — what is ready, what is blocked on what, what is behind, and only where it crosses more
than one head. **Under 200 lines, rewritten every turn, never appended to**: a turn that would push
it over drops the oldest section instead of adding one.

Four things do not belong here. A fact about a single pull request is that head's own
[`WORK/<repo>/<number>.md`](WORK). A convention or a ruling is an open issue on DESIRE_REPO. Turn
narration — anything carrying a timestamp and an agent name — is [`TURNS/<date>.md`](TURNS). What
waits on USER, and what USER is working on, is [`USER_TODO.md`](USER_TODO.md).

Last rewritten: never — this is the seed. Delete this line when the first turn writes a real one.

# Ruled, do not re-ask

<!-- Rulings USER has already made, one line each with the date. A turn that reopens one of these
has cost a night. Empty until the first ruling. -->

# The queue

<!-- Not a list of heads — that is what WORK/ is. What goes here is what one head's file cannot
say on its own: forced merge order, live file collisions between two heads, a lane that is blocked
as a lane. -->

# The open issues

<!-- The ones needing a design call or a ruling, by repo. Not every open issue: the ones whose
absence of an answer is blocking work. -->

# Who else is in these repos

<!-- One line per collaborator, saying only the part that changes an agent's work. The full read is
in OTHERS/<person>.md. -->
