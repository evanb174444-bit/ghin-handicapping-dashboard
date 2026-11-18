import sqlite3,json,collections,itertools,time
from pathlib import Path
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');db=sqlite3.connect('file:'+str(r/'data/raw/membership_refresh_2026-11-03/audit.sqlite')+'?mode=ro',uri=True)
counts={p:collections.Counter() for p in ['all','regular','junior']};start=time.time()
q='SELECT a.golfer,c.aid,c.pop FROM active a JOIN cell c ON c.id=a.cell GROUP BY a.golfer,c.aid,c.pop ORDER BY a.golfer'
for golfer,rows in itertools.groupby(db.execute(q),key=lambda x:x[0]):
 sets={p:set() for p in counts}
 for _,aid,pop in rows:
  sets['all'].add(aid)
  if pop in sets:sets[pop].add(aid)
 for pop,ids in sets.items():
  if ids:counts[pop][tuple(sorted(ids))]+=1
out={pop:[[list(ids),n] for ids,n in counter.items()] for pop,counter in counts.items()}
expected=json.loads((r/'data/processed/international_totals.json').read_text())
for pop,patterns in out.items():assert sum(n for ids,n in patterns)==expected['scopes']['all'][pop]['uniqueGolfers']
Path('/tmp/membership_association_unique_patterns.json').write_text(json.dumps(out,separators=(',',':')))
print('Anonymous association patterns reconciled:',{p:{'patterns':len(v),'unique':sum(n for _,n in v)} for p,v in out.items()},'seconds',round(time.time()-start,1))
