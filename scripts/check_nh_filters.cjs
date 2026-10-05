const {chromium}=require('/Users/EvanBelfi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:8765/Handicapping%20and%20GHIN%20Dashboard.html');
await page.locator('[data-top="membership"]').click();await page.locator('[data-sub="composition"]').click();await page.locator('[data-membership-population="all"]').click();
assert.equal(await page.locator('.nh-explorer .nh-filter-results strong').nth(0).textContent(),'438,165');
assert.equal(await page.locator('.nh-explorer .nh-filter-results strong').nth(1).textContent(),'433,444');
assert.equal(await page.locator('.nh-left').count(),0);
assert.equal(await page.locator('#nhGroupBy').inputValue(),'membershipType');
for(const group of ['membershipType','association','access','clubGroup','gender','age','club']) {
 await page.selectOption('#nhGroupBy',group);
 const counts=await page.locator('.nh-explorer .nh-club-scroll tbody td:nth-child(2)').allTextContents();
 assert.equal(counts.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),438165);
}
for(const [key,value] of [['membershipType','Junior'],['association','53'],['gender','Female'],['clubGroup','Affiliate / WORE']]) {
 await page.selectOption('#nhFilterDimension',key);await page.selectOption('#nhFilterValue',value);await page.locator('[data-nh-add]').click();
}
assert.equal(await page.locator('.nh-explorer .nh-filter-chips button').count(),4);
const result=await page.evaluate(()=>nhIntersection(MEMBERSHIP_COMPOSITION_DATA.all));assert.deepEqual({nh:result.nh,unique:result.unique,total:result.total},{nh:7853,unique:7730,total:8728});
const counts=await page.locator('.nh-explorer .nh-club-scroll tbody td:nth-child(2)').allTextContents();assert.equal(counts.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),result.nh);
await page.locator('.nh-explorer').screenshot({path:'reports/nh-filter-builder.png'});
await page.locator('[data-nh-remove="gender"]').click();assert.equal(await page.locator('.nh-explorer .nh-filter-chips button').count(),3);
await page.locator('[data-nh-clear]').click();assert.equal(await page.locator('.nh-explorer .nh-filter-results strong').first().textContent(),'438,165');
for(const [pop,total,unique] of [['regular','134,324','133,103'],['junior','303,455','300,488']]){
 await page.locator(`[data-membership-population="${pop}"]`).click();
 assert.equal(await page.locator('.nh-explorer .nh-filter-results strong').nth(0).textContent(),total);
 assert.equal(await page.locator('.nh-explorer .nh-filter-results strong').nth(1).textContent(),unique);
}
await page.locator('[data-membership-population="all"]').click();await page.setViewportSize({width:390,height:844});assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)));
assert.deepEqual(errors,[]);console.log('Stacked selection:',JSON.stringify({nh:result.nh,unique:result.unique,total:result.total}));console.log('Stacking, grouped results, add/remove/clear, population totals, and mobile checks passed.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
