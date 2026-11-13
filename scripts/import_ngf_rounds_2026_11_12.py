from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import re,json,hashlib,datetime
import pdfplumber
from pypdf import PdfReader
P=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');RAW=P/'data/raw/ngf/2026-11-12';RAW.mkdir(parents=True,exist_ok=True)
URL='https://www.ngf.org/monthly-rounds-played-reports/'
def fetch(url):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (public research)'}),timeout=60) as r:return r.read()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.href=None;self.text=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.text=[]
 def handle_data(self,t):
  if self.href:self.text.append(t)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append((self.href,' '.join(self.text).strip()));self.href=None
html=fetch(URL);(RAW/'index.html').write_bytes(html);parser=Links();parser.feed(html.decode())
months=['January','February','March','April','May','June','July','August','September','October','November','December'];sources={}
for href,label in parser.links:
 m=re.fullmatch('('+ '|'.join(months)+r')\s+(202[3-6])',label)
 if m and '.pdf' in href.lower():sources[f'{m[2]}-{months.index(m[1])+1:02}']=urljoin(URL,href)
assert len(sources)>=40,len(sources)
def parse(item):
 period,url=item;f=RAW/(period+'.pdf');data=f.read_bytes() if f.exists() else fetch(url)
 if not f.exists():f.write_bytes(data)
 reader=PdfReader(f);pages=[p.extract_text() or '' for p in reader.pages];text='\n'.join(pages)
 (RAW/(period+'.txt')).write_text(text)
 pattern=r'UNITED\s+STATES\s+([+\-−]?\d+(?:\.\d+)?)\s*%\s+([+\-−]?\d+(?:\.\d+)?)\s*%'
 m=re.search(pattern,text,re.I)
 with pdfplumber.open(f) as pdf:
  checked='\n'.join(p.filter(lambda obj:obj.get('object_type')!='char' or abs(obj.get('matrix',[1,0])[1])<0.001).extract_text() or '' for p in pdf.pages)
 independent=re.search(pattern,checked,re.I)
 if not m or not independent or m.groups()!=independent.groups():return {'month':period,'source':url,'error':'Independent national-row extraction mismatch','sha256':hashlib.sha256(data).hexdigest()}
 sourcepage=next(i+1 for i,t in enumerate(pages) if re.search(pattern,t,re.I))
 return {'month':period,'monthlyYoy':float(m[1].replace('−','-')),'ytdYoy':float(m[2].replace('−','-')),'source':url,'sourcePage':sourcepage,'sha256':hashlib.sha256(data).hexdigest()}
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(parse,sorted(sources.items())))
errors=[r for r in rows if 'error' in r];print('Reports',len(rows),'parse failures',errors,flush=True)
out={'meta':{'source':URL,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'publisher':'NGF / Golf Datatech','measure':'United States rounds played year-over-year percentage change','rawRoundCountsAvailable':False,'latestMonth':max(sources),'archiveIndexSha256':hashlib.sha256(html).hexdigest()},'months':rows}
(P/'data/processed/ngf_rounds_played.json').write_text(json.dumps(out,indent=2))
print('2026 rows',[(r['month'],r.get('monthlyYoy'),r.get('ytdYoy')) for r in rows if r['month'].startswith('2026')],flush=True)
assert not errors,'Inspect saved report text before installation'
