"""Rebuild the Hot Quesadillas static API from drops/NNNN.json.

Run after adding or editing a drop:  python3 build_api.py
Writes drops/index.json (source index) and everything under api/ (JSON, RSS feed, calendar, daily question).
Publicly each week is a "batch"; the source files stay in drops/.
"""
import json, glob, os, re, datetime, html
from email.utils import format_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://jimmy-grafton.github.io/quiz-night-console/"
TYPES = ["Geography", "Ancient History", "History", "Science & Nature", "Words & Language", "Film & TV",
         "Music", "Sport", "Food & Drink", "Art & Books", "People & Politics", "Business & Money"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def split_answer(a):
    """'Japan, Jamaica, Jordan. Each clue rules in one region.' -> ('Japan, Jamaica, Jordan', 'Each clue rules in one region.')"""
    m = re.match(r"^(.+?[^A-Z.])\.(\s+|$)(.*)$", a.strip(), re.S)
    if not m:
        return a.strip().rstrip("."), ""
    head, tail = m.group(1).strip(), m.group(3).strip()
    head = re.sub(r"\s*\([^)]*\)\s*$", "", head) or head   # drop a trailing aside like "(1977)"
    return head, tail


def clue(answer, level):
    """level 1: shape only.  level 2: first letter of each word."""
    out = []
    for word in re.split(r"(\s+|[,;/&-])", answer[:60]):
        if not word or not re.search(r"[A-Za-z0-9]", word):
            out.append(word)
            continue
        chars = [c for c in word]
        first = next((k for k, c in enumerate(chars) if c.isalnum()), 0)
        out.append("".join(c if (not c.isalnum()) or (level == 2 and k == first) else "_" for k, c in enumerate(chars)))
    s = "".join(out)
    return s + ("…" if len(answer) > 60 else "")


def first_letter(answer):
    m = re.search(r"[A-Za-z]", answer)
    return m.group(0).upper() if m else "#"


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    drops = sorted((json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(HERE, "drops", "[0-9]*.json"))), key=lambda d: d["n"])
    live = [d for d in drops if datetime.datetime.fromisoformat(d["releaseAt"].replace("Z", "+00:00")) <= now]

    json.dump({"drops": [f"{d['n']:04d}.json" for d in drops]}, open(os.path.join(HERE, "drops", "index.json"), "w"), indent=1)

    def enrich(q, d):
        ans, why = split_answer(q["a"])
        if q.get("ans"):
            ans = q["ans"].strip()
            why = q["a"].strip()
        return {"id": q["id"], "object": "question", "batch": d["n"], "type": q["cat"], "type_slug": slug(q["cat"]),
                "question": q["q"], "answer": ans, "explanation": why, "answer_full": q["a"],
                "options": sorted([ans] + list(q.get("wrong", [])), key=lambda o: hash((q["id"], o)) & 0xffff),
                "wrong_options": list(q.get("wrong", [])),
                "heat": {"max": 3, "one_knocked_out": 2, "two_knocked_out": 1},
                "letter": first_letter(ans), "released_at": d["releaseAt"]}

    def drop_obj(d, full=True):
        o = {"object": "batch", "number": d["n"], "id": f"batch_{d['n']:04d}", "released_at": d["releaseAt"],
             "question_count": len(d["questions"]), "types": sorted({q["cat"] for q in d["questions"]}),
             "max_heat": 3 * len(d["questions"]), "url": f"{SITE}api/batches/{d['n']:04d}.json"}
        if full:
            o["questions"] = [enrich(q, d) for q in d["questions"]]
        return o

    api = os.path.join(HERE, "api")
    for sub in ("batches", "types", "letters"):
        os.makedirs(os.path.join(api, sub), exist_ok=True)
    w = lambda name, obj: json.dump(obj, open(os.path.join(api, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    page = lambda data, **extra: {"object": "list", "count": len(data), **extra, "data": data}

    qs = [enrich(q, d) for d in live for q in d["questions"]]
    w("latest.json", drop_obj(live[-1]) if live else None)
    w("batches.json", page([drop_obj(d, False) for d in reversed(live)], url=f"{SITE}api/batches.json"))
    for d in live:
        w(f"batches/{d['n']:04d}.json", drop_obj(d))
    w("questions.json", page(qs, url=f"{SITE}api/questions.json"))

    by_type = {}
    for q in qs:
        by_type.setdefault(q["type"], []).append(q)
    w("types.json", page([{"object": "type", "name": t, "slug": slug(t), "count": len(by_type.get(t, [])),
                           "url": f"{SITE}api/types/{slug(t)}.json"} for t in TYPES], url=f"{SITE}api/types.json"))
    for t in TYPES:
        w(f"types/{slug(t)}.json", page(by_type.get(t, []), type=t, url=f"{SITE}api/types/{slug(t)}.json"))

    by_letter = {}
    for q in qs:
        by_letter.setdefault(q["letter"], []).append(q)
    for L in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        w(f"letters/{L}.json", page(by_letter.get(L, []), letter=L, url=f"{SITE}api/letters/{L}.json"))

    # Stats: the spice rack
    w("stats.json", {"object": "stats", "batches": len(live), "questions": len(qs),
                     "types": {t: len(by_type.get(t, [])) for t in TYPES},
                     "letters": {L: len(by_letter.get(L, [])) for L in sorted(by_letter)},
                     "generated_at": now.isoformat().replace("+00:00", "Z")})

    # A question for every day: deterministic by date, so everyone gets the same one
    if qs:
        days = []
        start = now.date()
        for k in range(14):
            day = start + datetime.timedelta(days=k)
            days.append({"date": day.isoformat(), "question": qs[(day.toordinal() * 7919) % len(qs)]})
        w("daily.json", page(days, note="One question per calendar day (UTC), the same for everyone."))

    # RSS feed of drops
    items = "".join(
        f"<item><title>Batch {d['n']}: {html.escape(', '.join(sorted({q['cat'] for q in d['questions']})[:3]))} and more</title>"
        f"<link>{SITE}#batch-{d['n']}</link><guid isPermaLink=\"false\">hq-batch-{d['n']}</guid>"
        f"<pubDate>{format_datetime(datetime.datetime.fromisoformat(d['releaseAt'].replace('Z', '+00:00')))}</pubDate>"
        f"<description>{html.escape(d['questions'][0]['q'])}</description></item>" for d in reversed(live))
    open(os.path.join(api, "feed.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Hot Quesadillas</title>'
        f"<link>{SITE}</link><description>25 questions you can work out, every Friday.</description>{items}</channel></rss>\n")

    # Calendar: a weekly reminder you can subscribe to
    open(os.path.join(api, "batches.ics"), "w", encoding="utf-8").write("\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Hot Quesadillas//Batches//EN", "X-WR-CALNAME:Hot Quesadillas",
        "BEGIN:VTIMEZONE", "TZID:Europe/London",
        "BEGIN:STANDARD", "DTSTART:19701025T020000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "TZOFFSETFROM:+0100", "TZOFFSETTO:+0000", "END:STANDARD",
        "BEGIN:DAYLIGHT", "DTSTART:19700329T010000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "TZOFFSETFROM:+0000", "TZOFFSETTO:+0100", "END:DAYLIGHT",
        "END:VTIMEZONE",
        "BEGIN:VEVENT", "UID:hq-weekly-batch@jimmy-grafton.github.io", f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        "DTSTART;TZID=Europe/London:20261023T080000", "DURATION:PT15M", "RRULE:FREQ=WEEKLY;BYDAY=FR",
        "SUMMARY:A fresh batch of Hot Quesadillas is out", f"URL:{SITE}", f"DESCRIPTION:25 new questions. {SITE}",
        "END:VEVENT", "END:VCALENDAR", ""]))

    print(f"{len(live)} batches, {len(qs)} questions, {len(by_type)} types, {len(by_letter)} letters")


if __name__ == "__main__":
    main()
