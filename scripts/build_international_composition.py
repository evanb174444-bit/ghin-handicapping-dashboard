"""Build composition aggregates from international rows; never infer absent club classifications."""
import csv,json,math,copy
from collections import Counter
from review_membership_exports import classify
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'data/processed/membership_composition.json').read_text())['populations']
totals=json.loads((ROOT/'data/processed/international_totals.json').read_text())['scopes']
rows={}
with Path('/Users/EvanBelfi/Downloads/01_active_international_full_2026-09-25.csv.csv').open(encoding='utf-8-sig') as f:
 for r in csv.DictReader(f):rows[r['membership_id']]=r

def number(x):
 try:
  v=float(x);return v if math.isfinite(v) else None
 except (ValueError,TypeError):return None

def profile(records,kind,bands):
 out={'bands':bands}
 for group in ['all','male','female']:
  rr=[r for r in records if group=='all' or r['gender'].lower()==group]
  counts=[0]*len(bands);vals=[]
  for r in rr:
   v=number(r['age_at_extraction'] if kind=='age' else r['handicap_index'])
   if kind=='age':
    if v is None or not 0<=v<=120:i=len(bands)-1
    else:i=next(i for i,e in enumerate([18,25,35,45,55,65,121]) if v<e);vals.append(v)
   else:
    if r['handicap_index_display'].upper()=='NH':i=len(bands)-2
    elif v is None:i=len(bands)-1
    else:i=next(i for i,e in enumerate([0,5,10,15,20,30,float('inf')]) if v<=e);vals.append(v)
   counts[i]+=1
  out[group+'Counts']=counts;out[group]=[100*n/len(rr) if rr else 0 for n in counts];out[group+'Average']=sum(vals)/len(vals) if vals else None
 return out
out={'international':{},'all':{}}
for pop in ['all','regular','junior']:
 records=[r for r in rows.values() if pop=='all' or r['usga_membership_type']=={'regular':'Standard','junior':'Junior'}.get(pop)]
 d={'counts':totals['international'][pop],'highIndexInsight':{'femaleShare':None},'clubMetadataAvailable':True}
 for key,labels,field in [('membership',['Regular','Junior','Unclassified'],'usga_membership_type'),('gender',['Male','Female','Unknown'],'gender')]:
  counts=dict.fromkeys(labels,0)
  for r in records:
   v=r[field];v={'Standard':'Regular','Junior':'Junior'}.get(v,'Unclassified') if key=='membership' else v if v in labels else 'Unknown'
   counts[v]+=1
  d[key]=list(counts.items())
 access=Counter();clubs=Counter()
 for r in records:
  a,c,_=classify(r['club_id'],r['club_category'],r['club_type'],set())
  access[a if a in ['Public','Private'] else 'Unknown — green-grass access not specified']+=1;clubs[c]+=1
 d['access']=[[k,access[k]] for k in ['Public','Private','Unknown — green-grass access not specified']]
 d['club']=[[k,clubs[k]] for k in ['Type 1','Type 2','Type 3','GC Clubs','Unknown'] if k!='Unknown' or clubs[k]]
 for kind in ['age','handicap']:d[kind]=profile(records,kind,base[pop][kind]['bands'])
 d['quality']={'ageUnknown':d['age']['allCounts'][-1],'missingGolferDetails':sum(not r['matched_golfer_id'] for r in records)}
 out['international'][pop]=d
 merged=copy.deepcopy(base[pop]);merged['counts']=totals['all'][pop];merged['clubMetadataAvailable']=True
 for key in ['membership','gender','access','club']:
  counts=dict(merged[key])
  for label,n in d[key]:counts[label]=counts.get(label,0)+n
  merged[key]=list(counts.items())
 for kind in ['age','handicap']:
  for group in ['all','male','female']:
   a=base[pop][kind];b=d[kind];counts=[x+y for x,y in zip(a[group+'Counts'],b[group+'Counts'])];merged[kind][group+'Counts']=counts;merged[kind][group]=[100*n/sum(counts) if sum(counts) else 0 for n in counts]
   end=-1 if kind=='age' else -2;na=sum(a[group+'Counts'][:end]);nb=sum(b[group+'Counts'][:end]);merged[kind][group+'Average']=((a[group+'Average'] or 0)*na+(b[group+'Average'] or 0)*nb)/(na+nb) if na+nb else None
 merged['quality']['ageUnknown']+=d['quality']['ageUnknown'];merged['quality']['missingGolferDetails']+=d['quality']['missingGolferDetails']
 out['all'][pop]=merged
 for data in [d,merged]:
  for key in ['membership','gender','access','club']:assert sum(n for _,n in data[key])==data['counts']['memberships']
  for kind in ['age','handicap']:assert sum(data[kind]['allCounts'])==data['counts']['memberships']
(ROOT/'data/processed/international_composition.json').write_text(json.dumps(out,separators=(',',':')))
print('International and combined composition totals and distributions verified.')
