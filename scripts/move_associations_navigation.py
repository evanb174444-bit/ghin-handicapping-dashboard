"""Keep Associations inside Membership, with its existing Totals and Insights views."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def migrate_associations_navigation(s):
    s=re.sub(r'^[ \t]*<button[^\n]*data-top="associations"[^\n]*</button>\n','',s,flags=re.M)
    s=s.replace('membership:[["composition","Composition"],["insights","Explorer"],["summary","Charts"]]', 'membership:[["composition","Composition"],["summary","Charts"],["associations","Associations"],["insights","Explorer"]]')
    s=s.replace('membership:[["composition","Composition"],["insights","Explorer"],["summary","Charts"],["associations","Associations"]]', 'membership:[["composition","Composition"],["summary","Charts"],["associations","Associations"],["insights","Explorer"]]')
    migration='if(savedNavigation.top==="associations"){savedNavigation={top:"membership",sub:savedNavigation.sub==="insights"?"association-insights":"associations"};}'
    if migration not in s:
        anchor='}catch(e){}let records=[]'
        assert anchor in s
        s=s.replace(anchor,'}catch(e){}'+migration+'let records=[]',1)
    s=s.replace('["acquisition","retention","recovery"].includes(savedNavigation.sub)', '["acquisition","retention","recovery","association-insights"].includes(savedNavigation.sub)')
    if '"membership.associations":' not in s:
        anchor='"associations.totals":associations,'
        assert anchor in s
        s=s.replace(anchor,'"membership.associations":associations,"membership.association-insights":associationInsights,'+anchor,1)
    s=s.replace('$("membershipPopulationMount").innerHTML=activeTop==="membership"?', '$("membershipPopulationMount").innerHTML=activeTop==="membership"?')
    s=s.replace('else if(target==="associations"){activeTop="associations";activeSub="totals"}', 'else if(target==="associations"){activeTop="membership";activeSub="associations"}')
    for line in (ROOT/'scripts/membership_chart_navigation.js').read_text().splitlines():
        name=line.split('(')[0].removeprefix('function ')
        s,n=re.subn(r'^function '+name+r'\(.*$',lambda _:line,s,flags=re.M)
        assert n==1,(name,n)
    return s
if __name__=='__main__':
    p=ROOT/'Handicapping and GHIN Dashboard.html'
    p.write_text(migrate_associations_navigation(p.read_text()))
    print('Moved Associations under Membership, retaining Totals/Insights and saved-navigation compatibility.')
