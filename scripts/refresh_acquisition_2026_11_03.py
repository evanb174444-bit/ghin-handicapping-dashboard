import csv,json,time,shutil
from pathlib import Path
from collections import defaultdict,Counter
R=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');source=R/'data/raw/membership_refresh_2026-11-03/membership_refresh_2026-11-03.csv.csv'
gc={str(r['club_id']) for r in json.loads((R/'reports/gc_recorded_club_types.json').read_text())['clubs']};sets=defaultdict(set);gsets=defaultdict(set);dates={};issues=Counter();start=time.time()
with source.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);idx={k:i for i,k in enumerate(next(reader))}
 for n,r in enumerate(reader,1):
  d=r[idx['golfer_creation_date']]
  if not d:issues['missing_creation_rows']+=1
  if '2026-01-01'<=d<'2026-11-01':
   scope=r[idx['association_scope']];scope={'AGA':'aga','International':'international'}.get(scope)
   if scope:
    assert r[idx['club_is_test']]=='No' and r[idx['association_is_test']]=='No'
    gid=int(r[idx['golfer_id']]);month=int(d[5:7])-1
    if gid in dates:assert dates[gid]==d[:7], 'Conflicting Creation Date month'
    else:dates[gid]=d[:7]
    pop={'Regular':'regular','Junior':'junior','Unclassified':'unclassified'}[r[idx['member_population']]]
    for s in [scope,'all']:
     for p in {pop,'all'}:
      sets[s,p,month].add(gid)
      if r[idx['club_id']] in gc:gsets[s,p,month].add(gid)
  if n%2000000==0:print(f'Scanned {n:,} rows in {time.time()-start:.0f}s',flush=True)
old=json.loads((R/'data/processed/acquisition.json').read_text());data=json.loads(json.dumps(old));changes=[]
for s in ['aga','international','all']:
 for p in ['all','regular','junior','unclassified']:
  vals=[len(sets[s,p,m]) for m in range(10)]+[None,None];gvals=[len(gsets[s,p,m]) for m in range(10)]+[None,None]
  for m in range(10):
   assert gvals[m]<=vals[m]
   prev=old['history'][s][p]['2026'][m]
   if prev!=vals[m]:changes.append(dict(scope=s,population=p,month=m+1,previous=prev,current=vals[m]))
  data['history'][s][p]['2026']=vals;data['scopes'][s][p]=vals;data['gc']['history'][s][p]['2026']=gvals
for p in ['all','regular','junior','unclassified']:
 for m in range(10):assert max(data['history'][s][p]['2026'][m] for s in ['aga','international'])<=data['history']['all'][p]['2026'][m]<=sum(data['history'][s][p]['2026'][m] for s in ['aga','international'])
data.update(source=source.name,latestMonth=9,snapshot='2026-11-03',methodology='Distinct golfer IDs by membership golfer_creation_date; all statuses. Non-test known AGA/international associations; trials excluded. 2026 Jan-Oct rebuilt from Nov3 membership snapshot. Pre-2026 history and approved corrections preserved. Current affiliation and type; absent golfers outside coverage.')
data['gc'].update(source=source.name,methodology='2026 GC subset uses the same Nov3 all-status membership source and established club list; earlier GC history preserved. Current affiliation, not original acquisition channel.')
backup=R/'backups/acquisition-before-2026-11-03-refresh';backup.mkdir(exist_ok=True)
for name in ['data/processed/acquisition.json','data/processed/acquisition_gc.json','scripts/membership_acquisition_history_view.js']:
 p=R/name;dest=backup/p.name
 if not dest.exists():shutil.copy2(p,dest)
page=R/'Handicapping and GHIN Dashboard.html';text=page.read_text();key='const ACQUISITION_DATA=';a=text.index(key)+len(key);obj,end=json.JSONDecoder().raw_decode(text[a:]);assert obj['history']==old['history'];text=text[:a]+json.dumps(data,separators=(',',':'))+text[a+end:]
view=R/'scripts/membership_acquisition_history_view.js';vold=view.read_text();vnew=vold.replace('January 2020–September 2026','January 2020–October 2026').replace('through September','through October').replace('October 13','November 3').replace('GC and total counts use separate November 3 exports.','2026 GC and total counts use the same November 3 export; older history retains its prior sources.').replace('acquisitionYear===2026?9:12','acquisitionYear===2026?10:12').replace('Math.min(acquisitionMonth,8)','Math.min(acquisitionMonth,9)')
# Functions in this source are embedded verbatim in the standalone page.
for o,nn in zip(vold.splitlines(),vnew.splitlines()):
 if o!=nn:
  assert o in text, o[:80];text=text.replace(o,nn,1)
# The default KPI month is separate from the chart's latestMonth state.
text=text.replace('let acquisitionYear=2026,','let acquisitionYear=2026,')
text=text.replace('membershipGrowthMonth=8','membershipGrowthMonth=8')
(R/'data/processed/acquisition.json').write_text(json.dumps(data,indent=2));(R/'data/processed/acquisition_gc.json').write_text(json.dumps(data['gc'],indent=2));view.write_text(vnew);page.write_text(text)
report=dict(sourceRows=n,creationField='golfer_creation_date',periodEndExclusive='2026-11-01',snapshot='2026-11-03',changes=changes,issues=dict(issues),allMonthly=data['history']['all']['all']['2026'],agaMonthly=data['history']['aga']['all']['2026'],gcMonthly=data['gc']['history']['all']['all']['2026'],olderHistoryPreserved=True)
(R/'reports/acquisition-refresh-2026-11-03.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='changes'}),flush=True)
