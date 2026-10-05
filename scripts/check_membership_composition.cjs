const {chromium} = require('/Users/EvanBelfi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8765/Handicapping%20and%20GHIN%20Dashboard.html');
  await page.locator('[data-top="membership"]').click();
  await page.locator('[data-sub="composition"]').click();
  const expected = require('../data/processed/membership_composition.json');
  for (const pop of ['all','regular','junior']) {
    const total = expected.populations[pop].counts.memberships.toLocaleString('en-US');
    await page.locator(`[data-membership-population="${pop}"]`).click();
    assert.equal(await page.locator('.live-membership-counts .primary strong').textContent(),total);
    assert.equal(await page.locator('.membership-live .composition-card').count(),7);
    const text=await page.locator('.membership-live').textContent();
    assert(!/NaN|undefined/.test(text));
    assert(text.includes('No Index'));
    const values=await page.evaluate(()=>MEMBERSHIP_COMPOSITION_DATA[membershipPopulation]);
    assert(values.affiliateAssociations.every(row=>row.name));
    assert((await page.locator('.subtitle').textContent()).includes(expected.meta.scope.label));
    assert.equal(await page.locator('.age-index-right .profile-key-insight strong').first().textContent(),(values.highIndexInsight.femaleShare*100).toFixed(1)+'%');
    assert.equal(await page.locator('.age-index-right .profile-key-insight strong').nth(1).textContent(),(values.highIndexInsight.femaleShareAbove30*100).toFixed(1)+'%');
    const nhTotal=values.handicap.allCounts[values.handicap.bands.indexOf('No Index')];
    assert.equal(await page.locator('.nh-explorer').count(),0);
    const affiliateTotal=values.affiliateAssociations.reduce((n,row)=>n+row.memberships,0);
    assert.equal(affiliateTotal,values.publicBreakdown.find(row=>row[0]==='Affiliate / WORE')[1]);
    assert.equal(values.clubBreakdown.reduce((n,r)=>n+r[1],0),values.counts.memberships);
    assert.equal(values.clubBreakdown.find(r=>r[0]==='Private Clubs')[1],values.access.find(r=>r[0]==='Private')[1]);
    assert.equal(values.clubBreakdown.find(r=>r[0]==='Unknown Access')[1],values.access.filter(r=>r[0]!=='Public'&&r[0]!=='Private').reduce((n,r)=>n+r[1],0));
    for (const mode of ['all','split']) {
      await page.locator(`[data-club-gender="${mode}"]`).click();
      await page.locator('[data-public-group="All Clubs"]').click();
      assert.equal(await page.locator('.public-explorer [data-public-group]').first().getAttribute('data-public-group'),'All Clubs');
      assert.equal(await page.locator('.club-selected-group h4').textContent(),'All Clubs');
      if(mode==='all') {
        assert.equal(await page.locator('.public-selection-summary .club-total-callout>strong').textContent(),total);
        const counts=await page.locator('.live-affiliate-table tbody td:nth-child(3)').allTextContents();
        assert.equal(counts.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),values.counts.memberships);
      } else {
        for(const [i,gender] of ['Male','Female'].entries()) {
          const expectedGender=values.gender.find(r=>r[0]===gender)[1];
          assert.equal(await page.locator('.public-selection-summary .club-gender-totals strong').nth(i).textContent(),expectedGender.toLocaleString('en-US'));
          const counts=await page.locator('.gender-number.'+gender.toLowerCase()+' strong').allTextContents();
          assert.equal(counts.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),expectedGender);
        }
      }

      if(mode==='all') assert.equal(await page.locator('.public-explorer-left .live-public-pool strong').textContent(),total);
      await page.locator('[data-public-group="Public Clubs"]').click();
      assert.equal(await page.locator('.public-subgroup').count(),8);
      const publicNames=new Set(values.publicBreakdown.map(r=>r[0]));
      if(mode==='all') {
        const publicTotal=values.access.find(r=>r[0]==='Public')[1];
        assert.equal(await page.locator('.public-selection-summary .club-total-callout>strong').textContent(),publicTotal.toLocaleString('en-US'));
        const counts=await page.locator('.live-affiliate-table tbody td:nth-child(3)').allTextContents();
        assert.equal(counts.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),publicTotal);
      } else for(const [i,gender] of ['Male','Female'].entries()) {
        const publicTotal=Object.entries(values.clubGenderAssociations[gender]).filter(([name])=>publicNames.has(name)).flatMap(([,rows])=>rows).reduce((n,r)=>n+r.memberships,0);
        assert.equal(await page.locator('.public-selection-summary .club-gender-totals strong').nth(i).textContent(),publicTotal.toLocaleString('en-US'));
      }
      for (const [group,count] of values.clubBreakdown) {
        await page.locator('[data-public-group]').filter({hasText:group==='Virtual clubs / eClubs'?'Other Type 3 (Virtual/eClubs)':group}).click();
        const tableRows=page.locator('.live-affiliate-table tbody tr');
        if(mode==='all') {
          assert.equal(await page.locator('.public-selection-summary .club-total-callout>strong').textContent(),count.toLocaleString('en-US'));
          assert.equal(await tableRows.count(),(values.clubAssociations[group]||[]).length);
        } else {
          for(const [i,gender] of ['Male','Female'].entries()) {
            const rows=values.clubGenderAssociations[gender]?.[group]||[];
            const sum=rows.reduce((n,r)=>n+r.memberships,0);
            assert.equal(await page.locator('.public-selection-summary .club-gender-totals strong').nth(i).textContent(),sum.toLocaleString('en-US'));
            const shown=await page.locator('.gender-number.'+gender.toLowerCase()+' strong').allTextContents();
            assert.equal(shown.reduce((n,v)=>n+Number(v.replaceAll(',','')),0),sum);
            const genderTotal=values.gender.find(r=>r[0]===gender)[1];
            const button=page.locator('[data-public-group]').filter({hasText:group==='Virtual clubs / eClubs'?'Other Type 3 (Virtual/eClubs)':group});
            assert.equal(await button.locator('.club-comparison-bar.'+gender.toLowerCase()+' b').textContent(),(genderTotal?100*sum/genderTotal:0).toFixed(1)+'%');
          }
          assert.equal(await page.locator('.public-explorer .club-comparison-bar').count(),22);
        }
      }
    }
    await page.locator('[data-club-gender="all"]').click();
    for(const key of ['access','membership','club','gender']) assert.equal(values[key].reduce((n,x)=>n+x[1],0),values.counts.memberships);
    for(const key of ['age','handicap']) for(const sex of ['male','female']) assert(Math.abs(values[key][sex].reduce((a,b)=>a+b,0)-100)<1e-7);
    for(const mode of ['all','split']) {
      await page.locator(`[data-age-index-view="${mode}"]`).click();
      for(const band of ['All ages',...values.age.bands]) {
        await page.locator('[data-age-band]').filter({hasText:band}).first().click();
        assert.equal(await page.locator('.age-selected-summary h4').textContent(),band);
        const cohort=band==='All ages'?{total:values.counts.memberships,profile:values.handicap}:values.handicapByAge[band];
        if(cohort?.total) {
          assert.equal(cohort.profile.allCounts.reduce((a,b)=>a+b,0),cohort.total);
          assert.equal(await page.locator('.age-index-band').count(),values.handicap.bands.length);
          for(const [i,sex] of (mode==='all'?['all']:['male','female']).entries()) {
            const mean=cohort.profile[sex+'Average'];
            assert.equal(await page.locator('.age-index-right .age-index-averages strong').nth(i).textContent(),mean==null?'—':mean.toFixed(1));
            const displayed=await page.locator('.age-index-band .club-comparison-bar.'+sex+' b').allTextContents();
            assert.deepEqual(displayed,cohort.profile[sex].map(v=>v.toFixed(1)+'%'));
          }
        } else assert(await page.locator('.age-index-right .public-empty').isVisible());
        assert.equal(await page.locator('.age-index-right .profile-key-insight').count(),band==='All ages'?1:0);
      }
    }
    await page.locator('[data-age-band="All ages"]').click();
    await page.locator('.age-index-explorer').screenshot({path:path.resolve(`reports/age-index-${pop}.png`)});
    await page.locator('[data-age-index-view="all"]').click();
    await page.locator('.composition-card.club').screenshot({path:path.resolve(`reports/club-donut-${pop}.png`)});
    await page.screenshot({path:path.resolve(`reports/membership-${pop}-desktop.png`),fullPage:true});
  }
  await page.locator('[data-composition-tile-key="access"][data-composition-tile-view="trends"]').click();
  assert(await page.locator('.live-history-empty').isVisible());
  await page.locator('[data-composition-tile-key="access"][data-composition-tile-view="snapshot"]').click();
  await page.locator('[data-membership-population="all"]').click();
  await page.locator('[data-public-group="Affiliate / WORE"]').click();
  await page.locator('[data-public-group="Affiliate / WORE"]').focus();
  await page.keyboard.press('Tab');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator('.club-selected-group h4').textContent(),'Public Green Grass Clubs');
  await page.locator('[data-club-gender="split"]').click();
  await page.locator('.public-explorer').screenshot({path:path.resolve('reports/public-explorer-desktop.png')});
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.resolve('reports/membership-all-mobile.png'),fullPage:true});
  await page.locator('.composition-card.age').screenshot({path:path.resolve('reports/membership-age-mobile.png')});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
  assert(!overflow,'Mobile horizontal overflow');
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('All 60 view/group/population combinations, association sums, empty state, keyboard selection, history, and mobile overflow checks passed; no page errors.');
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
