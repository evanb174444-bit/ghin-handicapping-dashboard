import json
from pathlib import Path
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');p=r/'data/processed/refresh-2026-11-03'
def load(n):return json.loads((p/(n+'.json')).read_text())
audit=json.loads((r/'reports/membership_refresh_2026-11-03.audit.json').read_text());total=load('international_totals');assocs=load('membership_associations');clubs=load('membership_clubs');i=load('membership_intersections');nh=load('nh_intersections')
assert audit['rows']==10279905 and audit['duplicate_membership_ids']==0
for s in ['aga','international','all']:
 for pop in ['all','regular','junior']:
  d=total['scopes'][s][pop];assert d==audit['snapshot'][s][pop]
  assert sum(x['memberships'] for x in assocs['scopes'][s][pop])==d['memberships']
  assert sum(x[pop] for x in clubs['clubs'] if s=='all' or x['scope']==s)==d['memberships']
  assert d['memberships']-d['uniqueGolfers']==d['additionalMemberships']
assert sum(c[5] for c in i['cells'])==total['scopes']['aga']['all']['memberships']
assert sum(n for ids,n in i['golferPatterns'])==total['scopes']['aga']['all']['uniqueGolfers']
assert sum(c[4] for c in nh['cells'])==total['scopes']['aga']['all']['memberships']
for date in total['dates'].values():assert date=='November 3, 2026'
print('PASS: source uniqueness, all scope/population totals, association/club partitions, Explorer membership and unique counts, NH denominators and dates.')
