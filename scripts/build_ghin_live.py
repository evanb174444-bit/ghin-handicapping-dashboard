"""Install aggregate GPS and Trials exports. No individual records or credentials."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((ROOT/'data/raw/ghin'/name).open(encoding='utf-8-sig')))
trials=read('trial_monthly_history_2026-10-02.csv');cohorts=read('trial_cohorts_2026-10-02.csv');gps=read('gps_monthly_activity_2026-10-02.csv')
for r in trials:
 for k in ['trial_records','unique_golfers']:r[k]=int(r[k])
 assert r['unique_golfers']<=r['trial_records']
for r in cohorts:
 for k in list(r)[2:]:r[k]=int(r[k])
 assert r['trials_created']==r['recorded_conversions']+r['no_recorded_conversion']
for r in gps:
 for k in ['activity_records','unique_golfers','unique_subscriptions','missing_golfer_id','missing_subscription_id']:r[k]=int(r[k])
 assert r['unique_golfers']<=r['activity_records']
assert len({(r['event_type'],r['event_month']) for r in trials})==len(trials)
assert len({(r['activity_status'],r['activity_month']) for r in gps})==len(gps)
out={'year':2026,'reportMonth':8,'trialReportMonth':9,'trials':trials,'cohorts':cohorts,'gps':gps,'gpsSnapshot':{'asOf':'2026-10-02 13:55:56 -0400','activeFlagged':100105,'currentDates':99703,'outsideDates':194,'missingDates':208,'source':'User-provided full reconciliation screenshot, October 2, 2026 10:56 AM; sql/ghin/07_gps_active_reconciliation.sql. Unique golfers counted once across all groups.'}}
destinations=read('ytd_trial_destinations_2026-10-02.csv')
gc_ids={str(r['club_id']) for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
aga_ids=set(map(str,json.loads((ROOT/'config/membership_scope.json').read_text())['association_ids']))
buckets={'gc':0,'aga':0,'nonAga':0,'unresolved':0}
for row in destinations:
 key='unresolved' if row['match_status']!='One same-day candidate' else 'gc' if row['club_id'] in gc_ids else 'aga' if row['association_id'] in aga_ids else 'nonAga'
 buckets[key]+=int(row['conversion_records'])
monthly={}
statuses={}
for row in destinations:
 month=row['conversion_month'];count=int(row['conversion_records'])
 monthly[month]=monthly.get(month,0)+count
 statuses[row['match_status']]=statuses.get(row['match_status'],0)+count
expected={r['event_month']:r['trial_records'] for r in trials if r['event_type']=='Sign-up recorded' and '2026-01-01'<=r['event_month']<'2026-10-01'}
assert monthly==expected,(monthly,expected)
assert sum(buckets.values())==sum(monthly.values())==76263
out['trialDestinations']={'month':'January–September 2026',**buckets,'noMatch':statuses.get('No same-day candidate',0),'multipleMatches':statuses.get('Multiple same-day candidates',0)}
(ROOT/'data/validation/ytd_trial_destinations.validation.json').write_text(json.dumps({'source':'data/raw/ghin/ytd_trial_destinations_2026-10-02.csv','rows':len(destinations),'monthly':monthly,'matchStatus':statuses,'buckets':buckets,'reconcilesToMonthlyExport':True,'retrievedAt':destinations[0]['retrieved_at']},indent=2))
out['trialSnapshot']=json.loads((ROOT/'data/raw/ghin/current_trial_pools_2026-10-02.json').read_text())
assert all(isinstance(out['trialSnapshot'][k],int) and out['trialSnapshot'][k]>=0 for k in ['active_trial_golfers','inactive_trial_golfers','overlapping_status_golfers'])
assert out['trialSnapshot']['overlapping_status_golfers']<=out['trialSnapshot']['active_trial_golfers']
assert out['gpsSnapshot']['activeFlagged']==sum(out['gpsSnapshot'][k] for k in ['currentDates','outsideDates','missingDates'])
out['gpsAutoRenew']=json.loads((ROOT/'data/processed/gps_active_auto_renew_status_2026-10-04.json').read_text())
out['gpsTenure']=json.loads((ROOT/'data/processed/gps_subscriber_tenure_revised_2026-10-04.json').read_text())
(ROOT/'data/processed/ghin_live.json').write_text(json.dumps(out,separators=(',',':')))
(ROOT/'data/validation/ghin_live.validation.json').write_text(json.dumps({'trialsMonthlyRows':len(trials),'trialCohorts':len(cohorts),'gpsMonthlyStatusRows':len(gps),'checks':'Unique monthly keys; unique counts <= records; trial cohort partitions reconcile; GPS screenshot snapshot partitions reconcile.','limitations':['GPS activity records are not subscriber history or verified paid transactions; status may be updated after record creation.','Trials signup-date counts match July/August Tableau conversions; no paid or destination-association claim.','Cohort conversion rates are observed through extraction, with unequal follow-up. Timing uses recorded trial_start_date, which may differ from creation. Current trial pools use unique golfers in non-test association 237 memberships, with active status taking precedence.','Trials use January-September, excluding partial October; GPS uses January-August. Complete exports remain available in Show data.']},indent=2))
p=ROOT/'Handicapping and GHIN Dashboard.html';s=p.read_text()
s=s.replace('activeTop==="ghin"&&["totals","advanced-gps"].includes(activeSub)?"Activity through August 2026','activeTop==="ghin"&&["totals","advanced-gps"].includes(activeSub)?"Activity through September 2026')
nav_hook='if(activeTop==="ghin"&&activeSub==="ghin-trials")$("membershipPopulationMount").innerHTML=trialHighlightSelector();'
if nav_hook not in s:
 s=s.replace('const view=activeTop==="ghin"?',nav_hook+'const view=activeTop==="ghin"?',1)

s=s.replace('ghin:[["totals","Totals"],["ghin-trials","GHIN Trials"]', 'ghin:[["ghin-trials","GHIN Trials"]')
for name in ['summaryTrialsCard','ghinTrials','advancedGps','ghinTotals','ghinChallenges']:
 s=re.sub(r'^function '+name+r'\(', 'function legacy_'+name+'(',s,count=1,flags=re.M)
start='// BEGIN LIVE GHIN PRODUCTS';end='// END LIVE GHIN PRODUCTS';block=start+'\nconst GHIN_LIVE_DATA='+json.dumps(out,separators=(',',':'))+';\n'+(ROOT/'scripts/ghin_live_view.js').read_text()+'\nconst GHIN_CHALLENGES_DATA='+(ROOT/'data/processed/ghin_challenges_live.json').read_text()+';\n'+(ROOT/'scripts/ghin_challenges_view.js').read_text()+'\n'+end
if start in s:
 a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:]
else:s=s.replace('const routeViews=',block+'\nconst routeViews=',1)
start='/* BEGIN LIVE GHIN PRODUCTS */';end='/* END LIVE GHIN PRODUCTS */';block=start+'\n'+(ROOT/'scripts/ghin_live.css').read_text()+'\n'+end
if start in s:
 a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:]
else:s=s.replace('</style>',block+'\n</style>',1)
s=s.replace('"Report Date: August 1, 2026";localStorage', 'activeTop==="ghin"&&["totals","ghin-trials","advanced-gps"].includes(activeSub)?"Activity through August 2026 · Extracted October 2, 2026":"Report Date: August 1, 2026";localStorage')
s=s.replace('activeTop==="ghin"&&["totals","ghin-trials","advanced-gps"].includes(activeSub)?', 'activeTop==="ghin"&&activeSub==="ghin-trials"?"Activity through September 2026 · Extracted October 2, 2026":activeTop==="ghin"&&["totals","advanced-gps"].includes(activeSub)?')
s=s.replace('activeTop==="ghin"&&["totals","advanced-gps"].includes(activeSub)?"Activity through', 'activeTop==="ghin"&&["totals","advanced-gps"].includes(activeSub)?"Subscribe through')
challenge_subtitle='activeTop==="ghin"&&activeSub==="ghin-challenges"?"Verified AGA challenges · Extracted October 3, 2026":'
subtitle_hook='document.querySelector(".subtitle").textContent='
if subtitle_hook+challenge_subtitle not in s:
 s=s.replace(subtitle_hook,subtitle_hook+challenge_subtitle,1)
p.write_text(s)
print('Installed verified GHIN product aggregates:',len(trials),'trial months/events,',len(cohorts),'cohorts,',len(gps),'GPS month/status groups.')
