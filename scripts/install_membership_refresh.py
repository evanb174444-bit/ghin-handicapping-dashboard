"""Install validated aggregates without rerunning legacy source builders or publishing."""
import json,re,shutil
from pathlib import Path
from audit_membership_refresh import ROOT
from membership_refresh_format import format_composition

FRESH=ROOT/'data/processed/refresh-2026-10-13'
PAGE=ROOT/'Handicapping and GHIN Dashboard.html'

def load(name):return json.loads((FRESH/(name+'.json')).read_text())
def dump(data):return json.dumps(data,separators=(',',':')).replace('</','<\\/')
def constant(text,name,data):
    marker='const '+name+'='
    a=text.index(marker)+len(marker)
    _,length=json.JSONDecoder().raw_decode(text[a:])
    return text[:a]+dump(data)+text[a+length:]

def main():
    validation=load('validation');acquisition=load('acquisition')
    assert acquisition['creationField']=='golfer_creation_date (v_golfer_clubs.golfer_creation_date)'
    assert acquisition['conflictingCreationMonths']==0
    names=load('association_names');scope=load('membership_scope');high=load('high_index_by_scope')
    compositions={s:format_composition(load('composition_review_'+s),{'populations':high[s]},names) for s in ['aga','international','all']}
    outputs={name:load(name) for name in ['membership_associations','membership_clubs','membership_intersections','nh_intersections','international_totals','acquisition']}
    outputs['membership_composition']=dict(meta=dict(mockData=False,extractionDates=['2026-10-13'],scope=scope,historicalTrendsAvailable=False),populations=compositions['aga'])
    outputs['international_composition']={s:compositions[s] for s in ['international','all']}
    outputs['high_index_insight']=dict(scope=scope,populations=high['aga'])
    backup=ROOT/'backups/membership-before-2026-10-13-refresh'
    backup.mkdir(exist_ok=True)
    for p in [PAGE]+[ROOT/'data/processed'/(name+'.json') for name in outputs]+[ROOT/'scripts'/name for name in ['membership_totals_view.js','membership_composition_view.js','home_snapshot_view.js']]:
        if p.exists():
            dest=backup/p.relative_to(ROOT)
            if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    text=PAGE.read_text()
    for name,data in [('MEMBERSHIP_COMPOSITION_DATA',compositions['aga']),('MEMBERSHIP_GEOGRAPHY_COMPOSITION',outputs['international_composition']),('MEMBERSHIP_GEOGRAPHY_COUNTS',outputs['international_totals']),('MEMBERSHIP_INTERSECTIONS',outputs['membership_intersections']),('NH_INTERSECTIONS',outputs['nh_intersections']),('MEMBERSHIP_ASSOCIATION_DATA',outputs['membership_associations']),('MEMBERSHIP_CLUB_DATA',outputs['membership_clubs']),('MEMBERSHIP_SCOPE',scope)]:
        text=constant(text,name,data)
    # Replace the acquisition mock and its population scaling as a single block.
    a=text.index('const ACQUISITION_DATA=');b=text.index('const RECOVERY_DATA=',a)
    text=text[:a]+'const ACQUISITION_DATA='+dump(acquisition)+';\nlet acquisitionMonth=8,acquisitionYear=2026,acquisitionChartType="line",acquisitionVisibleYears=new Set([2026]);\n'+(ROOT/'scripts/membership_acquisition_view.js').read_text()+'\n'+text[b:]
    # Current exports cannot calculate retention or recovery histories.
    for name,label,reason in [('retention','Retention','Renewal cohorts and historical active membership snapshots are needed to calculate retention.'),('recovery','Recovery','Membership reactivation event history is needed to calculate recovery.')]:
        replacement='function '+name+'(){return `<article class="card full"><div class="membership-card-head"><h3>'+label+'</h3></div><div class="live-history-empty"><strong>Historical data needed</strong><p>'+reason+' The October 13 current membership export does not provide this history.</p></div></article>`;}'
        text,n=re.subn(r'^function '+name+r'\(\).*$',lambda _:replacement,text,flags=re.M);assert n==1
    # Correct snapshot dates without relabeling the independent billing series.
    replacements={
        'Membership extracts: September 21–22, 2026':'Membership extract: October 13, 2026',
        'Membership extracts: September 21–25, 2026':'Membership extract: October 13, 2026',
        'Membership snapshot: September 21–25, 2026':'Membership extract: October 13, 2026',
        'All Associations · Sept 21–25, 2026':'All Associations · October 13, 2026',
        'The September 21–22, 2026 exports provide':'The October 13, 2026 export provides',
        "insights?'September 21–22, 2026':membershipScopeDate()":"insights?'October 13, 2026':membershipScopeDate()",
        'The live exports span':'The live extraction date is',
        '; they are not a single-time historical snapshot. One membership present in both exports uses its later Junior classification.':'. The file was exported in batches between 2:33 and 2:48 p.m. Eastern; it is not a certified single-time snapshot.',
        "d.unique?'Thru Sept · '":"d.unique?'Current extract · '",
        'September snapshot vs.':'October 13 extract vs.',
        '2026 uses current extracts; the combined scope spans September 21–25. The final bar compares a September snapshot with the prior annual count.':'2026 uses the October 13 extract. The final bar compares a current extract with the prior annual count.',
        'AGA 2026 counts come from the September 21–22 membership extract. International counts come from the September 25 extract. All Associations combines those extracts,':'AGA and international 2026 counts come from the October 13 membership export. All Associations combines qualifying memberships,',
        "y===2026?'2026 September'":"y===2026?(d.unique?'2026 October 13':'2026 September')",
        'y===2026&&membershipGrowthMonth===8':'y===2026&&membershipGrowthMonth===9',
    }
    for old,new in replacements.items():text=text.replace(old,new)
    # Add acquisition to the existing scope selector; preserve all other navigation.
    text=text.replace('["summary","composition","associations","association-clubs","association-insights"].includes(activeSub)','["summary","composition","associations","association-clubs","association-insights","acquisition"].includes(activeSub)')
    if 'textContent="Historical membership events not supplied"' not in text:
        text=text.replace('const view=activeTop===','if(activeTop==="membership"&&["retention","recovery"].includes(activeSub))document.querySelector(".subtitle").textContent="Historical membership events not supplied";const view=activeTop===',1)
    # Show current membership totals ahead of the independent historical billing chart.
    helper='''function membershipCurrentCounts(){const d=MEMBERSHIP_GEOGRAPHY_COUNTS.scopes[membershipGeography][membershipPopulation];return `<div class="membership-scope-notice"><strong>${membershipScopeLabel()}</strong><span>Active memberships · October 13, 2026</span></div><div class="live-membership-counts">${[['Active Memberships',d.memberships],['Active Unique Golfers',d.uniqueGolfers],['Multi-membership Golfers',d.multiMembershipGolfers],['Additional Memberships',d.additionalMemberships]].map(([label,value],i)=>`<div class="${i===0?'primary':''}"><span>${label}</span><strong>${fmt(value)}</strong></div>`).join('')}</div>`;}\n'''
    if 'function membershipCurrentCounts()' not in text:
        text=text.replace('function membershipSummary(){',helper+'function membershipSummary(){',1)
        text=text.replace('return `<div class="membership-summary">','return `<div class="membership-summary">${membershipCurrentCounts()}',1)
    for name,data in outputs.items():(ROOT/'data/processed'/(name+'.json')).write_text(dump(data)+'\n')
    PAGE.write_text(text)
    for filename in ['membership_totals_view.js','membership_composition_view.js','home_snapshot_view.js']:
        p=ROOT/'scripts'/filename;s=p.read_text()
        for old,new in replacements.items():s=s.replace(old,new)
        if filename=='membership_totals_view.js' and 'function membershipCurrentCounts()' not in s:
            s=s.replace('function membershipSummary(){',helper+'function membershipSummary(){',1).replace('return `<div class="membership-summary">','return `<div class="membership-summary">${membershipCurrentCounts()}',1)
        p.write_text(s)
    print(json.dumps(dict(installed=True,validation=validation,counts=outputs['international_totals']['scopes']),indent=2))

if __name__=='__main__':main()
