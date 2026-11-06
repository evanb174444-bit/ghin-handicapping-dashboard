"""Validate and install the September/October-only posting-mix export locally."""
from pathlib import Path
import json,csv,hashlib,shutil
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'data').exists(): ROOT=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard')
import sys
sys.path.insert(0,str(ROOT/'scripts'))
from import_score_methods import classify_breakdowns
source=Path('/Users/EvanBelfi/Downloads/scores_posting_mix_sep_oct_2026.csv.csv')
archive=ROOT/'data/raw/scores/2026-11-06/scores_posting_mix_sep_oct_2026.csv';archive.parent.mkdir(exist_ok=True)
if archive.exists(): assert archive.read_bytes()==source.read_bytes()
else:shutil.copyfile(source,archive)
with archive.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
months=['2026-09','2026-10'];assert sorted({r['posting_month'][:7] for r in rows})==months
fields=[k for k in rows[0] if k not in ['extracted_at','source_database','score_count']];seen=set();raw=Counter();tests=Counter();dates=set()
labels={'Total Adjusted Score':'total','Total Adjusted Score - Front 9 / Back 9':'total','Hole-by-Hole':'hole','Hole-by-Hole Stats':'stats','Missing from extract':'unknown','Unknown posting method':'unknown','Conflicting posting methods':'unknown','Unknown':'unknown','Conflicting labels':'unknown'}
for r in rows:
 key=tuple(r[k] for k in fields);assert key not in seen;seen.add(key)
 n=int(r['score_count']);assert n>=0
 assert r['association_scope'] in ['aga','international','test','trial_association','unknown','ambiguous']
 for k in ['is_regular','is_junior','is_trial','has_unclassified_membership']:assert r[k] in ['true','false','']
 assert r['posting_method'] in labels
 r['_count']=n;r['_method']=labels[r['posting_method']];r['_breakdowns']=classify_breakdowns(r)
 raw[r['posting_month'][:7]]+=n;dates.add(r['extracted_at'])
 if r['association_scope']=='test':tests[r['posting_month'][:7]]+=n
payloadPath=ROOT/'data/processed/score_counts.json';original=json.loads(payloadPath.read_text());payload=json.loads(payloadPath.read_text())
assert original['meta']['latestMonth']=='2026-08','Install against August baseline only'
backup=ROOT/'backups/scores-before-2026-11-06';backup.mkdir(exist_ok=True)
for name in ['data/processed/score_counts.json','Handicapping and GHIN Dashboard.html','scripts/scores_scope_view.js']:
 dest=backup/Path(name).name
 if not dest.exists():shutil.copyfile(ROOT/name,dest)
for scope,pops in payload['scopes'].items():
 for pop,data in pops.items():
  assert not any(r['month'] in months for r in data['months'])
  for month in months:
   d=dict(month=month,count=0,trial=0,unknownTrial=0,temporary=0,underReview=0,unknownAssociation=0,trialAssociation=0,unclassifiedPopulation=0,methods={k:0 for k in ['total','hole','stats','unknown']},breakdowns={k:Counter() for k in ['product','provider','membership','holes']},apiAccounts=Counter());associations={}
   for r in rows:
    if r['posting_month'][:7]!=month or r['association_scope']=='test' or (scope!='all' and r['association_scope']!=scope) or (pop!='all' and r['is_'+pop]!='true'):continue
    n=r['_count'];d['count']+=n;d['methods'][r['_method']]+=n
    for k,match in [('trial',r['is_trial']=='true'),('unknownTrial',not r['is_trial']),('temporary',r['status']=='Temporary'),('underReview',r['status']=='UnderReview'),('unknownAssociation',r['association_scope'] in ['unknown','ambiguous']),('trialAssociation',r['association_scope']=='trial_association'),('unclassifiedPopulation',r['is_regular']!='true' and r['is_junior']!='true')]:
     if match:d[k]+=n
    for k,v in r['_breakdowns'].items():d['breakdowns'][k][v]+=n
    if r['posting_application']=='API':d['apiAccounts'][r['posting_application_api']]+=n
    key=(r['association_scope'],r['association_id']);a=associations.setdefault(key,dict(id=r['association_id'],scope=r['association_scope'],name=r['association_name'] or 'Unmatched association',scores=0,junior=0));a['scores']+=n
    if r['is_junior']=='true':a['junior']+=n
   assert sum(d['methods'].values())==d['count']
   assert all(sum(v.values())==d['count'] for v in d['breakdowns'].values())
   assert sum(d['apiAccounts'].values())==d['breakdowns']['product'].get('API',0)
   assert sum(a['scores'] for a in associations.values())==d['count']
   data['months'].append(d);data['associationMonths'].append(dict(month=month,associations=list(associations.values())))
  # Recompute YTD association summary from retained original months plus new months.
  summary={}
  for m in data['associationMonths']:
   if not (m['month'].startswith('2025') or m['month'].startswith('2026')) or int(m['month'][5:])>10:continue
   for row in m['associations']:
    key=(row['scope'],row['id']);a=summary.setdefault(key,dict(id=row['id'],scope=row['scope'],name=row['name'],scores=0,prior=0,junior=0))
    if m['month'].startswith('2026'):a['scores']+=row['scores'];a['junior']+=row.get('junior',0);a['name']=row['name']
    else:a['prior']+=row['scores']
  data['associations']=sorted(summary.values(),key=lambda r:-r['scores'])
  assert data['months'][:20]==original['scopes'][scope][pop]['months']
  for k in ['historicalMonths','demographicMonths']:assert data[k]==original['scopes'][scope][pop][k]
for month in months:
 d=next(d for d in payload['scopes']['all']['all']['months'] if d['month']==month);assert d['count']==raw[month]-tests[month]
metadata=dict(source=archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),rows=len(rows),months=months,extractedAt=sorted(dates),database=sorted({r['source_database'] for r in rows}),rawMonthly=dict(raw),excludedTests=dict(tests),scorePeriodStart='2026-09-01',scorePeriodEndExclusive='2026-11-01',timezoneEvidence='CSV timestamps include -0500; session timezone name not supplied')
payload['meta'].update(latestMonth='2026-10',reportMonth=10,incrementalSources=payload['meta'].get('incrementalSources',[])+[metadata],demographicLatestMonth='2026-08')
payload['meta']['excludedTests'].update(tests)
report=dict(**metadata,validation='No duplicate aggregate keys; all months/methods/breakdown/association totals reconcile; prior installed months and demographics unchanged.',monthly={m:next(d['count'] for d in payload['scopes']['all']['all']['months'] if d['month']==m) for m in months},ytd={scope:{pop:sum(d['count'] for d in data['months'] if d['month'].startswith('2026')) for pop,data in pops.items()} for scope,pops in payload['scopes'].items()})
payloadPath.write_text(json.dumps(payload,separators=(',',':')))
(ROOT/'reports/scores_incremental_2026-11-06.json').write_text(json.dumps(report,indent=2)+'\n')
page=ROOT/'Handicapping and GHIN Dashboard.html';s=page.read_text();start=s.index('const SCORE_COUNTS_DATA=');end=s.index(';\n',start);s=s[:start]+'const SCORE_COUNTS_DATA='+json.dumps(payload,separators=(',',':'))+s[end:];page.write_text(s)
print(json.dumps({'monthly':report['monthly'],'ytdAll':report['ytd']['all']['all'],'sourceTimestamps':len(dates),'rawTestsExcluded':sum(tests.values())},indent=2))
