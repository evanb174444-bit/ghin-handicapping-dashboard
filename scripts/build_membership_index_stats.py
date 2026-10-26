"""Build anonymous exact-index patterns for the existing membership explorer."""
import csv,json,sqlite3,math
from pathlib import Path
from collections import Counter
from itertools import groupby
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'data/processed/membership_intersections.json').read_text())
clubids={(c['association'],c['id']):i for i,c in enumerate(d['clubs'])}
cellids={tuple(r[:5]):i for i,r in enumerate(d['cells'])}
priv=ROOT/'data/raw/membership_index_stats';priv.mkdir(exist_ok=True)
dbpath=priv/'index.sqlite'
assert not dbpath.exists(),'Inspect existing private index staging before rebuilding'
db=sqlite3.connect(dbpath);db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
db.execute('CREATE TABLE records(golfer INTEGER,cell INTEGER,hi INTEGER)')
def num(v):
 try:
  x=float(v)
  return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
counts=Counter();batch=[];plus_sign_mismatch=0
csv.field_size_limit(16*1024*1024)
source=ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):
  if r['membership_status']!='Active' or r['association_scope']!='AGA':continue
  age=num(r['age_at_extraction']) if r['matched_golfer_id'] else None
  ageband='Unknown / invalid' if age is None or not 0<=age<=120 else next(b for e,b in zip([18,25,35,45,55,65,121],d['ages']) if age<e)
  rawhi=num(r['handicap_index']) if r['matched_golfer_id'] and r['handicap_index_display'].strip().upper()!='NH' else None
  band='No Index' if r['handicap_index_display'].strip().upper()=='NH' else 'Unknown' if rawhi is None else next(b for e,b in zip([0,5,10,15,20,30,float('inf')],d['handicaps']) if rawhi<=e)
  gender=r['gender'] if r['gender'] in ('Male','Female') else 'Unknown'
  key=(clubids[(r['association_id'],r['club_id'])],d['genders'].index(gender),d['ages'].index(ageband),d['populations'].index(r['member_population']),d['handicaps'].index(band))
  cell=cellids[key];counts[cell]+=1
  if rawhi is not None and r['handicap_index_display'].strip().startswith('+') and rawhi>0:plus_sign_mismatch+=1
  hi=round(rawhi*10) if rawhi is not None and -10<=rawhi<=54 else None
  batch.append((int(r['golfer_id']),cell,hi))
  if len(batch)>=20000:db.executemany('INSERT INTO records VALUES (?,?,?)',batch);batch=[]
db.executemany('INSERT INTO records VALUES (?,?,?)',batch);db.commit()
assert all(counts[i]==r[5] for i,r in enumerate(d['cells'])),'Source membership counts differ'
assert not plus_sign_mismatch,'Plus Handicap sign convention requires review'
print('Membership cells reconciled',sum(counts.values()),flush=True)
patterns=Counter();conflicts=0;valid=0;gc={}
for gid,rows in groupby(db.execute('SELECT golfer,cell,hi FROM records ORDER BY golfer'),lambda r:r[0]):
 rows=list(rows);his={h for _,_,h in rows if h is not None}
 if len(his)>1:conflicts+=1;continue
 if not his:continue
 hi=next(iter(his));ids=tuple(sorted({c for _,c,h in rows if h is not None}))
 patterns[(ids,hi)]+=1;valid+=1
 if any(d['clubs'][d['cells'][c][0]]['clubGroup']=='GC Clubs' for c in ids):gc[gid]=hi
out={'meta':{'date':'October 13, 2026','unit':'Unique golfers with a valid Handicap Index','validGolfers':valid,'conflictingGolfersExcluded':conflicts,'indexScale':10},'patterns':[[list(ids),hi,n] for (ids,hi),n in patterns.items()]}
(ROOT/'data/processed/membership_index_stats.json').write_text(json.dumps(out,separators=(',',':')))
import statistics
audit={**out['meta'],'membershipsReconciled':sum(counts.values()),'gc':{'validGolfers':len(gc),'mean':statistics.mean(gc.values())/10,'median':statistics.median(gc.values())/10}}
(ROOT/'reports/membership_index_stats_validation.json').write_text(json.dumps(audit,indent=2))
print(audit,flush=True)
