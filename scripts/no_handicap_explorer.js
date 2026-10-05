let nhFilters={};
let nhGroupBy='membershipType';
const nhDimensionLabels={membershipType:'Membership Type',association:'Association',access:'Public / Private',clubGroup:'Club Group',gender:'Gender',age:'Age'};
function nhIntersection(d) {
 const data=NH_INTERSECTIONS,counts=new Map(),grouped=new Map(),matched=new Uint8Array(data.cells.length);
 let total=0,nh=0;
 const pop=membershipPopulation==='all'?null:membershipPopulation==='regular'?'Regular':'Junior';
 data.cells.forEach((r,i)=>{
  const club=data.clubs[r[0]],values={association:club.association,access:club.access,clubGroup:club.clubGroup,gender:data.genders[r[1]],age:data.ages[r[2]],membershipType:data.populations[r[3]]};
  if(pop&&values.membershipType!==pop)return;
  if(Object.entries(nhFilters).some(([key,value])=>values[key]!==value))return;
  total+=r[4];nh+=r[5];
  const key=nhGroupBy==='club'?String(r[0]):values[nhGroupBy];
  const group=grouped.get(key)||{key,total:0,nh:0};group.total+=r[4];group.nh+=r[5];grouped.set(key,group);
  if(r[5]){matched[i]=1;counts.set(r[0],(counts.get(r[0])||0)+r[5]);}
 });
 const unique=data.golferPatterns.reduce((n,[cells,count])=>n+(cells.some(i=>matched[i])?count:0),0);
 return {total,nh,unique,groups:[...grouped.values()].filter(r=>r.nh>0).sort((a,b)=>b.nh-a.nh),clubs:[...counts].sort((a,b)=>b[1]-a[1])};
}
function nhFilterLabel(key,value,d){return d.noHandicap.dimensions[key]?.[value]?.name||(key==='clubGroup'?clubGroupLabel(value):value);}
function nhFilterPane(d){
 const result=nhIntersection(d),data=NH_INTERSECTIONS;
 const keys=Object.keys(nhDimensionLabels).filter(key=>!(key in nhFilters));
 return `<section class="nh-workspace"><p class="nh-help">Combine filters to explore active memberships marked NH (No Index), then choose how to group the results.</p>
 <div class="nh-filter-chips">${Object.entries(nhFilters).map(([key,value])=>`<button type="button" data-nh-remove="${key}" aria-label="Remove ${esc(nhDimensionLabels[key])} filter">${esc(nhDimensionLabels[key])}: <strong>${esc(nhFilterLabel(key,value,d))}</strong> ×</button>`).join('')||'<span>No filters · All NH memberships</span>'}</div>
 <div class="nh-filter-add"><label>Add filter<select id="nhFilterDimension">${keys.map(key=>`<option value="${key}">${esc(nhDimensionLabels[key])}</option>`).join('')}</select></label><label>Value<select id="nhFilterValue"></select></label><button type="button" data-nh-add ${keys.length?'':'disabled'}>Add</button><button type="button" data-nh-clear>Clear all</button></div>
 <div class="nh-filter-results" aria-live="polite"><div><span>NH memberships</span><strong>${fmt(result.nh)}</strong></div><div><span>Unique golfers with NH</span><strong>${fmt(result.unique)}</strong></div><div><span>NH rate in selection</span><strong>${pct(result.total?result.nh/result.total:0)}</strong></div><div><span>All memberships in selection</span><strong>${fmt(result.total)}</strong></div></div>
 <div class="nh-results-toolbar"><label>Group results by<select id="nhGroupBy">${Object.entries({...nhDimensionLabels,club:'Club'}).map(([key,label])=>`<option value="${key}" ${key===nhGroupBy?'selected':''}>${label}</option>`).join('')}</select></label><span>${fmt(result.groups.length)} results · Ranked by NH memberships</span></div>
 <p class="nh-help">Share of NH uses matching NH memberships. NH rate uses all matching memberships in each row.</p>
 <div class="nh-club-scroll"><table class="nh-table"><thead><tr><th scope="col">${nhGroupBy==='club'?'Club / Association':esc(nhDimensionLabels[nhGroupBy])}</th><th scope="col">NH memberships</th><th scope="col">Share of NH</th><th scope="col">NH rate</th><th scope="col">All memberships</th></tr></thead><tbody>${result.groups.map(row=>{const club=nhGroupBy==='club'?data.clubs[Number(row.key)]:null;const label=club?club.name:nhFilterLabel(nhGroupBy,row.key,d);return `<tr><th scope="row">${esc(label)}${club?`<small>${esc(club.associationName)}</small><small>${esc(club.type)} · ${esc(clubGroupLabel(club.clubGroup))}</small>`:''}</th><td>${fmt(row.nh)}</td><td>${pct(result.nh?row.nh/result.nh:0)}</td><td>${pct(row.total?row.nh/row.total:0)}</td><td>${fmt(row.total)}</td></tr>`}).join('')}</tbody></table></div>${result.nh?'':'<p class="public-empty">No NH memberships match these filters.</p>'}</section>`;

}
function populateNhFilterValues(){
 const dim=document.getElementById('nhFilterDimension'),value=document.getElementById('nhFilterValue');if(!dim||!value)return;
 const d=MEMBERSHIP_COMPOSITION_DATA[membershipPopulation];
 value.innerHTML=Object.entries(d.noHandicap.dimensions[dim.value]||{}).sort((a,b)=>nhFilterLabel(dim.value,a[0],d).localeCompare(nhFilterLabel(dim.value,b[0],d))).map(([id,row])=>`<option value="${esc(id)}">${esc(nhFilterLabel(dim.value,id,d))}</option>`).join('');
}
function refreshNhExplorer(){
 const el=document.querySelector('.nh-explorer');if(!el)return;
 el.outerHTML=noHandicapExplorer(MEMBERSHIP_COMPOSITION_DATA[membershipPopulation]);populateNhFilterValues();
}
document.addEventListener('change',event=>{if(event.target.id==='nhFilterDimension')populateNhFilterValues();if(event.target.id==='nhGroupBy'){nhGroupBy=event.target.value;refreshNhExplorer();document.getElementById('nhGroupBy')?.focus({preventScroll:true});}});
document.addEventListener('click',event=>{
 const remove=event.target.closest?.('[data-nh-remove]'),add=event.target.closest?.('[data-nh-add]'),clear=event.target.closest?.('[data-nh-clear]');
 if(remove)delete nhFilters[remove.dataset.nhRemove];
 else if(clear)nhFilters={};
 else if(add){const key=document.getElementById('nhFilterDimension').value,value=document.getElementById('nhFilterValue').value;if(!key||!value)return;nhFilters[key]=value;}
 else return;
 refreshNhExplorer();
});
function noHandicapExplorer(d) {
 queueMicrotask(populateNhFilterValues);
 return `<article class="composition-card access nh-explorer"><div class="composition-band">No Handicap Explorer</div>${nhFilterPane(d)}<p class="live-profile-note">Counts include multiple club memberships. Only the unique-golfer card counts each golfer once. Unknown or missing Handicap Index records are separate from NH. Club Group keeps GC Clubs separate. All figures follow the selected All/Regular/Junior population and U.S. association scope.</p></article>`;
}
