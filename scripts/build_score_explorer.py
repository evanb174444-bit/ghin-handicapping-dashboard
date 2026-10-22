"""Join private score IDs to October 13 active memberships; publish anonymous patterns only."""
import csv,json,sqlite3,shutil,time
csv.field_size_limit(16*1024*1024)
from pathlib import Path
from collections import Counter
from itertools import groupby
from review_membership_exports import classify,numeric
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'data/raw/score_explorer_2026-10-21';PRIVATE.mkdir(exist_ok=True)
SOURCE=Path('/Users/EvanBelfi/Downloads/active_golfer_ytd_scores_2026-10-21.csv.csv')
MEMBERS=ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
DB=PRIVATE/'join.sqlite'
assert not DB.exists(),'Private staging already exists; inspect before rebuilding'
shutil.copy2(SOURCE,PRIVATE/SOURCE.name)
scores={};raw=Counter();score_sum=0
with SOURCE.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,strict=True):
  gid=int(r['golfer_id']);n=int(r['ytd_score_count']);assert gid not in scores and n>=0
  band=0 if n==0 else 1 if n<=7 else 2;scores[gid]=band;raw[band]+=1;score_sum+=n
print('Score export:',len(scores),dict(raw),flush=True)
db=sqlite3.connect(DB);db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF');db.execute('CREATE TABLE matches(golfer INTEGER,cell INTEGER)')
keys=['membershipType','association','access','clubGroup','clubType','gender','age','handicap','club','scope']
labels={k:[] for k in keys};lookup={k:{} for k in keys};cells=[];ci={}
def cell_id(values):
 ids=[]
 for k,v in zip(keys,values):
  if v not in lookup[k]:lookup[k][v]=len(labels[k]);labels[k].append(v)
  ids.append(lookup[k][v])
 key=tuple(ids)
 if key not in ci:ci[key]=len(cells);cells.append(ids)
 return ci[key]
unknown=cell_id(['No October 13 active membership match']*10)
gc={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
ages=['Under 18','18–24','25–34','35–44','45–54','55–64','65+'];his=['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+']
batch=[];read=0;matched_members=0;started=time.time()
with MEMBERS.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,strict=True):
  read+=1
  if r['membership_status']!='Active' or r['association_scope'] not in ('AGA','International'):continue
  gid=int(r['golfer_id'])
  if gid not in scores:continue
  access,kind,detail=classify(r['club_id'],r['club_category'],r['club_type'],gc)
  group=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access'
  age=numeric(r['age_at_extraction']) if r['matched_golfer_id'] else None
  ageband='Unknown / invalid' if age is None or not 0<=age<=120 else next(b for e,b in zip([18,25,35,45,55,65,121],ages) if age<e)
  hi=numeric(r['handicap_index']) if r['matched_golfer_id'] else None
  hiband='No Index' if r['handicap_index_display'].strip().upper()=='NH' else 'Unknown' if hi is None else next(b for e,b in zip([0,5,10,15,20,30,float('inf')],his) if hi<=e)
  vals=[r['member_population'],r['association_name']+' ('+r['association_id']+')',access,group,r['club_type'] or 'Unknown',r['gender'] if r['gender'] in ('Male','Female') else 'Unknown',ageband,hiband,r['club_name']+' ('+r['club_id']+')',r['association_scope']]
  batch.append((gid,cell_id(vals)));matched_members+=1
  if len(batch)>=20000:db.executemany('INSERT INTO matches VALUES (?,?)',batch);batch=[]
  if matched_members%1000000==0:print('Matched membership rows',matched_members,'elapsed',round(time.time()-started),flush=True)
db.executemany('INSERT INTO matches VALUES (?,?)',batch);db.commit();print('Building patterns',flush=True)
patterns=Counter();matched=Counter()
for gid,rs in groupby(db.execute('SELECT golfer,cell FROM matches ORDER BY golfer'),key=lambda r:r[0]):
 band=scores.pop(gid);ids=tuple(sorted({r[1] for r in rs}));patterns[(ids,band)]+=1;matched[band]+=1
unmatched=Counter(scores.values())
for band,n in unmatched.items():patterns[((unknown,),band)]+=n
assert all(matched[b]+unmatched[b]==raw[b] for b in range(3))
out={'meta':{'scoreSource':SOURCE.name,'membershipSource':MEMBERS.name,'scorePeriod':'January 1–October 21, 2026','membershipDate':'October 13, 2026','scoreDateBasis':'Filename and supplied query; two-column export has no extraction timestamp','totalGolfers':sum(raw.values()),'matchedGolfers':sum(matched.values()),'unmatchedGolfers':sum(unmatched.values()),'bucketCounts':[raw[b] for b in range(3)],'unmatchedBuckets':[unmatched[b] for b in range(3)],'scoreCount':score_sum},'keys':keys,'labels':labels,'cells':cells,'patterns':[[list(ids),band,n] for (ids,band),n in patterns.items()]}
(ROOT/'data/processed/score_explorer.json').write_text(json.dumps(out,separators=(',',':')))
(ROOT/'reports/score_explorer_validation.json').write_text(json.dumps(out['meta'],indent=2))
print(json.dumps(out['meta']),flush=True);print('Cells',len(cells),'patterns',len(patterns),flush=True)
db.close()
