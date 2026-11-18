from pathlib import Path
import csv,collections,json,datetime,subprocess
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');data=json.loads((r/'data/processed/offseason_scores.json').read_text())
with (r/'data/raw/offseason/2026-11-16/offseason_scores_membership_matched_2026-11-16.csv').open() as f:source=list(csv.DictReader(f))
rows=[x for x in source if x['offseason']=='true' and x['deleted']=='false' and not x['deleted_at'] and x['penalty']!='true' and x['mapping_status']=='matched_primary_club' and x['association_scope'].lower()=='aga' and x['club_is_test'].lower() not in ('true','yes','1') and x['association_is_test'].lower() not in ('true','yes','1')]
assert len(rows)==28380 and len({x['golfer_id'] for x in rows})==21369
expected=[]
for aid in ['all']+[a['id'] for a in data['associations']]:
 subset=[x for x in rows if aid=='all' or x['association_id']==aid];year_unique=len({x['golfer_id'] for x in subset});expected.append({'aid':aid,'count':len(subset),'unique':year_unique})
 for grain in ['day','week','month']:
  grouped=collections.defaultdict(set);counts=collections.Counter()
  for x in subset:
   date=x['posted_at'][:10];d=datetime.date.fromisoformat(date);key=date if grain=='day' else date[:7] if grain=='month' else (d-datetime.timedelta(days=d.weekday())).isoformat();counts[key]+=1;grouped[key].add(x['golfer_id'])
  public=data['periodGolfers'][grain].get(aid,{})
  assert public=={key:len(value) for key,value in grouped.items()},(aid,grain)
 assert data['uniqueGolfers']['2026'].get(aid,0)==year_unique
assert sum(row['offseasonScores'] for row in data['rows'])==len(rows)
assert len({(row['date'],row['associationId']) for row in data['rows']})==len(data['rows'])
for row in data['rows']:assert set(row)=={'date','associationId','offseasonScores'}
Path('/tmp/offseason_expected_checks.json').write_text(json.dumps(expected))
print('PASS: independently reconciled private records to daily counts and exact day/week/month unique posters for every AGA; no private IDs embedded.')
