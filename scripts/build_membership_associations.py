"""Build association snapshots from active memberships; embed aggregate counts only."""
import csv,json,sqlite3,tempfile
from pathlib import Path
from review_membership_exports import classify,numeric
ROOT=Path(__file__).resolve().parents[1]
allowed=set(json.loads((ROOT/'config/membership_scope.json').read_text())['association_ids'])
names=json.loads((ROOT/'config/association_names.json').read_text())
regions=json.loads((ROOT/'config/association_regions.json').read_text())['associations']
gc={r['club_id'] for r in json.loads((ROOT/'reports/gc_recorded_club_types.json').read_text())['clubs']}
files=[('aga','regular','01_active_standard_2026-09-21.csv.csv'),('aga','junior','02_active_junior_2026-09-22.csv.csv'),('aga','unclassified','03_active_unclassified_2026-09-22.csv'),('international',None,'01_active_international_full_2026-09-25.csv.csv')]
expected=json.loads((ROOT/'data/processed/international_totals.json').read_text())
out={'sources':[f for _,_,f in files],'scopes':{},'dates':expected['dates']}
with tempfile.TemporaryDirectory() as temp:
 db=sqlite3.connect(str(Path(temp)/'associations.sqlite'))
 db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
 db.execute('CREATE TABLE m(id TEXT PRIMARY KEY,golfer TEXT,scope TEXT,pop TEXT,association TEXT,club TEXT,gender TEXT,age REAL,access TEXT,is_gc INTEGER,club_type TEXT)')
 for scope,pop,file in files:
  batch=[]
  with (Path.home()/'Downloads'/file).open(encoding='utf-8-sig',newline='') as f:
   for r in csv.DictReader(f):
    aid=r['association_id']
    if scope=='aga' and aid not in allowed:continue
    if scope=='international':
     assert aid not in allowed and r['membership_status']=='Active'
     names[aid]=r.get('association_name') or names.get(aid,'Unknown association')
    access,kind,_=classify(r['club_id'],r['club_category'],r['club_type'],gc)
    age=numeric(r['age_at_extraction'])
    if age is not None and not 0<=age<=120:age=None
    if scope=='aga' and not r['matched_golfer_id']:age=None
    population=pop or {'Standard':'regular','Junior':'junior'}.get(r['usga_membership_type'],'unclassified')
    batch.append((r['membership_id'],r['golfer_id'],scope,population,aid,r['club_id'],r['gender'],age,access,int(kind=='GC Clubs'),r['club_type']))
    if len(batch)>=10000:db.executemany('INSERT OR REPLACE INTO m VALUES (?,?,?,?,?,?,?,?,?,?,?)',batch);batch=[]
  db.executemany('INSERT OR REPLACE INTO m VALUES (?,?,?,?,?,?,?,?,?,?,?)',batch);db.commit()
  print('Loaded',file,flush=True)
 for scope in ['aga','international','all']:
  out['scopes'][scope]={}
  for pop in ['all','regular','junior']:
   where=[];args=[]
   if scope!='all':where.append('scope=?');args.append(scope)
   if pop!='all':where.append('pop=?');args.append(pop)
   condition=' WHERE '+' AND '.join(where) if where else ''
   totals=db.execute('SELECT COUNT(*),COUNT(DISTINCT golfer) FROM m'+condition,args).fetchone()
   assert totals==(expected['scopes'][scope][pop]['memberships'],expected['scopes'][scope][pop]['uniqueGolfers']),(scope,pop,totals)
   rows=[]
   for aid,n,u,female,age,public,gcc,clubs,publicclubs,type2,ageKnown,under25,age65Plus in db.execute('''SELECT association,COUNT(*),COUNT(DISTINCT golfer),SUM(gender='Female'),AVG(age),SUM(access='Public'),SUM(is_gc),COUNT(DISTINCT club),COUNT(DISTINCT CASE WHEN access='Public' THEN club END),COUNT(DISTINCT CASE WHEN club_type='Type 2' THEN club END),COUNT(age),SUM(CASE WHEN age<25 THEN 1 ELSE 0 END),SUM(CASE WHEN age>=65 THEN 1 ELSE 0 END) FROM m'''+condition+' GROUP BY association',args):
    rows.append(dict(id=aid,name=names.get(aid,'Unknown association'),region=regions.get(aid,'International'),memberships=n,gcMemberships=gcc,activeGolfers=u,femalePct=female/n,averageAge=age,ageKnownCount=ageKnown,under25Count=under25,age65PlusCount=age65Plus,publicMembersPct=public/n,gcClubMembersPct=gcc/n,clubCount=clubs,publicClubsPct=publicclubs/clubs if clubs else None,type2ClubsPct=type2/clubs if clubs else None))
   assert sum(r['memberships'] for r in rows)==totals[0]
   out['scopes'][scope][pop]=rows
(ROOT/'data/processed/membership_associations.json').write_text(json.dumps(out,separators=(',',':')))
(ROOT/'data/validation/membership_associations.validation.json').write_text(json.dumps({'validation':'All nine scope/population membership and unique golfer totals match existing membership snapshots; association membership sums reconcile. Unique golfers deduplicated within association; clubs are those with active selected memberships.','sources':out['sources']},indent=2))
page=ROOT/'Handicapping and GHIN Dashboard.html';s=page.read_text()
start='// BEGIN LIVE MEMBERSHIP ASSOCIATIONS';end='// END LIVE MEMBERSHIP ASSOCIATIONS'
block=start+'\nconst MEMBERSHIP_ASSOCIATION_DATA='+json.dumps(out,separators=(',',':'))+';\n'+(ROOT/'scripts/membership_associations_view.js').read_text()+'\n'+end+'\n'
if start in s:
 a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:]
else:
 a=s.index('function associations(){');s=s[:a]+block+s[a:]
a=s.index('function associations(){');b=s.index('\nfunction ',a+5);s=s[:a]+'function associations(){return liveMembershipAssociations();}\n'+s[b:]
s=s.replace('activeTop==="membership"&&!["associations","association-insights"].includes(activeSub)?','activeTop==="membership"&&activeSub!=="association-insights"?')
s=s.replace('activeTop==="membership"&&["summary","composition"].includes(activeSub)', 'activeTop==="membership"&&["summary","composition","associations"].includes(activeSub)')
css=(ROOT/'scripts/membership_associations.css').read_text();marker='/* BEGIN MEMBERSHIP ASSOCIATIONS */';endmarker='/* END MEMBERSHIP ASSOCIATIONS */'
if marker in s:
 a=s.index(marker);b=s.index(endmarker,a)+len(endmarker);s=s[:a]+marker+'\n'+css+'\n'+endmarker+s[b:]
else:s=s.replace('</style>',marker+'\n'+css+'\n'+endmarker+'\n</style>',1)
from install_association_insights import install
s=install(s)
page.write_text(s)
print('Association snapshot and page updated.',flush=True)
