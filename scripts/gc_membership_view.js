function observeGCFrame(frame){
 const main=frame.contentDocument?.querySelector('main');if(!main)return;
 const resize=()=>{frame.style.height=Math.ceil(main.getBoundingClientRect().height+24)+'px';};
 new ResizeObserver(resize).observe(main);resize();
}
function openGCAcquisition(){gcMembershipView='acquisition';render();}
let gcMembershipView='totals';
function gcMembershipTotals(){
 const acquisition=gcMembershipView==='acquisition';
 return `<nav class="membership-charts-nav" aria-label="GC membership views">${[['totals','Totals'],['acquisition','Acquisition']].map(([view,label])=>`<button type="button" data-gc-membership-view="${view}" class="${gcMembershipView===view?'active':''}" aria-pressed="${gcMembershipView===view}" onclick="gcMembershipView='${view}';render()">${label}</button>`).join('')}</nav>${acquisition?gcJoinerChart():`<iframe onload="observeGCFrame(this)" class="gc-summary-frame" data-gc-summary-frame title="GC Membership Totals" src="gc-dashboard-summary/index.html?v=20261113"></iframe>`}`;
}
