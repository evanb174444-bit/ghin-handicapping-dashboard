function observeGCFrame(frame){
 const main=frame.contentDocument?.querySelector('main');if(!main)return;
 const resize=()=>{frame.style.height=Math.ceil(main.getBoundingClientRect().height+24)+'px';};
 new ResizeObserver(resize).observe(main);resize();
}
let gcAcquisitionView='totals';
function openGCAcquisition(){activeTop='gc';activeSub='acquisition';gcAcquisitionView='new-member-mix';render();}
function gcAcquisition(){
 const nav=`<nav class="membership-charts-nav" aria-label="GC acquisition views">${[['totals','New Member Totals'],['new-member-mix','New Member Mix'],['attribution','New Member Attribution']].map(([view,label])=>`<button type="button" class="${gcAcquisitionView===view?'active':''}" aria-pressed="${gcAcquisitionView===view}" onclick="gcAcquisitionView='${view}';render()">${label}</button>`).join('')}</nav>`;
 return nav+(gcAcquisitionView==='new-member-mix'?gcJoinerChart():gcMembershipTotals());
}
function gcMembershipTotals(){
 const view={'membership-totals':'summary',acquisition:'acquisition',retention:'retention',recovery:'recovery'}[activeSub]||'summary';
 const label={'membership-totals':'Membership Totals',acquisition:'Acquisition',retention:'Retention',recovery:'Recovery'}[activeSub]||'Membership Totals';
 return `<iframe onload="observeGCFrame(this)" class="gc-summary-frame" data-gc-summary-frame data-gc-lifecycle-frame title="GC ${label}" src="gc-dashboard-summary/lifecycle/index.html?view=${view}&acquisition=${gcAcquisitionView}&v=20261118-local"></iframe>`;
}
window.addEventListener('message',event=>{
 const frame=document.querySelector('[data-gc-lifecycle-frame]');if(!frame||event.source!==frame.contentWindow||event.origin!==location.origin)return;
 if(event.data?.type==='ghin-gc-lifecycle-view'){
  const route={summary:'membership-totals',acquisition:'acquisition',retention:'retention',recovery:'recovery'}[event.data.view];
  if(route&&route!==activeSub){activeSub=route;render();}
 }
 if(event.data?.type==='ghin-gc-existing-route'){
  activeSub=event.data.route==='associations'?'associations':'get-a-handicap';render();
 }
});
