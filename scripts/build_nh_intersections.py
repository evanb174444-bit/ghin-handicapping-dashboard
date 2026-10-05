"""Build anonymous aggregated cells and golfer patterns for intersecting NH filters."""
import csv,json,sqlite3,tempfile,sys
from pathlib import Path
from collections import Counter,defaultdict
from review_membership_exports import classify,numeric
ROOT=Path(__file__).resolve().parents[1]
scope=json.loads((ROOT/'config/membership_scope.json').read_text());allowed=set(scope['association_ids'])
gc={r['club_id'] for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
files=[('Regular','01_active_standard_2026-09-21.csv.csv'),('Junior','02_active_junior_2026-09-22.csv.csv'),('Unclassified','03_active_unclassified_2026-09-22.csv')]
clubs={};cells=Counter();nhcells=Counter();golfers=defaultdict(set)
with tempfile.TemporaryDirectory() as tmp:
 con=sqlite3.connect(str(Path(tmp)/'nh.sqlite'));con.execute('PRAGMA journal_mode=OFF');con.execute('PRAGMA synchronous=OFF')
 con.execute('CREATE TABLE r (id TEXT PRIMARY KEY,golfer TEXT,club TEXT,gender TEXT,age TEXT,pop TEXT,nh INTEGER)')
 for pop,file in files:
  batch=[]
  with (Path('/Users/EvanBelfi/Downloads')/file).open(encoding='utf-8-sig',newline='') as f:
   for r in csv.DictReader(f):
    if scope['mode']=='us' and r['association_id'] not in allowed:continue
    cid=r['club_id'];access,kind,detail=classify(cid,r['club_category'],r['club_type'],gc)
    group=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access'
    clubs[cid]={'id':cid,'name':r['club_name'],'association':r['association_id'],'access':access,'clubGroup':group,'type':r['club_type']}
    age=numeric(r['age_at_extraction']) if r['matched_golfer_id'] else None
    band='Unknown / invalid' if age is None or age<0 or age>120 else next(label for edge,label in [(18,'Under 18'),(25,'18–24'),(35,'25–34'),(45,'35–44'),(55,'45–54'),(65,'55–64'),(121,'65+')] if age<edge)
    batch.append((r['membership_id'],r['golfer_id'],cid,r['gender'] or 'Unknown',band,pop,int(r['handicap_index_display'].strip().upper()=='NH')))
    if len(batch)>=10000:con.executemany('INSERT OR REPLACE INTO r VALUES (?,?,?,?,?,?,?)',batch);batch=[];con.commit()
  con.executemany('INSERT OR REPLACE INTO r VALUES (?,?,?,?,?,?,?)',batch);con.commit()
 for golfer,club,gender,age,pop,nh in con.execute('SELECT golfer,club,gender,age,pop,nh FROM r'):
  key=(club,gender,age,pop);cells[key]+=1
  if nh:nhcells[key]+=1;golfers[golfer].add(key)
clubids=list(clubs);clubidx={c:i for i,c in enumerate(clubids)}
genders=['Male','Female','Unknown'];ages=['Under 18','18–24','25–34','35–44','45–54','55–64','65+','Unknown / invalid'];pops=['Regular','Junior','Unclassified']
keys=list(cells);idx={k:i for i,k in enumerate(keys)}
patterns=Counter(tuple(sorted(idx[k] for k in keys)) for keys in golfers.values())
names=json.loads((ROOT/'config/association_names.json').read_text())
for c in clubs.values():c['associationName']=names.get(c['association'],'Unknown association')
out={'scope':scope,'clubs':[clubs[c] for c in clubids],'genders':genders,'ages':ages,'populations':pops,'cells':[[clubidx[c],genders.index(g),ages.index(a),pops.index(p),n,nhcells.get((c,g,a,p),0)] for (c,g,a,p),n in cells.items()],'golferPatterns':[[list(pattern),n] for pattern,n in patterns.items()]}
assert sum(row[5] for row in out['cells'])==438165
assert sum(n for _,n in out['golferPatterns'])==433444
(ROOT/'data/processed/nh_intersections.json').write_text(json.dumps(out,separators=(',',':')))
print('Cells',len(cells),'Anonymous golfer patterns',len(patterns))
