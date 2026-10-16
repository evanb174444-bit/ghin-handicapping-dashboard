"""Read-only cohort diagnostics from the October 13 membership detail export."""
import csv,json
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
groups={k:defaultdict(set) for k in ['month','day','association','club','day_club','day_association','type','status','record_creation_day','membership_predates_2020']}
with src.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);header=next(reader);idx={k:i for i,k in enumerate(header)}
 for r in reader:
  d=r[idx['golfer_creation_date']][:10]
  if d[:7] != '2020-01':continue
  if r[idx['club_is_test']]!='No' or r[idx['association_is_test']]!='No':continue
  if r[idx['parent_federation']]!='United States Golf Association' or r[idx['association_id']]=='237':continue
  g=int(r[idx['golfer_id']]);m=d[:7];a=(r[idx['association_id']],r[idx['association_name']]);c=(r[idx['club_id']],r[idx['club_name']])
  keys={'month':(m,), 'day':(d,), 'association':(m,*a), 'club':(m,*a,*c), 'day_club':(d,*a,*c),'type':(m,r[idx['usga_membership_type']]),'status':(m,r[idx['membership_status']]), 'day_association':(d,*a), 'record_creation_day':(r[idx['golfer_record_created_at']][:10],), 'membership_predates_2020':(bool(r[idx['membership_creation_date']] and r[idx['membership_creation_date']]<'2020-01-01'),)}
  for k,key in keys.items():groups[k][key].add(g)
counts={k:[{'key':list(key),'count':len(v)} for key,v in sorted(group.items())] for k,group in groups.items()}
result={'source':str(src),'method':'Distinct GHIN per group. All statuses. AGA federation, explicitly non-test club and association, trial association 237 excluded. Associations/clubs/types/status groups may overlap. Current membership attributes, not creation-time attributes.','groups':counts}
(ROOT/'reports/acquisition_jan_2020_diagnostics.json').write_text(json.dumps(result,indent=2))
for k in ['month','day','association','club','day_club','day_association','type','status','record_creation_day','membership_predates_2020']:
 print(k, json.dumps(sorted(counts[k],key=lambda r:r['count'],reverse=True)[:15]))
