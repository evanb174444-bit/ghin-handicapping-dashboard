from pathlib import Path
import csv,json,collections
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');d=json.loads((r/'data/processed/offseason_scores.json').read_text())
lookup={x['score_course_id']:x['state_by_id'] or 'unknown' for x in csv.DictReader((r/'data/raw/offseason/2026-11-16/offseason_course_locations_2026-11-16.csv').open())};g=collections.defaultdict(lambda:collections.defaultdict(lambda:[0,set(),collections.defaultdict(lambda:[0,set()])]))
with (r/'data/raw/offseason/2026-11-16/offseason_scores_membership_matched_2026-11-16.csv').open() as f:
 for x in csv.DictReader(f):
  if x['score_eligible_non_deleted_non_penalty'].lower()!='true' or x['association_scope'].lower()!='aga':continue
  cid=x['course_id'] or 'unknown';state=lookup.get(cid,'unknown')
  for aid in ['all',x['association_id']]:
   b=g[aid][state];b[0]+=1;b[1].add(x['golfer_id']);c=b[2][cid];c[0]+=1;c[1].add(x['golfer_id'])
for aid,states in d['playedLocations']['byAssociation'].items():
 assert len(states)==len(g[aid])
 for state in states:
  b=g[aid][state['key']];assert (state['scores'],state['uniqueGolfers'])==(b[0],len(b[1]))
  assert sum(c['scores'] for c in state['courses'])==state['scores']
  assert state['courseCount']==sum(c['courseId']!='unknown' for c in state['courses'])
  for c in state['courses']:assert (c['scores'],c['uniqueGolfers'])==(b[2][c['courseId']][0],len(b[2][c['courseId']][1]))
 assert sum(s['scores'] for s in states)==sum(x['offseasonScores'] for x in d['rows'] if aid=='all' or x['associationId']==aid)
print('PASS: all state/course score totals and deduplicated golfers independently reconcile across every AGA.')
