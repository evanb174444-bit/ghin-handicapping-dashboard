"""Finish from validated checkpoints with small SQLite sorts on low-disk machines."""
import copy,json,sqlite3
from pathlib import Path
from collections import Counter
from audit_membership_refresh import ROOT,DB,SOURCE

OUT=ROOT/'data/processed/refresh-2026-10-13'
def load(name):return json.loads((OUT/(name+'.json')).read_text())
def save(name,x):(OUT/(name+'.json')).write_text(json.dumps(x,separators=(',',':'))+'\n')
def merge(a,b):
    if isinstance(a,dict):
        result=copy.deepcopy(a)
        for k,v in b.items():result[k]=merge(result[k],v) if k in result else copy.deepcopy(v)
        return result
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):return a+b
    assert a==b,(a,b)
    return a

def main():
    db=sqlite3.connect(DB)
    db.execute('PRAGMA cache_size=-16384');db.execute('PRAGMA temp_store=FILE')
    audit=json.loads((ROOT/'reports/membership_refresh_2026-10-13.audit.json').read_text())
    totals=load('international_totals');intersections=load('membership_intersections')
    clubs=intersections['clubs'];names={c['association']:c['associationName'] for c in clubs};scope_by_aid={c['association']:c['scope'] for c in clubs}
    regions=json.loads((ROOT/'config/association_regions.json').read_text())['associations']
    reviews={s:load('composition_review_'+s) for s in ['aga','international']}
    segments=merge(reviews['aga']['segments'],reviews['international']['segments'])
    reviews['all']=dict(scope=dict(mode='all',label='All Associations',definition='Eligible AGA and international memberships'),segments=segments)
    clubrows={(c['association'],c['id']):dict(c,type=c['mappedType'],recordedType=c['type'],all=0,regular=0,junior=0) for c in clubs}
    # The original private table is preserved, but duplicate raw staging was discarded.
    for aid,cid,pop,n in db.execute('SELECT aid,cid,pop,COUNT(*) FROM active a JOIN cell c ON a.cell=c.id GROUP BY aid,cid,pop'):
        r=clubrows[(aid,cid)];r['all']+=n
        if pop in ('regular','junior'):r[pop]+=n
    print('Club rollups complete',flush=True)
    associations=dict(sources=[SOURCE.name],dates=totals['dates'],scopes={s:{} for s in reviews})
    for pkey in ['all','regular','junior']:
        where='1' if pkey=='all' else f"pop='{pkey}'"
        rows=[]
        for aid,n,u,female,age,public,gcc,known,under25,over65 in db.execute("SELECT aid,COUNT(*),COUNT(DISTINCT golfer),SUM(gender='Female'),AVG(age),SUM(access='Public'),SUM(is_gc),COUNT(age),SUM(CASE WHEN age<25 THEN 1 ELSE 0 END),SUM(CASE WHEN age>=65 THEN 1 ELSE 0 END) FROM active a JOIN cell c ON a.cell=c.id WHERE "+where+' GROUP BY aid'):
            selected=[c for c in clubrows.values() if c['association']==aid and c[pkey]>0]
            nclubs=len({c['id'] for c in selected});pclubs=len({c['id'] for c in selected if c['access']=='Public'});t2=len({c['id'] for c in selected if c['recordedType']=='Type 2'})
            rows.append(dict(id=aid,name=names[aid],region=regions.get(aid,'International'),memberships=n,gcMemberships=gcc,activeGolfers=u,femalePct=female/n,averageAge=age,ageKnownCount=known,under25Count=under25,age65PlusCount=over65,publicMembersPct=public/n,gcClubMembersPct=gcc/n,clubCount=nclubs,publicClubsPct=pclubs/nclubs,type2ClubsPct=t2/nclubs))
        for scope in reviews:
            selected=[r for r in rows if scope=='all' or scope_by_aid[r['id']]==scope]
            assert sum(r['memberships'] for r in selected)==totals['scopes'][scope][pkey]['memberships']
            associations['scopes'][scope][pkey]=selected
        print('Association rollups complete: '+pkey,flush=True)
    insights={}
    for scope,review in reviews.items():
        insights[scope]={}
        for pkey,pop in [('all','All Members'),('regular','Regular'),('junior','Junior'),('unclassified','Unclassified')]:
            s=review['segments'][pop];expected=totals['scopes'][scope][pkey]
            s.update(unique_golfers=expected['uniqueGolfers'],multi_membership_golfers=expected['multiMembershipGolfers'],additional_memberships=expected['additionalMemberships'])
            assert s['total']==expected['memberships']
            for field in ['access','club_type','gender','membership_type','age','handicap']:assert sum(s[field].values())==s['total']
            for a in s['averages'].values():a['mean']=a['sum']/a['count']
            for cohort in s['handicap_by_age'].values():
                for a in cohort['averages'].values():a['mean']=a['sum']/a['count']
            where=('1' if scope=='all' else f"scope='{scope}'")+('' if pkey=='all' else f" AND pop='{pkey}'")
            s['no_handicap']['uniqueGolfers']=db.execute("SELECT COUNT(DISTINCT golfer) FROM active a JOIN cell c ON a.cell=c.id WHERE "+where+" AND hiband='No Index'").fetchone()[0]
            if pkey=='unclassified':continue
            insight={}
            for threshold in [20,30]:
                count,female,conflicts=db.execute("SELECT COUNT(*),COALESCE(SUM(female),0),COALESCE(SUM(conflict),0) FROM (SELECT golfer,MIN(gender='Female') female,COUNT(DISTINCT gender)>1 conflict FROM active a JOIN cell c ON a.cell=c.id WHERE "+where+f' AND hi>{threshold} GROUP BY golfer)').fetchone()
                assert not conflicts
                insight.update({f'golfersAbove{threshold}':count,f'femaleGolfersAbove{threshold}':female,('femaleShare' if threshold==20 else 'femaleShareAbove30'):female/count if count else None})
            insights[scope][pkey]=insight
        save('composition_review_'+scope,review)
        print('Composition and Index checks complete: '+scope,flush=True)
    for scope in ['aga','international','all']:
        for pkey in ['all','regular','junior']:
            expected={r['id']:r['memberships'] for r in associations['scopes'][scope][pkey]}
            actual=Counter()
            for c in clubrows.values():
                if (scope=='all' or c['scope']==scope) and c[pkey]:actual[c['association']]+=c[pkey]
            assert dict(actual)==expected
    save('membership_associations',associations)
    save('membership_clubs',dict(sources=[SOURCE.name],dates=totals['dates'],clubs=list(clubrows.values())))
    save('high_index_by_scope',insights);save('association_names',names);save('membership_scope',reviews['aga']['scope'])
    # Independent SQL check for a combined Explorer filter.
    n,u,nh=db.execute("SELECT COUNT(*),COUNT(DISTINCT golfer),SUM(hiband='No Index') FROM active a JOIN cell c ON a.cell=c.id WHERE scope='aga' AND aid IN ('53','1') AND gender='Female'").fetchone()
    save('validation',dict(activeMemberships=audit['snapshot']['all']['all']['memberships'],uniqueGolfers=audit['snapshot']['all']['all']['uniqueGolfers'],sourceRows=audit['rows'],filteredExplorerCheck=dict(total=n,unique=u,nh=nh),checks='Unique membership IDs; independent scope totals; demographic/club/association reconciliations; anonymous golfer patterns; consistent genders in Index counts.'))
    db.close()
    print('All refresh aggregates complete',flush=True)

if __name__=='__main__':main()
