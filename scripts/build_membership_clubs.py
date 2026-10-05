"""Aggregate club snapshots from the same deduplicated membership exports as Associations."""
import csv,json,sqlite3,tempfile
from pathlib import Path
from review_membership_exports import classify
ROOT=Path(__file__).resolve().parents[1]
associations=json.loads((ROOT/'data/processed/membership_associations.json').read_text())
names={r['id']:r['name'] for r in associations['scopes']['all']['all']}
allowed=set(json.loads((ROOT/'config/membership_scope.json').read_text())['association_ids'])
gc={r['club_id'] for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
files=list(zip(['aga','aga','aga','international'],['regular','junior','unclassified',None],associations['sources']))
clubs={}
with tempfile.TemporaryDirectory() as temp:
 db=sqlite3.connect(str(Path(temp)/'clubs.sqlite'))
 db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
 db.execute('CREATE TABLE m(id TEXT PRIMARY KEY,aid TEXT,cid TEXT,pop TEXT)')
 for scope,pop,file in files:
  batch=[]
  with (Path.home()/'Downloads'/file).open(encoding='utf-8-sig',newline='') as f:
   for r in csv.DictReader(f):
    aid=r['association_id'];cid=r['club_id']
    if scope=='aga' and aid not in allowed:continue
    access,kind,detail=classify(cid,r['club_category'],r['club_type'],gc)
    clubs[(aid,cid)]=dict(id=cid,name=r['club_name'] or 'Unnamed club',association=aid,associationName=names.get(aid,'Unknown association'),scope=scope,access=access if access in ('Public','Private') else 'Unknown',type=kind,recordedType=r['club_type'] or 'Unknown',category=r['club_category'] or 'Unknown',all=0,regular=0,junior=0)
    batch.append((r['membership_id'],aid,cid,pop or {'Standard':'regular','Junior':'junior'}.get(r['usga_membership_type'],'unclassified')))
    if len(batch)>=10000:db.executemany('INSERT OR REPLACE INTO m VALUES (?,?,?,?)',batch);batch=[]
  db.executemany('INSERT OR REPLACE INTO m VALUES (?,?,?,?)',batch);db.commit();print('Loaded',file,flush=True)
 for aid,cid,pop,n in db.execute('SELECT aid,cid,pop,COUNT(*) FROM m GROUP BY aid,cid,pop'):
  clubs[(aid,cid)]['all']+=n
  if pop in ('regular','junior'):clubs[(aid,cid)][pop]+=n
rows=list(clubs.values())
for scope in ('aga','international','all'):
 for pop in ('all','regular','junior'):
  actual={}
  for r in rows:
   if scope!='all' and r['scope']!=scope:continue
   actual[r['association']]=actual.get(r['association'],0)+r[pop]
  actual={k:v for k,v in actual.items() if v}
  expected={r['id']:r['memberships'] for r in associations['scopes'][scope][pop]}
  assert actual==expected,(scope,pop)
out=dict(sources=associations['sources'],dates=associations['dates'],clubs=rows)
(ROOT/'data/processed/membership_clubs.json').write_text(json.dumps(out,separators=(',',':')))
print('Validated club counts against every association across nine scope/population combinations:',len(rows),'clubs',flush=True)
