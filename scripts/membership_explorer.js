let membershipExplorerFilters={},membershipExplorerGroup='membershipType',membershipExplorerMeasure='memberships';
function membershipFilterValues(key){const value=membershipExplorerFilters[key];return value==null?[]:Array.isArray(value)?value:[value];}
const membershipExplorerDimensions={membershipType:'Membership Type',association:'Association',access:'Public / Private',clubGroup:'Club Group',clubType:'Club Type',gender:'Gender',age:'Age',handicap:'Handicap Index',club:'Club'};
function membershipExplorerLabel(key,value){
 const data=MEMBERSHIP_INTERSECTIONS;
 if(key==='club'){const club=data.clubs[Number(value)];return club.name+' — '+club.associationName;}
 if(key==='association')return data.clubs.find(c=>c.association===value)?.associationName||value;
 return key==='clubGroup'?clubGroupLabel(value):value;
}
function membershipExplorerValues(row){
 const data=MEMBERSHIP_INTERSECTIONS,club=data.clubs[row[0]];
 return {club:String(row[0]),association:club.association,access:club.access,clubGroup:club.clubGroup,clubType:club.type,gender:data.genders[row[1]],age:data.ages[row[2]],membershipType:data.populations[row[3]],handicap:data.handicaps[row[4]]};
}
let membershipExplorerOptionsCache;
function membershipExplorerOptions(){
 if(membershipExplorerOptionsCache)return membershipExplorerOptionsCache;
 const sets=Object.fromEntries(Object.keys(membershipExplorerDimensions).map(k=>[k,new Set()]));
 MEMBERSHIP_INTERSECTIONS.cells.forEach(row=>{for(const [key,value] of Object.entries(membershipExplorerValues(row)))sets[key].add(value);});
 const associationNames=new Map(MEMBERSHIP_INTERSECTIONS.clubs.map(c=>[c.association,c.associationName]));
 sets.age.add('Known age');
 return membershipExplorerOptionsCache=Object.fromEntries(Object.entries(sets).map(([key,set])=>[key,[...set].map(value=>({value,label:key==='association'?associationNames.get(value):membershipExplorerLabel(key,value)})).sort((a,b)=>a.label.localeCompare(b.label))]));
}
function membershipIndexSummary(hist){
 const n=[...hist.values()].reduce((a,b)=>a+b,0);if(!n)return {n:0,mean:null,median:null};
 let sum=0,cumulative=0,lo=null,hi=null;const left=Math.floor((n-1)/2),right=Math.floor(n/2);
 for(const [value,count] of [...hist].sort((a,b)=>a[0]-b[0])){sum+=value*count;cumulative+=count;if(lo===null&&cumulative>left)lo=value;if(hi===null&&cumulative>right)hi=value;}
 return {n,mean:sum/n/10,median:(lo+hi)/20};
}
function membershipIndexFormat(value){return value==null?'—':value<0?'+'+Math.abs(value).toFixed(1):value.toFixed(1);}
function membershipIndexStats(matched,cellGroups,groups){
 if(!MEMBERSHIP_INDEX_STATS)return null;
 const total=new Map(),byGroup=new Map();
 const add=(hist,hi,n)=>hist.set(hi,(hist.get(hi)||0)+n);
 for(const [cells,hi,n] of MEMBERSHIP_INDEX_STATS.patterns){
  const seen=new Set();for(const i of cells)if(matched[i])seen.add(cellGroups[i]);if(!seen.size)continue;
  add(total,hi,n);for(const key of seen){if(!byGroup.has(key))byGroup.set(key,new Map());add(byGroup.get(key),hi,n);}
 }
 for(const [key,group] of groups)group.indexStats=membershipIndexSummary(byGroup.get(key)||new Map());
 return membershipIndexSummary(total);
}
function membershipExplorerResult(selectedFilters=membershipExplorerFilters,selectedPopulation=membershipPopulation,selectedGroup=membershipExplorerGroup){
 const data=MEMBERSHIP_INTERSECTIONS,groups=new Map(),matched=new Uint8Array(data.cells.length),cellGroups=new Array(data.cells.length),nhCells=new Uint8Array(data.cells.length);
 const population=selectedPopulation==='all'?null:selectedPopulation==='regular'?'Regular':'Junior';
 let total=0,nh=0;
 const filters=Object.entries(selectedFilters).map(([key,value])=>[key,Array.isArray(value)?value:[value]]);
 data.cells.forEach((row,i)=>{
  const values=membershipExplorerValues(row);
  if(population&&values.membershipType!==population)return;
  if(filters.some(([key,choices])=>!choices.some(value=>key==='age'&&value==='Known age'?values.age!=='Unknown / invalid':values[key]===value)))return;
  matched[i]=1;const n=row[5],noIndex=values.handicap==='No Index'?n:0;
  total+=n;nh+=noIndex;
  const key=values[selectedGroup],group=groups.get(key)||{key,total:0,nh:0,unique:0,nhUnique:0};group.total+=n;group.nh+=noIndex;groups.set(key,group);cellGroups[i]=key;nhCells[i]=noIndex>0?1:0;
 });
 let unique=0,nhUnique=0;
 for(const [cells,count] of data.golferPatterns){
  const seen=new Set(),seenNH=new Set();
  for(const i of cells){if(!matched[i])continue;seen.add(cellGroups[i]);if(nhCells[i])seenNH.add(cellGroups[i]);}
  if(seen.size)unique+=count;if(seenNH.size)nhUnique+=count;
  for(const key of seen)groups.get(key).unique+=count;
  for(const key of seenNH)groups.get(key).nhUnique+=count;
 }
 const indexStats=membershipIndexStats(matched,cellGroups,groups);
 const metric=membershipExplorerMeasure==='golfers'?'unique':'total';
 return {matched,total,nh,unique,nhUnique,indexStats,additional:total-unique,groups:[...groups.values()].sort((a,b)=>b[metric]-a[metric]||String(a.key).localeCompare(String(b.key)))};
}
function membershipExplorer(){
 if(membershipCompareState)return membershipCompareView();
 const result=membershipExplorerResult(),isUnique=membershipExplorerMeasure==='golfers',metric=isUnique?'unique':'total',nhMetric=isUnique?'nhUnique':'nh',unit=isUnique?'unique golfers':'memberships';
 const keys=Object.keys(membershipExplorerDimensions);
 queueMicrotask(populateMembershipExplorerValues);
 return `<article class="composition-card membership-explorer"><div class="nh-workspace"><div class="mc-heading"><strong>Membership Explorer</strong><button type="button" data-mc-open>Compare segments</button></div><div class="me-filter-panel"><div class="nh-filter-add me-compact-toolbar"><label for="meFilterDimension" class="me-filter-by">Select filters</label><select id="meFilterDimension"><option value="" disabled selected>Select a Filter</option>${keys.map(key=>`<option value="${key}">${membershipExplorerDimensions[key]}</option>`).join('')}</select><select id="meFilterValue" aria-label="Filter value" disabled><option value="" disabled selected>Select a Value</option></select><button type="button" data-me-add disabled>+ Add</button></div>
 ${Object.keys(membershipExplorerFilters).length?`<div class="nh-filter-chips">${Object.keys(membershipExplorerFilters).map(key=>`<div class="me-filter-group" role="group" aria-label="${esc(membershipExplorerDimensions[key])}: match any selected value"><span class="me-filter-group-label">${esc(membershipExplorerDimensions[key])}:</span>${membershipFilterValues(key).map(value=>`<button type="button" data-me-remove="${key}" data-me-value="${esc(value)}" aria-label="Remove ${esc(membershipExplorerDimensions[key])}: ${esc(membershipExplorerLabel(key,value))}"><strong>${esc(membershipExplorerLabel(key,value))}</strong> ×</button>`).join('<span class="me-filter-operator">OR</span>')}</div>`).join('<span class="me-filter-operator me-filter-and">AND</span>')}<button type="button" class="me-clear-inline" data-me-clear>Clear all</button></div>`:''}
 ${membershipPopulation==='all'&&membershipFilterValues('handicap').length===1&&membershipFilterValues('handicap')[0]==='30.1+'&&Object.keys(membershipExplorerFilters).length===1?`<p class="me-finding">Women represent <strong>${pct(MEMBERSHIP_COMPOSITION_DATA.all.highIndexInsight.femaleShareAbove30)}</strong> of unique golfers in this selection (${fmt(MEMBERSHIP_COMPOSITION_DATA.all.highIndexInsight.femaleGolfersAbove30)} of ${fmt(MEMBERSHIP_COMPOSITION_DATA.all.highIndexInsight.golfersAbove30)}). The table below follows the selected counting measure.</p>`:''}</div>
 <div class="nh-filter-results" aria-live="polite"><div><span>Total Memberships</span><strong>${fmt(result.total)}</strong></div><div><span>Unique golfers</span><strong>${fmt(result.unique)}</strong></div><div><span>Memberships beyond the first</span><strong>${fmt(result.additional)}</strong></div><div><span>No Handicap rate</span><strong>${pct(result[metric]?result[nhMetric]/result[metric]:0)}</strong><small>${fmt(result[nhMetric])} NH ${unit}</small></div></div>
 <div class="me-index-kpis" aria-live="polite"><div><span>Average Handicap Index</span><strong data-me-average>${result.indexStats?membershipIndexFormat(result.indexStats.mean):(membershipIndexLoadError?'Unavailable':'Loading…')}</strong><small>${result.indexStats?fmt(result.indexStats.n)+' unique golfers with a valid Index':''}</small></div><div><span>Median Handicap Index</span><strong data-me-median>${result.indexStats?membershipIndexFormat(result.indexStats.median):(membershipIndexLoadError?'Unavailable':'Loading…')}</strong><small>Middle Index among the same golfers</small></div></div>
 <p class="live-source-note">Index statistics always count each golfer once, regardless of the counting toggle. NH and Unknown are excluded; plus handicaps count as negative values. October 13, 2026 snapshot.</p>
 <div class="nh-results-toolbar"><label>Group results by<select id="meGroupBy">${Object.entries(membershipExplorerDimensions).map(([key,label])=>`<option value="${key}" ${key===membershipExplorerGroup?'selected':''}>${label}</option>`).join('')}</select></label><div class="me-count-controls"><div class="me-count-control-row"><span class="me-count-label" id="meCountLabel">Count by</span><div class="me-measure-toggle" role="group" aria-labelledby="meCountLabel">${[['memberships','Memberships'],['golfers','Unique Golfers']].map(([key,label])=>`<button type="button" data-me-measure="${key}" aria-pressed="${membershipExplorerMeasure===key}">${label}</button>`).join('')}</div></div><span class="me-result-caption">${fmt(result.groups.length)} results · Ranked by ${unit}</span></div></div>
 <div class="nh-club-scroll"><table class="nh-table"><thead><tr><th scope="col">${esc(membershipExplorerDimensions[membershipExplorerGroup])}</th><th scope="col">${isUnique?'Unique golfers':'Memberships'}</th><th scope="col">Share</th><th scope="col">NH ${unit}</th><th scope="col">NH rate</th><th scope="col">Golfers with Index</th><th scope="col">Average Index</th><th scope="col">Median Index</th></tr></thead><tbody>${result.groups.map(row=>`<tr><th scope="row">${esc(membershipExplorerLabel(membershipExplorerGroup,row.key))}</th><td>${fmt(row[metric])}</td><td>${pct(result[metric]?row[metric]/result[metric]:0)}</td><td>${fmt(row[nhMetric])}</td><td>${pct(row[metric]?row[nhMetric]/row[metric]:0)}</td><td>${row.indexStats?fmt(row.indexStats.n):'—'}</td><td>${membershipIndexFormat(row.indexStats?.mean)}</td><td>${membershipIndexFormat(row.indexStats?.median)}</td></tr>`).join('')}</tbody></table></div>${isUnique?'<p class="live-source-note">Each golfer counts once within each row. Golfers can appear in more than one group, so row counts and shares may sum to more than the overall total or 100%. NH counts golfers with at least one matching No Index membership.</p>':''}${result.total?'':'<p class="public-empty">No memberships match these filters.</p>'}</div></article>`;
}
function populateMembershipExplorerValues(){
 const dim=document.getElementById('meFilterDimension'),value=document.getElementById('meFilterValue');if(!dim||!value)return;
 value.innerHTML='<option value="" disabled selected>Select a Value</option>'+(dim.value?(membershipExplorerOptions()[dim.value]||[]).filter(row=>!membershipFilterValues(dim.value).includes(row.value)).map(row=>`<option value="${esc(row.value)}">${esc(row.label)}</option>`).join(''):'');
 value.disabled=!dim.value||value.options.length===1;
 const canvas=document.createElement('canvas'),context=canvas.getContext('2d');
 for(const select of [dim,value]){const style=getComputedStyle(select);context.font=style.font;const width=Math.ceil(Math.max(...Array.from(select.options,option=>context.measureText(option.text).width)))+56;select.style.width=width+'px';}

 const add=document.querySelector('[data-me-add]');if(add)add.disabled=true;
}

function refreshMembershipExplorer(){const el=document.querySelector('.membership-explorer');if(el){const breakdown=el.querySelector('.mc-breakdown');if(breakdown&&membershipCompareState)membershipCompareState.breakdownOpen=breakdown.open;el.outerHTML=membershipExplorer();}}
document.addEventListener('change',event=>{if(event.target.id==='meFilterDimension')populateMembershipExplorerValues();if(event.target.id==='meFilterValue'){const add=document.querySelector('[data-me-add]');if(add)add.disabled=!event.target.value;}if(event.target.id==='meGroupBy'){membershipExplorerGroup=event.target.value;refreshMembershipExplorer();document.getElementById('meGroupBy')?.focus({preventScroll:true});}});
document.addEventListener('click',event=>{
 const measure=event.target.closest?.('[data-me-measure]');if(measure){membershipExplorerMeasure=measure.dataset.meMeasure;refreshMembershipExplorer();document.querySelector(`[data-me-measure="${membershipExplorerMeasure}"]`)?.focus({preventScroll:true});return;}
 const remove=event.target.closest?.('[data-me-remove]'),add=event.target.closest?.('[data-me-add]'),clear=event.target.closest?.('[data-me-clear]');
 let keepDimension='';
 if(remove){const key=remove.dataset.meRemove,remaining=membershipFilterValues(key).filter(value=>value!==remove.dataset.meValue);if(remaining.length)membershipExplorerFilters[key]=remaining;else delete membershipExplorerFilters[key];}
 else if(clear)membershipExplorerFilters={};
 else if(add){const key=document.getElementById('meFilterDimension').value,value=document.getElementById('meFilterValue').value;if(!key||!value)return;membershipExplorerFilters[key]=[...new Set([...membershipFilterValues(key),value])];keepDimension=key;}
 else return;
 refreshMembershipExplorer();
 if(keepDimension)queueMicrotask(()=>{document.getElementById('meFilterDimension').value=keepDimension;populateMembershipExplorerValues();document.getElementById('meFilterValue').focus({preventScroll:true});});
});

let membershipInsightPosition=0, membershipInsightsExpanded=false;
let membershipInsightTotalsCache;
function membershipInsightTotals(){
 if(membershipInsightTotalsCache)return membershipInsightTotalsCache;
 const keys=['association','club','clubType','clubGroup','handicap'],maps=Object.fromEntries(keys.map(k=>[k,new Map()]));
 for(const row of MEMBERSHIP_INTERSECTIONS.cells){const values=membershipExplorerValues(row);for(const key of keys)maps[key].set(values[key],(maps[key].get(values[key])||0)+row[5]);}
 return membershipInsightTotalsCache=Object.fromEntries(keys.map(key=>[key,[...maps[key]].sort((a,b)=>b[1]-a[1])]));
}
function membershipInsightSets(){
 const all=MEMBERSHIP_COMPOSITION_DATA.all,junior=MEMBERSHIP_COMPOSITION_DATA.junior,regular=MEMBERSHIP_COMPOSITION_DATA.regular;
 const nhCount=d=>d.handicap.allCounts[d.handicap.bands.indexOf('No Index')];
 const nh=nhCount(all),jnh=nhCount(junior),rnh=nhCount(regular),total=all.counts.memberships;
 const ages=Object.fromEntries(all.age.bands.map((band,i)=>[band,all.age.femaleCounts[i]]));
 const known=all.age.femaleCounts.reduce((n,v)=>n+v,0)-(ages['Unknown / invalid']||0);
 const young=ages['Under 18']/known,older=(ages['55–64']+ages['65+'])/known;
 const hi=all.highIndexInsight,publicTotal=all.access.find(r=>r[0]==='Public')[1],female=all.gender.find(r=>r[0]==='Female')[1];
 const totals=membershipInsightTotals(),topAssociations=totals.association.slice(0,5),associationSum=topAssociations.reduce((n,r)=>n+r[1],0),topClub=totals.club[0],topType=totals.clubType[0],topGroup=totals.clubGroup[0],topHI=totals.handicap.find(r=>!['No Index','Unknown'].includes(r[0]));
 const bar=(label,value,share,color='#315f8b')=>({label,value,share,color});
 return {
 'Public / Private':[
 {title:'Public clubs account for '+pct(publicTotal/total)+' of memberships',value:fmt(publicTotal),caption:'Public memberships',note:'Share of all U.S. memberships. Unknown access remains separate.',bars:all.access.map(([label,n])=>bar(label,fmt(n),n/total)),filters:{access:'Public'},group:'clubGroup'},
 {title:'Affiliate / WORE is the largest public membership group',value:pct(all.publicBreakdown.find(r=>r[0]==='Affiliate / WORE')[1]/publicTotal),caption:'of public memberships',note:'Club groups use the reviewed classifications; GC Clubs are separate.',bars:[...all.publicBreakdown].sort((a,b)=>b[1]-a[1]).slice(0,3).map(([label,n])=>bar(clubGroupLabel(label),fmt(n),n/publicTotal)),filters:{access:'Public'},group:'clubGroup'}],
 'Membership Type':[
 {title:'Regular memberships outnumber Junior memberships by '+(regular.counts.memberships/junior.counts.memberships).toFixed(1)+' to 1',value:pct(regular.counts.memberships/total),caption:'of all memberships are Regular',note:fmt(regular.counts.memberships)+' Regular · '+fmt(junior.counts.memberships)+' Junior. Unclassified memberships remain in the total.',filters:{},group:'membershipType'}],
 'Association':[
 {title:'Five associations account for '+pct(associationSum/total)+' of all memberships',value:fmt(associationSum),caption:'Memberships across the five largest associations',note:topAssociations.map(([id])=>membershipExplorerLabel('association',id)).join(' · ')+'. Memberships, not unique golfers.',filters:{},group:'association'}],
 'Club Group':[
 {title:clubGroupLabel(topGroup[0])+' is the largest single club group',value:pct(topGroup[1]/total),caption:'of all memberships · '+fmt(topGroup[1])+' memberships',note:'Public memberships are split across several groups; GC Clubs are shown separately.',filters:{},group:'clubGroup'}],
 'Club Type':[
 {title:topType[0]+' accounts for '+pct(topType[1]/total)+' of memberships',value:fmt(topType[1]),caption:'Memberships in '+topType[0]+' clubs',note:'Club type includes GC Clubs within their source type. Type 1 indicates green-grass clubs, not public or private access.',filters:{},group:'clubType'}],
 'Handicap Index':[
 {title:topHI[0]+' is the most common Handicap Index band',value:fmt(topHI[1]),caption:pct(topHI[1]/total)+' of all memberships',note:'Membership-weighted distribution. No Index and Unknown remain in the overall denominator.',filters:{},group:'handicap'}],
 'Club':[
 {title:MEMBERSHIP_INTERSECTIONS.clubs[Number(topClub[0])].name+' has the largest membership count',value:fmt(topClub[1]),caption:pct(topClub[1]/total)+' of all memberships in one club',note:MEMBERSHIP_INTERSECTIONS.clubs[Number(topClub[0])].associationName+'. This is a club registration count, not a measure of facility size or rounds played.',filters:{},group:'club'}],
 'No Handicap':[
 {title:'Juniors account for '+pct(jnh/nh)+' of memberships without an Index',value:fmt(nh),caption:'NH memberships · '+pct(nh/total)+' of all memberships',note:'Composition of NH memberships. Rounded shares may not sum to 100%.',stack:true,bars:[bar('Junior',fmt(jnh),jnh/nh,'#d87900'),bar('Regular',fmt(rnh),rnh/nh),bar('Unclassified',fmt(nh-jnh-rnh),(nh-jnh-rnh)/nh,'#98a4b5')],filters:{handicap:'No Index'},group:'membershipType'},
 {title:'No Handicap is far more common among Junior memberships',value:pct(jnh/junior.counts.memberships),caption:'of Junior memberships are NH',note:'Each rate uses all memberships of that type as its denominator.',bars:[bar('Junior NH rate',fmt(jnh)+' NH',jnh/junior.counts.memberships,'#d87900'),bar('Regular NH rate',fmt(rnh)+' NH',rnh/regular.counts.memberships)],filters:{handicap:'No Index'},group:'membershipType'}],
 'Gender':[
 {title:'Women represent '+pct(hi.femaleShareAbove30)+' of golfers with an Index above 30',value:pct(hi.femaleShareAbove30),caption:'of unique golfers above 30 are women',note:fmt(hi.femaleGolfersAbove30)+' of '+fmt(hi.golfersAbove30)+' golfers · Each golfer counted once.',bars:[bar('Women',fmt(hi.femaleGolfersAbove30),hi.femaleShareAbove30,'#ce604c')],filters:{handicap:'30.1+'},group:'gender'},
 {title:'Women hold '+pct(female/total)+' of all memberships',value:fmt(female),caption:'Female memberships',note:'Membership counts include multiple club memberships per golfer.',bars:all.gender.map(([label,n])=>bar(label,fmt(n),n/total,label==='Female'?'#ce604c':'#315f8b')),filters:{},group:'gender'}],
 'Age':[
 {title:'Women’s memberships cluster at the age extremes',value:pct(young+older),caption:'of female memberships with known age are under 18 or 55+',note:'Unknown and invalid ages excluded. Memberships, not unique golfers.',bars:[bar('Under 18',fmt(ages['Under 18']),young,'#367f70'),bar('55+',fmt(ages['55–64']+ages['65+']),older,'#367f70')],filters:{gender:'Female',age:'Known age'},group:'age'},
 {title:'Age is missing or invalid for '+pct(all.quality.ageUnknown/total)+' of memberships',value:fmt(all.quality.ageUnknown),caption:'Memberships without a valid age',note:'Valid ages are 0–120. Missing ages limit conclusions about the full membership population.',bars:[bar('Unknown / invalid',fmt(all.quality.ageUnknown),all.quality.ageUnknown/total,'#98a4b5')],filters:{age:'Unknown / invalid'},group:'membershipType'}]
 };
}
function membershipInsightDeck(){return Object.entries(membershipInsightSets()).flatMap(([topic,cards])=>cards.map(card=>({...card,topic})));}
function membershipInsightCallouts(){
 const cards=membershipInsightDeck(),topic=cards[membershipInsightPosition].topic;
 const visible=Array.from({length:3},(_,offset)=>{const index=(membershipInsightPosition+offset)%cards.length;return {...cards[index],index};});
 return `<section class="membership-insights" aria-label="Membership key insights"><button type="button" class="insight-accordion-toggle" data-toggle-insights aria-expanded="${membershipInsightsExpanded}" aria-controls="insightAccordionContent"><span class="insight-caret" aria-hidden="true">${membershipInsightsExpanded?'▾':'▸'}</span><svg class="insight-bulb" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M9 18h6M10 21h4M9 15c0-1.5-3-2.5-3-6a6 6 0 0 1 12 0c0 3.5-3 4.5-3 6v1H9z"/></svg>Insights</button><div id="insightAccordionContent" class="insight-accordion-content" ${membershipInsightsExpanded?'':'hidden'}><div class="membership-insights-heading"><label class="insight-topic-select"><span class="insight-category-heading">Insight Category:</span><select id="insightTopicSelect">${Object.keys(membershipInsightSets()).map(label=>`<option value="${esc(label)}" ${label===topic?'selected':''}>${esc(label)}</option>`).join('')}</select></label><button type="button" class="category-definitions-link" data-category-definitions aria-haspopup="dialog">Category Definitions</button></div>
 <div id="membershipInsightCarousel" class="insight-tile-carousel" ${membershipInsightsExpanded?'':'hidden'} role="region" aria-roledescription="carousel" aria-label="Membership insights">
 <div class="insight-tile-window">${visible.map(card=>`<article class="insight-summary-tile" role="group" aria-roledescription="slide" aria-label="${card.index+1} of ${cards.length}" data-insight-index="${card.index}"><span>${card.topic}</span><h4>${esc(card.title)}</h4><strong>${card.value}</strong><p>${esc(card.caption)}</p><small>${esc(card.note)}</small><button type="button" data-me-insight="${card.index}">Explore this →</button></article>`).join('')}</div>
 <div class="insight-deck-controls"><button class="insight-side-arrow" type="button" data-insight-step="-1" aria-label="Previous insight">←</button><div class="insight-dots">${cards.map((card,index)=>`<button type="button" data-insight-position="${index}" aria-label="Start at insight ${index+1}: ${esc(card.title)}" aria-current="${index===membershipInsightPosition?'true':'false'}"></button>`).join('')}</div><button class="insight-side-arrow" type="button" data-insight-step="1" aria-label="Next insight">→</button></div>
 </div></div></section>`;
}
function refreshInsightCarousel(){const el=document.querySelector('.membership-insights');if(el)el.outerHTML=membershipInsightCallouts();}
document.addEventListener('click',event=>{
 const topic=event.target.closest?.('[data-insight-topic]'),step=event.target.closest?.('[data-insight-step]'),dot=event.target.closest?.('[data-insight-position]');
 if(topic||step||dot){
  const cards=membershipInsightDeck();
  membershipInsightPosition=dot?Number(dot.dataset.insightPosition):topic?cards.findIndex(c=>c.topic===topic.dataset.insightTopic):(membershipInsightPosition+Number(step.dataset.insightStep)+cards.length)%cards.length;
  const attr=topic?'data-insight-topic':dot?'data-insight-position':'data-insight-step',value=(topic||dot||step).getAttribute(attr);
  refreshInsightCarousel();document.querySelector(`[${attr}="${value}"]`)?.focus({preventScroll:true});return;
 }
 const button=event.target.closest?.('[data-me-insight]');if(!button)return;
 const card=membershipInsightDeck()[Number(button.dataset.meInsight)];if(!card)return;
 membershipExplorerFilters=Object.fromEntries(Object.entries(card.filters).map(([key,value])=>[key,[value]]));membershipExplorerGroup=card.group;membershipPopulation='all';render();
 document.querySelector('.membership-explorer')?.scrollIntoView({behavior:'smooth',block:'start'});
 document.getElementById('meGroupBy')?.focus({preventScroll:true});
});

document.addEventListener('change',event=>{
 if(event.target.id!=='insightTopicSelect')return;
 membershipInsightPosition=membershipInsightDeck().findIndex(card=>card.topic===event.target.value);
 refreshInsightCarousel();document.getElementById('insightTopicSelect')?.focus({preventScroll:true});
});

function openCategoryDefinitions(){
 let dialog=document.getElementById('categoryDefinitionsDialog');
 if(!dialog){
  dialog=document.createElement('dialog');dialog.id='categoryDefinitionsDialog';dialog.className='category-definitions-dialog';dialog.setAttribute('aria-labelledby','categoryDefinitionsTitle');
  const definitions=[
  [
    "Membership Type",
    "The membership classification: Regular, Junior, or Unclassified. Junior is never inferred from the golfer’s age. Regular memberships generally infer an adult who has a paid membership."
  ],
  [
    "Association",
    "The golf association attached to the membership’s club. U.S. scope includes Golf PR and excludes Guam. It does not mean the golfer resides in the U.S."
  ],
  [
    "Public / Private",
    "The club’s access classification. Type 1 clubs may be Public or Private. Type 2, Type 3, Affiliate/WORE and the GC club list are Public."
  ],
  [
    "Club Group",
    "This list includes Private Clubs, Public Green Grass Clubs, Affiliate / WORE, GC Clubs, Semi-Private, Other Type 3 (Virtual/eClubs), Resort, Municipal, Military, or Unknown Access. Each membership belongs to one group. GC Clubs take precedence and are shown separately. Affiliate/WORE (aka \"without real estate\") may include more than one club type; it is not synonymous with Type 2."
  ],
  [
    "Club Type",
    "Type 1/2/3 classification. Type 1 means a green-grass club with real estate and can be public or private. Type 2 means an affiliate or independent club without green-grass facilities. Type 3 covers virtual clubs/eClubs. GC Clubs retain their source type here, even though they are separated in Club Group."
  ],
  [
    "Gender",
    "Male, Female, or Unknown. Unknown values remain in overall totals."
  ],
  [
    "Age",
    "Grouped as Under 18, 18–24, 25–34, 35–44, 45–54, 55–64, or 65+. Missing or invalid values are separate. Known age includes valid ages from 0–120 and excludes Unknown / invalid."
  ],
  [
    "Handicap Index",
    "Current indexes as calculated by GHIN. NH means No Index. Unknown is missing or unusable Index data and is kept separate from NH."
  ],
  [
    "Club",
    "The individual club attached to the membership. Counts measure club registrations, not facility size or rounds played. Club names are paired with association names to distinguish similarly named clubs."
  ],
  [
    "No Handicap (NH)",
    "A membership explicitly marked NH (No Index). NH rate is NH memberships divided by all memberships in the same selection or row. Share of NH uses the total NH membership pool instead."
  ]
];
  dialog.innerHTML=`<header><div><h2 id="categoryDefinitionsTitle">Category Definitions</h2><p>How to read the Membership Explorer</p></div><button type="button" data-close-definitions aria-label="Close category definitions">×</button></header><div class="category-definitions-content"><aside><strong>Memberships and unique golfers</strong><p>A membership is one golfer’s registration with one club. A golfer may have multiple memberships. Unique golfers counts each golfer once within the combined selection. Memberships beyond the first equals total memberships minus unique golfers.</p><p>Multiple values within one filter match any selected value (OR). Different filters combine as an intersection (AND). The counting toggle switches table counts, ranking, shares and NH rates between memberships and unique golfers. Unique-golfer shares use all matching unique golfers; a golfer can appear in multiple groups.</p></aside><dl>${definitions.map(([name,definition])=>`<div><dt>${name}</dt><dd>${definition}</dd></div>`).join('')}</dl></div>`;
  document.body.appendChild(dialog);
  dialog.querySelector('[data-close-definitions]').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();});
 }
 dialog.showModal();
}
document.addEventListener('click',event=>{if(event.target.closest?.('[data-category-definitions]'))openCategoryDefinitions();});

document.addEventListener('click',event=>{if(!event.target.closest?.('[data-toggle-insights]'))return;membershipInsightsExpanded=!membershipInsightsExpanded;refreshInsightCarousel();document.querySelector('[data-toggle-insights]')?.focus({preventScroll:true});});

let membershipCompareState=null;
const membershipCompareMetrics={unique:'Unique golfers',mean:'Average Index',median:'Median Index',nhRate:'No Index %',valid:'Golfers with Index'};
function membershipCompareValue(r,key){if(!r)return null;if(key==='unique')return r.unique;if(key==='nhRate')return r.unique?r.nhUnique/r.unique:null;if(key==='valid')return r.indexStats?.n??null;return r.indexStats?.[key]??null;}
function membershipCompareFormat(v,key){if(v==null)return '—';return key==='nhRate'?pct(v):['mean','median'].includes(key)?membershipIndexFormat(v):fmt(v);}
function membershipCompareDifference(a,b,key){if(a==null||b==null)return '—';const d=b-a,sign=d>0?'+':d<0?'−':'';return sign+(key==='nhRate'?(Math.abs(d)*100).toFixed(1)+' pp':['mean','median'].includes(key)?Math.abs(d).toFixed(1):fmt(Math.abs(d)));}
function membershipCompareView(){
 const state=membershipCompareState,results=state.segments.map(s=>membershipExplorerResult(s.filters,s.population,state.group));
 let overlap=0;for(const [cells,n] of MEMBERSHIP_INTERSECTIONS.golferPatterns)if(cells.some(i=>results[0].matched[i])&&cells.some(i=>results[1].matched[i]))overlap+=n;
 const choices=Object.entries(membershipExplorerDimensions).map(([k,v])=>`<option value="${k}">${esc(v)}</option>`).join('');
 const panels=state.segments.map((segment,i)=>`<section class="mc-segment" data-mc-panel="${i}" aria-label="Segment ${i?'B':'A'} filters"><h3>Segment ${i?'B':'A'}</h3><label>Members<select data-mc-pop="${i}">${[['all','All Members'],['regular','Regular Members'],['junior','Junior Members']].map(([k,v])=>`<option value="${k}" ${segment.population===k?'selected':''}>${v}</option>`).join('')}</select></label><div class="mc-filter-row"><select data-mc-dimension="${i}" aria-label="Segment ${i?'B':'A'} filter"><option value="">Select a Filter</option>${choices}</select><select data-mc-value="${i}" aria-label="Segment ${i?'B':'A'} value" disabled><option value="">Select a Value</option></select><button type="button" data-mc-add="${i}" disabled>+ Add</button></div><div class="mc-chips">${Object.entries(segment.filters).map(([key,values])=>`<div><strong>${esc(membershipExplorerDimensions[key])}:</strong> ${values.map(value=>`<button type="button" data-mc-remove="${i}" data-key="${key}" data-value="${esc(value)}" aria-label="Remove ${esc(membershipExplorerLabel(key,value))} from Segment ${i?'B':'A'}">${esc(membershipExplorerLabel(key,value))} ×</button>`).join(' <small>OR</small> ')}</div>`).join('')||'<span>No additional filters</span>'}</div><button type="button" data-mc-clear="${i}">Clear filters</button></section>`).join('');
 const rows=Object.entries(membershipCompareMetrics).map(([key,label])=>{const a=membershipCompareValue(results[0],key),b=membershipCompareValue(results[1],key);return `<tr><th scope="row">${label}</th><td>${membershipCompareFormat(a,key)}</td><td>${membershipCompareFormat(b,key)}</td><td>${membershipCompareDifference(a,b,key)}</td></tr>`;}).join('');
 const maps=results.map(r=>new Map(r.groups.map(g=>[g.key,g]))),keys=[...new Set([...maps[0].keys(),...maps[1].keys()])].sort((a,b)=>((maps[0].get(b)?.unique||0)+(maps[1].get(b)?.unique||0))-((maps[0].get(a)?.unique||0)+(maps[1].get(a)?.unique||0))||String(a).localeCompare(String(b)));
 const groupRows=keys.map(key=>{const values=maps.map(m=>{const r=m.get(key);return !r&&['unique','valid'].includes(state.metric)?0:membershipCompareValue(r,state.metric);});return `<tr><th scope="row">${esc(membershipExplorerLabel(state.group,key))}</th><td>${membershipCompareFormat(values[0],state.metric)}</td><td>${membershipCompareFormat(values[1],state.metric)}</td><td>${membershipCompareDifference(values[0],values[1],state.metric)}</td></tr>`;}).join('');
 return `<article class="composition-card membership-explorer mc-workspace"><div class="nh-workspace"><div class="mc-heading"><div><h2>Compare segments</h2><span>Unique golfers · October 13, 2026</span></div><button type="button" data-mc-close>Back to Explorer</button></div><div class="mc-panels">${panels}</div><div class="mc-actions"><button type="button" data-mc-copy>Copy A to B</button><button type="button" data-mc-swap>Swap A and B</button></div><div class="nh-club-scroll"><table class="nh-table mc-table"><caption>Segment comparison</caption><thead><tr><th scope="col">Metric</th><th scope="col">Segment A</th><th scope="col">Segment B</th><th scope="col">Difference (B − A)</th></tr></thead><tbody>${rows}</tbody></table></div><p class="live-source-note">${fmt(overlap)} golfers belong to both segments and count once in each. Index statistics exclude NH and Unknown; plus handicaps use negative values. Rate differences are percentage points (pp).</p>${!MEMBERSHIP_INDEX_STATS?'<p role="status">'+(membershipIndexLoadError?'Index statistics are unavailable.':'Loading Index statistics…')+'</p>':''}<details class="mc-breakdown" ${state.breakdownOpen?'open':''}><summary>Break down this comparison</summary><div class="nh-results-toolbar"><label>Group results by<select data-mc-group>${Object.entries(membershipExplorerDimensions).map(([k,v])=>`<option value="${k}" ${state.group===k?'selected':''}>${v}</option>`).join('')}</select></label><label>Compare metric<select data-mc-metric>${Object.entries(membershipCompareMetrics).map(([k,v])=>`<option value="${k}" ${state.metric===k?'selected':''}>${v}</option>`).join('')}</select></label></div><div class="nh-club-scroll"><table class="nh-table mc-table"><caption>${esc(membershipCompareMetrics[state.metric])} by ${esc(membershipExplorerDimensions[state.group])}</caption><thead><tr><th scope="col">${esc(membershipExplorerDimensions[state.group])}</th><th scope="col">Segment A</th><th scope="col">Segment B</th><th scope="col">Difference (B − A)</th></tr></thead><tbody>${groupRows||'<tr><td colspan="4">No golfers match either segment.</td></tr>'}</tbody></table></div><p class="live-source-note">A golfer may appear in more than one group. Filters within a category use OR; different categories must match the same membership. NH counts golfers with at least one matching No Index membership.</p></details></div></article>`;
}
document.addEventListener('change',event=>{
 const el=event.target;if(!membershipCompareState)return;
 if(el.hasAttribute('data-mc-dimension')){const i=el.dataset.mcDimension,value=document.querySelector(`[data-mc-value="${i}"]`);value.innerHTML='<option value="">Select a Value</option>'+(membershipExplorerOptions()[el.value]||[]).filter(r=>!membershipCompareState.segments[i].filters[el.value]?.includes(r.value)).map(r=>`<option value="${esc(r.value)}">${esc(r.label)}</option>`).join('');value.disabled=!el.value;document.querySelector(`[data-mc-add="${i}"]`).disabled=true;return;}
 if(el.hasAttribute('data-mc-value')){document.querySelector(`[data-mc-add="${el.dataset.mcValue}"]`).disabled=!el.value;return;}
 if(el.hasAttribute('data-mc-pop'))membershipCompareState.segments[el.dataset.mcPop].population=el.value;
 else if(el.hasAttribute('data-mc-group'))membershipCompareState.group=el.value;
 else if(el.hasAttribute('data-mc-metric'))membershipCompareState.metric=el.value;
 else return;
 refreshMembershipExplorer();
});
document.addEventListener('click',event=>{
 const el=event.target.closest('button');if(!el)return;
 const clone=x=>JSON.parse(JSON.stringify(x));
 if(el.hasAttribute('data-mc-open')){const segment={filters:Object.fromEntries(Object.keys(membershipExplorerFilters).map(k=>[k,[...membershipFilterValues(k)]])),population:membershipPopulation};membershipCompareState={segments:[clone(segment),clone(segment)],group:membershipExplorerGroup,metric:'mean'};}
 else if(!membershipCompareState)return;
 else if(el.hasAttribute('data-mc-close'))membershipCompareState=null;
 else if(el.hasAttribute('data-mc-copy'))membershipCompareState.segments[1]=clone(membershipCompareState.segments[0]);
 else if(el.hasAttribute('data-mc-swap'))membershipCompareState.segments.reverse();
 else if(el.hasAttribute('data-mc-clear'))membershipCompareState.segments[el.dataset.mcClear].filters={};
 else if(el.hasAttribute('data-mc-add')){const i=el.dataset.mcAdd,key=document.querySelector(`[data-mc-dimension="${i}"]`).value,value=document.querySelector(`[data-mc-value="${i}"]`).value;if(!key||!value)return;const f=membershipCompareState.segments[i].filters;f[key]=[...new Set([...(f[key]||[]),value])];}
 else if(el.hasAttribute('data-mc-remove')){const f=membershipCompareState.segments[el.dataset.mcRemove].filters,key=el.dataset.key;f[key]=f[key].filter(v=>v!==el.dataset.value);if(!f[key].length)delete f[key];}
 else return;
 refreshMembershipExplorer();
});

// Keep the breakdown open while its controls refresh the comparison.
document.addEventListener('toggle',event=>{
 if(event.target.matches?.('.mc-breakdown')&&event.target.isConnected&&membershipCompareState)membershipCompareState.breakdownOpen=event.target.open;
},true);
