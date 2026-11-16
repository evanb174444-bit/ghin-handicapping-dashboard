const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const r='/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard',s=fs.readFileSync(r+'/Handicapping and GHIN Dashboard.html','utf8');
const source=s.slice(s.indexOf('let gahViews='),s.indexOf('const RETENTION_DATA='));
const ctx=vm.createContext({meta:{months:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']},fmt:n=>Math.round(n).toLocaleString('en-US'),short:n=>String(n),esc:s=>String(s)});vm.runInContext(source,ctx);
assert.equal(vm.runInContext('gahSelectedFunnelPeriod().values.at(-1)',ctx),5273);
for(const [period,expected] of [['month',5273],['ytd',108943],['all',116536]]){
 vm.runInContext(`gahFunnelView='${period}'`,ctx);const html=vm.runInContext('getAHandicap()',ctx);assert(html.includes(expected.toLocaleString('en-US')));assert(!html.includes('NaN'));assert(!html.includes('undefined'));assert(html.includes('Jan–Oct 2026'));assert(html.includes('Data notes'));
}
for(const [month,expected] of [[8,7007],[9,5273]]){
 vm.runInContext(`gahKpiPeriod='month';gahKpiMonth=${month};gahFunnelView='month';gahFunnelMonth=${month}`,ctx);const html=vm.runInContext('getAHandicap()',ctx);assert(html.includes(expected.toLocaleString('en-US')));assert(html.includes(month===8?'259,019':'225,017'));
}
vm.runInContext("gahViews.checkout='quarterly';gahViews.registrations='quarterly';gahViews.checkoutRate='quarterly';gahViews.conversion='quarterly'",ctx);const html=vm.runInContext('getAHandicap()',ctx);assert(html.includes('117,388'));assert(html.includes('103,247'));
assert.equal(vm.runInContext('GAH_EXACT_FUNNEL_MONTHLY[2026][7][0]',ctx),147637);assert.equal(vm.runInContext('GAH_HISTORY.sessions[2026][7]',ctx),365218);assert.equal(vm.runInContext('GAH_HISTORY.sessions[2026][8]',ctx),259019);
console.log('PASS: September/October, YTD, retained-period, Q3 cumulative charts; monthly funnel refreshed consistently; traffic through October; future months remain missing.');
