# Hot Quesadillas

Twenty-five questions you can work out. A fresh batch every Friday at 00:00 London.

Play: https://jimmy-grafton.github.io/quiz-night-console/
API reference: https://jimmy-grafton.github.io/quiz-night-console/docs/

## How it works

- Every question starts at full heat, worth 3. Players can turn the heat down for a clue (the answer's shape, then its initials), and the question is worth 2, then 1. A batch is scored out of 75.
- `index.html` is the whole game: static, no build step. Scores live in each player's browser.
- `docs/` is the API reference. `api/openapi.json` is the OpenAPI 3.1 spec.

## Repository layout

| Path | What it is |
|---|---|
| `drops/NNNN.json` | Source of truth: one file per weekly batch (`n`, `releaseAt`, 25 `questions` of `{id, cat, q, a, ans}`) |
| `drops/index.json` | List of source files, read by the game |
| `api/` | Generated public API: JSON, RSS feed, calendar, daily question, embed widget |
| `img/` | Generated artwork: one image per question type, plus the social card |
| `build_api.py` | Rebuilds `drops/index.json` and `api/` from `drops/` |
| `tools/make_art.py` | Regenerates the favicon, icons, social card and type artwork |

## Adding a batch

1. Write `drops/NNNN.json`. `ans` is the short answer the clues are built from; `a` is the answer with a line on how to work it out.
2. Run `python3 build_api.py`.
3. Commit and push. A weekly scheduled task does this automatically every Friday just after midnight London.
