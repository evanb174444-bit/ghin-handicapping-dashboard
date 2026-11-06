"""Build Composition GC filters from the approved active-membership audit staging.
Only aggregate counts leave the private staging database. Existing scope/population
and GC club classifications are preserved; unique golfers are deduplicated anew.
"""
import json, sqlite3
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'data').exists(): ROOT=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard')
from sys import path
path.insert(0,str(ROOT/'scripts'))
from membership_refresh_format import age_bands,hi_bands,profile
D=ROOT/'data/processed/refresh-2026-11-03'
clubs={str(r['id']):r for r in json.loads((D/'membership_clubs.json').read_text())['clubs']}
con=sqlite3.connect('file:'+str(ROOT/'data/raw/membership_refresh_2026-11-03/audit.sqlite')+'?mode=ro',uri=True)
con.row_factory=sqlite3.Row
views=['gc','exclude'];scopes=['aga','international','all'];pops=['all','regular','junior']
def fresh():
 return {'total':0,**{k:Counter() for k in ['access','membership','club','gender','age','handicap']},'age_by_gender':{},'handicap_by_gender':{},'averages':{}}
s={(v,s,p):fresh() for v in views for s in scopes for p in pops}
def avg(d,key,total,n):
 if n:
  a=d['averages'].setdefault(key,{'sum':0,'count':0});a['sum']+=total;a['count']+=n
print('Aggregating membership composition',flush=True)
for r in con.execute('SELECT c.*,COUNT(*) n,SUM(a.age) ages,COUNT(a.age) na,SUM(a.hi) his,COUNT(a.hi) nh FROM active a JOIN cell c ON c.id=a.cell GROUP BY c.id'):
 v='gc' if r['is_gc'] else 'exclude';club=clubs[r['cid']];n=r['n']
 for scope in [r['scope'],'all']:
  for pop in ['all']+([r['pop']] if r['pop'] in pops[1:] else []):
   d=s[v,scope,pop];d['total']+=n
   for k,val in [('access',r['access']),('club',club['mappedType']),('membership',r['pop'].title()),('gender',r['gender']),('age',r['ageband']),('handicap',r['hiband'])]: d[k][val]+=n
   for key,band in [('age',r['ageband']),('handicap',r['hiband'])]: d[key+'_by_gender'].setdefault(r['gender'],Counter())[band]+=n
   for key,valid,total,num in [('age',r['ageband']!='Unknown / invalid',r['ages'],r['na']),('handicap',r['hiband'] not in ['No Index','Unknown'],r['his'],r['nh'])]:
    if valid:
     avg(d,key+'_all',total,num);avg(d,key+'_'+r['gender'],total,num)
result={v:{scope:{} for scope in scopes} for v in views}
for v in views:
 for scope in scopes:
  for pop in pops:
   print('Deduplicating',v,scope,pop,flush=True)
   conditions=['c.is_gc='+('1' if v=='gc' else '0')]
   if scope!='all':conditions.append("c.scope='"+scope+"'")
   if pop!='all':conditions.append("c.pop='"+pop+"'")
   q='SELECT COUNT(*),COALESCE(SUM(n>1),0),COALESCE(SUM(n-1),0) FROM (SELECT a.golfer,COUNT(*) n FROM active a JOIN cell c ON c.id=a.cell WHERE '+' AND '.join(conditions)+' GROUP BY a.golfer)'
   unique,multi,extra=con.execute(q).fetchone();d=s[v,scope,pop]
   for a in d['averages'].values():a['mean']=a['sum']/a['count']
   out={'counts':{'memberships':d['total'],'uniqueGolfers':unique,'multiMembershipGolfers':multi,'additionalMemberships':extra},'quality':{'ageUnknown':d['age']['Unknown / invalid'],'missingGolferDetails':None},'highIndexInsight':{'femaleShare':None},'age':profile(d,'age',age_bands),'handicap':profile(d,'handicap',hi_bands)}
   for k,labels in [('access',['Public','Private','Unknown — green-grass access not specified']),('membership',['Regular','Junior','Unclassified']),('club',['Type 1','Type 2','Type 3','GC Clubs']),('gender',['Male','Female','Unknown'])]:
    out[k]=[[label,d[k][label]] for label in labels]+[[label,n] for label,n in d[k].items() if label not in labels]
    assert sum(n for _,n in out[k])==d['total']
   assert unique+extra==d['total']
   result[v][scope][pop]=out
# Verify every count and distribution partitions the previously installed snapshot.
for scope in scopes:
 baseline=json.loads((D/('composition_review_'+scope+'.json')).read_text())['segments']
 for pop in pops:
  raw=baseline[{'all':'All Members','regular':'Regular','junior':'Junior'}[pop]]
  assert sum(result[v][scope][pop]['counts']['memberships'] for v in views)==raw['total']
  for field,source in [('access','access'),('club','club_type'),('gender','gender'),('membership','membership_type')]:
   combined=Counter()
   for v in views:combined.update(dict(result[v][scope][pop][field]))
   assert combined==Counter(raw[source]),(scope,pop,field)
  for field in ['age','handicap']:
   assert [sum(result[v][scope][pop][field]['allCounts'][i] for v in views) for i in range(len(result['gc'][scope][pop][field]['bands']))]==[raw[field].get(b,0) for b in result['gc'][scope][pop][field]['bands']]
(D/'composition_gc_filters.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print(json.dumps({v:result[v]['all']['all']['counts'] for v in views}),flush=True)
print('All scope/population partition checks passed',flush=True)
