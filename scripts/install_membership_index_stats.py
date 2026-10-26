from pathlib import Path
import gzip,base64
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'Handicapping and GHIN Dashboard.html';h=p.read_text()
source=(ROOT/'scripts/membership_explorer.js').read_text().strip()
ui='// BEGIN MEMBERSHIP EXPLORER UI\n'+source+'\n// END MEMBERSHIP EXPLORER UI'
if '// BEGIN MEMBERSHIP EXPLORER UI' in h:
 start=h.index('// BEGIN MEMBERSHIP EXPLORER UI');end=h.index('// END MEMBERSHIP EXPLORER UI',start)+len('// END MEMBERSHIP EXPLORER UI')
 h=h[:start]+ui+h[end:]
else:
 assert source in h,'Membership explorer source not found'
 h=h.replace(source,ui,1)
payload=base64.b64encode(gzip.compress((ROOT/'data/processed/membership_index_stats.json').read_bytes(),mtime=0)).decode()
block="""// BEGIN MEMBERSHIP INDEX STATISTICS
let MEMBERSHIP_INDEX_STATS=null,membershipIndexLoadError=false;
const MEMBERSHIP_INDEX_READY=unpackScoreExplorerData('PAYLOAD').then(data=>{MEMBERSHIP_INDEX_STATS=data;refreshMembershipExplorer();}).catch(error=>{membershipIndexLoadError=true;console.error('Unable to load membership Index statistics',error);refreshMembershipExplorer();});
// END MEMBERSHIP INDEX STATISTICS
""".replace('PAYLOAD',payload)
if '// BEGIN MEMBERSHIP INDEX STATISTICS' in h:
 start=h.index('// BEGIN MEMBERSHIP INDEX STATISTICS');end=h.index('// END MEMBERSHIP INDEX STATISTICS',start)+len('// END MEMBERSHIP INDEX STATISTICS\n');h=h[:start]+block+h[end:]
else:
 at=h.index(source);h=h[:at]+block+h[at:]
css="""/* MEMBERSHIP INDEX STATISTICS */
.me-index-kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:14px 0;}
.me-index-kpis>div{background:#fff;border:1px solid #c8d8e9;border-top:4px solid #315f8b;border-radius:9px;padding:14px;}
.me-index-kpis span,.me-index-kpis small{display:block;color:#526176;font-size:13px;}
.me-index-kpis strong{display:block;color:#193f66;font-size:26px;margin:6px 0;}
.membership-explorer .nh-table{min-width:1050px;}
@media(max-width:650px){.me-index-kpis{grid-template-columns:1fr;}}
"""
if '/* MEMBERSHIP INDEX STATISTICS */' not in h:h=h.replace('</style>',css+'\n</style>',1)
start_marker='/* BEGIN MEMBERSHIP COMPARE */';end_marker='/* END MEMBERSHIP COMPARE */'
comparison_css=start_marker+'\n'+(ROOT/'scripts/membership_compare.css').read_text()+'\n'+end_marker
if start_marker in h:
 start=h.index(start_marker);end=h.index(end_marker,start)+len(end_marker);h=h[:start]+comparison_css+h[end:]
else:h=h.replace('</style>',comparison_css+'\n</style>',1)
p.write_text(h)
print('Installed exact Index statistics; HTML MB',round(p.stat().st_size/1e6,1))
