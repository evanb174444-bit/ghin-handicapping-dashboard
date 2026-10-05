"""Install the peer comparison view without rebuilding membership aggregates."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def install(s):
 start='// BEGIN ASSOCIATION PEER INSIGHTS';end='// END ASSOCIATION PEER INSIGHTS'
 block=start+'\n'+(ROOT/'scripts/association_insights_view.js').read_text()+'\n'+end
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end)
 else:
  a=s.index('function associationInsights(');b=s.index('\n',a)
 s=s[:a]+block+s[b:]
 s=s.replace('activeTop==="membership"&&activeSub!=="association-insights"?', 'activeTop==="membership"?')
 s=s.replace('activeTop==="membership"&&["summary","composition","associations"].includes(activeSub)', 'activeTop==="membership"&&["summary","composition","associations","association-insights"].includes(activeSub)')
 a=s.index('/* BEGIN MEMBERSHIP ASSOCIATIONS */');b=s.index('/* END MEMBERSHIP ASSOCIATIONS */',a)
 return s[:a]+'/* BEGIN MEMBERSHIP ASSOCIATIONS */\n'+(ROOT/'scripts/membership_associations.css').read_text()+'\n'+s[b:]
if __name__=='__main__':
 p=ROOT/'Handicapping and GHIN Dashboard.html';p.write_text(install(p.read_text()))
