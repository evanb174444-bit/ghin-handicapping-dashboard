"""GC subset of new-golfer cohorts, using the established GC club-ID list."""
import csv,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
gc={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
sets=defaultdict(set)
with source.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);idx={k:i for i,k in enumerate(next(reader))}
 for r in reader:
  if r[idx['club_id']] not in gc:continue
  d=r[idx['golfer_creation_date']]
  if not '2022-01-01'<=d<'2026-10-01':continue  # Evan: GC did not exist in 2020 or 2021.
  if r[idx['club_is_test']]!='No' or r[idx['association_is_test']]!='No' or r[idx['association_id']]=='237':continue
  fed=r[idx['parent_federation']].strip()
  if not fed:continue
  scope='aga' if fed=='United States Golf Association' else 'international'
  pop={'Standard':'regular','Junior':'junior'}.get(r[idx['usga_membership_type']],'unclassified')
  gid=int(r[idx['golfer_id']]);year=d[:4];month=int(d[5:7])-1
  for s in [scope,'all']:
   for p in [pop,'all']:sets[(s,p,year,month)].add(gid)
data=json.loads((ROOT/'data/processed/acquisition.json').read_text())
history={s:{p:{y:[None if n is None else len(sets[(s,p,y,m)]) for m,n in enumerate(months)] for y,months in years.items()} for p,years in pops.items()} for s,pops in data['history'].items()}
for s,pops in history.items():
 for p,years in pops.items():
  for y,months in years.items():
   for m,n in enumerate(months):
    if n is not None:assert 0<=n<=data['history'][s][p][y][m],(s,p,y,m,n)
result={'source':str(source),'clubList':'reports/gc_recorded_club_types.json','clubCount':len(gc),'history':history,'excludedPreGCYears':[2020,2021],'methodology':'GC is zero for 2020 and 2021 per Evan. New golfers by golfer_creation_date with at least one qualifying GC membership in the October 13 extract. All statuses. GC has precedence for golfers also in other clubs; remainder is total minus GC. Current affiliation, not verified original acquisition channel. GC detail extract and historical total aggregate are separate October 13 exports.'}
(ROOT/'data/processed/acquisition_gc.json').write_text(json.dumps(result,indent=2))
print(json.dumps({y:sum(v for v in row if v is not None) for y,row in history['aga']['all'].items()}))
