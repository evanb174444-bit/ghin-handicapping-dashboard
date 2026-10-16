import csv,json
from pathlib import Path
from collections import defaultdict,Counter
root=Path(__file__).resolve().parents[1]
gc={str(r['club_id']) for r in json.loads((root/'reports/gc_recorded_club_types.json').read_text())['clubs']}
golfers={}
with (root/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv').open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);i={k:n for n,k in enumerate(next(reader))}
 for r in reader:
  if r[i['club_id']] not in gc:continue
  md=r[i['membership_creation_date']][:10];gd=r[i['golfer_creation_date']][:10]
  if not '2023-01-01'<=md<'2024-01-01':continue
  if r[i['club_is_test']]!='No' or r[i['association_is_test']]!='No' or r[i['association_id']]=='237' or not r[i['parent_federation']].strip():continue
  gid=r[i['golfer_id']];club=(r[i['club_id']],r[i['club_name']]);provider=r[i['front_end_provider']]
  old=golfers.get(gid)
  if old is None or md<old[0]:golfers[gid]=[md,gd,{club},{provider}]
  elif md==old[0]:old[2].add(club);old[3].add(provider)
monthly=defaultdict(Counter);days=Counter();clubs=defaultdict(set);providers=defaultdict(set);dailyclubs=defaultdict(set)
for gid,(md,gd,cs,ps) in golfers.items():
 kind='migrators' if gd and gd<md else 'same_day_new' if gd==md else 'other'
 monthly[md[:7]][kind]+=1
 if kind=='migrators' and md.startswith('2023-04'):
  days[md]+=1
  for club in cs:clubs[club].add(gid);dailyclubs[(md,*club)].add(gid)
  for provider in ps:providers[provider].add(gid)
res={'method':'Unique 2023 GC joiners, earliest GC membership date within year. Prior golfer creation calendar date = migrator. Current export attributes, all qualifying statuses. Club/provider groups may overlap.','monthly':dict(sorted(monthly.items())),'april_migrator_days':dict(sorted(days.items())),'april_migrator_clubs':sorted([{'club_id':k[0],'club_name':k[1],'golfers':len(v)} for k,v in clubs.items()],key=lambda x:-x['golfers']),'april_current_provider':{k:len(v) for k,v in providers.items()},'top_april_day_clubs':sorted([{'date':k[0],'club_id':k[1],'club_name':k[2],'golfers':len(v)} for k,v in dailyclubs.items()],key=lambda x:-x['golfers'])[:15]}
assert sum(v['migrators'] for v in monthly.values())==70053
(root/'reports/gc_2023_migration_months.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
