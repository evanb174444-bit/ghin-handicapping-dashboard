"""Join private score IDs to November 3 active memberships; publish anonymous patterns only."""
import csv,json,sqlite3,shutil,time,sys
TRIAL="--trial" in sys.argv
csv.field_size_limit(16*1024*1024)
from pathlib import Path
from collections import Counter
from itertools import groupby
from datetime import date
from review_membership_exports import classify,numeric
ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'data/raw/score_participation_2026-11-06';PRIVATE.mkdir(exist_ok=True)
SOURCE=Path('/Users/EvanBelfi/Downloads/score_participation_2026-11-06.csv.csv')
MEMBERS=ROOT/'data/raw/membership_refresh_2026-11-03/membership_refresh_2026-11-03.csv.csv'
DB=PRIVATE/('trial-matches.sqlite' if TRIAL else 'member-matches.sqlite')
REUSE='--reuse-matches' in sys.argv
assert REUSE or not DB.exists(),'Private staging already exists; inspect before rebuilding'
archived=PRIVATE/SOURCE.name
if archived.exists():SOURCE=archived
else:shutil.copy2(SOURCE,archived)
scores={};raw=Counter();score_sum=0;captures=set();metadata=set()
with SOURCE.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,strict=True):
  if r['population']!=('trial' if TRIAL else 'non_trial'):continue
  captures.add(r['extracted_at']);metadata.add((r['source_database'],r['reporting_timezone'],r['score_period_start'],r['score_period_end_exclusive']))
  gid=int(r['golfer_id']);n=int(r['ytd_score_count']);assert gid not in scores and n>=0
  band=0 if n==0 else 1 if n<=7 else 2 if n<=24 else 3 if n<=49 else 4;scores[gid]=band;raw[band]+=1;score_sum+=n
assert scores and captures and metadata
assert all(x[1]=='America/New_York' and x[2].startswith('2026-01-01') and x[3].startswith('2026-11-06') for x in metadata)
print('Score export:',len(scores),dict(raw),'captures',len(captures),flush=True)
if REUSE:
 db=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True)
 prior=json.loads((ROOT/('data/processed/score_trial_explorer.json' if TRIAL else 'data/processed/score_explorer.json')).read_text())
 assert prior['meta']['membershipSource']==MEMBERS.name and prior['meta']['scoreSource']==SOURCE.name
 keys,labels,cells=prior['keys'],prior['labels'],prior['cells'];unknown=0
else:
 db=sqlite3.connect(DB);db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF');db.execute('CREATE TABLE matches(golfer INTEGER,cell INTEGER)')
 keys=['membershipType','association','access','clubGroup','clubType','gender','age','handicap','club','scope','golferCreationYear','membershipCreationYear']
 labels={k:[] for k in keys};lookup={k:{} for k in keys};cells=[];ci={}
 def cell_id(values):
  ids=[]
  for k,v in zip(keys,values):
   if v not in lookup[k]:lookup[k][v]=len(labels[k]);labels[k].append(v)
   ids.append(lookup[k][v])
  key=tuple(ids)
  if key not in ci:ci[key]=len(cells);cells.append(ids)
  return ci[key]
 unknown=cell_id(['No November 3 active membership match']*len(keys))
 def creation_year(value):
  try:
   parsed=date.fromisoformat(value.strip()[:10])
   return str(parsed.year) if date(1900,1,1)<=parsed<=date(2026,11,3) else 'Unknown / invalid'
  except (ValueError,AttributeError):return 'Unknown / invalid'
 
 gc={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
 ages=['Under 18','18–24','25–34','35–44','45–54','55–64','65+'];his=['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+']
 batch=[];read=0;matched_members=0;started=time.time()
 with MEMBERS.open(encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f,strict=True):
   read+=1
   if r['membership_status']!='Active' or r['association_scope'] not in (('Trial',) if TRIAL else ('AGA','International')):continue
   gid=int(r['golfer_id'])
   if gid not in scores:continue
   access,kind,detail=classify(r['club_id'],r['club_category'],r['club_type'],gc)
   group=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access'
   age=numeric(r['age_at_extraction']) if r['matched_golfer_id'] else None
   ageband='Unknown / invalid' if age is None or not 0<=age<=120 else next(b for e,b in zip([18,25,35,45,55,65,121],ages) if age<e)
   hi=numeric(r['handicap_index']) if r['matched_golfer_id'] else None
   hiband='No Index' if r['handicap_index_display'].strip().upper()=='NH' else 'Unknown' if hi is None else next(b for e,b in zip([0,5,10,15,20,30,float('inf')],his) if hi<=e)
   vals=[r['member_population'],r['association_name']+' ('+r['association_id']+')',access,group,r['club_type'] or 'Unknown',r['gender'] if r['gender'] in ('Male','Female') else 'Unknown',ageband,hiband,r['club_name']+' ('+r['club_id']+')',r['association_scope'],creation_year(r['golfer_creation_date']),creation_year(r['membership_creation_date'])]
   batch.append((gid,cell_id(vals)));matched_members+=1
   if len(batch)>=20000:db.executemany('INSERT INTO matches VALUES (?,?)',batch);batch=[]
   if matched_members%1000000==0:print('Matched membership rows',matched_members,'elapsed',round(time.time()-started),flush=True)
 db.executemany('INSERT INTO matches VALUES (?,?)',batch);db.commit();print('Building patterns',flush=True)
patterns=Counter();matched=Counter()
for gid,rs in groupby(db.execute('SELECT golfer,cell FROM matches ORDER BY golfer'),key=lambda r:r[0]):
 band=scores.pop(gid);ids=tuple(sorted({r[1] for r in rs}));patterns[(ids,band)]+=1;matched[band]+=1
unmatched=Counter(scores.values())
for band,n in unmatched.items():patterns[((unknown,),band)]+=n
assert all(matched[b]+unmatched[b]==raw[b] for b in range(5))
out={'meta':{'scoreSource':SOURCE.name,'membershipSource':MEMBERS.name,'scorePeriod':'January 1–November 6, 2026','membershipDate':'November 3, 2026','scoreDateBasis':'CSV score_period_start through score_period_end_exclusive; score created_at', 'extractionTimestamps':sorted(captures),'sourceMetadata':[list(x) for x in sorted(metadata)],'totalGolfers':sum(raw.values()),'matchedGolfers':sum(matched.values()),'unmatchedGolfers':sum(unmatched.values()),'bucketLabels':['0 scores','1–7 scores','8–24 scores','25–49 scores','50+ scores'],'bucketCounts':[raw[b] for b in range(5)],'unmatchedBuckets':[unmatched[b] for b in range(5)],'scoreCount':score_sum,'creationDateFields':{'golferCreationYear':'golfer_creation_date','membershipCreationYear':'membership_creation_date'}},'keys':keys,'labels':labels,'cells':cells,'patterns':[[list(ids),band,n] for (ids,band),n in patterns.items()]}
(ROOT/('data/processed/score_trial_explorer.json' if TRIAL else 'data/processed/score_explorer.json')).write_text(json.dumps(out,separators=(',',':')))
(ROOT/('reports/score_trial_explorer_validation.json' if TRIAL else 'reports/score_explorer_validation.json')).write_text(json.dumps(out['meta'],indent=2))
print(json.dumps({k:v for k,v in out['meta'].items() if k not in ('extractionTimestamps','sourceMetadata')}),flush=True);print('Cells',len(cells),'patterns',len(patterns),flush=True)
db.close()
