let gcMembershipView='totals';
function gcMembershipTotals(){
 const acquisition=gcMembershipView==='acquisition';
 return `<nav class="membership-charts-nav" aria-label="GC membership views">${[['totals','Totals'],['acquisition','Acquisition']].map(([view,label])=>`<button type="button" data-gc-membership-view="${view}" class="${gcMembershipView===view?'active':''}" aria-pressed="${gcMembershipView===view}" onclick="gcMembershipView='${view}';render()">${label}</button>`).join('')}</nav>${acquisition?gcJoinerChart():`<iframe class="gc-summary-frame" data-gc-summary-frame title="GC Membership Totals" src="gc-dashboard-summary/index.html?v=20261002"></iframe>`}`;
}
