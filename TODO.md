> Read desire/EVENING.md and run a 🌙 Evening turn for tonight.

Tonight's head: `sweep.py` loses a whole sweep to one dropped connection.
Measured at `2026-10-07T00:1x Z` — a bare invocation over the five repos in
play died on `pulls/<n>/comments` with
`http.client.RemoteDisconnected: Remote end closed connection without
response`, after printing three findings and before reading discopy's pull
requests at all.

- [WIP] @session_019mnX56dTbkFMMmhBUQQBS6-2026-10-07 00:23 retry a transport failure in the one `urlopen`, bounded, and leave every
      HTTP status answering exactly as it does today
- [WIP] @session_019mnX56dTbkFMMmhBUQQBS6-2026-10-07 00:23 catch in `main` the transport failures `urllib` does not wrap, so an
      exhausted retry exits 2 (unreadable) rather than 1 (findings)
- [WIP] @session_019mnX56dTbkFMMmhBUQQBS6-2026-10-07 00:23 tests for all four cases: a drop retried, an `HTTPError` not retried,
      the last drop raised, and the exit code it lands on
- [ ] land the same change in MEMORY_REPO's live copy the same turn
      (`AGENTS.md`), and re-run the sweep from the patched file
