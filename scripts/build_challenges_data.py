"""Build verified-AGA challenge records from aggregate exports."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((ROOT/'data/raw/ghin'/name).open(encoding='utf-8-sig')))
associations=[r for r in json.loads((ROOT/'config/association_scope_lookup.json').read_text()) if r['is_aga']=='Yes' and r['is_test']=='No' and r['status']=='Active']
regions=json.loads((ROOT/'config/association_regions.json').read_text())['associations']
labels=json.loads((ROOT/'config/association_names.json').read_text())
agas={r['association_id']:labels.get(r['association_id'],r['association_name']) for r in associations}
names={r['challenge_id']:r['challenge_name'] for r in read('ghin_challenge_names_2026-10-03.csv')}
# The lookup confirms challenges.course_id matches crs_courses.id, not course_num.
# The alternate course_num join can duplicate rows; collapse only identical ID/name pairs.
course_names={}
for row in read('challenge_course_names_2026-10-03.csv'):
 course_id=row['course_id'];name=row['course_name_by_id']
 assert name and (course_id not in course_names or course_names[course_id]==name)
 course_names[course_id]=name
raw=read('ghin_challenges_2026-10-03.csv');result=[];excluded={'deleted':[],'notVerifiedAga':[],'explicitTest':[]}
# Explicit test challenge names in the supplied export, including tests hosted by real AGAs.
test_ids={'129','933'}
for r in raw:
 key='deleted' if r['status']=='deleted' else 'notVerifiedAga' if r['association_id'] not in agas else 'explicitTest' if r['challenge_id'] in test_ids else None
 if key:excluded[key].append(r['challenge_id']);continue
 assert r['challenge_id'] in names
 result.append({'id':r['challenge_id'],'name':names[r['challenge_id']],'association':r['association_id'],'course':r['course_id'],'courseName':course_names[r['course_id']],'aga':agas[r['association_id']],'status':r['status'],'start':r['start_date'],'end':r['end_date'],'golfers':int(r['no_of_golfers']),'ranked':int(r['no_of_ranked_golfers']),'scores':int(r['no_of_posted_scores'])})
assert len({r['id'] for r in result})==len(result)
assert all(0<=r['ranked']<=r['golfers'] for r in result)
out={'asOf':'2026-10-03','throughMonth':9,'year':2026,'associations':[{'id':k,'name':v,'region':regions[k]} for k,v in agas.items()],'challenges':result,'excludedCounts':{k:len(v) for k,v in excluded.items()}}
(ROOT/'data/processed/ghin_challenges_live.json').write_text(json.dumps(out,separators=(',',':')))
(ROOT/'data/validation/ghin_challenges_live.validation.json').write_text(json.dumps({'rows':len(result),'excluded':excluded,'sourceRows':len(raw),'totals':{k:sum(r[k] for r in result) for k in ['golfers','ranked','scores']},'definition':'Active non-test AGAs from association_scope_lookup; deleted challenges and explicitly named test challenge IDs 129 and 933 excluded. Counts are challenge participations, not unique people.'},indent=2))
print('Verified challenges:',len(result),'excluded:',out['excludedCounts'])
