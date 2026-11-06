"""Build active snapshot history from preserved, validated dated aggregate folders.
Run after each membership refresh; never infer historical active status from current records.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1] if Path(__file__).parent.name=='scripts' else Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard')
records=[]
for folder in sorted((ROOT/'data/processed').glob('refresh-*')):
 date=folder.name.removeprefix('refresh-')
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):continue
 if not all((folder/f).exists() for f in ['international_totals.json','membership_associations.json','validation.json']):continue
 totals=json.loads((folder/'international_totals.json').read_text());associations=json.loads((folder/'membership_associations.json').read_text());scopes={}
 for scope,pops in totals['scopes'].items():
  scopes[scope]={}
  for pop,d in pops.items():
   if pop not in ['all','regular','junior']:continue
   rows=associations['scopes'][scope][pop]
   assert len({r['id'] for r in rows})==len(rows)
   pairs=sum(r['activeGolfers'] for r in rows)
   assert d['uniqueGolfers']<=pairs<=d['memberships']
   assert sum(r['memberships'] for r in rows)==d['memberships']
   scopes[scope][pop]={'uniqueGolfers':d['uniqueGolfers'],'associationMemberships':pairs,'memberships':d['memberships']}
 records.append({'date':date,'label':totals['dates']['all'],'source':totals['sources'],'scopes':scopes})
assert len(records)>=2
out={'definition':'Qualifying active memberships at actual extraction dates. Association memberships count each golfer once per association. Changes compare consecutive captured snapshots, not certified month ends. No interpolation or retrospective status reconstruction.','snapshots':records}
path=ROOT/'data/processed/active_snapshot_history.json';path.write_text(json.dumps(out,indent=2))
page=ROOT/'Handicapping and GHIN Dashboard.html';text=page.read_text();constant='const ACTIVE_MEMBERSHIP_SNAPSHOT_HISTORY='+json.dumps(out,separators=(',',':'))+';\n'
if 'const ACTIVE_MEMBERSHIP_SNAPSHOT_HISTORY=' in text:
 a=text.index('const ACTIVE_MEMBERSHIP_SNAPSHOT_HISTORY=');b=text.index('\n',a);text=text[:a]+constant+text[b+1:]
else:
 a=text.index('function membershipCurrentCounts()');text=text[:a]+constant+text[a:]
page.write_text(text)
print(json.dumps([{'date':r['date'],**r['scopes']['all']['all']} for r in records]))
