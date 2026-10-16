import csv,json
from pathlib import Path
from collections import defaultdict
root=Path(__file__).resolve().parents[1]
gc={str(r['club_id']) for r in json.loads((root/'reports/gc_recorded_club_types.json').read_text())['clubs']}
sets=defaultdict(set);rowcounts=defaultdict(int)
with (root/'data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv').open(newline='',encoding='utf-8-sig') as f:
 reader=csv.reader(f);i={k:j for j,k in enumerate(next(reader))}
 for r in reader:
  if r[i['club_id']] not in gc or r[i['club_is_test']]!='No' or r[i['association_is_test']]!='No' or r[i['association_id']]=='237' or not r[i['parent_federation']].strip():continue
  gid=int(r[i['golfer_id']]);g=r[i['golfer_creation_date']];m=r[i['membership_creation_date']]
  if '2026-01-01'<=g<'2026-10-01':sets['golfer_created_ytd'].add(gid)
  if '2026-01-01'<=m<'2026-10-01':
   sets['membership_created_ytd'].add(gid);rowcounts['membership_created_ytd']+=1
   if g and g<'2026-01-01':sets['membership_ytd_golfer_before_2026'].add(gid)
   elif not g:sets['membership_ytd_missing_golfer_date'].add(gid)
   elif g>='2026-10-01':sets['membership_ytd_golfer_after_period'].add(gid)
a=sets['golfer_created_ytd'];b=sets['membership_created_ytd']
r={'source':'October 13 membership detail export, qualifying GC club IDs, all statuses','unique_counts':{k:len(v) for k,v in sets.items()},'membership_rows':dict(rowcounts),'both':len(a&b),'membership_date_only':len(b-a),'golfer_date_only':len(a-b),'gc_dashboard_ytd':161556,'note':'Current GC dashboard uses completed-month snapshot history; this is a same-extract date comparison, not a reproduction of that history.'}
(root/'reports/gc_acquisition_date_reconciliation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
