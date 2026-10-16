"""GC joiners by whether GHIN creation predates GC membership creation."""
import csv,json
from pathlib import Path
from collections import defaultdict,Counter
root=Path(__file__).resolve().parents[1]
source=root/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
gc={str(r['club_id']) for r in json.loads((root/'reports/gc_recorded_club_types.json').read_text())['clubs']}
cohorts=defaultdict(dict);rowcounts=Counter();timestamp_samples=[]
with source.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);idx={k:i for i,k in enumerate(next(reader))}
 for r in reader:
  if r[idx['club_id']] not in gc or r[idx['club_is_test']]!='No' or r[idx['association_is_test']]!='No' or r[idx['association_id']]=='237' or not r[idx['parent_federation']].strip():continue
  md=r[idx['membership_creation_date']][:10];gd=r[idx['golfer_creation_date']][:10]
  if not '2022-01-01'<=md<'2026-10-01':continue
  if len(timestamp_samples)<3:timestamp_samples.append([r[idx['membership_creation_date']],r[idx['golfer_creation_date']]])
  year=int(md[:4]);gid=int(r[idx['golfer_id']])
  for period in ['full_available']+(['jan_sep'] if int(md[5:7])<=9 else []):
   key=(year,period);rowcounts[key]+=1
   if gid not in cohorts[key]:cohorts[key][gid]=[md,{gd}]
   else:
    cohorts[key][gid][0]=min(cohorts[key][gid][0],md);cohorts[key][gid][1].add(gd)
results=[]
for (year,period),golfers in sorted(cohorts.items()):
 c=Counter()
 for md,dates in golfers.values():
  if len(dates)>1:c['conflicting_golfer_dates']+=1;continue
  gd=next(iter(dates))
  if not gd:c['missing_golfer_date']+=1
  elif gd<md:
   c['migrators']+=1
   c['prior_year_ghin' if gd[:4]<md[:4] else 'same_year_earlier_day_ghin']+=1
  elif gd==md:c['same_day_new']+=1
  else:c['golfer_date_after_membership']+=1
 assert sum(c[k] for k in ['migrators','same_day_new','golfer_date_after_membership','missing_golfer_date','conflicting_golfer_dates'])==len(golfers)
 results.append({'year':year,'period':period,'end':'September' if period=='jan_sep' or year==2026 else 'December','unique_gc_joiners':len(golfers),'membership_rows':rowcounts[(year,period)],**dict(c),'migrator_share':c['migrators']/len(golfers)})
report={'source':str(source),'gc_club_list':'reports/gc_recorded_club_types.json','method':'Calendar-date comparison. All qualifying membership statuses. Distinct golfer per membership-creation-year/period, earliest GC membership date within that period if multiple rows. Earlier Golfer Creation Date = migrator by Evan definition. Same-day = new by date rule, not independent proof of joining channel. Later/missing/conflicting dates are separate. Current extract and established GC club list; not historical snapshots.','results':results,'sample_date_formats':timestamp_samples}
(root/'reports/gc_migrators_by_year.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
