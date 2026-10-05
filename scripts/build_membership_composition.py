"""Embed reviewed aggregate membership composition into the local standalone HTML."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT/'reports/membership_composition_review_2026-09-22.json').read_text())
age_bands = ['Under 18','18–24','25–34','35–44','45–54','55–64','65+','Unknown / invalid']
hi_bands = ['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+','No Index','Unknown']

def items(s, key, labels):
    return [[label, s[key].get(label, 0)] for label in labels]

def profile(s, key, bands):
    out = {'bands': bands, 'allCounts':[s[key].get(b,0) for b in bands],
           'all':[100*s[key].get(b,0)/s['total'] if s['total'] else 0 for b in bands],
           'allAverage':s['averages'].get(key+'_all',{}).get('mean')}
    for gender, prop in [('Male','male'),('Female','female')]:
        counts = s[key+'_by_gender'].get(gender,{})
        denominator = s['gender'].get(gender,0)
        assert sum(counts.values()) == denominator
        out[prop] = [100*counts.get(b,0)/denominator if denominator else 0 for b in bands]
        out[prop+'Counts'] = [counts.get(b,0) for b in bands]
        out[prop+'Average'] = s['averages'].get(key+'_'+gender,{}).get('mean')
    return out

scope = source.get('scope', {'mode':'worldwide','label':'Worldwide Associations','definition':'Worldwide association scope'})
data = {}
names_path = ROOT/'config/association_names.json'
association_names = json.loads(names_path.read_text()) if names_path.exists() else {}
insight = json.loads((ROOT/'data/processed/high_index_insight.json').read_text())
assert insight['scope'] == scope, 'Rebuild high-index insight for the current scope'
for key,pop in [('all','All Members'),('regular','Regular'),('junior','Junior')]:
    s = source['segments'][pop]
    data[key] = {
        'noHandicap':s['no_handicap'],
        'highIndexInsight':insight['populations'][key],
        'counts': {'memberships':s['total'],'uniqueGolfers':s['unique_golfers'],
                   'multiMembershipGolfers':s['multi_membership_golfers'],'additionalMemberships':s['additional_memberships']},
        'access':items(s,'access',['Public','Private','Unknown — green-grass access not specified']),
        'membership':items(s,'membership_type',['Regular','Junior','Unclassified']),
        'club':items(s,'club_type',['Type 1','Type 2','Type 3','GC Clubs']),
        'gender':items(s,'gender',['Male','Female','Unknown']),
        'publicBreakdown':items(s,'public_breakdown',['Public Green Grass Clubs','Semi-Private','Resort','Municipal','Military','Affiliate / WORE','Virtual clubs / eClubs','GC Clubs']),
        'clubBreakdown':items(s,'club_breakdown',['Private Clubs','Public Green Grass Clubs','Semi-Private','Resort','Municipal','Military','Affiliate / WORE','Virtual clubs / eClubs','GC Clubs','Unknown Access']),
        'clubGenderAssociations':{gender:{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in groups.items()} for gender,groups in s['club_gender_associations'].items()},
        'clubAssociations':{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in s['club_by_association'].items()},
        'publicAssociations':{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in s['public_by_association'].items()},
        'affiliateAssociations':[{'id':aid,'name':association_names.get(aid), 'memberships':count}
            for aid,count in sorted(s['affiliate_by_association'].items(),key=lambda item:(-item[1],item[0]))],
        'handicapByAge':{band:{'total':c['total'],'profile':profile(c,'handicap',hi_bands)} for band,c in s['handicap_by_age'].items()},
        'age':profile(s,'age',age_bands), 'handicap':profile(s,'handicap',hi_bands),
        'quality':{'ageUnknown':s['age']['Unknown / invalid'],'missingGolferDetails':s['issues'].get('missing_golfer_details',0)}
    }
    for aid,segment in data[key]['noHandicap']['dimensions']['association'].items():
        segment['name']=association_names.get(aid, 'Unknown association')
    for club in data[key]['noHandicap']['clubs'].values():
        club['associationName']=association_names.get(club['association'],'Unknown association')
    for field in ['access','membership','club','gender']:
        assert sum(v for _,v in data[key][field]) == s['total']
    assert sum(v for _,v in data[key]['clubBreakdown']) == s['total']
    assert sum(v for _,v in data[key]['publicBreakdown']) == s['access']['Public']
    assert sum(row['memberships'] for row in data[key]['affiliateAssociations']) == s['public_breakdown'].get('Affiliate / WORE',0)

output = ROOT/'data/processed/membership_composition.json'
output.write_text(json.dumps({'meta':{'mockData':False,'extractionDates':['2026-09-21','2026-09-22'],
    'scope':scope,'historicalTrendsAvailable':False},'populations':data},indent=2))
html = ROOT/'Handicapping and GHIN Dashboard.html'
s = html.read_text()
start = s.index('const MEMBERSHIP_COMPOSITION_DATA=')
end = s.index('function compositionDonut(',start)
s = s[:start]+'const MEMBERSHIP_COMPOSITION_DATA='+json.dumps(data,separators=(',',':'))+';\nconst MEMBERSHIP_SCOPE='+json.dumps(scope,separators=(',',':'))+';\n'+s[end:]
start = s.index('function compositionDonut(')
end = s.index('\nfunction ', start)
s = s[:start]+(ROOT/'scripts/composition_donut.js').read_text().strip()+'\n'+s[end:]
membership_intersections=json.loads((ROOT/'data/processed/membership_intersections.json').read_text())
assert membership_intersections['scope']==scope
nh_intersections=json.loads((ROOT/'data/processed/nh_intersections.json').read_text())
assert nh_intersections['scope']==scope
view = (ROOT/'scripts/membership_composition_view.js').read_text().strip()+'\nconst NH_INTERSECTIONS='+json.dumps(nh_intersections,separators=(',',':'))+';\n'+(ROOT/'scripts/no_handicap_explorer.js').read_text().strip()+'\nconst MEMBERSHIP_INTERSECTIONS='+json.dumps(membership_intersections,separators=(',',':'))+';\n'+(ROOT/'scripts/membership_explorer.js').read_text().strip()
if 'function liveCompositionLegend(' in s:
    start = s.index('let membershipInsightSection=') if 'let membershipInsightSection=' in s else s.index('function liveCompositionLegend(')
    end = s.index('\nfunction membershipSummary(',start)
    s = s[:start]+view+'\n'+s[end:]
else:
    s,n = re.subn(r'^function membershipComposition\(\).*$',lambda _:view,s,flags=re.M)
    assert n == 1
# Null-safe means for empty demographic groups.
for prop in ['maleAverage','femaleAverage']:
    s=s.replace('${data.'+prop+'.toFixed(1)}','${data.'+prop+' == null ? "—" : data.'+prop+'.toFixed(1)}')
old='function render(){localStorage.setItem'
new='function render(){document.querySelector(".subtitle").textContent=activeTop==="membership"&&activeSub==="composition"?"Membership extracts: September 21–22, 2026":"Report Date: August 1, 2026";localStorage.setItem'
if old in s:s=s.replace(old,new,1)
s=s.replace('"Membership extracts: September 21–22, 2026"', 'MEMBERSHIP_SCOPE.label+" · Membership extracts: September 21–22, 2026"')
# Membership explorers have their own tab beside Composition.
s=s.replace('["composition","Membership Composition"]', '["composition","Composition"]')
if '["insights",' not in s[s.index('membership:[['):s.index('],associations:',s.index('membership:[['))]:
    s=s.replace('membership:[["composition","Composition"],', 'membership:[["composition","Composition"],["insights","Insights"],')
s=s.replace('membership:[["composition","Composition"],["insights","Insights"]', 'membership:[["composition","Composition"],["insights","Explorer"]')
if '"membership.insights":' not in s:
    s=s.replace('"membership.composition":membershipComposition,', '"membership.composition":membershipComposition,"membership.insights":()=>membershipComposition(true),')
s=s.replace('activeTop==="membership"&&activeSub==="composition"?', 'activeTop==="membership"&&["composition","insights"].includes(activeSub)?')
# Totals use the available snapshot and flag illustrative history.
totals_source=(ROOT/'scripts/membership_totals_view.js').read_text()
geography_counts=json.loads((ROOT/'data/processed/international_totals.json').read_text())
totals_source=totals_source.replace('const MEMBERSHIP_GEOGRAPHY_COMPOSITION=null;', 'const MEMBERSHIP_GEOGRAPHY_COMPOSITION='+(ROOT/'data/processed/international_composition.json').read_text().strip()+';')
totals_source=totals_source.replace('const MEMBERSHIP_GEOGRAPHY_COUNTS=null;', 'const MEMBERSHIP_GEOGRAPHY_COUNTS='+json.dumps(geography_counts,separators=(',',':'))+';')
for name in ['membershipGrowthCard','membershipYoyCard','membershipProjectionCard','membershipProjectionChart','membershipSummary']:
    pattern=r'^function '+name+r'\([^\n]*' if name!='membershipProjectionChart' else r'^function membershipProjectionChart\([^\n]*\n.*?^}'
    flags=re.M|(re.S if name=='membershipProjectionChart' else 0)
    replacement=re.search(pattern,totals_source,flags).group(0)
    s,count=re.subn(pattern,lambda _:replacement,s,flags=flags)
    assert count==1,(name,count)
helpers=totals_source[:totals_source.index('function membershipGrowthCard(')]
if 'function membershipDummyMark(' in s:
    begin=s.index('function membershipDummyMark(');end=s.index('function membershipGrowthCard(',begin)
    s=s[:begin]+helpers+s[end:]
else:s=s.replace('function membershipGrowthCard(',helpers+'function membershipGrowthCard(',1)
s=s.replace('membershipGrowthMonth=7,','membershipGrowthMonth=8,')
s=s.replace('["composition","insights"].includes(activeSub)', '["composition","insights","summary"].includes(activeSub)')
s=s.replace('max=Math.ceil(Math.max(...values)*1.15/500000)*500000,','scaleStep=Math.pow(10,Math.floor(Math.log10(Math.max(1,...values))))/2,max=Math.ceil(Math.max(1,...values)*1.15/scaleStep)*scaleStep,')
s=s.replace('Dummy international data preview','Membership extracts: September 21–25, 2026')
# Scope control preview on Membership Totals only.
scope_hook='if(activeTop==="membership"&&activeSub==="summary"){$("membershipPopulationMount").insertAdjacentHTML("afterbegin",membershipScopeControl());document.querySelector(".subtitle").textContent=membershipScopeLabel()+" · "+(membershipGeography==="aga"?"Membership extracts: September 21–22, 2026":"Membership extracts: September 21–25, 2026");}/* membership-scope-preview */'
if '/* membership-scope-preview */' not in s:
    s=s.replace('const view=activeTop===',scope_hook+'const view=activeTop===',1)
s=s.replace('(membershipGeography==="aga"?"Membership extracts: September 21–22, 2026":"Membership extracts: September 21–25, 2026")','("Membership extracts: "+membershipScopeDate())')
s=s.replace('if(activeTop==="membership"&&activeSub==="summary"){$("membershipPopulationMount").insertAdjacentHTML','if(activeTop==="membership"&&["summary","composition"].includes(activeSub)){$("membershipPopulationMount").insertAdjacentHTML')
# Charts groups the four reporting pages under a third navigation row.
s=s.replace('["summary","Totals"],["acquisition","Acquisition"],["retention","Retention"],["recovery","Recovery"]', '["summary","Charts"]',1)
chart_navigation=(ROOT/'scripts/membership_chart_navigation.js').read_text().strip()
s=re.sub(r'^function renderSecondary\(\).*$',lambda _:chart_navigation.split('\n')[0],s,flags=re.M)
nav_helper=chart_navigation.split('\n')[1]
if 'function membershipChartsNav(' in s:
    s=re.sub(r'^function membershipChartsNav\(\).*$',lambda _:nav_helper,s,flags=re.M)
else:s=s.replace('function renderSecondary(){',nav_helper+'\nfunction renderSecondary(){',1)
s=s.replace('if(savedItems.some(([id])=>id===savedNavigation.sub))', 'if(savedItems.some(([id])=>id===savedNavigation.sub)||(activeTop==="membership"&&["acquisition","retention","recovery"].includes(savedNavigation.sub)))')
if '/* membership-charts-nav */' not in s:
    s=s.replace(';bindDynamic()}', ';$("app").insertAdjacentHTML("afterbegin",membershipChartsNav());/* membership-charts-nav */bindDynamic()}',1)
style='''
/* Reviewed membership composition */
.live-source-note{color:#526176;font-size:13px;margin:0 0 16px;line-height:1.5}
.live-membership-counts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:20px}
.live-membership-counts>div{padding:16px;background:#fff;border:1px solid #dbe3ee;border-radius:14px;display:flex;flex-direction:column;justify-content:space-between;gap:10px}
.live-membership-counts span{font-size:12px;color:#526176;font-weight:700;line-height:1.4}
.live-membership-counts strong{font-size:25px;color:#14395f}.live-membership-counts .primary{border-top:3px solid #14395f}
.membership-live .composition-card{height:auto!important;min-height:0!important}
.membership-live .composition-donut-layout{padding:20px!important;display:flex!important;flex-direction:column!important}
.membership-live .composition-card:not(.composition-trend-card) .composition-donut-wrap{width:min(430px,100%)!important;height:auto!important;min-width:0!important;min-height:0!important;max-width:430px!important;max-height:none!important;aspect-ratio:1/1}
.live-composition-legend{list-style:none;margin:0;padding:0 24px 22px;display:grid;gap:8px}
.live-composition-legend li{display:grid;grid-template-columns:10px minmax(0,1fr) auto;gap:8px;align-items:center;font-size:12px;color:#334155}
.live-composition-legend i{width:9px;height:9px;border-radius:50%}.live-composition-legend strong{white-space:nowrap}.live-composition-legend small{color:#64748b;margin-left:8px}
.live-profile-note{font-size:12px;line-height:1.6;color:#526176;margin:0;padding:0 24px 20px}
.live-public-pool{padding:22px 24px 0;display:flex;flex-direction:column;gap:5px}.live-public-pool strong{font-size:34px;color:#14395f;line-height:1.15}.live-public-pool span{font-size:12px;font-weight:700;color:#526176}.live-public-pool p{font-size:12px;color:#526176;margin:3px 0 0;line-height:1.5}
.live-affiliate-table-wrap{margin:22px 24px;max-height:620px;overflow:auto}.live-affiliate-table{width:100%;border-collapse:collapse;font-size:12px}.live-affiliate-table th{position:sticky;top:0;background:#f5f7fa;color:#526176;font-size:11px;text-align:left;padding:10px 6px;z-index:1}.live-affiliate-table td{padding:11px 6px;border-bottom:1px solid #e8eef6;color:#334155}.live-affiliate-table th:nth-last-child(-n+2),.live-affiliate-table td:nth-last-child(-n+2){text-align:right;white-space:nowrap}.live-affiliate-table td:first-child{color:#64748b;width:26px}.live-affiliate-table small{display:block;color:#64748b;font-size:10px;margin-top:3px}.live-affiliate-associations{align-self:start}
.membership-live .live-public-breakdown{grid-column:span 1}.membership-live .live-public-breakdown .composition-bars{display:grid;grid-template-columns:1fr;padding:24px}.live-public-breakdown .composition-bars-total{grid-column:1/-1}
.live-history-empty{min-height:350px;padding:50px 30px;display:flex;flex-direction:column;justify-content:center;text-align:center;color:#526176;line-height:1.6}.live-history-empty strong{font-size:20px;color:#14395f}
.live-data-notes{font-size:12px;color:#526176;line-height:1.6;margin-top:20px}.live-data-notes summary{cursor:pointer;font-weight:700}
@media(max-width:700px){.live-membership-counts{grid-template-columns:repeat(2,minmax(0,1fr))}.live-membership-counts strong{font-size:21px}.membership-live .live-public-breakdown .composition-bars{grid-template-columns:1fr}.live-composition-legend{padding-left:14px;padding-right:14px}.live-composition-legend li{font-size:11px}.live-composition-legend small{display:block;margin-left:0;text-align:right}}
@media(max-width:700px){.membership-live .profile-card-body{padding-left:18px!important;padding-right:18px!important}.membership-live .composition-card .profile-distribution-row{grid-template-columns:96px minmax(0,1fr);gap:8px}.membership-live .composition-card .profile-distribution-row>span{font-size:12px;white-space:normal;line-height:1.3}.membership-live .age-pair>div,.membership-live .handicap-pair>div{grid-template-columns:minmax(0,1fr) 42px;column-gap:8px}.membership-live .age-pair>div::before,.membership-live .handicap-pair>div::before{right:50px}.membership-live .age-pair b,.membership-live .handicap-pair b{min-width:42px;width:42px;font-size:12px}.membership-live .age-pair i,.membership-live .handicap-pair i{min-width:0}}
'''
style += (ROOT/'scripts/public_membership_explorer.css').read_text()
style += (ROOT/'scripts/chart_data_disclosure.css').read_text()
if '/* Reviewed membership composition */' in s:
    s=re.sub(r'/\* Reviewed membership composition \*/.*?(?=</style>)',lambda _:style.strip()+'\n',s,flags=re.S)
else:s=s.replace('</style>',style+'\n</style>',1)
from move_associations_navigation import migrate_associations_navigation
s=migrate_associations_navigation(s)
html.write_text(s)
print('Updated local standalone membership composition and aggregate JSON.')
