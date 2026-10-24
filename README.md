# ScoreKeeper 🏆

**Game-night scores, kept honestly.**

Someone always "forgets" the score. ScoreKeeper ends the argument: add
players, enter each round, and the leaderboard updates live with the
leader highlighted. End the game and the winner gets a banner — and the
game is saved for the rematch debate.

## Try it

**Live demo:** https://jamescarterxyz.github.io/scorekeeper/

Or just open `index.html` — it's one file, no build step, no install.

## What it does

- **Players + rounds** — add any number of players, enter scores round
  by round; running totals update instantly.
- **Live leaderboard** — sorted highest-first, current leader
  highlighted.
- **Undo** — one tap removes the last round (for the inevitable
  "wait, I meant 9, not 6").
- **Winner banner** — end the game and the winner (or a tie) is
  announced in big letters.
- **Saved games** — finished games are kept in your browser, with
  totals and winner, and can be deleted.
- **JSON export / import** — take a game to another device, or keep a
  backup. Import restores players, rounds, and the finished state.

## Privacy

No account, no server, no tracking. Everything lives in your browser's
localStorage. The file works offline and never sends anything anywhere.

## Honest limits (v1)

- Games live in one browser — export JSON to move them to another
  device (sync is a possible v2).
- Scores are whole numbers; no decimal or negative-score games yet.
- Clearing browser data deletes saved games — export the ones that
  matter.

## Test it

```bash
python3 tests/test_scorekeeper.py
```

Headless Chromium drives the real page: two rounds (totals 13/17/12),
leader highlight, reload persistence, undo, winner banner, saved games,
and a full JSON export → new game → import round-trip.

## License

MIT — free for everyone, forever.
