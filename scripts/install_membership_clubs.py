"""Install the Clubs tab and its aggregate dataset."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def install(s):
 start='// BEGIN MEMBERSHIP CLUBS';end='// END MEMBERSHIP CLUBS'
 block=start+'\nconst MEMBERSHIP_CLUB_DATA='+json.dumps(json.loads((ROOT/'data/processed/membership_clubs.json').read_text()),separators=(',',':'))+';\n'+(ROOT/'scripts/membership_clubs_view.js').read_text()+'\n'+end+'\n'
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:]
 else:s=s.replace('const routeViews=',block+'const routeViews=',1)
 if '"membership.association-clubs":' not in s:s=s.replace('"membership.association-insights":', '"membership.association-clubs":membershipClubs,"membership.association-insights":',1)
 s=s.replace('["acquisition","retention","recovery","association-insights"]','["acquisition","retention","recovery","association-clubs","association-insights"]')
 s=s.replace('["summary","composition","associations","association-insights"]','["summary","composition","associations","association-clubs","association-insights"]')
 for line in (ROOT/'scripts/membership_chart_navigation.js').read_text().splitlines():
  name=line.split('(')[0].removeprefix('function ')
  s,n=re.subn(r'^function '+name+r'\(.*$',lambda _:line,s,flags=re.M);assert n==1
 start='/* BEGIN MEMBERSHIP CLUBS */';end='/* END MEMBERSHIP CLUBS */'
 css=start+'\n'+(ROOT/'scripts/membership_clubs.css').read_text()+'\n'+end
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+css+s[b:]
 else:s=s.replace('</style>',css+'\n</style>',1)
 return s
if __name__=='__main__':
 p=ROOT/'Handicapping and GHIN Dashboard.html';p.write_text(install(p.read_text()))
