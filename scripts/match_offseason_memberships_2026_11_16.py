from pathlib import Path
import csv,json,hashlib,collections,datetime,shutil,time
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');source=Path('/Users/EvanBelfi/Downloads/offseason_scores_full_2026-11-16.csv.csv');membership=r/'data/raw/membership_refresh_2026-11-03/membership_refresh_2026-11-03.csv.csv'
with source.open(encoding='utf-8-sig',newline='') as f: reader=csv.DictReader(f);score_columns=reader.fieldnames;scores=list(reader)
targets={row['golfer_id'] for row in scores};primary=collections.defaultdict(set);clubmeta=collections.defaultdict(set);flags=collections.defaultdict(set);seen=set();target_membership_count=collections.Counter();start=time.monotonic()
with membership.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.reader(f);columns=next(reader);ix={name:i for i,name in enumerate(columns)}
 names=['club_id','club_association_id','association_id','association_name','parent_federation','association_scope','club_name','club_is_test','association_is_test','club_category','club_type'];mi=[ix[k] for k in names]
 for number,row in enumerate(reader,1):
  cid=row[ix['club_id']]
  clubmeta[cid].add(tuple(row[i] for i in mi))
  gid=row[ix['golfer_id']]
  if gid in targets:
   seen.add(gid);target_membership_count[gid]+=1;pc=row[ix['primary_club_id']]
   if pc:primary[gid].add(pc)
   flags[(gid,cid)].add(row[ix['usga_membership_type']])
  if number%2000000==0:print(f'Scanned {number:,} memberships; located {len(seen):,} target golfers; elapsed {time.monotonic()-start:.0f}s',flush=True)
print(f'Scan complete: {number:,} rows, {len(seen):,} target golfers',flush=True)
def truth(value):return str(value).lower() in ('true','t','yes','1')
def mapping(gid):
 base={'membership_snapshot':'2026-11-03','mapping_status':'','primary_club_id':'','club_name':'','association_id':'','association_name':'','association_scope':'','parent_federation':'','member_population':'Unclassified','club_category':'','club_type':'','club_is_test':'','association_is_test':''}
 if gid not in seen:base['mapping_status']='golfer_not_in_membership_export';return base
 pc=primary[gid]
 if not pc:base['mapping_status']='primary_club_missing';return base
 if len(pc)!=1:base['mapping_status']='ambiguous_primary_club';return base
 cid=next(iter(pc));base['primary_club_id']=cid;details=clubmeta.get(cid,set())
 if not details:base['mapping_status']='primary_club_not_in_membership_export';return base
 if len(details)!=1:base['mapping_status']='ambiguous_primary_club_metadata';return base
 d=dict(zip(names,next(iter(details))))
 base.update({k:d[k] for k in ['club_name','association_id','association_name','association_scope','parent_federation','club_category','club_type','club_is_test','association_is_test']})
 if d['club_association_id'] and d['association_id'] and d['club_association_id']!=d['association_id']:base['mapping_status']='conflicting_association_ids';return base
 if not d['association_id'] or not d['association_name']:base['mapping_status']='primary_club_association_missing';return base
 types=flags.get((gid,cid),set());regular='Standard' in types;junior='Junior' in types
 base['member_population']='Regular and Junior' if regular and junior else 'Regular' if regular else 'Junior' if junior else 'Unclassified'
 base['mapping_status']='matched_primary_club';return base
mapping_by_golfer={gid:mapping(gid) for gid in targets};joined=[]
for score in scores:
 m=mapping_by_golfer[score['golfer_id']];row={**score,**m};row['score_eligible_non_deleted_non_penalty']=str(not truth(score['deleted']) and not score['deleted_at'] and not truth(score['penalty'])).lower();row['test_mapping']=str(truth(m['club_is_test']) or truth(m['association_is_test'])).lower();joined.append(row)
out=r/'data/raw/offseason/2026-11-16';out.mkdir(parents=True,exist_ok=True);shutil.copy2(source,out/'offseason_scores_full_2026-11-16.csv')
with (out/'offseason_scores_membership_matched_2026-11-16.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(joined[0]));writer.writeheader();writer.writerows(joined)
status=collections.Counter(row['mapping_status'] for row in joined);gstatus=collections.Counter(m['mapping_status'] for m in mapping_by_golfer.values());eligible=[row for row in joined if row['score_eligible_non_deleted_non_penalty']=='true'];matched=[row for row in eligible if row['mapping_status']=='matched_primary_club'];aga=[row for row in matched if row['association_scope'].lower()=='aga' and row['test_mapping']=='false'];totals=collections.Counter((row['association_id'],row['association_name']) for row in aga)
report={'source':source.name,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'membershipSource':str(membership.relative_to(r)),'membershipSourceBytes':membership.stat().st_size,'membershipSnapshot':'2026-11-03','membershipRowsScanned':number,'rawScores':len(scores),'uniqueScoreIds':len({row['score_id'] for row in scores}),'uniqueGolfers':len(targets),'scoreMappingStatus':dict(status),'golferMappingStatus':dict(gstatus),'eligibleNonDeletedNonPenalty':len(eligible),'eligibleMappingStatus':dict(collections.Counter(row['mapping_status'] for row in eligible)),'eligibleScope':dict(collections.Counter(row['association_scope'] or 'unmatched' for row in eligible)),'eligibleMemberPopulation':dict(collections.Counter(row['member_population'] for row in eligible)),'testMappingScores':sum(row['test_mapping']=='true' for row in eligible),'agaAssignedEligibleScores':len(aga),'agaTotals':[{'associationId':a,'associationName':n,'scores':count} for (a,n),count in sorted(totals.items(),key=lambda item:-item[1])],'postedMin':min(row['posted_at'] for row in scores),'postedMax':max(row['posted_at'] for row in scores),'matchedFile':str((out/'offseason_scores_membership_matched_2026-11-16.csv').relative_to(r)),'method':'One mapping per golfer using the November 3 primary_club_id; club/AGA metadata from the same export. No arbitrary fallback to another membership. Current affiliation, not historical affiliation at posting. Offseason uses source offseason=true; no seasonal-calendar inference. Raw score flags retained. No share-of-all denominator.','published':False,'dashboardUpdated':False}
assert sum(status.values())==len(scores);assert len({row['score_id'] for row in joined})==len(scores)
(r/'reports/offseason_membership_matching_2026-11-16.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
