from pathlib import Path
import csv,json,shutil,re
root=Path(__file__).resolve().parents[1]
src=Path('/Users/EvanBelfi/Downloads/score_posting_counts_by_type_2026.csv.csv')
rows=list(csv.DictReader(src.open(encoding='utf-8-sig')))
assert len(rows)==12
bands=['0 scores','1–7 scores','8+ scores']
assert {r['population'] for r in rows}=={'all','regular','junior','unclassified'}
assert len({(r['extracted_at'],r['score_period_start'],r['score_period_end']) for r in rows})==1
assert rows[0]['score_period_start']=='2026-01-01' and rows[0]['score_period_end'].startswith('2026-10-21')
payload={'extractedAt':rows[0]['extracted_at'],'periodStart':rows[0]['score_period_start'],'periodEnd':rows[0]['score_period_end'],'scope':'all','source':'score_posting_counts_by_type_2026.csv','populations':{}}
for pop in ['all','regular','junior','unclassified']:
    selected=[r for r in rows if r['population']==pop]
    assert [r['posting_bucket'] for r in selected]==bands
    counts=[int(r['golfer_count']) for r in selected];assert all(n>=0 for n in counts)
    total=sum(counts);assert total>0
    assert all(int(r['population_total'])==total for r in selected)
    for r,n in zip(selected,counts):assert abs(float(r['golfer_percentage'])-n/total*100)<=.0051
    payload['populations'][pop]={'totalGolfers':total,'buckets':[{'label':r['posting_bucket'],'count':n,'percentage':float(r['golfer_percentage'])} for r,n in zip(selected,counts)]}
for pop in ['regular','junior','unclassified']:
    assert all(r['count']<=a['count'] for r,a in zip(payload['populations'][pop]['buckets'],payload['populations']['all']['buckets']))
shutil.copy2(src,root/'data/raw/scores/score_posting_counts_by_type_2026.csv')
(root/'data/processed/score_participation.json').write_text(json.dumps(payload,indent=2))
p=root/'scripts/scores_scope_view.js';old=p.read_text();start=old.index('function liveScoresParticipation(');end=old.index('\nfunction liveScoresTotals()',start)
fn='''function liveScoresParticipation(total,period,year){
 const source=PARTICIPATION_DATA;
 const data=source.populations[scoresPopulation];
 const populationLabel={all:'All Members',regular:'Regular Members',junior:'Junior Members'}[scoresPopulation];
 const available=scoresGeography==='all'&&!!data&&scoresPopulation!=='unclassified';
 const heading=`<div class="scores-card-band"><span>Score Posting Participation</span></div>`;
 if(!available)return `<article class="card full scores-participation" data-score-participation>${heading}<div class="scores-participation-body"><h3>Participation breakdown unavailable for this selection</h3><p class="scores-participation-explanation">Available for All Associations with All Members, Regular Members or Junior Members, January 1–October 21, 2026. Association-specific and Trial Golfer breakdowns are not supplied.</p></div></article>`;
 const colors=['#8c9fb2','#537fa6','#173d66'];
 return `<article class="card full scores-participation" data-score-participation>${heading}<div class="scores-participation-body">
 <div class="scores-participation-intro"><div><h3>How often are golfers posting?</h3><p>January 1–October 21, 2026 · All Associations · ${populationLabel} · Active at export</p></div><span class="scores-participation-status">${fmt(data.totalGolfers)} unique golfers</span></div>
 <div class="scores-participation-buckets">${data.buckets.map((b,i)=>`<section class="scores-participation-bucket band-${i}"><h4>${b.label}</h4><strong style="color:#173d66" data-participation-count="${b.count}">${fmt(b.count)}</strong><span style="font-size:18px;font-weight:700;color:${colors[i]}">${b.percentage.toFixed(2)}%</span><small>of active golfers</small></section>`).join('')}</div>
 <div style="display:flex;height:42px;border-radius:22px;overflow:hidden;margin:24px 0 18px" role="img" aria-label="${data.buckets.map(b=>b.label+': '+b.percentage.toFixed(2)+' percent').join('; ')}">${data.buckets.map((b,i)=>`<div style="width:${100*b.count/data.totalGolfers}%;background:${colors[i]};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:13px">${b.percentage.toFixed(1)}%</div>`).join('')}</div>
 
 <details class="live-data-notes"><summary>Show data</summary><table class="nh-table"><thead><tr><th>Scores posted</th><th>Unique golfers</th><th>Share</th></tr></thead><tbody>${data.buckets.map(b=>`<tr><th scope="row">${b.label}</th><td>${fmt(b.count)}</td><td>${b.percentage.toFixed(2)}%</td></tr>`).join('')}<tr><th>Total</th><td>${fmt(data.totalGolfers)}</td><td>100.00%</td></tr></tbody></table><p>Each golfer counts once, even with multiple active memberships. Eligibility uses active memberships at export time, from the same query snapshot as the score cutoff. Test clubs, test associations and Trial Association 237 are excluded. Scores use creation dates from January 1 through the October 21, 2026 extraction timestamp, excluding deleted and penalty records.</p><p>Source: October 21, 2026 counts export. Extraction timestamp: ${esc(source.extractedAt)}. The CSV supplies the score period, counts and percentages. Percentages are rounded and may not sum to exactly 100%. This population differs from the headline score total, which includes trial postings and scores from golfers who may now be inactive. Regular and Junior refer to the USGA membership type linked through the club rate, not age. Each golfer counts once within a group; golfers with both types appear in both, and once in All Members. All Members includes unclassified memberships. The export also identifies ${fmt(source.populations.unclassified.totalGolfers)} golfers with at least one unclassified membership; this group can overlap Regular or Junior. Age, gender and association breakdowns are not supplied.</p></details>
 </div></article>`;
}
'''.replace('PARTICIPATION_DATA',json.dumps(payload,separators=(',',':')))
new=old[:start]+fn+old[end:]
page=root/'Handicapping and GHIN Dashboard.html';html=page.read_text();assert old.strip() in html
backup=root/'backups/participation-type-import-2026-10-21';backup.mkdir(exist_ok=True);
if not (backup/page.name).exists():shutil.copy2(page,backup/page.name)
p.write_text(new);page.write_text(html.replace(old.strip(),new.strip(),1))
print('Validated population totals:',{k:v['totalGolfers'] for k,v in payload['populations'].items()})
