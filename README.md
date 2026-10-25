# Hot Quesadillas

Weekly drops of 25 trivia questions, written in a deducible house style. Live at https://jimbogif.github.io/quiz-night-console/

- `index.html` is the whole app (static, no build step).
- `drops/index.json` lists the drop files; each `drops/NNNN.json` holds one drop: `n`, `releaseAt` (UTC ISO, Friday 00:00 London), and 25 `questions` of `{id, cat, q, a}`.
- A weekly scheduled task writes the next drop and commits it here every Thursday night, ready for Friday.
- Scores and drop times are saved in each visitor's browser.

## API

Read-only JSON, served from the same site. Full docs: https://jimmy-grafton.github.io/quiz-night-console/docs/

| Endpoint | Returns |
|---|---|
| `api/latest.json` | This week's drop |
| `api/drops.json` | Every released drop: number, release date, count, URL |
| `drops/NNNN.json` | One drop in full |
| `api/questions.json` | Every released question, tagged with its drop |
| `api/types.json` | Question count per type |

Run `python3 build_api.py` after adding a drop file.
