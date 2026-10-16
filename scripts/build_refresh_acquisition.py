"""Distinct creation cohorts from all eligible membership statuses in the refresh."""
import csv,json,sqlite3
from collections import Counter
from itertools import groupby
from audit_membership_refresh import ROOT,DB,SOURCE

def main():
    staging=SOURCE.parent/'acquisition.sqlite'
    if staging.exists():staging.unlink()  # Regenerable private staging owned by this script.
    db=sqlite3.connect(staging)
    db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
    db.execute('CREATE TABLE m(id INTEGER PRIMARY KEY,golfer INTEGER,scope INTEGER,pop INTEGER,month INTEGER)')
    batch=[];missing=0
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,strict=True):
            date=r['golfer_creation_date']
            if not date:missing+=1;continue
            if not '2026-01-01'<=date<'2026-10-01':continue
            scope=['AGA','International','Trial','Unresolved'].index(r['association_scope'])
            pop=['Regular','Junior','Unclassified','Trial'].index(r['member_population'])
            batch.append((int(r['membership_id']),int(r['golfer_id']),scope,pop,int(date[:4])*100+int(date[5:7])))
            if len(batch)==10000:db.executemany('INSERT INTO m VALUES (?,?,?,?,?)',batch);batch=[];db.commit()
    db.executemany('INSERT INTO m VALUES (?,?,?,?,?)',batch);db.commit()
    conflict_count=db.execute('SELECT COUNT(*) FROM (SELECT golfer FROM m GROUP BY golfer HAVING MIN(month)<>MAX(month))').fetchone()[0]
    assert conflict_count==0,'Creation month differs across memberships for the same golfer'
    candidates=dict(db.execute('SELECT golfer,MIN(month) FROM m GROUP BY golfer'))
    assert len(candidates)<1000000,'Use partitioned validation if the cohort exceeds one million golfers'
    # A second bounded scan checks candidate dates against memberships outside the period.
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,strict=True):
            expected=candidates.get(int(r['golfer_id']))
            if expected is None:continue
            date=r['golfer_creation_date']
            assert date and int(date[:4])*100+int(date[5:7])==expected,'Creation month conflicts outside the selected period'
    del candidates
    monthly={s:{p:[0]*9+[None]*3 for p in ['all','regular','junior','unclassified']} for s in ['aga','international','all','trial','unresolved']}
    reconciliation=Counter();unfiltered=[0]*9;conflicts=0
    for golfer,rows in groupby(db.execute('SELECT golfer,scope,pop,month FROM m WHERE month>=202601 AND month<202610 ORDER BY golfer'),key=lambda row:row[0]):
        records=list(rows);months={r[3] for r in records}
        assert len(months)==1,'Conflicting creation month for a golfer'
        month=months.pop()%100-1;unfiltered[month]+=1
        groups={(r[1],r[2]) for r in records}
        scopes={s for s,p in groups}
        label='main' if scopes & {0,1} else 'trial_only' if 2 in scopes else 'unresolved_only'
        reconciliation[label]+=1
        if scopes & {0,1} and 2 in scopes:reconciliation['main_with_trial_membership']+=1
        if scopes >= {0,1}:reconciliation['aga_international_overlap']+=1
        for scope,codes in [('aga',{0}),('international',{1}),('all',{0,1}),('trial',{2}),('unresolved',{3})]:
            matched={p for s,p in groups if s in codes}
            if not matched:continue
            monthly[scope]['all'][month]+=1
            for i,pop in enumerate(['regular','junior','unclassified']):
                if i in matched:monthly[scope][pop][month]+=1
    diagnostic=[27519,27895,53964,88126,84490,78029,63520,52861,32221]
    out=dict(source=SOURCE.name,creationField='golfer_creation_date (v_golfer_clubs.golfer_creation_date)',fieldConfirmedBy='Evan, October 13, 2026',missingCreationDateRows=missing,conflictingCreationMonths=conflict_count,periodStart='2026-01-01',periodEndExclusive='2026-10-01',timezone='America/New_York',scopes=monthly,
        methodology='Unique GHIN numbers by golfer Creation Date. All membership statuses retained. Scope and membership type use affiliations represented in the October 13 export, not historical affiliation at creation. Non-test clubs and associations only. Trial memberships and unresolved associations excluded from main counts. Golfers absent from the membership export are outside coverage.',
        reconciliation=dict(reconciliation,representedGolfers=sum(unfiltered),representedMonthly=unfiltered,earlierUnfilteredDiagnostic=sum(diagnostic),diagnosticMonthly=diagnostic,diagnosticMinusRepresented=sum(diagnostic)-sum(unfiltered),limitation='The earlier diagnostic used a DIFFERENT date field (v_golfers.created_at) as well as different scope and extraction time. Its difference is not an exclusion count. The full golfer table and both date fields are needed for a like-for-like reconciliation.'))
    path=ROOT/'data/processed/refresh-2026-10-13/acquisition.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
