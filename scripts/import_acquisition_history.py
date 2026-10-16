"""Validate the database aggregate export and install acquisition history locally."""
import csv,json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/EvanBelfi/Downloads/new_golfers_historical_2026-10-13.csv.csv')
OUT=ROOT/'data/processed/acquisition.json'
PAGE=ROOT/'Handicapping and GHIN Dashboard.html'
scopes={'AGA':'aga','International':'international','All Associations':'all'}
pops={'All Members':'all','Regular':'regular','Junior':'junior','Unclassified':'unclassified'}
rows=list(csv.DictReader(SOURCE.open(encoding='utf-8-sig',newline=''),strict=True))
history={s:{p:{str(y):[0]*(9 if y==2026 else 12)+([None]*3 if y==2026 else []) for y in range(2020,2027)} for p in pops.values()} for s in scopes.values()}
seen=set()
for r in rows:
    assert set(r)=={'reporting_month','scope','population','new_golfers'}
    date=r['reporting_month'];year,month,day=map(int,date.split('-'))
    assert 2020<=year<=2026 and 1<=month<=12 and day==1 and date<'2026-10-01'
    s=scopes[r['scope']];p=pops[r['population']];key=(s,p,date)
    assert key not in seen;seen.add(key)
    n=int(r['new_golfers']);assert n>=0
    history[s][p][str(year)][month-1]=n
for y in range(2020,2027):
    for m in range(9 if y==2026 else 12):
        for s in scopes.values():
            assert (s,'all',f'{y}-{m+1:02}-01') in seen,'Missing main monthly aggregate'
            alln=history[s]['all'][str(y)][m]
            assert max(history[s][p][str(y)][m] for p in ['regular','junior','unclassified'])<=alln
            assert sum(history[s][p][str(y)][m] for p in ['regular','junior','unclassified'])>=alln
        for p in pops.values():
            a=history['aga'][p][str(y)][m];i=history['international'][p][str(y)][m];n=history['all'][p][str(y)][m]
            assert max(a,i)<=n<=a+i
old=json.loads(OUT.read_text())
changes=[dict(scope=s,population=p,month=f'2026-{m+1:02}',previous=old['scopes'][s][p][m],current=history[s][p]['2026'][m]) for s in scopes.values() for p in pops.values() for m in range(9) if old['scopes'][s][p][m]!=history[s][p]['2026'][m]]
backup=ROOT/'backups/acquisition-before-history-2026-10-13';backup.mkdir(exist_ok=True)
for p in [PAGE,OUT,ROOT/'scripts/membership_acquisition_view.js']:
    dest=backup/p.name
    if not dest.exists():shutil.copy2(p,dest)
raw=ROOT/'data/raw/acquisition_history_2026-10-13';raw.mkdir(exist_ok=True);shutil.copy2(SOURCE,raw/SOURCE.name)
data=dict(source=SOURCE.name,sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),creationField='golfer_creation_date (v_golfer_clubs.golfer_creation_date)',years=list(range(2020,2027)),latestYear=2026,latestMonth=8,history=history,scopes={s:{p:history[s][p]['2026'] for p in pops.values()} for s in scopes.values()},methodology='Distinct GHIN numbers by Creation Date. All membership statuses included. Non-test clubs and associations, known parent federation, trial association 237 excluded. Scope and member type follow memberships represented in the database view. Absent subgroup rows from the grouped SQL result are zero; future months are unavailable.')
gc_path=ROOT/'data/processed/acquisition_gc.json'
if gc_path.exists():data['gc']=json.loads(gc_path.read_text())
overrides_path=ROOT/'data/processed/acquisition_annual_overrides.json'
if overrides_path.exists():data['annualOverrides']=json.loads(overrides_path.read_text())
adjustments_path=ROOT/'data/processed/acquisition_adjustments.json'
if adjustments_path.exists():data['adjustments']=json.loads(adjustments_path.read_text())
text=PAGE.read_text();a=text.index('const ACQUISITION_DATA=');b=text.index('const RECOVERY_DATA=',a)
block='const ACQUISITION_DATA='+json.dumps(data,separators=(',',':'))+';\nlet acquisitionMonth=8,acquisitionYear=2026,acquisitionChartType="line",acquisitionVisibleYears=new Set(ACQUISITION_DATA.years);\n'+(ROOT/'scripts/membership_acquisition_history_view.js').read_text()+'\n'
PAGE.write_text(text[:a]+block+text[b:]);OUT.write_text(json.dumps(data,indent=2)+'\n')
report=dict(rows=len(rows),period='2020-01 through 2026-09',changesFromEarlier2026Export=changes,checks='Unique month/scope/population keys; complete main monthly series; population and geography distinct-count bounds; zero only for absent grouped subgroup rows.',totals2026={s:sum(data['scopes'][s]['all'][:9]) for s in scopes.values()})
(ROOT/'reports/acquisition_history_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
