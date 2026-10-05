from pathlib import Path
import json
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
gc_rows=json.loads((ROOT/'gc-dashboard-summary/data/membership_monthly.json').read_text())
gc_latest=max((r for r in gc_rows if r.get('activeGolfers') is not None),key=lambda r:(r['year'],r['monthNum']))
gc_prior=next((r for r in gc_rows if r['year']==gc_latest['year']-1 and r['monthNum']==gc_latest['monthNum']),{})
gc_date=date(gc_latest['year']+(gc_latest['monthNum']==12),gc_latest['monthNum']%12+1,1)
gc_highlight={'current':gc_latest['activeGolfers'],'prior':gc_prior.get('activeGolfers'),'period':'Active memberships · '+gc_date.strftime('%b 1, %Y'),'basis':'vs '+gc_date.replace(year=gc_date.year-1).strftime('%b 1, %Y')}
p=ROOT/'scripts/scores_scope_view.js';s=p.read_text().replace('function liveScoresAnnualTotals(data,ytd=false){','function liveScoresAnnualTotals(data,ytd=false,viewOverride=null){').replace("const view=ytd?scoresYtdTotalsView:scoresAnnualTotalsView,kind=", "const view=viewOverride||(ytd?scoresYtdTotalsView:scoresAnnualTotalsView),kind=");p.write_text(s)
p=ROOT/'Handicapping and GHIN Dashboard.html';s=p.read_text();a=s.index('let scoresGeography=');b=s.index('// END LIVE SCORE COUNTS',a);s=s[:a]+(ROOT/'scripts/scores_scope_view.js').read_text()+'\n'+s[b:]
a=s.index('function summaryMembershipSnapshot(');b=s.index('\nconst MEMBERSHIP_SUMMARY_DATA=',a);s=s[:a]+(ROOT/'scripts/home_snapshot_view.js').read_text().replace('__HOME_GC_HIGHLIGHT__',json.dumps(gc_highlight))+s[b:]
start='/* BEGIN HOME SNAPSHOT */';end='/* END HOME SNAPSHOT */';css=start+'\n'+(ROOT/'scripts/home_snapshot.css').read_text()+'\n'+end
if start in s:
 a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+css+s[b:]
else:s=s.replace('</style>',css+'\n</style>',1)
s=s.replace(':"Report Date: August 1, 2026";localStorage', ':activeTop==="summary"?"Membership snapshot: September 21–25, 2026 · Scores through August 31, 2026":"Report Date: August 1, 2026";localStorage')
p.write_text(s)
