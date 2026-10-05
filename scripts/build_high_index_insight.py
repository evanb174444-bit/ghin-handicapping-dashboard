"""Calculate unique-golfer female share above 20, using the approved membership scope."""
import csv,json,sqlite3,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scope=json.loads((ROOT/'config/membership_scope.json').read_text())
allowed=set(scope['association_ids'])
files=[('regular','01_active_standard_2026-09-21.csv.csv'),('junior','02_active_junior_2026-09-22.csv.csv'),('unclassified','03_active_unclassified_2026-09-22.csv')]
with tempfile.TemporaryDirectory() as tmp:
 con=sqlite3.connect(str(Path(tmp)/'insight.sqlite'))
 con.execute('PRAGMA journal_mode=OFF');con.execute('PRAGMA synchronous=OFF')
 con.execute('CREATE TABLE memberships (id TEXT PRIMARY KEY,golfer TEXT,pop TEXT,gender TEXT,above INTEGER)')
 for pop,name in files:
  with (Path('/Users/EvanBelfi/Downloads')/name).open(encoding='utf-8-sig',newline='') as f:
   batch=[]
   for r in csv.DictReader(f):
    if scope['mode']=='us' and r['association_id'] not in allowed:continue
    try:above=(float(r['handicap_index']) if r['matched_golfer_id'] and r['handicap_index_display'].strip().upper()!='NH' else 0)
    except ValueError:above=0
    batch.append((r['membership_id'],r['golfer_id'],pop,r['gender'],above))
    if len(batch)==10000:
     con.executemany('INSERT OR REPLACE INTO memberships VALUES (?,?,?,?,?)',batch);batch=[];con.commit()
   con.executemany('INSERT OR REPLACE INTO memberships VALUES (?,?,?,?,?)',batch);con.commit()
 result={}
 for pop in ['all','regular','junior']:
  where='' if pop=='all' else ' AND pop=?'
  args=() if pop=='all' else (pop,)
  result[pop]={}
  for threshold in (20,30):
   total,female,conflicts=con.execute("SELECT COUNT(*),SUM(female),SUM(conflict) FROM (SELECT golfer,MIN(gender='Female') female,COUNT(DISTINCT gender)>1 conflict FROM memberships WHERE above>?"+where+' GROUP BY golfer)',(threshold,)+args).fetchone()
   assert not conflicts,'Conflicting genders require review'
   result[pop].update({f'golfersAbove{threshold}':total,f'femaleGolfersAbove{threshold}':female or 0,'femaleShare' if threshold==20 else 'femaleShareAbove30':female/total if total else None})
 (ROOT/'data/processed/high_index_insight.json').write_text(json.dumps({'scope':scope,'populations':result},indent=2)+'\n')
 print(json.dumps(result))
