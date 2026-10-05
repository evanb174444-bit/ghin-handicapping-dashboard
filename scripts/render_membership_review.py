"""Render the aggregate review as a readable Markdown report."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
r = json.loads((root/'reports/membership_composition_review_2026-09-22.json').read_text())
s = r['segments']
pops = ['All Members','Regular','Junior','Unclassified']
lines = ['# Membership composition review', '',
         'Active memberships from the September 21–22, 2026 exports. Trials and test clubs excluded. NH memberships included. Aggregates used by the local membership composition dashboard.', '',
         'One membership was exported as Regular on September 21 and Junior on September 22. The approved resolution uses its later Junior classification, reducing Regular by one. No other memberships were deduplicated by golfer.', '',
         'These live exports are not a certified single-time snapshot. The source database is ghin2020pilot; its connection identity still needs confirmation as Production BigData.', '']

lines += [r.get('scope', {}).get('label', 'Worldwide Associations'), r.get('scope', {}).get('definition', ''), '']

def table(title, rows):
    lines.extend(['## '+title,'','| Measure | '+' | '.join(pops)+' |','|---|---:|---:|---:|---:|'])
    for label,values in rows:
        lines.append('| '+label+' | '+' | '.join(values)+' |')
    lines.append('')

table('Membership and golfer counts', [(label,[f'{s[p][key]:,}' for p in pops]) for label,key in [
    ('Memberships','total'),('Unique golfers','unique_golfers'),
    ('Golfers with multiple memberships','multi_membership_golfers'),
    ('Memberships beyond each golfer’s first','additional_memberships')]])
lines += ['Unique golfers and multi-membership counts are recalculated within each selection and are not additive across selections.', '']

for title,field,order in [
    ('Access type','access',['Public','Private','Unknown — green-grass access not specified']),
    ('Club type','club_type',['Type 1','Type 2','Type 3','GC Clubs']),
    ('Gender','gender',['Male','Female','Unknown']),
    ('Public breakdown','public_breakdown',['Public Green Grass Clubs','Semi-Private','Resort','Municipal','Military','Affiliate / WORE','Virtual clubs / eClubs','GC Clubs']),
    ('Age bands','age',['Under 18','18–24','25–34','35–44','45–54','55–64','65+','Unknown / invalid']),
    ('Handicap Index bands','handicap',['Plus / Scratch','0.1–5.0','5.1–10.0','10.1–15.0','15.1–20.0','20.1–30.0','30.1+','No Index','Unknown'])]:
    rows=[]
    for label in order:
        values=[]
        for p in pops:
            n=s[p][field].get(label,0)
            denominator=s[p]['access']['Public'] if field=='public_breakdown' else s[p]['total']
            values.append(f'{n:,} ({100*n/denominator:.2f}%)')
        rows.append((label,values))
    table(title,rows)
    if field=='public_breakdown':
        lines += ['Percentages use Public memberships only. GC Clubs have precedence. Source Public splits by Type 1 (Public Green Grass Clubs), Type 2 (Affiliate), and Type 3 (Virtual clubs/eClubs). Other known categories retain their detail; unspecified Type 2/3 categories become Affiliate/eClub.', '']

table('Averages', [(label,[f"{s[p]['averages'][key]['mean']:.2f}" for p in pops]) for label,key in [
    ('Age — all','age_all'),('Age — male','age_Male'),('Age — female','age_Female'),
    ('Handicap Index — all','handicap_all'),('Handicap Index — male','handicap_Male'),('Handicap Index — female','handicap_Female')]])
lines += ['Averages are membership-weighted. Age averages exclude missing ages and the review’s provisional invalid-age range (below 0 or above 120). Handicap Index averages exclude NH and unavailable values; valid plus indexes retain their numeric sign.', '',
          '## Checks and limitations','',
          '- Every main composition table sums to the membership total in each selection. Public detail sums to Public memberships.',
          '- All 57 club IDs from the September GC source were matched; 543,298 memberships are classified as GC Clubs, all Regular in these exports.',
          '- 309 memberships have no matching golfer details. Their membership records remain included.',
          '- 1,710,489 memberships (43.42%) have missing or invalid ages, including 7,663 ages outside 0–120. Age averages describe the usable subset only.',
          '- 354 memberships have an unknown Handicap Index; these are separate from the 449,776 explicitly recorded as NH.',
          '- Junior is a membership designation, not an age rule. The Junior export includes 142 memberships aged 25 or older; these remain Junior.',
          '- One duplicate membership across Regular and Junior is assigned to the later Junior export for this review only. Source CSVs are unchanged.',
          '- Extraction on different dates can miss changes between groups, even after duplicate checks. Trends and historical August 1 values cannot be established from these exports.', '',
          '## Source classification combinations','',
          'Evan approved retaining the recorded Type 1/2/3 for Affiliate/WORE while treating their access as Public. GC Clubs remain separate. Type 2/3 are Public even when the source category says Private. The following combinations are retained for traceability:', '',
          '| Source combination and applied mapping | Memberships |','|---|---:|']
for key,n in r['classification_conflicts'].items():
    lines.append(f'| {key} | {n:,} |')
lines += ['', 'These counts flag source combinations, not additional memberships to subtract. Some rules may overlap. Preserve all original categories and types.', '',
          '## Source files','']
for f in r['sources']:
    lines.append(f"- {f['file']}: {f['rows']:,} records; extracted {f['extraction_start']} to {f['extraction_end']}.")
lines += ['', 'GC lookup: the 57 distinct Club Number values in the September GC dashboard Current Month_Golfer Detail.csv source, including all statuses.', '']
out = root/'reports/membership_composition_review_2026-09-22.md'
out.write_text('\n'.join(lines))
print(out)
