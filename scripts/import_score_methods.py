"""Validate method export and roll it up without losing unmatched scores."""
import csv, json
from collections import Counter

def load_methods(root, baseline):
    source = root/'data/raw/scores/score_monthly_posting_methods_2025_2026.csv'
    combined=root/'data/raw/scores/score_monthly_dashboard_2025_2026.csv'
    if combined.exists(): source=combined
    full=source==combined
    if not source.exists(): return baseline, None
    with source.open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
    fields=[k for k in baseline[0] if k not in ('extracted_at','score_count')]
    aggregate=Counter(); old=Counter(); new=Counter(); seen=set()
    labels={'Total Adjusted Score':'total','Total Adjusted Score - Front 9 / Back 9':'total','Hole-by-Hole':'hole','Hole-by-Hole Stats':'stats','Missing from extract':'unknown','Unknown posting method':'unknown','Conflicting posting methods':'unknown','Unknown':'unknown','Conflicting labels':'unknown'}
    for r in baseline: old[r['posting_month'][:7]]+=int(r['score_count'])
    for r in rows:
        n=int(r['score_count']); assert n>=0
        assert r['posting_method'] in labels
        assert r['association_scope'] in {'aga','international','test','trial_association','unknown','ambiguous'}
        for flag in ['is_regular','is_junior','is_trial','has_unclassified_membership']: assert r[flag] in {'true','false',''}
        key=tuple(r[k] for k in fields)
        unique=key+tuple(r[k] for k in (['posting_method','posting_application','posting_application_api','posting_source','number_of_holes','number_of_played_holes'] if full else ['posting_method']))
        assert unique not in seen, 'Duplicate aggregate row in export'
        seen.add(unique); aggregate[key]+=n; new[r['posting_month'][:7]]+=n
        r['method_category']=labels[r['posting_method']]
        if full: r['breakdowns']=classify_breakdowns(r)
    assert set(old)==set(new), 'Month coverage changed'
    drift={m:new[m]-old[m] for m in sorted(old)}
    assert all(abs(drift[m])<=50 for m in old), 'Larger than reviewed monthly drift; investigate'
    extracted=sorted({r['extracted_at'] for r in rows})
    rolled=[dict(zip(fields,key),extracted_at='; '.join(extracted),score_count=str(n)) for key,n in aggregate.items()]
    report={'source':source.name,'rows':len(rows),'months':len(new),'extractedAt':extracted,'monthlyDifferenceFromSeptember28':drift,'reconciliation':'Small differences from prior export; all Scores views use this export consistently. Multiple extraction timestamps retained; not a single database snapshot.','ytdMethods':dict(Counter({k:sum(int(r['score_count']) for r in rows if r['method_category']==k and r['posting_month'].startswith('2026') and r['association_scope']!='test') for k in ['total','hole','stats','unknown']}))}
    (root/'data/validation/score_methods.validation.json').write_text(json.dumps(report,indent=2))
    report['consolidated']=full
    (root/'data/validation/score_methods.validation.json').write_text(json.dumps(report,indent=2))
    return rolled, dict(rows=rows,meta=report)


def classify_breakdowns(r):
    app=r['posting_application']; api=r['posting_application_api'].lower()
    direct={'Mobile App','GHIN.com','Admin Portal','Kiosk'}
    product='GHIN Mobile App' if app=='Mobile App' else app if app in direct|{'API','Migration'} else 'Unknown'
    provider='GHIN' if app in direct else 'Migration / provider unknown' if app=='Migration' else 'Unknown provider'
    mappings=[('golf genius','Golf Genius'),('new start mobile','New Start Mobile'),('adminescape','AdminEscape'),('blue golf','Blue Golf'),('arccos golf','Arccos Golf'),('fore tees','ForeTees'),('shotzoom','ShotZoom'),('golfnet','Golfnet'),('unknown golf','Unknown Golf'),('golf pad','Golf Pad'),('live tourney','Live Tourney'),('youth on course','Youth on Course'),('leaderboard systems','Leaderboard Systems'),('gallus golf','Gallus Golf'),('wa golf api','WA Golf'),('vision perfect','Vision Perfect'),('go club golf','Go Club Golf'),('golf nations','Golf Nations'),('golf status','Golf Status'),('amateur golf society','Amateur Golf Society'),('coreworx','Coreworx')]
    if app=='API':
        for needle,label in mappings:
            if needle in api: provider=label;break
    regular=r['is_regular']=='true';junior=r['is_junior']=='true'
    membership='Both Regular and Junior' if regular and junior else 'Regular' if regular else 'Junior' if junior else 'Unclassified'
    holes=r['number_of_played_holes']
    holes='9 holes' if holes=='9' else '18 holes' if holes=='18' else '10–17 holes' if holes.isdigit() and 10<=int(holes)<=17 else 'Unknown / other holes'
    return dict(product=product,provider=provider,membership=membership,holes=holes)
