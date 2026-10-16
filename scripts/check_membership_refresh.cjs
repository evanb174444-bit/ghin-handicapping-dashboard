const {chromium}=require('/Users/EvanBelfi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const counts=require('../data/processed/international_totals.json');
const acquisition=require('../data/processed/acquisition.json');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('file://'+path.join(root,'Handicapping and GHIN Dashboard.html'));
 await page.locator('[data-top="membership"]').click();
 await page.locator('[data-sub="composition"]').click();
 for(const scope of ['aga','international','all']){
  await page.selectOption('[aria-label="Association scope"]',scope);
  for(const pop of ['all','regular','junior']){
   await page.locator(`[data-membership-population="${pop}"]`).click();
   const expected=counts.scopes[scope][pop];
   assert.equal(await page.locator('.live-membership-counts .primary strong').innerText(),expected.memberships.toLocaleString('en-US'));
   const data=await page.evaluate(()=>scopedCompositionData(membershipPopulation));
   assert.deepEqual(data.counts,expected);
   for(const field of ['access','membership','club','gender'])assert.equal(data[field].reduce((n,r)=>n+r[1],0),expected.memberships);
   for(const field of ['age','handicap'])assert.equal(data[field].allCounts.reduce((n,v)=>n+v,0),expected.memberships);
   assert(!/NaN|undefined/.test(await page.locator('.membership-live').innerText()));
   assert((await page.locator('.subtitle').innerText()).includes('October 13'));
  }
 }
 await page.selectOption('[aria-label="Association scope"]','all');
 await page.locator('[data-membership-population="all"]').click();
 await page.screenshot({path:path.join(root,'reports/membership-refresh-composition.png')});
 await page.locator('[data-sub="summary"]').click();
 assert.equal(await page.locator('.live-membership-counts .primary strong').innerText(),'3,956,144');
 await page.locator('[data-membership-measure="unique"]').click();
 assert.equal(await page.evaluate(()=>membershipTotalsData().current),3654391);
 await page.locator('[data-membership-measure="memberships"]').click();
 assert.equal(await page.evaluate(()=>membershipTotalsData().current),3814564,'Billing source must stay unchanged');
 await page.locator('[data-chart-section="acquisition"]').click();
 for(const scope of ['aga','international','all']){
  await page.selectOption('[aria-label="Association scope"]',scope);
  for(const pop of ['all','regular','junior']){
   await page.locator(`[data-membership-population="${pop}"]`).click();
   for(const month of [0,8]){
    await page.selectOption('#acqMonth',String(month));
    const expected=acquisition.scopes[scope][pop];
    const values=await page.locator('.acq-kpi-value').allTextContents();
    assert.equal(values[0],expected[month].toLocaleString('en-US'));
    assert.equal(values[1],expected.slice(0,month+1).reduce((a,b)=>a+b,0).toLocaleString('en-US'));
   }
   assert(!/NaN|undefined|198,450|1,566,570/.test(await page.locator('.acquisition-page').innerText()));
  }
 }
 await page.selectOption('[aria-label="Association scope"]','all');
 await page.locator('[data-membership-population="all"]').click();
 await page.locator('[data-acq-type="bar"]').click();
 await page.locator('[data-acq-type="line"]').click();
 assert(await page.locator('.acquisition-page > .membership-scope-notice').evaluate(e=>e.getBoundingClientRect().width>e.parentElement.getBoundingClientRect().width*.95));
 await page.screenshot({path:path.join(root,'reports/membership-refresh-acquisition.png')});
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:path.join(root,'reports/membership-refresh-acquisition-mobile.png')});
 await page.setViewportSize({width:1440,height:1050});
 for(const sub of ['retention','recovery']){
  await page.locator(`[data-chart-section="${sub}"]`).click();
  assert((await page.locator('#app').innerText()).includes('Historical data needed'));
 }
 await page.locator('[data-sub="insights"]').click();
 for(const pop of ['all','regular','junior']){
  await page.locator(`[data-membership-population="${pop}"]`).click();
  const result=await page.evaluate(()=>membershipExplorerResult());
  assert.equal(result.total,counts.scopes.aga[pop].memberships);
  assert.equal(result.unique,counts.scopes.aga[pop].uniqueGolfers);
 }
 await page.locator('[data-membership-population="all"]').click();
 const addFilter=async(key,value)=>{await page.selectOption('#meFilterDimension',key);await page.selectOption('#meFilterValue',value);await page.locator('[data-me-add]').click();};
 await addFilter('association','53');await addFilter('association','1');await addFilter('gender','Female');
 const filtered=await page.evaluate(()=>membershipExplorerResult());
 const independent=require('../data/processed/refresh-2026-10-13/validation.json').filteredExplorerCheck;
 for(const key of ['total','unique','nh'])assert.equal(filtered[key],independent[key]);
 await page.locator('[data-me-clear]').click();
 const nh=await page.evaluate(()=>({actual:nhIntersection(MEMBERSHIP_COMPOSITION_DATA.all),expected:MEMBERSHIP_COMPOSITION_DATA.all.noHandicap.uniqueGolfers}));
 assert.equal(nh.actual.unique,nh.expected);
 // Every association and club rollup reconciles independently to the scoped totals.
 const rollups=await page.evaluate(()=>({associations:MEMBERSHIP_ASSOCIATION_DATA,clubs:MEMBERSHIP_CLUB_DATA}));
 for(const scope of ['aga','international','all'])for(const pop of ['all','regular','junior']){
  assert.equal(rollups.associations.scopes[scope][pop].reduce((n,r)=>n+r.memberships,0),counts.scopes[scope][pop].memberships);
  assert.equal(rollups.clubs.clubs.filter(r=>scope==='all'||r.scope===scope).reduce((n,r)=>n+r[pop],0),counts.scopes[scope][pop].memberships);
 }
 await page.locator('[data-sub="summary"]').click();
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:path.join(root,'reports/membership-refresh-mobile.png')});
 assert.deepEqual(errors,[]);
 await browser.close();
 console.log('PASS: composition across 9 scope/population combinations, acquisition across 18 period selections, explorer distinct counts, association/club rollups, billing preservation, unavailable history, and mobile layout.');
})().catch(e=>{console.error(e);process.exit(1);});
