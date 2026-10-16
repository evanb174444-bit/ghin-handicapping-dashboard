"""Shared approved membership composition aggregation."""
from collections import Counter
from review_membership_exports import classify, numeric, average_add

def add_membership(r, segments, gc, seen_gc, conflict_counts):
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
