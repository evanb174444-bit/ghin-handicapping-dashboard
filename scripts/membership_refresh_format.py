"""Format refreshed composition using the existing dashboard schema."""
age_bands = ['Under 18', '18–24', '25–34', '35–44', '45–54', '55–64', '65+', 'Unknown / invalid']
hi_bands = ['Plus / Scratch', '0.1–5.0', '5.1–10.0', '10.1–15.0', '15.1–20.0', '20.1–30.0', '30.1+', 'No Index', 'Unknown']
def items(s, key, labels):
    return [[label, s[key].get(label, 0)] for label in labels]+[[label,n] for label,n in s[key].items() if label not in labels]

def profile(s, key, bands):
    out = {'bands': bands, 'allCounts':[s[key].get(b,0) for b in bands],
           'all':[100*s[key].get(b,0)/s['total'] if s['total'] else 0 for b in bands],
           'allAverage':s['averages'].get(key+'_all',{}).get('mean')}
    for gender, prop in [('Male','male'),('Female','female')]:
        counts = s[key+'_by_gender'].get(gender,{})
        denominator = s['gender'].get(gender,0)
        assert sum(counts.values()) == denominator
        out[prop] = [100*counts.get(b,0)/denominator if denominator else 0 for b in bands]
        out[prop+'Counts'] = [counts.get(b,0) for b in bands]
        out[prop+'Average'] = s['averages'].get(key+'_'+gender,{}).get('mean')
    return out

def format_composition(source, insight, association_names):
    data = {}
    for key,pop in [('all','All Members'),('regular','Regular'),('junior','Junior')]:
        s = source['segments'][pop]
        data[key] = {
            'noHandicap':s['no_handicap'],
            'highIndexInsight':insight['populations'][key],
            'counts': {'memberships':s['total'],'uniqueGolfers':s['unique_golfers'],
                       'multiMembershipGolfers':s['multi_membership_golfers'],'additionalMemberships':s['additional_memberships']},
            'access':items(s,'access',['Public','Private','Unknown — green-grass access not specified']),
            'membership':items(s,'membership_type',['Regular','Junior','Unclassified']),
            'club':items(s,'club_type',['Type 1','Type 2','Type 3','GC Clubs']),
            'gender':items(s,'gender',['Male','Female','Unknown']),
            'publicBreakdown':items(s,'public_breakdown',['Public Green Grass Clubs','Semi-Private','Resort','Municipal','Military','Affiliate / WORE','Virtual clubs / eClubs','GC Clubs']),
            'clubBreakdown':items(s,'club_breakdown',['Private Clubs','Public Green Grass Clubs','Semi-Private','Resort','Municipal','Military','Affiliate / WORE','Virtual clubs / eClubs','GC Clubs','Unknown Access']),
            'clubGenderAssociations':{gender:{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in groups.items()} for gender,groups in s['club_gender_associations'].items()},
            'clubAssociations':{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in s['club_by_association'].items()},
            'publicAssociations':{group:[{'id':aid,'name':association_names.get(aid),'memberships':count} for aid,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))] for group,counts in s['public_by_association'].items()},
            'affiliateAssociations':[{'id':aid,'name':association_names.get(aid), 'memberships':count}
                for aid,count in sorted(s['affiliate_by_association'].items(),key=lambda item:(-item[1],item[0]))],
            'handicapByAge':{band:{'total':c['total'],'profile':profile(c,'handicap',hi_bands)} for band,c in s['handicap_by_age'].items()},
            'age':profile(s,'age',age_bands), 'handicap':profile(s,'handicap',hi_bands),
            'quality':{'ageUnknown':s['age'].get('Unknown / invalid',0),'missingGolferDetails':s['issues'].get('missing_golfer_details',0)}
        }
        for aid,segment in data[key]['noHandicap']['dimensions']['association'].items():
            segment['name']=association_names.get(aid, 'Unknown association')
        for club in data[key]['noHandicap']['clubs'].values():
            club['associationName']=association_names.get(club['association'],'Unknown association')
        for field in ['access','membership','club','gender']:
            assert sum(v for _,v in data[key][field]) == s['total']
        assert sum(v for _,v in data[key]['clubBreakdown']) == s['total']
        assert sum(v for _,v in data[key]['publicBreakdown']) == s['access']['Public']
        assert sum(row['memberships'] for row in data[key]['affiliateAssociations']) == s['public_breakdown'].get('Affiliate / WORE',0)

    return data
