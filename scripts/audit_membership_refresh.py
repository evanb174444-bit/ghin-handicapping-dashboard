"""Validate the single refresh export, using compact private disk staging."""
import csv, json, sqlite3, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
DB = SOURCE.parent/'audit.sqlite'

def main():
    if DB.exists():
        raise RuntimeError('Audit staging already exists; inspect before rerunning')
    db=sqlite3.connect(DB)
    db.execute('PRAGMA journal_mode=OFF')
    db.execute('PRAGMA synchronous=OFF')
    db.execute('PRAGMA cache_size=-32768')
    db.execute('CREATE TABLE m(id INTEGER PRIMARY KEY, golfer INTEGER, scope INTEGER, pop INTEGER, active INTEGER, month INTEGER)')
    counts={k:Counter() for k in ['source','scope','status','population','date_checks','issues']}
    batch=[]; n=0; started=time.time()
    before=SOURCE.stat()
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,strict=True):
            n+=1
            assert None not in r and all(v is not None for v in r.values()),n
            assert r['membership_id'] and r['golfer_id'],n
            assert r['club_is_test']=='No' and r['association_is_test']!='Yes',n
            scope=('Trial' if r['association_id']=='237' else 'Unresolved' if r['association_is_test']!='No' else 'AGA' if r['parent_federation']=='United States Golf Association' else 'International' if r['parent_federation'].strip() else 'Unresolved')
            pop='Trial' if scope=='Trial' else {'Standard':'Regular','Junior':'Junior'}.get(r['usga_membership_type'],'Unclassified')
            assert scope==r['association_scope'] and pop==r['member_population'],n
            counts['source'][json.dumps([r['extracted_at'],r['source_database'],r['reporting_timezone']])]+=1
            counts['scope'][scope]+=1; counts['status'][r['membership_status']]+=1; counts['population'][pop]+=1
            a,b=r['golfer_creation_date'],r['golfer_record_created_at']
            check='both_missing' if not a and not b else 'one_missing' if not a or not b else 'exact_match' if a==b else 'same_day' if a[:10]==b[:10] else 'same_month' if a[:7]==b[:7] else 'different_month'
            counts['date_checks'][check]+=1
            if not r['matched_golfer_id']:counts['issues']['missing_golfer_details']+=1
            if r['matched_golfer_id'] and r['matched_golfer_id']!=r['golfer_id']:raise RuntimeError('Golfer join mismatch')
            if r['club_association_id']!=r['association_id']:counts['issues']['membership_club_association_difference']+=1
            month=int(b[:4])*100+int(b[5:7]) if b else None
            batch.append((int(r['membership_id']),int(r['golfer_id']),['AGA','International','Trial','Unresolved'].index(scope),['Regular','Junior','Unclassified','Trial'].index(pop),int(r['membership_status']=='Active'),month))
            if len(batch)==10000:
                db.executemany('INSERT INTO m VALUES (?,?,?,?,?,?)',batch);batch=[];db.commit()
            if n%1000000==0:print(f'Validated {n:,} rows in {time.time()-started:.0f}s',flush=True)
    db.executemany('INSERT INTO m VALUES (?,?,?,?,?,?)',batch);db.commit()
    assert (before.st_size,before.st_mtime_ns)==(SOURCE.stat().st_size,SOURCE.stat().st_mtime_ns)
    print('Source scan complete; calculating scope totals',flush=True)
    counts['rows']=n
    counts['duplicate_membership_ids']=0
    counts['snapshot']={}
    for scope,code in [('aga',0),('international',1),('all',None),('trial',2),('unresolved',3)]:
        counts['snapshot'][scope]={}
        for pop,pcode in [('all',None),('regular',0),('junior',1),('unclassified',2)]:
            where='active=1 AND '+('scope IN (0,1)' if code is None else f'scope={code}')+('' if pcode is None else f' AND pop={pcode}')
            unique,members,multi=db.execute(f'SELECT COUNT(*),COALESCE(SUM(n),0),COALESCE(SUM(n>1),0) FROM (SELECT golfer,COUNT(*) n FROM m WHERE {where} GROUP BY golfer)').fetchone()
            counts['snapshot'][scope][pop]=dict(memberships=members,uniqueGolfers=unique,multiMembershipGolfers=multi,additionalMemberships=members-unique)
    out=ROOT/'reports/membership_refresh_2026-10-13.audit.json'
    out.write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps({k:v for k,v in counts.items() if k!='source'},indent=2),flush=True)

if __name__=='__main__':main()
