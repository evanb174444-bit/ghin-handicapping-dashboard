"""Aggregate current geography totals without embedding golfer identifiers."""
import csv,json,sqlite3,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOWNLOADS=Path('/Users/EvanBelfi/Downloads')
allowed=set(json.loads((ROOT/'config/membership_scope.json').read_text())['association_ids'])
files=[('aga','Regular','01_active_standard_2026-09-21.csv.csv'),('aga','Junior','02_active_junior_2026-09-22.csv.csv'),('aga','Unclassified','03_active_unclassified_2026-09-22.csv'),('international',None,'01_active_international_full_2026-09-25.csv.csv')]
with tempfile.TemporaryDirectory() as temp:
 db=sqlite3.connect(str(Path(temp)/'counts.db'))
 db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
 db.execute('CREATE TABLE memberships(id TEXT PRIMARY KEY, golfer TEXT NOT NULL, scope TEXT, population TEXT, association TEXT NOT NULL)')
 for scope,population,name in files:
  batch=[]
  with (DOWNLOADS/name).open(encoding='utf-8-sig',newline='') as f:
   for row in csv.DictReader(f):
    if scope=='aga' and row['association_id'] not in allowed:continue
    if scope=='international':
     assert row['association_id'] not in allowed
     assert row['parent_federation'].strip() and row['parent_federation']!='United States Golf Association'
     assert row['membership_status']=='Active'
    assert row['golfer_id'] and row['membership_id']
    pop=population or {'Standard':'Regular','Junior':'Junior'}.get(row['usga_membership_type'],'Unclassified')
    batch.append((row['membership_id'],row['golfer_id'],scope,pop,row['association_id']))
    if len(batch)==10000:
     db.executemany('INSERT OR REPLACE INTO memberships VALUES (?,?,?,?,?)',batch);batch=[]
  db.executemany('INSERT OR REPLACE INTO memberships VALUES (?,?,?,?,?)',batch);db.commit()
 out={'sources':[name for _,_,name in files],'dates':{'aga':'September 21–22, 2026','international':'September 25, 2026','all':'September 21–25, 2026'},'scopes':{}}
 for scope in ['aga','international','all']:
  out['scopes'][scope]={}
  for key,pop in [('all',None),('regular','Regular'),('junior','Junior'),('unclassified','Unclassified')]:
   where=[];args=[]
   if scope!='all':where.append('scope=?');args.append(scope)
   if pop:where.append('population=?');args.append(pop)
   condition=' WHERE '+' AND '.join(where) if where else ''
   memberships,unique=db.execute('SELECT COUNT(*),COUNT(DISTINCT golfer) FROM memberships'+condition,args).fetchone()
   pairs=db.execute('SELECT COUNT(*) FROM (SELECT golfer,association FROM memberships'+condition+' GROUP BY golfer,association)',args).fetchone()[0]
   multi=db.execute('SELECT COUNT(*) FROM (SELECT golfer FROM memberships'+condition+' GROUP BY golfer HAVING COUNT(*)>1)',args).fetchone()[0]
   out['scopes'][scope][key]={'memberships':memberships,'uniqueGolfers':unique,'golferAssociationPairs':pairs,'additionalAssociationPairs':pairs-unique,'sameAssociationExtraMemberships':memberships-pairs,'multiMembershipGolfers':multi,'additionalMemberships':memberships-unique}
 assert out['scopes']['aga']['all']['memberships']==3840678
 assert out['scopes']['aga']['all']['uniqueGolfers']==3544477
 out['overlap']={pop:out['scopes']['aga'][pop]['uniqueGolfers']+out['scopes']['international'][pop]['uniqueGolfers']-out['scopes']['all'][pop]['uniqueGolfers'] for pop in ['all','regular','junior','unclassified']}
 (ROOT/'reports/membership_association_pair_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
