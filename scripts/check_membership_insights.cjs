const {chromium}=require('/Users/EvanBelfi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8765/Handicapping%20and%20GHIN%20Dashboard.html');await page.locator('[data-top="membership"]').click();await page.locator('[data-sub="composition"]').click();assert.equal(await page.locator('.membership-explorer-unit').count(),0);assert.equal(await page.locator('.composition-card').count(),4);await page.locator('[data-sub="insights"]').click();assert.equal(await page.locator('.membership-explorer-unit').count(),1);assert.equal(await page.locator('.public-explorer').count(),0);await page.locator('[data-insight-section="clubs"]').click();assert.equal(await page.locator('.public-explorer').count(),1);assert.equal(await page.locator('.membership-explorer-unit').count(),0);await page.locator('[data-insight-section="age"]').click();assert.equal(await page.locator('.age-index-right').count(),1);assert.equal(await page.locator('.public-explorer').count(),0);await page.locator('[data-insight-section="membership"]').click();await page.locator('[data-membership-population="all"]').click();
await page.locator('[data-category-definitions]').click();
assert(await page.locator('#categoryDefinitionsDialog').isVisible());assert.equal(await page.locator('#categoryDefinitionsDialog dt').count(),10);
await page.keyboard.press('Escape');assert(!(await page.locator('#categoryDefinitionsDialog').isVisible()));
await page.locator('[data-category-definitions]').click();await page.locator('[data-close-definitions]').click();assert(!(await page.locator('#categoryDefinitionsDialog').isVisible()));
const cards=await page.evaluate(()=>membershipInsightDeck());
assert.equal(await page.locator('.insight-summary-tile').count(),3);assert.equal(await page.locator('.insight-chart').count(),0);
for(const topic of [...new Set(cards.map(c=>c.topic))]){await page.selectOption('#insightTopicSelect',topic);assert.equal(await page.locator('.insight-summary-tile>span').first().textContent(),topic);}
await page.selectOption('#insightTopicSelect','Membership Type');
for(let i=0;i<cards.length;i++){
 assert.equal(await page.locator('.insight-summary-tile').first().getAttribute('data-insight-index'),String(i));
 await page.locator(`[data-me-insight="${i}"]`).click();assert.deepEqual(await page.evaluate(()=>membershipExplorerFilters),cards[i].filters);assert.equal(await page.locator('#meGroupBy').inputValue(),cards[i].group);
 await page.locator('[data-insight-step="1"]').click();
}
assert.equal(await page.evaluate(()=>membershipInsightPosition),0);await page.locator('[data-insight-step="-1"]').click();assert.equal(await page.evaluate(()=>membershipInsightPosition),cards.length-1);
await page.locator('[data-me-insight="0"]').click();assert.deepEqual(await page.evaluate(()=>membershipExplorerFilters),cards[0].filters);
await page.selectOption('#insightTopicSelect','No Handicap');await page.locator('.membership-insights').screenshot({path:'reports/membership-insight-carousel.png'});
await page.setViewportSize({width:390,height:844});assert.equal(await page.locator('.insight-summary-tile:visible').count(),1);assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)));assert.deepEqual(errors,[]);console.log('Three-tile deck, all eight drilldowns, topic jumps, arrow wrapping and mobile passed.');
await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
