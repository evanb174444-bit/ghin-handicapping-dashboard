"""Stream historical demographic aggregates; keep historical totals separate from mix data."""
import csv
import hashlib
import json
from collections import Counter, defaultdict

def load_history(root):
    scopes = {s: {p: Counter() for p in ('all','regular','junior','trial')} for s in ('all','aga','international')}
    mix = {s:{p:defaultdict(lambda:dict(trial=0,breakdowns={k:Counter() for k in ('membership','gender','age','access','club','clubGroup')})) for p in ('all','regular','junior','trial')} for s in scopes}
    association_months = {s:{p:defaultdict(dict) for p in ('all','regular','junior','trial')} for s in scopes}
    from review_membership_exports import classify, GC_SOURCE
    gc=set()
    with GC_SOURCE.open(encoding='utf-16',newline='') as f:
        gc={r['Club Number'].strip() for r in csv.DictReader(f,delimiter='\t') if r['Club Number'].strip()}
    reports = []
    covered = set()
    for path in sorted((root/'data/raw/scores').glob('score_monthly_demographics_*.csv')):
        raw, tests = Counter(), Counter()
        seen = set()
        rows = 0
        dates, databases = set(), set()
        with path.open(encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            dimensions = [k for k in reader.fieldnames if k not in ('extracted_at','source_database','score_count')]
            for r in reader:
                key = hashlib.sha256(json.dumps([r[k] for k in dimensions]).encode()).digest()
                assert key not in seen, f'Duplicate aggregate in {path.name}'
                seen.add(key)
                n = int(r['score_count']); assert n >= 0
                m = r['posting_month'][:7]
                assert '2022-01' <= m <= '2026-08', 'Unexpected demographic export period'
                scope = r['association_scope']
                assert scope in ('aga','international','test','unknown','ambiguous','trial_association')
                for flag in ('is_regular','is_junior','is_trial'):
                    assert r[flag] in ('true','false','')
                raw[m] += n; rows += 1
                dates.add(r['extracted_at']); databases.add(r['source_database'])
                if scope == 'test': tests[m] += n; continue
                regular,junior=r['is_regular']=='true',r['is_junior']=='true'
                membership='Both Regular and Junior' if regular and junior else 'Regular' if regular else 'Junior' if junior else 'Unclassified'
                access,club,detail=classify(r['primary_club_id'],r['primary_club_category'],r['primary_club_type'],gc)
                access=access if access in ('Public','Private') else 'Unknown'
                dims=dict(membership=membership,gender=r['gender'] or 'Unknown',age=r['age_band_at_extraction'] or 'Unknown',access=access,club=club,clubGroup=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access')
                pops=['all']+[p for p in ('regular','junior','trial') if r['is_'+p]=='true']
                for s in ('all', scope) if scope in ('aga','international') else ('all',):
                    for p in pops:
                        scopes[s][p][m] += n
                        ak=(scope,r['association_id'])
                        am=association_months[s][p][m]
                        if ak not in am: am[ak]=dict(id=r['association_id'],scope=scope,name=r['association_name'] or 'Unmatched association',scores=0,junior=0)
                        am[ak]['scores']+=n
                        if junior: am[ak]['junior']+=n
                        bucket=mix[s][p][m]
                        if r['is_trial']=='true':bucket['trial']+=n
                        for k,v in dims.items():bucket['breakdowns'][k][v]+=n
        assert not covered.intersection(raw), 'Historical files overlap months'
        for year in {m[:4] for m in raw}:
            assert {m for m in raw if m.startswith(year)} == {f'{year}-{i:02}' for i in range(1,9 if year == '2026' else 13)}, 'Incomplete demographic reporting period'
        covered.update(raw)
        for m in raw: assert scopes['all']['all'][m] == raw[m]-tests[m]
        reports.append(dict(source=path.name,rows=rows,rawMonthly=dict(raw),excludedTests=dict(tests),extractedAt=sorted(dates),databases=sorted(databases)))
    result={s:{p:[dict(month=m,count=counts.get(m,0),**mix[s][p][m]) for m in sorted(covered)] for p,counts in pops.items()} for s,pops in scopes.items()}
    for s,pops in result.items():
        for p,months in pops.items():
            for month in months:
                month['associations']=list(association_months[s][p][month['month']].values())
                assert sum(a['scores'] for a in month['associations'])==month['count']
    for pops in result.values():
        for months in pops.values():
            for month in months:
                for values in month['breakdowns'].values():assert sum(values.values())==month['count']
    report=dict(sources=reports,monthlyTotals=result,validation='Unique aggregates; complete years through 2025 and January–August 2026; non-test totals reconcile to source. No independent database total supplied.')
    (root/'data/validation/score_history.validation.json').write_text(json.dumps(report,indent=2))
    return result, reports
