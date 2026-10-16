"""Inspect golfer-level status separately from membership status; no source edits."""
import csv,json
from pathlib import Path
from collections import Counter,defaultdict
root=Path(__file__).resolve().parents[1]
source=root/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv'
statuses=Counter();archived=defaultdict(set);membership=Counter();missing=0
with source.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);idx={k:i for i,k in enumerate(next(reader))}
 for row in reader:
  status=row[idx['golfer_status']];statuses[status]+=1
  if not row[idx['matched_golfer_id']]:missing+=1
  if 'archiv' not in status.lower():continue
  gid=int(row[idx['golfer_id']]);archived['all_export'].add(gid);membership[row[idx['membership_status']]]+=1
  if row[idx['club_is_test']]!='No' or row[idx['association_is_test']]!='No' or row[idx['association_id']]=='237' or not row[idx['parent_federation']].strip():continue
  date=row[idx['golfer_creation_date']]
  scope='AGA' if row[idx['parent_federation']]=='United States Golf Association' else 'International'
  archived[scope].add(gid)
  if date and '2020-01-01'<=date<'2026-10-01':archived[scope+'_'+date[:4]].add(gid)
report={'source':str(source),'golfer_status_membership_rows':dict(statuses),'missing_joined_golfer_rows':missing,'archived_unique_golfers':{k:len(v) for k,v in archived.items()},'archived_membership_status_rows':dict(membership),'note':'No status exclusion in acquisition SQL. Archived golfers represented by qualifying membership rows would be included. Absence from this export does not establish whether the database views exclude archived records.'}
(root/'reports/archived_golfer_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
