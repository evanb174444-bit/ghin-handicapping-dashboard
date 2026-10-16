"""Build October refresh aggregates. Private identifiers stay in SQLite staging."""
import csv,json,sqlite3,time,copy
from collections import Counter
from pathlib import Path
from itertools import groupby
from review_membership_exports import fresh,classify,numeric
from membership_refresh_composition import add_membership
from audit_membership_refresh import SOURCE,DB,ROOT

OUT=ROOT/'data/processed/refresh-2026-10-13'
POPS=['All Members','Regular','Junior','Unclassified']
AGES=['Under 18','18–24','25–34','35–44','45–54','55–64','65+','Unknown / invalid']
HIS=['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+','No Index','Unknown']

def save(name,data):
    (OUT/(name+'.json')).write_text(json.dumps(data,separators=(',',':'))+'\n')

def main():
    OUT.mkdir(exist_ok=True)
    audit=json.loads((ROOT/'reports/membership_refresh_2026-10-13.audit.json').read_text())
    assert audit['duplicate_membership_ids']==0
    db=sqlite3.connect(DB)
    db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF');db.execute('PRAGMA cache_size=-32768')
    db.execute('CREATE TABLE active(id INTEGER PRIMARY KEY,golfer INTEGER,cell INTEGER,age REAL,hi REAL)')
    gc={r['club_id'] for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
    segments={scope:{p:fresh() for p in POPS} for scope in ['aga','international','all']}
    names={};clubs={};cell_index={};cells=[];cell_counts=Counter();seen_gc=set();conflicts=Counter();batch=[];n=0;started=time.time();date_pairs=Counter()
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f,strict=True):
            a,b=r['golfer_creation_date'][:7],r['golfer_record_created_at'][:7]
            if a!=b:date_pairs[(a,b)]+=1
            if r['membership_status']!='Active' or r['association_scope'] not in ('AGA','International'):continue
            n+=1;scope=r['association_scope'].lower();pop=r['member_population'];r['population']=pop
            aid=r['association_id'];cid=r['club_id'];names[aid]=r['association_name'] or 'Unknown association'
            r['gender']=r['gender'] if r['gender'] in ('Male','Female') else 'Unknown'
            for target in (scope,'all'):add_membership(r,segments[target],gc,seen_gc,conflicts)
            access,kind,detail=classify(cid,r['club_category'],r['club_type'],gc)
            group=detail if access=='Public' else 'Private Clubs' if access=='Private' else 'Unknown Access'
            clubkey=(aid,cid)
            club=dict(id=cid,name=r['club_name'] or 'Unnamed club',association=aid,associationName=names[aid],scope=scope,access=access,clubGroup=group,type=r['club_type'] or 'Unknown',mappedType=kind,category=r['club_category'] or 'Unknown')
            if clubkey in clubs:assert clubs[clubkey]==club,'Conflicting club metadata'
            else:clubs[clubkey]=club
            age=numeric(r['age_at_extraction']) if r['matched_golfer_id'] else None
            age=age if age is not None and 0<=age<=120 else None
            ageband=AGES[-1] if age is None else next(b for e,b in zip([18,25,35,45,55,65,121],AGES) if age<e)
            hi=numeric(r['handicap_index']) if r['matched_golfer_id'] and r['handicap_index_display'].strip().upper()!='NH' else None
            hiband='No Index' if r['handicap_index_display'].strip().upper()=='NH' else 'Unknown' if hi is None else next(b for e,b in zip([0,5,10,15,20,30,float('inf')],HIS) if hi<=e)
            key=(clubkey,r['gender'],ageband,pop,hiband)
            if key not in cell_index:cell_index[key]=len(cells);cells.append(key)
            cell=cell_index[key];cell_counts[cell]+=1
            batch.append((int(r['membership_id']),int(r['golfer_id']),cell,age,hi))
            if len(batch)==10000:db.executemany('INSERT INTO active VALUES (?,?,?,?,?)',batch);batch=[];db.commit()
            if n%500000==0:print(f'Aggregated {n:,} active memberships in {time.time()-started:.0f}s',flush=True)
    db.executemany('INSERT INTO active VALUES (?,?,?,?,?)',batch);db.commit()
    save('creation_date_month_differences',[dict(membershipCreationMonth=a,golferRecordCreationMonth=b,membershipRows=n) for (a,b),n in date_pairs.items()])
    assert n==audit['snapshot']['all']['all']['memberships']
    print('Building anonymous golfer patterns and distinct counts',flush=True)
    db.execute('CREATE TABLE cell(id INTEGER PRIMARY KEY, scope TEXT,pop TEXT,aid TEXT,cid TEXT,gender TEXT,ageband TEXT,hiband TEXT,access TEXT,is_gc INTEGER,kind TEXT)')
    db.executemany('INSERT INTO cell VALUES (?,?,?,?,?,?,?,?,?,?,?)',[(i,clubs[c]['scope'],p.lower(),c[0],c[1],g,a,h,clubs[c]['access'],int(clubs[c]['mappedType']=='GC Clubs'),clubs[c]['type']) for i,(c,g,a,p,h) in enumerate(cells)])
    db.commit()
    # Group identifiers only inside private staging; public patterns contain cell indexes.
    patterns=Counter();nhpatterns=Counter();nhkeys={};nhcells=Counter();nhcounts=Counter();agaidx={};agacells=[]
    for i,key in enumerate(cells):
        if clubs[key[0]]['scope']!='aga':continue
        agaidx[i]=len(agacells);agacells.append(key)
        nhkey=key[:4]
        if nhkey not in nhkeys:nhkeys[nhkey]=len(nhkeys)
        nhcells[nhkey]+=cell_counts[i]
        if key[4]=='No Index':nhcounts[nhkey]+=cell_counts[i]
    for golfer,rows in groupby(db.execute('SELECT golfer,cell FROM active ORDER BY golfer'),key=lambda row:row[0]):
        ids={cell for _,cell in rows if cell in agaidx}
        if ids:patterns[tuple(sorted(agaidx[i] for i in ids))]+=1
        nhids={nhkeys[cells[i][:4]] for i in ids if cells[i][4]=='No Index'}
        if nhids:nhpatterns[tuple(sorted(nhids))]+=1
    clubkeys=list(clubs);clubidx={c:i for i,c in enumerate(clubkeys)}
    genders=['Male','Female','Unknown'];pops=POPS[1:]
    cfg=json.loads((ROOT/'config/membership_scope.json').read_text())
    cfg.update(source=SOURCE.name,association_ids=sorted({a for a,c in clubkeys if clubs[(a,c)]['scope']=='aga'}))
    base=dict(scope=cfg,clubs=list(clubs.values()),genders=genders,ages=AGES,populations=pops)
    save('membership_intersections',dict(base,handicaps=HIS,cells=[[clubidx[c],genders.index(g),AGES.index(a),pops.index(p),HIS.index(h),cell_counts[i]] for i,(c,g,a,p,h) in enumerate(cells) if i in agaidx],golferPatterns=[[list(k),n] for k,n in patterns.items()]))
    save('nh_intersections',dict(base,cells=[[clubidx[c],genders.index(g),AGES.index(a),pops.index(p),nhcells[k],nhcounts[k]] for k in nhkeys for c,g,a,p in [k]],golferPatterns=[[list(k),n] for k,n in nhpatterns.items()]))
    assert sum(patterns.values())==audit['snapshot']['aga']['all']['uniqueGolfers']
    dates={s:'October 13, 2026' for s in segments}
    totals=dict(sources=[SOURCE.name],dates=dates,scopes={s:audit['snapshot'][s] for s in segments})
    totals['overlap']={p:sum(totals['scopes'][s][p]['uniqueGolfers'] for s in ['aga','international'])-totals['scopes']['all'][p]['uniqueGolfers'] for p in ['all','regular','junior','unclassified']}
    save('international_totals',totals)
    for scope in ['aga','international']:
        save('composition_review_'+scope,dict(scope=cfg if scope=='aga' else dict(mode=scope,label=scope,definition='Eligible international association memberships'),segments=segments[scope]))
    # Release large in-memory cells before the final, bounded SQL checks.
    db.close()
    del segments,cells,cell_counts,patterns,nhpatterns,clubs,cell_index
    from finish_membership_refresh import main as finish
    finish()

if __name__=='__main__':main()
