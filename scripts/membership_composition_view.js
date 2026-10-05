let membershipInsightSection='membership';
try {const saved=localStorage.getItem('ghin_insight_section');if(['membership','clubs','age'].includes(saved))membershipInsightSection=saved;} catch(e){}
document.addEventListener('click',event=>{
 const button=event.target.closest?.('[data-insight-section]');if(!button)return;
 membershipInsightSection=button.dataset.insightSection;
 try{localStorage.setItem('ghin_insight_section',membershipInsightSection);}catch(e){}
 render();document.querySelector(`[data-insight-section="${membershipInsightSection}"]`)?.focus({preventScroll:true});
});
function chartDataDisclosure(items,total){
  return `<details class="chart-data-disclosure"><summary><span class="chart-data-show">Show data</span><span class="chart-data-hide">Hide data</span></summary><div class="chart-data-table-wrap"><table><caption>Data breakdown</caption><thead><tr><th scope="col">Category</th><th scope="col">Count</th><th scope="col">Share</th></tr></thead><tbody>${items.map(item=>`<tr ${item.attributes||''}><th scope="row"><i style="background:${item.color}" aria-hidden="true"></i>${esc(item.label)}</th><td>${fmt(item.value)}</td><td>${pct(total?item.value/total:0)}</td></tr>`).join('')}</tbody><tfoot><tr><th scope="row">Total</th><td>${fmt(total)}</td><td>${pct(total?1:0)}</td></tr></tfoot></table></div></details>`;
}
function liveCompositionLegend(items, colors) {
  const total=items.reduce((n,item)=>n+item[1],0);
  return chartDataDisclosure(items.map(([label,value],i)=>({label,value,color:colors[i]})),total);
}
function liveCompositionDonut(title, tone, items, colors) {
  return compositionDonut(title, tone, items, colors)
    .replace('<span>Total</span>', '<span>Memberships</span>')
    .replace('</article>', `${liveCompositionLegend(items, colors)}</article>`);
}
function liveCompositionTrend(title, tone) {
  return `<article class="composition-card ${tone}"><div class="composition-band">${title}</div><div class="live-history-empty"><strong>Historical snapshots needed</strong><p>The September 21–22, 2026 exports provide the current membership composition. Earlier snapshots are needed to show a trend.</p></div></article>`;
}
const clubGroupLabel = name => name === 'Virtual clubs / eClubs' ? 'Other Type 3 (Virtual/eClubs)' : name;
let selectedPublicGroup = 'All Clubs';
let clubGenderView = 'all';
let selectedClubAssociation=null;
let associationClubSort={key:"total",direction:"desc"};
function clubAssociationDetails(){
 const data=MEMBERSHIP_INTERSECTIONS,byAssociation=new Map();
 for(const row of data.cells){
  const club=data.clubs[row[0]],pop=data.populations[row[3]],gender=data.genders[row[1]];
  if(membershipPopulation!=='all'&&pop!==(membershipPopulation==='regular'?'Regular':'Junior'))continue;
  if(selectedPublicGroup!=='All Clubs'&&(selectedPublicGroup==='Public Clubs'?club.access!=='Public':club.clubGroup!==selectedPublicGroup))continue;
  if(clubGenderView==='split'&&!['Male','Female'].includes(gender))continue;
  const clubs=byAssociation.get(club.association)||new Map();
  const entry=clubs.get(club.id)||{...club,total:0,male:0,female:0,regular:0,junior:0,nh:0,knownAge:0,older:0,knownIndex:0,above20:0,types:new Set()};
  entry.total+=row[5];if(gender==='Male')entry.male+=row[5];if(gender==='Female')entry.female+=row[5];
  entry.types.add(club.type||'Unknown');
  if(pop==='Regular')entry.regular+=row[5];if(pop==='Junior')entry.junior+=row[5];
  const age=data.ages[row[2]],hi=data.handicaps[row[4]];
  if(age!=='Unknown / invalid')entry.knownAge+=row[5];if(['55–64','65+'].includes(age))entry.older+=row[5];
  if(hi==='No Index')entry.nh+=row[5];if(!['No Index','Unknown'].includes(hi))entry.knownIndex+=row[5];if(['20.1–30.0','30.1+'].includes(hi))entry.above20+=row[5];
  clubs.set(club.id,entry);byAssociation.set(club.association,clubs);
 }
 return byAssociation;
}
function associationClubPanel(clubs,split){
 if(!selectedClubAssociation)return '';
 const rows=[...(clubs.get(selectedClubAssociation)?.values()||[])];
 const total=rows.reduce((n,r)=>n+r.total,0),male=rows.reduce((n,r)=>n+r.male,0),female=rows.reduce((n,r)=>n+r.female,0);
 const name=rows[0]?.associationName||'Selected association';
 const columns=[['name','Club','text'],['total','Memberships','count'],['share','Share','pct'],['typeLabel','Club Type','text'],['regular','Regular','count'],['junior','Junior','count'],['juniorShare','Junior %','pct'],['femaleShare','Female %','pct'],['nh','NH count','count'],['nhRate','NH rate','pct'],['olderShare','Age 55+ %','pct'],['above20Share','Index >20 %','pct']];
 if(split)columns.splice(3,0,['male','Male','count'],['maleShare','Male share','pct'],['female','Female','count'],['femaleGroupShare','Female share','pct']);
 for(const row of rows)Object.assign(row,{share:total?row.total/total:null,typeLabel:[...row.types].sort().join(' / '),juniorShare:row.junior/row.total,femaleShare:row.female/row.total,nhRate:row.nh/row.total,olderShare:row.knownAge?row.older/row.knownAge:null,above20Share:row.knownIndex?row.above20/row.knownIndex:null,maleShare:male?row.male/male:null,femaleGroupShare:female?row.female/female:null});
 const sort=associationClubSort;rows.sort((a,b)=>{const x=a[sort.key],y=b[sort.key];if(x==null||y==null)return x==null?(y==null?a.name.localeCompare(b.name):1):-1;const delta=typeof x==='string'?x.localeCompare(y,undefined,{numeric:true}):x-y;return delta*(sort.direction==='asc'?1:-1)||a.name.localeCompare(b.name);});
 return `<section class="association-club-panel" id="association-club-panel" tabindex="-1" aria-label="Clubs in selected association"><header><div><h3>${esc(name)} · ${esc(clubGroupLabel(selectedPublicGroup))}</h3><p>${fmt(rows.length)} clubs · ${fmt(total)} memberships${split?' · Male/Female comparison':''}</p></div><button type="button" data-close-club-panel aria-label="Close club list">×</button></header><div class="association-club-scroll"><table class="live-affiliate-table club-detail-table"><thead><tr>${columns.map(([key,label])=>`<th scope="col" aria-sort="${sort.key===key?(sort.direction==='asc'?'ascending':'descending'):'none'}"><button type="button" data-club-sort="${key}">${label} <span aria-hidden="true">${sort.key===key?(sort.direction==='asc'?'↑':'↓'):'↕'}</span></button></th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr data-club-id="${esc(row.id)}">${columns.map(([key,label,kind])=>`<td data-column="${key}" data-sort-value="${esc(row[key]==null?'':String(row[key]))}">${row[key]==null?'—':kind==='text'?esc(row[key]):kind==='pct'?pct(row[key]):fmt(row[key])}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="live-profile-note">Share uses memberships in this association and selected club group. Junior %, Female %, and NH rate use each club’s matching memberships. Age 55+ % excludes unknown/invalid ages. Index &gt;20 % excludes NH and unknown indexes. — means no eligible memberships. Regular and Junior counts exclude Unclassified memberships.${split?' Male/Female shares use the respective gender totals across these clubs.':''}</p></section>`;
}
document.addEventListener('click',event=>{
 const button=event.target.closest?.('[data-club-sort]');if(!button)return;
 const key=button.dataset.clubSort;associationClubSort={key,direction:associationClubSort.key===key?(associationClubSort.direction==='asc'?'desc':'asc'):['name','typeLabel'].includes(key)?'asc':'desc'};
 const scroll=document.querySelector('.association-club-scroll'),left=scroll?.scrollLeft||0;
 document.getElementById('association-club-panel').outerHTML=associationClubPanel(clubAssociationDetails(),clubGenderView==='split');
 document.querySelector('.association-club-scroll').scrollLeft=left;
 document.querySelector(`[data-club-sort="${key}"]`)?.focus({preventScroll:true});
});
function publicMembershipExplorer(d) {
  const split=clubGenderView==='split';
  const publicGroups=[...d.publicBreakdown].sort((a,b)=>b[1]-a[1]);
  const publicNames=new Set(publicGroups.map(r=>r[0]));
  const groups=[d.clubBreakdown.find(r=>r[0]==='Private Clubs'),['Public Clubs',publicGroups.reduce((n,r)=>n+r[1],0)],...publicGroups,d.clubBreakdown.find(r=>r[0]==='Unknown Access')];
  const total=d.counts.memberships;
  const combinedAssociations = groups => {
    const combined = new Map();
    Object.values(groups).forEach(rows=>rows.forEach(row=>{
      const entry=combined.get(row.id)||{...row,memberships:0};
      entry.memberships+=row.memberships;
      combined.set(row.id,entry);
    }));
    return [...combined.values()].sort((a,b)=>b.memberships-a.memberships||String(a.id).localeCompare(String(b.id)));
  };
  const associationRows=(source,group)=>group==='All Clubs'?combinedAssociations(source):group==='Public Clubs'?combinedAssociations(Object.fromEntries(Object.entries(source).filter(([name])=>publicNames.has(name)))):(source[group]||[]);
  const genderRows=(gender,group)=>associationRows(d.clubGenderAssociations[gender]||{},group);
  const sum=rows=>rows.reduce((n,r)=>n+r.memberships,0);
  const genderTotal=gender=>d.gender.find(r=>r[0]===gender)?.[1]||0;
  const rows=associationRows(d.clubAssociations,selectedPublicGroup);
  const selectedTotal=sum(rows);
  const maleRows=genderRows('Male',selectedPublicGroup),femaleRows=genderRows('Female',selectedPublicGroup);
  const maleTotal=sum(maleRows),femaleTotal=sum(femaleRows);
  const maleMap=Object.fromEntries(maleRows.map(r=>[r.id,r.memberships])),femaleMap=Object.fromEntries(femaleRows.map(r=>[r.id,r.memberships]));
  const comparisonRows=rows.filter(r=>(maleMap[r.id]||0)+(femaleMap[r.id]||0)>0).sort((a,b)=>((maleMap[b.id]||0)+(femaleMap[b.id]||0))-((maleMap[a.id]||0)+(femaleMap[a.id]||0)));
  const visibleRows=split?comparisonRows:rows;
  const associationClubs=clubAssociationDetails();
  if(selectedClubAssociation&&!visibleRows.some(row=>String(row.id)===selectedClubAssociation))selectedClubAssociation=null;
  const genderCell=(count,denominator,gender)=>`<td class="gender-number ${gender.toLowerCase()}"><strong>${fmt(count)}</strong><small>${pct(denominator?count/denominator:0)}</small></td>`;
  return `<article class="composition-card access public-explorer ${split?'club-comparison':''}">
    <div class="composition-band">Club Membership Explorer <div class="club-gender-toggle" role="group" aria-label="Club membership gender">${[['all','All'],['split','Male/Female']].map(([key,label])=>`<button type="button" data-club-gender="${key}" aria-pressed="${clubGenderView===key}">${label}</button>`).join('')}</div></div>
    <div class="public-explorer-grid"><div class="public-explorer-left">
      <div class="club-aligned-heading"><h3>Select a Club Type</h3><p>Select a club group to explore its associations.</p>
      ${split?`<div class="club-gender-totals club-overall-counts"><div><span>Male memberships</span><strong>${fmt(genderTotal('Male'))}</strong></div><div><span>Female memberships</span><strong>${fmt(genderTotal('Female'))}</strong></div></div>`:`<div class="club-total-callout live-public-pool"><span>Total Memberships</span><strong>${fmt(total)}</strong></div>`}
      <button type="button" class="public-group ${selectedPublicGroup==='All Clubs'?'selected':''}" data-public-group="All Clubs" aria-pressed="${selectedPublicGroup==='All Clubs'}" aria-controls="public-association-detail"><span class="public-group-heading"><span>All Clubs</span><strong>${fmt(total)} memberships</strong><span class="public-group-arrow" aria-hidden="true">→</span></span></button><div class="club-aligned-caption">${split?'<div class="club-comparison-legend"><span><i class="male"></i>Male</span><span><i class="female"></i>Female</span></div>':'Public subgroups ranked by memberships'}</div></div>
      <div class="public-group-list" aria-label="Club membership groups">${groups.map(([name,count])=>`<button type="button" class="public-group ${publicNames.has(name)?'public-subgroup':''} ${name==='Public Clubs'?'public-parent':''} ${name===selectedPublicGroup?'selected':''}" data-public-group="${esc(name)}" aria-pressed="${name===selectedPublicGroup}" aria-controls="public-association-detail"><span class="public-group-heading"><span>${esc(clubGroupLabel(name))}</span>${split?'':`<strong>${fmt(count)} <small>· ${pct(total?count/total:0)}</small></strong>`}<span class="public-group-arrow" aria-hidden="true">→</span></span>${split?['Male','Female'].map(gender=>{const n=sum(genderRows(gender,name)),den=genderTotal(gender),share=den?n/den:0;return `<span class="club-comparison-bar ${gender.toLowerCase()}" aria-label="${gender}: ${fmt(n)} memberships, ${pct(share)}"><span class="public-group-track"><span style="width:${share*100}%"></span></span><b>${pct(share)}</b></span>`}).join(''):`<span class="public-group-track"><span style="width:${total?100*count/total:0}%"></span></span>`}</button>`).join('')}</div>
      <p class="live-profile-note">${split?'Bars show shares within each gender; unknown gender is excluded from the comparison.':'Shares use Total Memberships, including unknown gender.'} Indented groups are included in Public Clubs, not additional memberships. Unknown Access is separate.</p>
    </div><section class="public-explorer-right" id="public-association-detail" aria-label="Association breakdown">
      <div class="club-aligned-heading public-selection-summary" aria-live="polite" aria-atomic="true"><h3>Then Select an Association</h3><p>Explore association memberships within the selected club group.</p>${split?`<div class="club-gender-totals"><div><span>Male memberships</span><strong>${fmt(maleTotal)}</strong></div><div><span>Female memberships</span><strong>${fmt(femaleTotal)}</strong></div></div>`:`<div class="club-total-callout"><span>Selected Group Memberships</span><strong>${fmt(selectedTotal)}</strong></div>`}<div class="club-selected-group"><h4>${esc(clubGroupLabel(selectedPublicGroup))}</h4><span>${fmt(visibleRows.length)} associations</span></div><div class="club-aligned-caption">${split?'Counts and shares within each gender · Ranked by combined total':'Associations ranked by total memberships'}</div></div>
      ${visibleRows.length?`<div class="live-affiliate-table-wrap"><table class="live-affiliate-table"><thead><tr><th scope="col">#</th><th scope="col">Association</th>${split?'<th scope="col">Male<small>Count · Share</small></th><th scope="col">Female<small>Count · Share</small></th><th scope="col">Clubs</th>':'<th scope="col">Memberships</th><th scope="col">Clubs</th><th scope="col">Share</th>'}</tr></thead><tbody>${visibleRows.map((row,i)=>`<tr data-association-id="${esc(row.id)}" class="${selectedClubAssociation===String(row.id)?'selected-association':''}"><td>${i+1}</td><td><button type="button" data-club-association="${esc(row.id)}" aria-pressed="${selectedClubAssociation===String(row.id)}" aria-controls="association-club-panel">${esc(row.name||'Unknown association')}</button></td>${split?genderCell(maleMap[row.id]||0,maleTotal,'Male')+genderCell(femaleMap[row.id]||0,femaleTotal,'Female')+`<td>${fmt(associationClubs.get(String(row.id))?.size||0)}</td>`:`<td>${fmt(row.memberships)}</td><td>${fmt(associationClubs.get(String(row.id))?.size||0)}</td><td>${pct(selectedTotal?row.memberships/selectedTotal:0)}</td>`}</tr>`).join('')}</tbody></table></div>`:'<div class="public-empty">No memberships in this group for the selected filters.</div>'}
    </section></div>${associationClubPanel(associationClubs,split)}
  </article>`;
}
document.addEventListener('click', event => {
  const association=event.target.closest?.('[data-club-association]')||event.target.closest?.('.public-explorer-right tr[data-association-id]')?.querySelector('[data-club-association]'),close=event.target.closest?.('[data-close-club-panel]');
  if(association||close){selectedClubAssociation=association?association.dataset.clubAssociation:null;document.querySelector('.public-explorer').outerHTML=publicMembershipExplorer(MEMBERSHIP_COMPOSITION_DATA[membershipPopulation]);if(association){const panel=document.getElementById('association-club-panel');panel?.scrollIntoView({behavior:'smooth',block:'start'});panel?.focus({preventScroll:true});}return;}
  const genderButton = event.target.closest?.('[data-club-gender]');
  if(genderButton){
    clubGenderView=genderButton.dataset.clubGender;
    genderButton.closest('.public-explorer').outerHTML=publicMembershipExplorer(MEMBERSHIP_COMPOSITION_DATA[membershipPopulation]);
    document.querySelector(`[data-club-gender="${clubGenderView}"]`)?.focus({preventScroll:true});
    return;
  }
  const button = event.target.closest?.('[data-public-group]');
  if (!button) return;
  selectedPublicGroup = button.dataset.publicGroup;
  const card = button.closest('.public-explorer');
  card.outerHTML = publicMembershipExplorer(MEMBERSHIP_COMPOSITION_DATA[membershipPopulation]);
  [...document.querySelectorAll('[data-public-group]')].find(b=>b.dataset.publicGroup===selectedPublicGroup)?.focus({preventScroll:true});
});
const profileGenderViews = {age:'all', handicap:'all'};
function liveMemberProfile(key, data) {
  const split=profileGenderViews[key]==='split';
  const title=key==='age'?'Age Profile':'Handicap Index Profile';
  const averageLabel=key==='age'?'Average Age':'Average Handicap Index';
  const controls=`<div class="profile-view-toggle" role="group" aria-label="${title} grouping"><button type="button" data-profile-key="${key}" data-profile-view="all" aria-pressed="${!split}">All</button><button type="button" data-profile-key="${key}" data-profile-view="split" aria-pressed="${split}">Male / Female</button></div>`;
  if(split){return (key==='age'?compositionAge(data):compositionHandicap(data)).replace('<div class="composition-body',controls+'<div class="composition-body');}
  const max=Math.max(1,...data.all);
  return `<article class="composition-card ${key}"><div class="composition-band">${title}</div>${controls}<div class="composition-body profile-card-body"><div class="handicap-summary profile-all-summary"><div><span>${averageLabel}</span><strong>${data.allAverage==null?'—':data.allAverage.toFixed(1)}</strong></div></div><div class="profile-all-legend">All memberships · All genders</div><div class="profile-chart profile-distribution">${data.bands.map((band,i)=>`<div class="profile-distribution-row profile-all-row"><span>${esc(band)}</span><div class="profile-all-bar"><div class="profile-all-track"><i style="width:${data.all[i]/max*100}%"></i></div><b>${data.all[i].toFixed(1)}%</b></div></div>`).join('')}</div></div></article>`;
}
document.addEventListener('click',event=>{
  const button=event.target.closest?.('[data-profile-view]');
  if(!button)return;
  const key=button.dataset.profileKey,view=button.dataset.profileView;
  profileGenderViews[key]=view;
  render();
  document.querySelector(`[data-profile-key="${key}"][data-profile-view="${view}"]`)?.focus({preventScroll:true});
});
let selectedAgeBand = 'All ages', selectedHandicapBand=null, ageDetailGroup='association',ageDetailSort={key:'total',direction:'desc'};
function ageIndexExplorer(d,ageNote,ageInsight,indexNote,indexInsight) {
  const split=profileGenderViews.age==='split';
  const selected=selectedAgeBand==='All ages'?{total:d.counts.memberships,profile:d.handicap}:d.handicapByAge[selectedAgeBand];
  const hp=selected?.profile;
  const sexes=split?['male','female']:['all'];
  const avg=(value)=>value==null?'—':value.toFixed(1);
  const summaries=(data,label)=>`<div class="age-index-averages ${split?'split':''}">${sexes.map(sex=>`<div class="${sex}"><span>${sex==='all'?'':sex==='male'?'Male ':'Female '}Average ${label}</span><strong>${avg(data?.[sex+'Average'])}</strong></div>`).join('')}</div>`;
  const bars=(data,i,max=100)=>sexes.map(sex=>`<span class="club-comparison-bar ${sex}"><span class="public-group-track"><span style="width:${(data[sex][i]||0)/max*100}%"></span></span><b>${(data[sex][i]||0).toFixed(1)}%</b></span>`).join('');
  const legend=split?'<div class="club-comparison-legend"><span><i class="male"></i>Male</span><span><i class="female"></i>Female</span></div>':'';
  const maxAge=Math.max(1,...sexes.flatMap(sex=>d.age[sex]));
  const maxIndex=hp?Math.max(1,...sexes.flatMap(sex=>hp[sex])):1;
  return `<article class="composition-card age age-index-explorer"><div class="composition-band">Age &amp; Handicap Explorer <div class="club-gender-toggle" role="group" aria-label="Age and handicap grouping">${[['all','All'],['split','Male/Female']].map(([key,label])=>`<button type="button" data-age-index-view="${key}" aria-pressed="${profileGenderViews.age===key}">${label}</button>`).join('')}</div></div>
  <div class="age-index-grid"><section class="age-index-left" aria-label="Age groups"><div class="age-index-heading"><h3>Select an Age Group</h3><p>Select an age group to explore its Handicap Index.</p>${summaries(d.age,'Age')}<button type="button" data-age-band="All ages" aria-pressed="${selectedAgeBand==='All ages'}" class="age-selector ${selectedAgeBand==='All ages'?'selected':''}"><span>All ages</span><strong>${fmt(d.counts.memberships)} memberships <span class="age-selection-arrow" aria-hidden="true">→</span></strong></button>${legend}</div>
  <div class="age-selector-list">${d.age.bands.map((band,i)=>`<button type="button" data-age-band="${esc(band)}" aria-pressed="${selectedAgeBand===band}" class="age-selector ${selectedAgeBand===band?'selected':''}"><span class="age-selector-label">${esc(band)}<small>${fmt(d.age.allCounts[i])} <span class="age-selection-arrow" aria-hidden="true">→</span></small></span>${bars(d.age,i,maxAge)}</button>`).join('')}</div>${ageNote}${ageInsight}</section>
  <section class="age-index-right" aria-label="Handicap Index for selected age"><div class="age-index-heading" aria-live="polite"><h3>Then Select a Handicap Index Range</h3><p>Select a range to explore who is in this group and where they belong.</p>${summaries(hp,'Handicap Index')}<div class="age-selected-summary"><h4>${esc(selectedAgeBand)}</h4><strong>${fmt(selected?.total||0)} memberships</strong></div>${legend}</div>
  ${selected?.total?`<div class="age-index-distribution">${hp.bands.map((band,i)=>`<button type="button" data-handicap-band="${esc(band)}" aria-pressed="${selectedHandicapBand===band}" class="age-index-band handicap-selector ${selectedHandicapBand===band?'selected':''}"><span>${esc(band)} <span class="handicap-selection-arrow" aria-hidden="true">↓</span></span>${bars(hp,i,maxIndex)}</button>`).join('')}</div>`:'<div class="public-empty">No memberships in this age group for the selected population.</div>'}
  ${indexNote}${selectedAgeBand==='All ages'?indexInsight:''}</section></div>${ageCohortPanel()}</article>`;
}
document.addEventListener('click',event=>{
  const age=event.target.closest?.('[data-age-band]'),view=event.target.closest?.('[data-age-index-view]');
  if(!age&&!view)return;
  if(age)selectedAgeBand=age.dataset.ageBand;
  if(view)profileGenderViews.age=profileGenderViews.handicap=view.dataset.ageIndexView;
  const value=age?age.dataset.ageBand:view.dataset.ageIndexView;
  render();
  const attr=age?'data-age-band':'data-age-index-view';
  [...document.querySelectorAll('['+attr+']')].find(b=>b.getAttribute(attr)===value)?.focus({preventScroll:true});
});
const ageDetailDimensions={association:'Association',clubGroup:'Club Group',access:'Public / Private',gender:'Gender',membershipType:'Membership Type',club:'Club'};
function ageCohortResult(){
 const data=MEMBERSHIP_INTERSECTIONS,groups=new Map(),matched=new Map();let total=0,unique=0;
 const pop=membershipPopulation==='all'?null:membershipPopulation==='regular'?'Regular':'Junior';
 data.cells.forEach((row,i)=>{
  if(pop&&data.populations[row[3]]!==pop)return;
  if(selectedAgeBand!=='All ages'&&data.ages[row[2]]!==selectedAgeBand)return;
  if(data.handicaps[row[4]]!==selectedHandicapBand)return;
  const values=membershipExplorerValues(row),club=data.clubs[row[0]],key=ageDetailGroup==='club'?club.id:values[ageDetailGroup];
  const label=ageDetailGroup==='club'?club.name+' — '+club.associationName:membershipExplorerLabel(ageDetailGroup,key);
  const group=groups.get(key)||{key,label,total:0,unique:0,male:0,female:0};group.total+=row[5];if(values.gender==='Male')group.male+=row[5];if(values.gender==='Female')group.female+=row[5];groups.set(key,group);matched.set(i,key);total+=row[5];
 });
 for(const [cells,count] of data.golferPatterns){const keys=new Set();for(const i of cells)if(matched.has(i))keys.add(matched.get(i));if(keys.size){unique+=count;for(const key of keys)groups.get(key).unique+=count;}}
 const rows=[...groups.values()],male=rows.reduce((n,r)=>n+r.male,0),female=rows.reduce((n,r)=>n+r.female,0);for(const row of rows){row.share=total?row.total/total:0;row.maleShare=male?row.male/male:0;row.femaleShare=female?row.female/female:0;}
 const sort=ageDetailSort;rows.sort((a,b)=>{const d=sort.key==='label'?a.label.localeCompare(b.label):a[sort.key]-b[sort.key];return d*(sort.direction==='asc'?1:-1)||a.label.localeCompare(b.label);});
 return {total,unique,rows};
}
function ageCohortPanel(){
 if(!selectedHandicapBand)return '<section class="age-cohort-panel age-cohort-prompt"><h3>Explore the Selected Group</h3><p>Select a Handicap Index range above to see the memberships and unique golfers behind it.</p></section>';
 const result=ageCohortResult();
 const columns=[['label',ageDetailDimensions[ageDetailGroup]],['total','Memberships'],['unique','Unique golfers'],['share','Share of selected memberships']];
 const split=profileGenderViews.age==='split';if(split)columns.push(['male','Male · Count / Share'],['female','Female · Count / Share']);
 return `<section class="age-cohort-panel" id="age-cohort-panel" tabindex="-1"><header><div><h3>${esc(selectedAgeBand)} · ${esc(selectedHandicapBand)}</h3><p>Explore the Selected Group · ${membershipPopulation==='all'?'All membership types':membershipPopulation==='regular'?'Regular':'Junior'} · U.S. associations</p></div></header><div class="age-cohort-metrics"><div><span>Memberships</span><strong>${fmt(result.total)}</strong></div><div><span>Unique golfers</span><strong>${fmt(result.unique)}</strong></div></div><label class="age-cohort-group">Group by<select id="ageCohortGroup">${Object.entries(ageDetailDimensions).map(([key,label])=>`<option value="${key}" ${ageDetailGroup===key?'selected':''}>${label}</option>`).join('')}</select></label><div class="age-cohort-scroll"><table class="live-affiliate-table"><thead><tr>${columns.map(([key,label])=>`<th aria-sort="${ageDetailSort.key===key?(ageDetailSort.direction==='asc'?'ascending':'descending'):'none'}"><button type="button" data-age-detail-sort="${key}">${label} ${ageDetailSort.key===key?(ageDetailSort.direction==='asc'?'↑':'↓'):'↕'}</button></th>`).join('')}</tr></thead><tbody>${result.rows.map(row=>`<tr><td>${esc(row.label)}</td><td>${fmt(row.total)}</td><td>${fmt(row.unique)}</td><td>${pct(row.share)}</td>${split?`<td class="cohort-male">${fmt(row.male)}<small>${pct(row.maleShare)}</small></td><td class="cohort-female">${fmt(row.female)}<small>${pct(row.femaleShare)}</small></td>`:''}</tr>`).join('')}</tbody></table>${result.total?'':'<p>No memberships match this age and Handicap Index selection.</p>'}</div><p class="live-profile-note">All genders remain in the overall totals. Shares use selected memberships.${split?' Male and Female columns show membership counts and shares within each gender’s selected age-and-Index group; unknown gender is excluded from those two columns.':''} Unique golfers are counted once per row and once in the overall total; a golfer may appear in multiple groups, so row-level unique counts may not add up to the overall total.</p></section>`;
}
document.addEventListener('click',event=>{
 const band=event.target.closest?.('[data-handicap-band]'),sort=event.target.closest?.('[data-age-detail-sort]');
 if(band){selectedHandicapBand=band.dataset.handicapBand;render();const panel=document.getElementById('age-cohort-panel');panel?.scrollIntoView({behavior:'smooth',block:'start'});panel?.focus({preventScroll:true});}
 if(sort){const key=sort.dataset.ageDetailSort;ageDetailSort={key,direction:ageDetailSort.key===key?(ageDetailSort.direction==='asc'?'desc':'asc'):key==='label'?'asc':'desc'};document.getElementById('age-cohort-panel').outerHTML=ageCohortPanel();document.querySelector(`[data-age-detail-sort="${key}"]`)?.focus({preventScroll:true});}
});
document.addEventListener('change',event=>{if(event.target.id!=='ageCohortGroup')return;ageDetailGroup=event.target.value;document.getElementById('age-cohort-panel').outerHTML=ageCohortPanel();document.getElementById('ageCohortGroup')?.focus({preventScroll:true});});
function membershipComposition(insights = false) {
  const d = insights ? MEMBERSHIP_COMPOSITION_DATA[membershipPopulation] : scopedCompositionData(membershipPopulation);
  const chart = (key, title, tone, items, colors) => compositionTileControl(key,
    liveCompositionDonut(title, tone, items, colors), liveCompositionTrend(title, tone));
  const ageNote = `<p class="live-profile-note">${fmt(d.quality.ageUnknown)} memberships have missing or invalid age (${pct(d.quality.ageUnknown / d.counts.memberships)}). Averages use available ages from 0–120. ${profileGenderViews.age==='split'?'Bars show percentages within each gender, including unknown ages.':'Bars show percentages of all memberships, including unknown gender and age.'}</p>`;
  const femaleAgeCounts = Object.fromEntries(d.age.bands.map((band,i)=>[band,d.age.femaleCounts[i]]));
  const femaleKnownAge = d.age.femaleCounts.reduce((sum,n)=>sum+n,0) - (femaleAgeCounts['Unknown / invalid'] || 0);
  const femaleOlderShare = femaleKnownAge ? ((femaleAgeCounts['55–64'] || 0)+(femaleAgeCounts['65+'] || 0))/femaleKnownAge : 0;
  const femaleYoungShare = femaleKnownAge ? (femaleAgeCounts['Under 18'] || 0)/femaleKnownAge : 0;
  const ageInsightNote = femaleKnownAge ? `<aside class="profile-key-insight age-key-insight"><span>Key insight</span><p>${membershipPopulation==='all'?'Women’s memberships cluster at the age extremes:':'Among female '+(membershipPopulation==='regular'?'Regular':'Junior')+' memberships,'} <strong>${pct(femaleOlderShare)}</strong> are age 55+ and <strong>${pct(femaleYoungShare)}</strong> are under 18—<strong>${pct(femaleOlderShare+femaleYoungShare)}</strong> combined.</p><small>Among female memberships with a known age. Missing or invalid ages are excluded.</small></aside>` : '';
  const indexNote = `<p class="live-profile-note">NH memberships remain in totals and appear as No Index. Averages exclude No Index and Unknown. ${profileGenderViews.handicap==='split'?'Bars show percentages within each gender.':'Bars show percentages of all memberships, including unknown gender.'}</p>`;
  const insight = d.highIndexInsight;
  const insightNote = insight.femaleShare == null ? '' : `<aside class="profile-key-insight"><span>Key insight</span><p>Women make up <strong>${pct(insight.femaleShare)}</strong> of unique golfers with a Handicap Index above 20${membershipPopulation==='all'?'':membershipPopulation==='regular'?' among Regular members':' among Junior members'}.</p><small>${fmt(insight.femaleGolfersAbove20)} of ${fmt(insight.golfersAbove20)} golfers · Each golfer counted once</small>${insight.femaleShareAbove30 == null ? '' : `<p>Women make up <strong>${pct(insight.femaleShareAbove30)}</strong> of unique golfers with a Handicap Index above 30${membershipPopulation==='all'?'':membershipPopulation==='regular'?' among Regular members':' among Junior members'}.</p><small>${fmt(insight.femaleGolfersAbove30)} of ${fmt(insight.golfersAbove30)} golfers · Each golfer counted once</small>`}</aside>`;
  const profile = (markup, note) => markup.replace('</article>', `${note}</article>`);
  const cards = insights ? [membershipInsightSection==='clubs'?publicMembershipExplorer(d):membershipInsightSection==='age'?ageIndexExplorer(d,ageNote,ageInsightNote,indexNote,insightNote):
    `<section class="membership-explorer-unit" aria-label="Membership Explorer">${membershipInsightCallouts()}<h2 class="membership-explorer-heading">Membership Explorer</h2>${membershipExplorer()}</section>`
  ] : [
    d.clubMetadataAvailable===false?`<article class="composition-card access"><div class="composition-band">Access Type</div><div class="live-history-empty"><strong>no data</strong><p>Club access classifications were not included in the international export.</p></div></article>`:chart('access', 'Access Type', 'access', d.access, ['#2f6597', '#a9c4dc', '#b8bec8', '#b8bec8']),
    chart('membership', 'Membership Type', 'membership', d.membership, ['#b64545', '#e7aaaa', '#b8bec8']),
    d.clubMetadataAvailable===false?`<article class="composition-card club"><div class="composition-band">Club Type</div><div class="live-history-empty"><strong>no data</strong><p>Club types were not included in the international export.</p></div></article>`:chart('club', 'Club Type', 'club', d.club, ['#244f7e', '#b62f42', '#8b98a8', '#6d6288', '#b8bec8']),
    chart('gender', 'Gender', 'gender', d.gender, ['#2f7a56', '#91c7ad', '#d8e6df']),
    compositionTileControl('age',compositionAge(d.age).replace('composition-card age','composition-card age composition-static-profile'),liveCompositionTrend('Age Profile','age')),
    compositionTileControl('handicap',compositionHandicap(d.handicap).replace('composition-card handicap','composition-card handicap composition-static-profile'),liveCompositionTrend('Handicap Index Profile','handicap')),
  ];
  const measures = [['Total Memberships', d.counts.memberships], ['Unique golfers', d.counts.uniqueGolfers],
    ['Unique Regular Golfers', membershipPopulation === 'junior' ? 0 : (insights?MEMBERSHIP_COMPOSITION_DATA.regular:scopedCompositionData('regular')).counts.uniqueGolfers],
    ['Unique Junior Golfers', membershipPopulation === 'regular' ? 0 : (insights?MEMBERSHIP_COMPOSITION_DATA.junior:scopedCompositionData('junior')).counts.uniqueGolfers]];
  return `<section class="membership-composition membership-live">
    ${insights?`<nav class="insights-tertiary-nav" aria-label="Insights sections">${[['membership','Membership'],['clubs','Golf Clubs'],['age','Age & Handicap']].map(([key,label])=>`<button type="button" data-insight-section="${key}" aria-current="${membershipInsightSection===key?'page':'false'}">${label}</button>`).join('')}</nav>`:''}
    ${insights?'':`<div class="live-membership-counts">${measures.map(([label, value], i) => `<div class="${i === 0 ? 'primary' : ''}"><span>${label}</span><strong>${fmt(value)}</strong></div>`).join('')}</div>`}
    <div class="composition-grid">${cards.join('')}</div>
    <details class="live-data-notes"><summary>About these membership numbers</summary>${insights&&membershipInsightSection==='membership'?`<p>Share uses all matching memberships. NH rate is the portion of each row marked No Index. Values within a filter use OR; different filters use AND. Unique golfers are counted once within the combined selection. Memberships beyond the first equals Total Memberships minus unique golfers. Unknown ages, genders and indexes remain available as separate values. Club Type follows the source Type 1/2/3; Club Group keeps GC Clubs separate.</p>`:''}<p>${insights?esc(MEMBERSHIP_SCOPE.definition):esc(membershipScopeLabel())+' follows association affiliation, not golfer residence. All Associations counts each golfer once across both scopes.'}</p>${!insights&&d.clubMetadataAvailable===false?'<p>International club access and club type were not supplied. Those memberships appear as Unknown in the classification charts.</p>':''}<p>Each qualifying club membership is counted. Unique golfers and multiple-membership measures are recalculated within the selected population. Unclassified memberships remain included in All Members. GC identification uses the 57 club IDs in the September GC source.</p><p>The live exports span ${insights?'September 21–22, 2026':membershipScopeDate()}; they are not a single-time historical snapshot. One membership present in both exports uses its later Junior classification. ${d.quality.missingGolferDetails==null?'Matching golfer-record coverage: no data.':fmt(d.quality.missingGolferDetails)+' memberships in this selection have no matching golfer details.'} Averages are membership-weighted.</p></details>
  </section>`;
}
