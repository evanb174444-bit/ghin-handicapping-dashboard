"""Aggregate GC joiners by membership date and earlier/same-day GHIN creation."""
import csv,json
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
gc={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
cohorts=defaultdict(dict)
with source.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);idx={k:i for i,k in enumerate(next(reader))}
 for r in reader:
  if r[idx['club_id']] not in gc:continue
  md=r[idx['membership_creation_date']][:10];gd=r[idx['golfer_creation_date']][:10]
  if not '2022-01-01'<=md<'2026-10-01':continue
  if r[idx['club_is_test']]!='No' or r[idx['association_is_test']]!='No' or r[idx['association_id']]=='237' or not r[idx['parent_federation']].strip():continue
  year=md[:4];gid=int(r[idx['golfer_id']]);old=cohorts[year].get(gid)
  if old is None:cohorts[year][gid]=[md,{gd}]
  else:old[0]=min(old[0],md);old[1].add(gd)
history={str(y):[dict(total=0,newGHIN=0,existingGHIN=0,unknown=0) if y<2026 or m<9 else None for m in range(12)] for y in range(2022,2027)}
for year,golfers in cohorts.items():
 for md,dates in golfers.values():
  gd=next(iter(dates)) if len(dates)==1 else ''
  group='unknown' if not gd or gd>md else 'existingGHIN' if gd<md else 'newGHIN'
  row=history[year][int(md[5:7])-1];row['total']+=1;row[group]+=1
for year,months in history.items():
 for row in months:
  if row:assert row['total']==row['newGHIN']+row['existingGHIN']+row['unknown']
reference=json.loads((ROOT/'reports/gc_migrators_by_year.json').read_text())['results']
for r in reference:
 months=history[str(r['year'])][:(9 if r['period']=='jan_sep' or r['year']==2026 else 12)]
 assert sum(v['total'] for v in months)==r['unique_gc_joiners']
 assert sum(v['existingGHIN'] for v in months)==r['migrators']
 assert sum(v['newGHIN'] for v in months)==r['same_day_new']
result=dict(source=source.name,extractDate='2026-10-13',years=list(range(2022,2027)),latestYear=2026,latestMonth=8,history=history,methodology='Distinct GC joiners by GC membership creation calendar date, all statuses. Earliest qualifying GC membership date per golfer within year. New to GHIN: golfer creation on same date. Existing GHIN: golfer creation before membership date. Later, missing or conflicting dates are Unknown. Current October 13 extract and established GC club list; reconstructed history can differ from original monthly snapshots.')
(ROOT/'data/processed/gc_joiner_history.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: monthly stacks sum; all full-year and Jan–Sep cohorts match independent migration analysis.')
print(json.dumps({y:{k:sum(r[k] for r in rows[:9] if r) for k in ['total','newGHIN','existingGHIN','unknown']} for y,rows in history.items()}))
