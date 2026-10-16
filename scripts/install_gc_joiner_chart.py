"""Install GC Membership Totals/Acquisition navigation and joiner comparison."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
page=ROOT/'Handicapping and GHIN Dashboard.html';text=page.read_text()
data=json.loads((ROOT/'data/processed/gc_joiner_history.json').read_text())
start=text.find('const GC_JOINER_DATA=')
if start<0:start=text.index('function gcMembershipTotals(){')
end=text.index("let gcAssociationView=",start)
block='const GC_JOINER_DATA='+json.dumps(data,separators=(',',':'))+';\n'+(ROOT/'scripts/gc_joiner_view.js').read_text()+'\n'+(ROOT/'scripts/gc_membership_view.js').read_text()+'\n'
text=text.replace('["membership-totals","Membership Totals"]','["membership-totals","Membership"]')
# Renaming the visible label changes offsets; locate the existing block again.
start=text.find('const GC_JOINER_DATA=')
if start<0:start=text.index('function gcMembershipTotals(){')
end=text.index("let gcAssociationView=",start)
page.write_text(text[:start]+block+text[end:])
print('Installed GC Membership tabs: Totals and Acquisition.')
