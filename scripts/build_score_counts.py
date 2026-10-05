"""Import reconciled score aggregates and update only the Scores views and home score tile."""
import csv, json, shutil, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/Users/EvanBelfi/Downloads/score_monthly_counts_by_association_2025_2026.csv.csv')
DEST = ROOT / 'data/raw/scores/score_monthly_counts_by_association_2025_2026.csv'
if SOURCE.exists(): shutil.copyfile(SOURCE, DEST)
with DEST.open(encoding='utf-8-sig') as f: rows = list(csv.DictReader(f))
def number(r):
    n=int(r['score_count']); assert n >= 0; return n
months=sorted({r['posting_month'][:7] for r in rows})
assert months == [f'2025-{m:02}' for m in range(1,13)]+[f'2026-{m:02}' for m in range(1,9)]
assert {r['association_scope'] for r in rows} <= {'aga','international','test','trial_association','unknown','ambiguous'}
for field in ['is_regular','is_junior','is_trial']:
    assert {r[field] for r in rows} <= {'true','false',''}
original=Counter()
with (ROOT/'data/raw/scores/score_monthly_totals_including_temporary.csv').open() as f:
    for r in csv.DictReader(f): original[r['posting_month'][:7]]+=number(r)
raw=Counter(); tests=Counter()
for r in rows:
    raw[r['posting_month'][:7]]+=number(r)
    if r['association_scope']=='test': tests[r['posting_month'][:7]]+=number(r)
assert dict(raw)==dict(original), 'Source totals differ: investigate before importing.'
from import_score_methods import load_methods
rows, methods = load_methods(ROOT, rows)
if methods:
    raw=Counter(); tests=Counter()
    for r in rows:
        raw[r['posting_month'][:7]]+=number(r)
        if r['association_scope']=='test': tests[r['posting_month'][:7]]+=number(r)
latest=months[-1]; year=int(latest[:4]); end=int(latest[5:])
def ytd(month, y): return month[:4]==str(y) and int(month[5:7])<=end
scopes={}
for scope in ['all','aga','international']:
    scopes[scope]={}
    for pop in ['all','regular','junior','trial']:
        selected=[r for r in rows if r['association_scope']!='test' and (scope=='all' or r['association_scope']==scope) and (pop=='all' or r['is_'+pop]=='true')]
        monthly={m:dict(month=m,count=0,trial=0,unknownTrial=0,temporary=0,underReview=0,unknownAssociation=0,trialAssociation=0,unclassifiedPopulation=0) for m in months}
        association_months={m:{} for m in months}
        associations={}
        for r in selected:
            n=number(r); m=r['posting_month'][:7]; d=monthly[m]; d['count']+=n
            if r['is_trial']=='true': d['trial']+=n
            if not r['is_trial']: d['unknownTrial']+=n
            if r['status']=='Temporary': d['temporary']+=n
            if r['status']=='UnderReview': d['underReview']+=n
            if r['association_scope'] in ['unknown','ambiguous']: d['unknownAssociation']+=n
            if r['association_scope']=='trial_association': d['trialAssociation']+=n
            if r['is_regular']!='true' and r['is_junior']!='true': d['unclassifiedPopulation']+=n
            key=(r['association_scope'],r['association_id'])
            am=association_months[m]
            if key not in am: am[key]=dict(id=r['association_id'],scope=r['association_scope'],name=r['association_name'] or 'Unmatched association',scores=0,junior=0)
            am[key]['scores']+=n
            if r['is_junior']=='true':am[key]['junior']+=n
            if key not in associations: associations[key]=dict(id=r['association_id'],scope=r['association_scope'],name=r['association_name'] or 'Unmatched association',scores=0,prior=0,junior=0)
            a=associations[key]
            if ytd(m,year):
                a['scores']+=n
                if r['is_junior']=='true': a['junior']+=n
            elif ytd(m,year-1): a['prior']+=n
        data=dict(months=list(monthly.values()),associations=sorted(associations.values(),key=lambda r:-r['scores']))
        data['associationMonths']=[dict(month=m,associations=list(association_months[m].values())) for m in months]
        assert sum(a['scores'] for a in data['associations'])==sum(d['count'] for d in data['months'] if ytd(d['month'],year))
        if methods:
            method_months={m:{k:0 for k in ['total','hole','stats','unknown']} for m in months}
            api_months={m:Counter() for m in months}
            breakdown_months={m:{k:Counter() for k in ['product','provider','membership','holes']} for m in months}
            for r in methods['rows']:
                if r['association_scope']=='test' or (scope!='all' and r['association_scope']!=scope) or (pop!='all' and r['is_'+pop]!='true'): continue
                method_months[r['posting_month'][:7]][r['method_category']]+=number(r)
                if r.get('posting_application')=='API': api_months[r['posting_month'][:7]][r['posting_application_api']]+=number(r)
                if 'breakdowns' in r:
                    for k,v in r['breakdowns'].items(): breakdown_months[r['posting_month'][:7]][k][v]+=number(r)
            for d in data['months']:
                d['methods']=method_months[d['month']]
                assert sum(d['methods'].values())==d['count']
                if methods['meta']['consolidated']:
                    d['breakdowns']=breakdown_months[d['month']]
                    d['apiAccounts']=api_months[d['month']]
                    assert sum(d['apiAccounts'].values())==d['breakdowns']['product'].get('API',0)
                    for counts in d['breakdowns'].values(): assert sum(counts.values())==d['count']
        scopes[scope][pop]=data
for m in months: assert next(x['count'] for x in scopes['all']['all']['months'] if x['month']==m)==raw[m]-tests[m]
payload=dict(meta=dict(firstMonth=months[0],latestMonth=latest,year=year,reportMonth=end,source=DEST.name,extractedAt=sorted({r['extracted_at'] for r in rows}),database=sorted({r['source_database'] for r in rows}),excludedTests=dict(tests)),scopes=scopes)
if methods:
    payload['meta']['postingMethods']=methods['meta']
    payload['meta']['source']=methods['meta']['source']
    payload['meta']['extractedAt']=methods['meta']['extractedAt']
from import_score_history import load_history
history, history_sources = load_history(ROOT)
for scope, pops in scopes.items():
    for pop, data in pops.items():
        data['historicalMonths'] = [m for m in history[scope][pop] if m['month'] < '2025-01']
        data['demographicMonths'] = history[scope][pop]
        data['associationMonths'] = [dict(month=m['month'],associations=m['associations']) for m in data['historicalMonths']] + data['associationMonths']
reconciliation = []
for scope, pops in scopes.items():
    for pop, data in pops.items():
        existing = {m['month']:m['count'] for m in data['months']}
        for month in data['demographicMonths']:
            if month['month'] in existing:
                reconciliation.append(dict(scope=scope,population=pop,month=month['month'],existing=existing[month['month']],demographic=month['count'],difference=month['count']-existing[month['month']]))
(ROOT/'data/validation/score_demographics_reconciliation.json').write_text(json.dumps(reconciliation,indent=2))
payload['meta']['historicalSources'] = history_sources
(ROOT/'data/processed/score_counts.json').write_text(json.dumps(payload,separators=(',',':')))
helper=(ROOT/'scripts/scores_scope_view.js').read_text().strip()
page=ROOT/'Handicapping and GHIN Dashboard.html';s=page.read_text()
start=s.index('// Scope selections are available;') if '// Scope selections are available;' in s else s.index('// BEGIN LIVE SCORE COUNTS')
endpos=s.index('let scoresPopulation="all";',start)
s=s[:start]+'// BEGIN LIVE SCORE COUNTS\nconst SCORE_COUNTS_DATA='+json.dumps(payload,separators=(',',':'))+';\n'+helper+'\n// END LIVE SCORE COUNTS\n'+s[endpos:]
old='if(activeTop==="scores"){if(scoresGeography!=="all")$("app").innerHTML=scoresScopePendingView();else $("app").insertAdjacentHTML("afterbegin",scoresScopePendingNotice());}'
new='if(activeTop==="scores"){$("app").innerHTML=liveScoresPage();document.querySelector(".subtitle").textContent="Scores through August 31, 2026 · "+scoresScopeLabel();}'
if old in s: s=s.replace(old,new,1)
else: assert new in s
old='${summaryTrendCard("SCORES POSTED","scores",c.map(x=>x.scoresGhin),p.map(x=>x.scoresGhin),"scores","Open Scores →","▲ 6.3%","▲ 6.3%")}'
if old in s: s=s.replace(old,'${liveScoresHomeCard()}',1)
else: assert '${liveScoresHomeCard()}' in s
css=(ROOT/'scripts/scores_counts.css').read_text()
if '/* BEGIN LIVE SCORE STYLES */' in s:
    s=re.sub(r'/\* BEGIN LIVE SCORE STYLES \*/.*?/\* END LIVE SCORE STYLES \*/',lambda _: '/* BEGIN LIVE SCORE STYLES */\n'+css+'\n/* END LIVE SCORE STYLES */',s,flags=re.S)
else: s=s.replace('</style>','/* BEGIN LIVE SCORE STYLES */\n'+css+'\n/* END LIVE SCORE STYLES */\n</style>',1)
trial_button = '<button type="button" data-scores-population="trial" class="${scoresPopulation==="trial"?"active":""}">Trial Golfers</button>'
if 'data-scores-population="trial"' not in s:
    junior_button = '<button type="button" data-scores-population="junior" class="${scoresPopulation==="junior"?"active":""}">Junior Members</button>'
    assert s.count(junior_button) == 1
    s=s.replace(junior_button,junior_button+trial_button,1)
page.write_text(s)
report=dict(months=len(months),rows=len(rows),monthlyReconciliation='exact within latest export; documented small drift from prior export' if methods else 'exact',excludedTests=dict(tests),ytd={scope:{pop:sum(d['count'] for d in scopes[scope][pop]['months'] if ytd(d['month'],year)) for pop in ['all','regular','junior','trial']} for scope in scopes})
(ROOT/'data/validation/score_counts.validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
