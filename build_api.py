# Rebuilds the read-only JSON API from drops/*.json. Run after adding a drop.
import json, glob, os, datetime
here = os.path.dirname(os.path.abspath(__file__))
drops = sorted((json.load(open(f)) for f in glob.glob(os.path.join(here, 'drops', '[0-9]*.json'))), key=lambda d: d['n'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
live = [d for d in drops if d['releaseAt'] <= now.replace('+00:00', 'Z')]
json.dump({"drops": [f"{d['n']:04d}.json" for d in drops]}, open(os.path.join(here, 'drops', 'index.json'), 'w'), indent=1)
qs = [{**q, "drop": d['n'], "releaseAt": d['releaseAt']} for d in live for q in d['questions']]
types = {}
for q in qs: types[q['cat']] = types.get(q['cat'], 0) + 1
w = lambda name, obj: json.dump(obj, open(os.path.join(here, 'api', name), 'w'), ensure_ascii=False, indent=1)
w('latest.json', live[-1] if live else None)
w('drops.json', [{"n": d['n'], "releaseAt": d['releaseAt'], "count": len(d['questions']), "url": f"drops/{d['n']:04d}.json"} for d in live])
w('questions.json', qs)
w('types.json', types)
print(len(live), 'drops,', len(qs), 'questions')
