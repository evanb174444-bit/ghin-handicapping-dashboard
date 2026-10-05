"""Read private CSVs in bounded batches; write aggregate review only, never HTML."""
import csv
import json
import math
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GC_SOURCE = Path('/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard/data/raw/2026-09/Current Month_Golfer Detail.csv')
FILES = [('Regular', '01_active_standard_2026-09-21.csv.csv'),
         ('Junior', '02_active_junior_2026-09-22.csv.csv'),
         ('Unclassified', '03_active_unclassified_2026-09-22.csv')]
FIELDS = ['membership_id', 'golfer_id', 'club_id', 'club_category', 'club_type',
          'gender', 'age_at_extraction', 'handicap_index', 'handicap_index_display',
          'matched_golfer_id', 'association_id', 'extracted_at', 'membership_updated_at', 'club_name']

def numeric(v):
    try:
        n = float(v)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None

def fresh():
    return {'total': 0, 'access': Counter(), 'club_type': Counter(),
            'public_breakdown': Counter(), 'gender': Counter(), 'membership_type': Counter(),
            'age': Counter(), 'handicap': Counter(), 'raw_category': Counter(),
            'raw_club_type': Counter(), 'averages': {}, 'issues': Counter(),
            'age_by_gender': {}, 'handicap_by_gender': {}, 'affiliate_by_association': Counter(), 'public_by_association': {}, 'club_breakdown': Counter(), 'club_by_association': {}, 'club_gender_associations': {}, 'handicap_by_age': {}, 'no_handicap': {'dimensions':{},'clubs':{}}}

def average_add(s, key, value):
    a = s['averages'].setdefault(key, {'sum': 0, 'count': 0})
    a['sum'] += value
    a['count'] += 1

def classify(club, category, kind, gc):
    if club in gc:
        return 'Public', 'GC Clubs', 'GC Clubs'
    mapped_type = kind or 'Unknown'
    if category in ('Affiliate', 'WORE') or mapped_type in ('Type 2', 'Type 3'):
        access = 'Public'
    elif category == 'Private':
        access = 'Private'
    elif category in ('Public', 'Semi-Private', 'Resort', 'Municipal', 'Military'):
        access = 'Public'
    else:
        access = 'Unknown — green-grass access not specified' if kind == 'Type 1' else 'Unknown'
    detail = None
    if access == 'Public':
        if category in ('Affiliate', 'WORE'):
            detail = 'Affiliate / WORE'
        elif category == 'Public':
            detail = {'Type 1': 'Public Green Grass Clubs', 'Type 2': 'Affiliate / WORE',
                      'Type 3': 'Virtual clubs / eClubs'}.get(mapped_type, 'Other / unspecified Public')
        elif category in ('Semi-Private', 'Resort', 'Municipal', 'Military'):
            detail = category
        elif mapped_type == 'Type 2':
            detail = 'Affiliate / WORE'
        elif mapped_type == 'Type 3':
            detail = 'Virtual clubs / eClubs'
        else:
            detail = 'Other / unspecified Public'
    return access, mapped_type, detail

def main():
    scope = json.loads((ROOT/"config/membership_scope.json").read_text())
    excluded = {}
    gc = {}
    with GC_SOURCE.open(encoding='utf-16', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            cid = r['Club Number'].strip()
            if cid:
                gc[cid] = r['Club Name'].strip()
    print(f'GC source: {len(gc)} club IDs', flush=True)
    segments = {p: fresh() for p in ['All Members', 'Regular', 'Junior', 'Unclassified']}
    metadata, overlaps, seen_gc = [], [], set()
    conflict_counts = Counter()
    with tempfile.TemporaryDirectory(prefix='ghin-review-') as tmp:
        con = sqlite3.connect(str(Path(tmp) / 'staging.sqlite'))
        con.execute('PRAGMA journal_mode=OFF')
        con.execute('PRAGMA synchronous=OFF')
        con.execute('PRAGMA temp_store=FILE')
        cols = ','.join(f'{k} TEXT' + (' PRIMARY KEY' if k == 'membership_id' else '') for k in FIELDS)
        con.execute(f'CREATE TABLE records ({cols}, population TEXT)')
        insert = 'INSERT INTO records VALUES (' + ','.join('?' for _ in range(len(FIELDS)+1)) + ')'
        for pop, filename in FILES:
            p = Path('/Users/EvanBelfi/Downloads') / filename
            before = p.stat()
            count, times = 0, Counter()
            with p.open(encoding='utf-8-sig', newline='') as f:
                for r in csv.DictReader(f, strict=True):
                    count += 1
                    assert None not in r and all(v is not None for v in r.values())
                    assert r['membership_id'] and r['golfer_id']
                    assert r['membership_status'] == 'Active' and r['club_is_test'] == 'No'
                    assert r['association_id'] != '237'
                    expected = {'Regular': 'Standard', 'Junior': 'Junior'}.get(pop)
                    assert r['usga_membership_type'] == expected if expected else r['usga_membership_type'] not in ('Standard', 'Junior')
                    times[r['extracted_at']] += 1
                    values = [r[k] for k in FIELDS] + [pop]
                    try:
                        con.execute(insert, values)
                    except sqlite3.IntegrityError:
                        old = con.execute('SELECT population,golfer_id FROM records WHERE membership_id=?', (r['membership_id'],)).fetchone()
                        assert old[1] == r['golfer_id'], 'Conflicting golfer IDs for a membership'
                        overlaps.append({'earlier_population': old[0], 'later_population': pop,
                                         'proposal': 'Use later export for review; classification pending approval'})
                        con.execute('DELETE FROM records WHERE membership_id=?', (r['membership_id'],))
                        con.execute(insert, values)
                    if count % 100000 == 0:
                        con.commit()
            con.commit()
            after = p.stat()
            assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            metadata.append({'file': filename, 'rows': count, 'bytes': before.st_size,
                             'extraction_start': min(times), 'extraction_end': max(times),
                             'query_timestamps': len(times)})
            print(f'Loaded {pop}: {count:,}', flush=True)
        if scope['mode'] == 'us':
            allowed = scope['association_ids']
            placeholders = ','.join('?' for _ in allowed)
            predicate = f'association_id NOT IN ({placeholders})'
            excluded = dict(con.execute('SELECT association_id,COUNT(*) FROM records WHERE '+predicate+' GROUP BY association_id', allowed))
            con.execute('DELETE FROM records WHERE '+predicate, allowed)
            con.commit()
        for vals in con.execute('SELECT * FROM records'):
            r = dict(zip(FIELDS + ['population'], vals))
            pop, cid, cat, kind = r['population'], r['club_id'], r['club_category'], r['club_type']
            access, mapped_type, detail = classify(cid, cat, kind, gc)
            if cid in gc:
                seen_gc.add(cid)
            elif cat in ('Affiliate', 'WORE') and kind != 'Type 2':
                conflict_counts[f'{cat} / {kind} → Public; retain {kind}'] += 1
            if kind in ('Type 2','Type 3') and cat == 'Private':
                conflict_counts[f'Private / {kind} → Public'] += 1
            gender = r['gender'] or 'Unknown'
            age = numeric(r['age_at_extraction'])
            hi = numeric(r['handicap_index'])
            display = r['handicap_index_display'].strip()
            if not r['matched_golfer_id']:
                age = hi = None
            if age is None or age < 0 or age > 120:
                age_band = 'Unknown / invalid'
            else:
                age_band = next(label for edge,label in [(18,'Under 18'),(25,'18–24'),(35,'25–34'),(45,'35–44'),(55,'45–54'),(65,'55–64'),(121,'65+')] if age < edge)
            if display.upper() == 'NH':
                hi_band = 'No Index'
            elif hi is None:
                hi_band = 'Unknown'
            else:
                hi_band = next(label for edge,label in [(0,'Plus / Scratch'),(5,'0.1–5.0'),(10,'5.1–10.0'),(15,'10.1–15.0'),(20,'15.1–20.0'),(30,'20.1–30.0'),(float('inf'),'30.1+')] if hi <= edge)
            for s in (segments[pop], segments['All Members']):
                s['total'] += 1
                cohort=s['handicap_by_age'].setdefault(age_band, {'total':0,'gender':Counter(),'handicap':Counter(),'handicap_by_gender':{},'averages':{}})
                cohort['total'] += 1
                cohort['gender'][gender] += 1
                cohort['handicap'][hi_band] += 1
                cohort['handicap_by_gender'].setdefault(gender,Counter())[hi_band] += 1
                if hi_band not in ('No Index','Unknown'):
                    average_add(cohort,'handicap_all',hi)
                    average_add(cohort,'handicap_'+gender,hi)
                for field,value in [('access',access),('club_type',mapped_type),('gender',gender),('membership_type',pop),('age',age_band),('handicap',hi_band),('raw_category',cat or 'Missing'),('raw_club_type',kind or 'Missing')]:
                    s[field][value] += 1
                group = detail if access == 'Public' else ('Private Clubs' if access == 'Private' else 'Unknown Access')
                s['club_breakdown'][group] += 1
                nh=s['no_handicap']
                dimensions={'association':r['association_id'] or 'Unknown','access':access,'clubGroup':group,'clubType':kind or 'Unknown','gender':gender,'age':age_band,'membershipType':pop}
                for dimension,label in dimensions.items():
                    segment=nh['dimensions'].setdefault(dimension,{}).setdefault(label,{'total':0,'nh':0,'clubs':Counter()})
                    segment['total']+=1
                    if hi_band=='No Index':
                        segment['nh']+=1
                        segment['clubs'][cid]+=1
                if hi_band=='No Index':
                    club=nh['clubs'].setdefault(cid,{'name':r['club_name'],'association':r['association_id'],'type':kind,'group':group,'nh':0})
                    club['nh']+=1

                s['club_by_association'].setdefault(group, Counter())[r['association_id'] or 'Unknown'] += 1
                s['club_gender_associations'].setdefault(gender, {}).setdefault(group, Counter())[r['association_id'] or 'Unknown'] += 1
                if detail:
                    s['public_breakdown'][detail] += 1
                    s['public_by_association'].setdefault(detail, Counter())[r['association_id'] or 'Unknown'] += 1
                if detail == 'Affiliate / WORE':
                    s['affiliate_by_association'][r['association_id'] or 'Unknown'] += 1
                s['age_by_gender'].setdefault(gender, Counter())[age_band] += 1
                s['handicap_by_gender'].setdefault(gender, Counter())[hi_band] += 1
                if age_band != 'Unknown / invalid':
                    average_add(s,'age_all',age)
                    average_add(s,'age_'+gender,age)
                if hi_band not in ('No Index','Unknown'):
                    average_add(s,'handicap_all',hi)
                    average_add(s,'handicap_'+gender,hi)
                if not r['matched_golfer_id']:
                    s['issues']['missing_golfer_details'] += 1
                if age is not None and (age < 0 or age > 120):
                    s['issues']['age_outside_0_to_120'] += 1
                if display.startswith('+') and hi is not None and hi > 0:
                    s['issues']['positive_numeric_index_with_plus_display'] += 1
                if not r['association_id']:
                    s['issues']['missing_association'] += 1
        for pop,s in segments.items():
            where = '' if pop == 'All Members' else ' WHERE population=?'
            args = () if pop == 'All Members' else (pop,)
            unique,multi,extra = con.execute('SELECT COUNT(*),SUM(n>1),SUM(n-1) FROM (SELECT golfer_id,COUNT(*) n FROM records'+where+' GROUP BY golfer_id)',args).fetchone()
            s['unique_golfers'],s['multi_membership_golfers'],s['additional_memberships'] = unique,multi,extra
            nh_where=" WHERE UPPER(TRIM(handicap_index_display))='NH'"+('' if pop=='All Members' else ' AND population=?')
            s['no_handicap']['uniqueGolfers']=con.execute('SELECT COUNT(DISTINCT golfer_id) FROM records'+nh_where,args).fetchone()[0]
            for dimension,values in s['no_handicap']['dimensions'].items():
                assert sum(v['nh'] for v in values.values())==s['handicap'].get('No Index',0)
                assert sum(v['total'] for v in values.values())==s['total']
                for v in values.values():assert sum(v['clubs'].values())==v['nh']

            assert unique + extra == s['total']
            for field in ['access','club_type','gender','membership_type','age','handicap','raw_category','raw_club_type']:
                assert sum(s[field].values()) == s['total'], (pop,field)
            assert sum(s['public_breakdown'].values()) == s['access']['Public']
            assert sum(s['affiliate_by_association'].values()) == s['public_breakdown'].get('Affiliate / WORE', 0)
            assert sum(s['club_breakdown'].values()) == s['total']
            for gender, groups in s['club_gender_associations'].items():
                assert sum(sum(counts.values()) for counts in groups.values()) == s['gender'][gender]
            for group, count in s['club_breakdown'].items():
                assert sum(sum(groups.get(group, {}).values()) for groups in s['club_gender_associations'].values()) == count
            for group, counts in s['club_by_association'].items():
                assert sum(counts.values()) == s['club_breakdown'][group]
            for group, counts in s['public_by_association'].items():
                assert sum(counts.values()) == s['public_breakdown'][group]
            assert sum(c['total'] for c in s['handicap_by_age'].values()) == s['total']
            for cohort in s['handicap_by_age'].values():
                assert sum(cohort['handicap'].values()) == cohort['total']
                for a in cohort['averages'].values():
                    a['mean']=a['sum']/a['count']
            for a in s['averages'].values():
                a['mean'] = a['sum']/a['count']
        assert sum(segments[p]['total'] for p in ['Regular','Junior','Unclassified']) == segments['All Members']['total']
    result = {'scope': scope, 'excluded_memberships_by_association': excluded, 'status': 'Reviewed membership aggregates', 'sources': metadata,
              'gc_source': str(GC_SOURCE), 'gc_club_ids': len(gc), 'matched_gc_clubs':len(seen_gc),
              'unmatched_gc_clubs': [{'club_id': k, 'club_name': v} for k,v in gc.items() if k not in seen_gc],
              'overlap_resolution_proposed':overlaps,'classification_conflicts':dict(conflict_counts),
              'methodology':['Membership-weighted counts and averages; trial memberships excluded; NH included in membership totals.',
                             'Age below 0 or above 120 held in Unknown / invalid for review.',
                             'Later Junior export used for one overlapping membership in this review only.',
                             'Affiliate/WORE → Public, retaining recorded Type 1/2/3; authoritative GC clubs remain separate. Type 2/3 → Public.',
                             'Public detail gives GC Clubs precedence, then known category. Source Public uses Type 1 → Public Green Grass Clubs, Type 2 → Affiliate, Type 3 → eClub; unspecified Type 2/3 uses Affiliate/eClub.'],
              'segments':segments}
    out = ROOT/'reports/membership_composition_review_2026-09-22.json'
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps({'counts':{k:{f:s[f] for f in ['total','unique_golfers','multi_membership_golfers','additional_memberships','access','club_type','public_breakdown','gender','age','handicap','averages','issues']} for k,s in segments.items()},'gc_clubs':len(gc),'matched_gc_clubs':len(seen_gc),'conflicts':dict(conflict_counts),'overlaps':overlaps},indent=2))

if __name__ == '__main__':
    main()
