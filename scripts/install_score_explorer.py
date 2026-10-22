from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
page=ROOT/'Handicapping and GHIN Dashboard.html';h=page.read_text()
view=ROOT/'scripts/scores_scope_view.js';old=view.read_text();new=old.replace('${liveScoresParticipation()}</section>','${scoreParticipationExplorer()}</section>')
assert old.strip() in h;h=h.replace(old.strip(),new.strip(),1);view.write_text(new)
block='// BEGIN SCORE PARTICIPATION EXPLORER\nconst SCORE_EXPLORER_DATA='+ (ROOT/'data/processed/score_explorer.json').read_text()+';\n'+(ROOT/'scripts/score_explorer_view.js').read_text()+'\n// END SCORE PARTICIPATION EXPLORER\n'
if '// BEGIN SCORE PARTICIPATION EXPLORER' in h:
 start=h.index('// BEGIN SCORE PARTICIPATION EXPLORER');end=h.index('// END SCORE PARTICIPATION EXPLORER',start)+len('// END SCORE PARTICIPATION EXPLORER\n');h=h[:start]+block+h[end:]
else:h=h.replace('// END LIVE SCORE COUNTS', '// END LIVE SCORE COUNTS\n'+block,1)
css='''\n/* SCORE EXPLORER CONTROLS */
.score-participation-explorer .nh-filter-add label{width:auto;flex:0 0 auto;margin:0;font-size:14px;}.score-participation-explorer #seDimension{width:210px;flex:0 0 auto;}.score-participation-explorer #seValue{width:330px;flex:0 1 330px;}.score-participation-explorer .nh-results-toolbar{margin-bottom:16px;}

.scores-explorer,.score-participation-explorer,.score-participation-explorer .scores-participation{min-width:0;max-width:100%;width:100%;box-sizing:border-box;}
.score-participation-explorer .nh-club-scroll{min-width:0;max-width:100%;}

.score-participation-explorer select{max-width:100%;padding:10px 12px;border:1px solid #c8d8e9;border-radius:8px;background:#fff;color:#173d66;font:inherit;font-size:14px;}
.score-participation-explorer #seValue{max-width:440px;}
.score-participation-explorer [data-se-add],.score-participation-explorer [data-se-clear]{padding:10px 15px;border:0;border-radius:8px;background:#173d66;color:#fff;font-weight:700;cursor:pointer;}
.score-participation-explorer .nh-table{min-width:780px;}
.score-participation-explorer .nh-table th,.score-participation-explorer .nh-table td{white-space:nowrap;}
@media(max-width:650px){.score-participation-explorer #seValue{max-width:100%;width:100%;}.score-participation-explorer .scores-participation-body{min-width:0;}}
'''
if '/* SCORE EXPLORER CONTROLS */' not in h:h=h.replace('</style>',css+'\n</style>',1)
sort_css='''/* SCORE EXPLORER SORT */
.score-participation-explorer [data-se-sort]{border:0;background:transparent;color:inherit;font:inherit;font-weight:700;padding:6px 0;cursor:pointer;text-align:inherit;}
.score-participation-explorer [data-se-sort] span{margin-left:4px;color:#537fa6;}
.score-participation-explorer [data-se-sort]:hover{color:#123b66;text-decoration:underline;}
.score-participation-explorer [data-se-sort]:focus-visible{outline:2px solid #287bd1;outline-offset:4px;border-radius:2px;}
'''
if '/* SCORE EXPLORER SORT */' not in h:h=h.replace('</style>',sort_css+'\n</style>',1)
page.write_text(h);print('Installed explorer; HTML MB',round(page.stat().st_size/1e6,1))
