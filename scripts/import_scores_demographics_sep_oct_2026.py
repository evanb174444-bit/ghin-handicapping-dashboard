"""Install Sept/Oct demographic aggregates; retain independent posting totals and all prior history."""
from pathlib import Path
import sys,json,csv,hashlib,shutil
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'data').exists():ROOT=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard')
sys.path.insert(0,str(ROOT/'scripts'))
from review_membership_exports import classify
source=Path('/Users/EvanBelfi/Downloads/scores_demographics_sep_oct_2026.csv.csv');archive=ROOT/'data/raw/scores/2026-11-06/scores_demographics_sep_oct_2026.csv'
archive.parent.mkdir(exist_ok=True)
if archive.exists():assert archive.read_bytes()==source.read_bytes()
else:shutil.copyfile(source,archive)
months=['2026-09','2026-10'];scopes=['all','aga','international'];pops=['all','regular','junior','trial'];dimensions=['membership','gender','age','access','club','clubGroup']
gc={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']};assert len(gc)==57
def fresh(m):return dict(month=m,count=0,trial=0,breakdowns={k:Counter() for k in dimensions},associations={})
result={s:{p:{m:fresh(m) for m in months} for p in pops} for s in scopes};raw=Counter();tests=Counter();dates=set();databases=set();seen=set();nrows=0
with archive.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);keys=[k for k in reader.fieldnames if k not in ['extracted_at','source_database','score_count']]
 for r in reader:
  key=tuple(r[k] for k in keys);assert key not in seen,'Duplicate aggregate';seen.add(key);nrows+=1
  n=int(r['score_count']);assert n>=0;m=r['posting_month'][:7];assert m in months
  scope=r['association_scope'];assert scope in ['aga','international','test','unknown','ambiguous','trial_association']
  for k in ['is_regular','is_junior','is_trial','has_unclassified_membership']:assert r[k] in ['true','false','']
  dates.add(r['extracted_at']);databases.add(r['source_database']);raw[m]+=n
  if scope=='test':tests[m]+=n;continue
  regular,junior=r['is_regular']=='true',r['is_junior']=='true'
  membership='Both Regular and Junior' if regular and junior else 'Regular' if regular else 'Junior' if junior else 'Unclassified'
  access,club,detail=classify(r['primary_club_id'],r['primary_club_category'],r['primary_club_type'],gc);access=access if access in ['Public','Private'] else 'Unknown'
  dims=dict(membership=membership,gender=r['gender'] or 'Unknown',age=r['age_band_at_extraction'] or 'Unknown',access=access,club=club,clubGroup=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access')
  for s in (['all',scope] if scope in ['aga','international'] else ['all']):
   for p in ['all']+[p for p in pops[1:] if r['is_'+p]=='true']:
    d=result[s][p][m];d['count']+=n
    if r['is_trial']=='true':d['trial']+=n
    for k,v in dims.items():d['breakdowns'][k][v]+=n
    key=(scope,r['association_id']);a=d['associations'].setdefault(key,dict(id=r['association_id'],scope=scope,name=r['association_name'] or 'Unmatched association',scores=0,junior=0));a['scores']+=n
    if junior:a['junior']+=n
assert set(raw)==set(months)
payloadPath=ROOT/'data/processed/score_counts.json';payload=json.loads(payloadPath.read_text());original=json.loads(payloadPath.read_text());assert payload['meta']['demographicLatestMonth']=='2026-08'
backup=ROOT/'backups/scores-before-demographics-2026-11-06';backup.mkdir(exist_ok=True)
for name in ['data/processed/score_counts.json','Handicapping and GHIN Dashboard.html','scripts/scores_scope_view.js']:
 dest=backup/Path(name).name
 if not dest.exists():shutil.copyfile(ROOT/name,dest)
reconciliation=[]
for s in scopes:
 for p in pops:
  data=payload['scopes'][s][p];assert not any(d['month'] in months for d in data['demographicMonths'])
  for m in months:
   d=result[s][p][m];d['associations']=list(d['associations'].values())
   assert sum(a['scores'] for a in d['associations'])==d['count']
   assert all(sum(v.values())==d['count'] for v in d['breakdowns'].values())
   posting=next(r['count'] for r in data['months'] if r['month']==m)
   reconciliation.append(dict(scope=s,population=p,month=m,postingCount=posting,demographicCount=d['count'],difference=d['count']-posting))
   data['demographicMonths'].append(d)
  assert data['demographicMonths'][:-2]==original['scopes'][s][p]['demographicMonths']
  for key in ['months','historicalMonths','associationMonths','associations']:assert data[key]==original['scopes'][s][p][key]
for m in months:
 assert result['all']['all'][m]['count']==raw[m]-tests[m]
 assert abs(next(r['difference'] for r in reconciliation if r['scope']=='all' and r['population']=='all' and r['month']==m))<=50
metadata=dict(source=archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),rows=nrows,months=months,rawMonthly=dict(raw),excludedTests=dict(tests),extractedAt=sorted(dates),database=sorted(databases),definition='Established demographic export; current gender/age and primary-club affiliation. Separate capture from posting mix; differences preserved, no rescaling.',timezoneEvidence='Source offsets -0500; session timezone name not supplied')
payload['meta']['demographicLatestMonth']='2026-10';payload['meta']['demographicIncrementalSources']=payload['meta'].get('demographicIncrementalSources',[])+[metadata]
report=dict(**metadata,reconciliation=reconciliation,validation='Unique aggregate groups; nonnegative counts; exactly two months; all categories/associations reconcile; prior demographic history and all posting totals unchanged.')
(ROOT/'reports/scores_demographics_incremental_2026-11-06.json').write_text(json.dumps(report,indent=2)+'\n');payloadPath.write_text(json.dumps(payload,separators=(',',':')))
h=ROOT/'Handicapping and GHIN Dashboard.html';text=h.read_text();a=text.index('const SCORE_COUNTS_DATA=');b=text.index(';\n',a);h.write_text(text[:a]+'const SCORE_COUNTS_DATA='+json.dumps(payload,separators=(',',':'))+text[b:])
print(json.dumps({'rows':nrows,'allMonths':[{k:r[k] for k in ['month','demographicCount','difference']} for r in reconciliation if r['scope']=='all' and r['population']=='all'],'maxScopeDifference':max(abs(r['difference']) for r in reconciliation),'sourceTimestamps':len(dates)},indent=2))
