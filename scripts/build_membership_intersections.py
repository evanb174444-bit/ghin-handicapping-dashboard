"""Build anonymous aggregated cells and golfer patterns for intersecting membership filters."""
import csv,json,sqlite3,tempfile,sys
from pathlib import Path
from collections import Counter,defaultdict
from review_membership_exports import classify,numeric
ROOT=Path(__file__).resolve().parents[1]
scope=json.loads((ROOT/'config/membership_scope.json').read_text());allowed=set(scope['association_ids'])
gc={r['club_id'] for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
files=[('Regular','01_active_standard_2026-09-21.csv.csv'),('Junior','02_active_junior_2026-09-22.csv.csv'),('Unclassified','03_active_unclassified_2026-09-22.csv')]
clubs={};cells=Counter();patterns=Counter();idx={}
with tempfile.TemporaryDirectory() as tmp:
 con=sqlite3.connect(str(Path(tmp)/'nh.sqlite'));con.execute('PRAGMA journal_mode=OFF');con.execute('PRAGMA synchronous=OFF')
 con.execute('CREATE TABLE r (id TEXT PRIMARY KEY,golfer TEXT,club TEXT,gender TEXT,age TEXT,pop TEXT,hi TEXT)')
 for pop,file in files:
  batch=[]
  with (Path('/Users/EvanBelfi/Downloads')/file).open(encoding='utf-8-sig',newline='') as f:
   for r in csv.DictReader(f):
    if scope['mode']=='us' and r['association_id'] not in allowed:continue
    cid=r['club_id'];access,kind,detail=classify(cid,r['club_category'],r['club_type'],gc)
    group=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access'
    clubkey=json.dumps([cid,r['association_id'],access,group,r['club_type']],separators=(',',':'))
    clubs[clubkey]={'id':cid,'name':r['club_name'],'association':r['association_id'],'access':access,'clubGroup':group,'type':r['club_type']}
    age=numeric(r['age_at_extraction']) if r['matched_golfer_id'] else None
    band='Unknown / invalid' if age is None or age<0 or age>120 else next(label for edge,label in [(18,'Under 18'),(25,'18–24'),(35,'25–34'),(45,'35–44'),(55,'45–54'),(65,'55–64'),(121,'65+')] if age<edge)
    hi=numeric(r['handicap_index']) if r['matched_golfer_id'] else None
    hi_band='No Index' if r['handicap_index_display'].strip().upper()=='NH' else 'Unknown' if hi is None else next(label for edge,label in [(0,'Plus / Scratch'),(5,'0.1–5.0'),(10,'5.1–10.0'),(15,'10.1–15.0'),(20,'15.1–20.0'),(30,'20.1–30.0'),(float('inf'),'30.1+')] if hi<=edge)
    batch.append((r['membership_id'],r['golfer_id'],clubkey,r['gender'] or 'Unknown',band,pop,hi_band))
    if len(batch)>=10000:con.executemany('INSERT OR REPLACE INTO r VALUES (?,?,?,?,?,?,?)',batch);batch=[];con.commit()
  con.executemany('INSERT OR REPLACE INTO r VALUES (?,?,?,?,?,?,?)',batch);con.commit()
 previous=None;current=set()
 for golfer,club,gender,age,pop,hi in con.execute('SELECT golfer,club,gender,age,pop,hi FROM r ORDER BY golfer'):
  if previous is not None and golfer!=previous:
   patterns[tuple(sorted(current))]+=1;current=set()
  key=(club,gender,age,pop,hi)
  if key not in idx:idx[key]=len(idx)
  cells[key]+=1;current.add(idx[key]);previous=golfer
 if previous is not None:patterns[tuple(sorted(current))]+=1
clubids=list(clubs);clubidx={c:i for i,c in enumerate(clubids)}
genders=['Male','Female','Unknown'];ages=['Under 18','18–24','25–34','35–44','45–54','55–64','65+','Unknown / invalid'];pops=['Regular','Junior','Unclassified']
his=['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+','No Index','Unknown']
names=json.loads((ROOT/'config/association_names.json').read_text())
for c in clubs.values():c['associationName']=names.get(c['association'],'Unknown association')
out={'scope':scope,'clubs':[clubs[c] for c in clubids],'genders':genders,'ages':ages,'populations':pops,'handicaps':his,'cells':[[clubidx[c],genders.index(g),ages.index(a),pops.index(p),his.index(h),n] for (c,g,a,p,h),n in cells.items()],'golferPatterns':[[list(pattern),n] for pattern,n in patterns.items()]}
assert sum(row[5] for row in out['cells'])==3840678
assert sum(n for _,n in out['golferPatterns'])==3544477
(ROOT/'data/processed/membership_intersections.json').write_text(json.dumps(out,separators=(',',':')))
print('Cells',len(cells),'Anonymous golfer patterns',len(patterns))
