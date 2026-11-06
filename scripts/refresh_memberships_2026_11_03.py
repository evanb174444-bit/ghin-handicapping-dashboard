import sys,types,os,json,hashlib,time
from pathlib import Path
ROOT=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard')
sys.path.insert(0,str(ROOT/'scripts'))
RAW=ROOT/'data/raw/membership_refresh_2026-11-03';OUT=ROOT/'data/processed/refresh-2026-11-03'
def module(name):
 p=ROOT/'scripts'/(name+'.py');s=p.read_text().replace('2026-10-13','2026-11-03').replace('October 13, 2026','November 3, 2026')
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(s,str(p),'exec'),m.__dict__);return m
stage=sys.argv[1]
os.environ.setdefault('TMPDIR',str(RAW))
if stage=='audit':
 RAW.mkdir(exist_ok=True);dest=RAW/'membership_refresh_2026-11-03.csv.csv';source=Path('/Users/EvanBelfi/Downloads/memberships_2026-11-03.csv')
 if not dest.exists():os.link(source,dest)
 h=hashlib.sha256();start=time.monotonic()
 with dest.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 (RAW/'source_manifest.json').write_text(json.dumps({'source':str(source),'archived':str(dest),'method':'hard link preserves source inode without duplicating 4GB on low disk','bytes':dest.stat().st_size,'sha256':h.hexdigest(),'snapshot_date':'2026-11-03'},indent=2))
 print('Raw source archived/checksummed',round(time.monotonic()-start,1),flush=True)
 module('audit_membership_refresh').main()
elif stage=='build':
 module('audit_membership_refresh');module('finish_membership_refresh');module('build_membership_refresh').main()
elif stage=='index':
 p=ROOT/'scripts/build_membership_index_stats.py';s=p.read_text().replace('2026-10-13','2026-11-03').replace('October 13, 2026','November 3, 2026')
 s=s.replace("ROOT/'data/processed/membership_intersections.json'","ROOT/'data/processed/refresh-2026-11-03/membership_intersections.json'")
 s=s.replace("ROOT/'data/raw/membership_index_stats'","ROOT/'data/raw/membership_refresh_2026-11-03/index_stats'")
 s=s.replace("ROOT/'data/processed/membership_index_stats.json'","ROOT/'data/processed/refresh-2026-11-03/membership_index_stats.json'")
 s=s.replace("ROOT/'reports/membership_index_stats_validation.json'","ROOT/'reports/membership_index_stats_2026-11-03.validation.json'")
 exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
elif stage=='install':
 import shutil,gzip,base64
 from membership_refresh_format import format_composition
 backup=ROOT/'backups/membership-before-2026-11-03-refresh';backup.mkdir(exist_ok=False)
 page=ROOT/'Handicapping and GHIN Dashboard.html';h=page.read_text()
 def load(name):return json.loads((OUT/(name+'.json')).read_text())
 def dump(data):return json.dumps(data,separators=(',',':')).replace('</','<\\/')
 def constant(text,name,data):
  marker='const '+name+'=';a=text.index(marker)+len(marker);_,n=json.JSONDecoder().raw_decode(text[a:]);return text[:a]+dump(data)+text[a+n:]
 names=load('association_names');scope=load('membership_scope');high=load('high_index_by_scope');validation=load('validation')
 compositions={s:format_composition(load('composition_review_'+s),{'populations':high[s]},names) for s in ['aga','international','all']}
 outputs={name:load(name) for name in ['membership_associations','membership_clubs','membership_intersections','nh_intersections','international_totals','membership_index_stats']}
 outputs.update(membership_composition=dict(meta=dict(mockData=False,extractionDates=['2026-11-03'],scope=scope,historicalTrendsAvailable=False),populations=compositions['aga']),international_composition={s:compositions[s] for s in ['international','all']},high_index_insight=dict(scope=scope,populations=high['aga']))
 targets=[page]+[ROOT/'data/processed'/(n+'.json') for n in outputs]
 jsfiles=['membership_totals_view.js','membership_composition_view.js','home_snapshot_view.js','membership_explorer.js','membership_associations_view.js','membership_clubs_view.js']
 targets += [ROOT/'scripts'/n for n in jsfiles]
 for p in targets:
  if p.exists():dest=backup/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 immutable=['ACQUISITION_DATA','GHIN_LIVE_DATA','SCORE_EXPLORER_DATA']
 before_hashes={}
 for name in immutable:
  marker='const '+name+'='
  if marker in h:
   at=h.index(marker)+len(marker)
   try:_,n=json.JSONDecoder().raw_decode(h[at:]);before_hashes[name]=hashlib.sha256(h[at:at+n].encode()).hexdigest()
   except ValueError:pass
 for name,data in [('MEMBERSHIP_COMPOSITION_DATA',compositions['aga']),('MEMBERSHIP_GEOGRAPHY_COMPOSITION',outputs['international_composition']),('MEMBERSHIP_GEOGRAPHY_COUNTS',outputs['international_totals']),('MEMBERSHIP_INTERSECTIONS',outputs['membership_intersections']),('NH_INTERSECTIONS',outputs['nh_intersections']),('MEMBERSHIP_ASSOCIATION_DATA',outputs['membership_associations']),('MEMBERSHIP_CLUB_DATA',outputs['membership_clubs']),('MEMBERSHIP_SCOPE',scope)]:h=constant(h,name,data)
 replacements={
 'All Associations · October 13, 2026':'All Associations · November 3, 2026',
 'Active memberships · October 13, 2026':'Active memberships · November 3, 2026',
 'October 13 extract vs.':'November 3 extract vs.',
 '2026 October 13':'2026 November 3',
 '2026 uses the October 13 extract.':'2026 uses the November 3 extract.',
 'AGA and international 2026 counts come from the October 13 membership export.':'AGA and international 2026 counts come from the November 3 membership export.',
 'The October 13, 2026 export provides the current membership composition.':'The November 3, 2026 export provides the current membership composition.',
 "insights?'October 13, 2026':membershipScopeDate()":"insights?'November 3, 2026':membershipScopeDate()",
 'exported in batches between 2:33 and 2:48 p.m. Eastern':'exported in 1,028 batches between 3:33 and 3:47 p.m. Eastern on November 3',
 'October 13, 2026 snapshot.':'November 3, 2026 snapshot.',
 'Unique golfers · October 13, 2026':'Unique golfers · November 3, 2026',
 'Membership extract: October 13, 2026':'Membership extract: November 3, 2026',
 }
 for old,new in replacements.items():h=h.replace(old,new)
 for name in jsfiles:
  p=ROOT/'scripts'/name
  if not p.exists():continue
  text=p.read_text()
  for old,new in replacements.items():text=text.replace(old,new)
  p.write_text(text)
 payload=base64.b64encode(gzip.compress((OUT/'membership_index_stats.json').read_bytes(),mtime=0)).decode()
 marker='// BEGIN MEMBERSHIP INDEX STATISTICS';endmarker='// END MEMBERSHIP INDEX STATISTICS'
 a=h.index(marker);b=h.index(endmarker,a)+len(endmarker)
 h=h[:a]+"""// BEGIN MEMBERSHIP INDEX STATISTICS
let MEMBERSHIP_INDEX_STATS=null,membershipIndexLoadError=false;
const MEMBERSHIP_INDEX_READY=unpackScoreExplorerData('"""+payload+"""').then(data=>{MEMBERSHIP_INDEX_STATS=data;refreshMembershipExplorer();}).catch(error=>{membershipIndexLoadError=true;console.error('Unable to load membership Index statistics',error);refreshMembershipExplorer();});
// END MEMBERSHIP INDEX STATISTICS"""+h[b:]
 for name,expected in before_hashes.items():
  at=h.index('const '+name+'=')+len('const '+name+'=');_,n=json.JSONDecoder().raw_decode(h[at:]);assert hashlib.sha256(h[at:at+n].encode()).hexdigest()==expected,name
 for name,data in outputs.items():(ROOT/'data/processed'/(name+'.json')).write_text(dump(data)+'\n')
 page.write_text(h)
 (OUT/'installation.json').write_text(json.dumps({'installed':True,'snapshot':'2026-11-03','validation':validation,'unchanged_constants':before_hashes,'backup':str(backup)},indent=2))
 print('Installed locally',json.dumps(validation),flush=True)
