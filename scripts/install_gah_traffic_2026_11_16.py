from pathlib import Path
import csv,io,json,re,hashlib,gzip,shutil
r=Path('/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard');p=r/'Handicapping and GHIN Dashboard.html';s=p.read_text();old=s
b=r/'backups/gah-traffic-2026-11-16';b.mkdir(exist_ok=True)
if not (b/'dashboard.html.gz').exists():
 with gzip.open(b/'dashboard.html.gz','wt') as f:f.write(s)
records=[]
for month,n in [(9,13),(10,14)]:
 raw=Path(f'/Users/EvanBelfi/Downloads/download ({n}).csv');text=raw.read_text(encoding='utf-8-sig');period=f'2026{month:02d}01-2026{month:02d}'+('30' if month==9 else '31');assert period in text and 'GAH traffic validation Nov 2026-Free form 1' in text
 rows=list(csv.reader(io.StringIO('\n'.join(l for l in text.splitlines() if l.strip() and not l.startswith('#')))));assert rows[0]==['Page path + query string','Sessions','Engaged sessions'];data={row[0]:[int(row[1]),int(row[2])] for row in rows[1:]};assert data[''][0]>data['/'][0]>0
 dest=r/f'data/raw/ga4/2026-11-16/getahandicap_traffic_{period}.csv';shutil.copy2(raw,dest)
 vals={'sessions':data[''][0],'bounceHomeSessions':data['/'][0],'bounceHomeEngaged':data['/'][1],'bouncePaymentSessions':data['/payment'][0],'bouncePaymentEngaged':data['/payment'][1],'paymentPageSessions':data['/payment'][0],'pricingSessions':data['/aga-search'][0],'profileSessions':data['/profile-lookup'][0]}
 for field,value in vals.items():
  pattern=r'(\n  '+field+r':\{[^\n]*?2026:\[)([^\]]+)(\])';m=re.search(pattern,s);assert m,field
  a=json.loads('['+m[2]+']');assert a[month-1] is None;a[month-1]=value;s=s[:m.start(2)]+','.join('null' if v is None else str(v) for v in a)+s[m.end(2):]
 records.append({'month':month,'values':vals,'source':str(dest.relative_to(r)),'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'availableDataPercent':100,'homeBounceRate':(1-data['/'][1]/data['/'][0])*100,'paymentBounceRate':(1-data['/payment'][1]/data['/payment'][0])*100})
s=s.replace('Funnel through October 2026 · Traffic through August 2026','Funnel and traffic through October 2026')
s=s.replace('Array.from({length:8},(_,i)=>i):[selectedMonth]','Array.from({length:10},(_,i)=>i):[selectedMonth]')
s=s.replace('Jan–Aug 2026','Jan–Oct 2026')
s=s.replace('Traffic and bounce-rate data remain through August 2026.','Traffic and bounce-rate data refreshed through October 2026 using the hostname getahandicap.usga.org and exact page paths including query strings: / for homepage and /payment for checkout. September and October reports use 100% of available data. October engagement jumps sharply in GA4 (homepage bounce 1.3% versus 39.3% in September); treat this as a reporting break pending tracking validation, rather than assuming a behavioral improvement.')
assert s!=old and 'Funnel through October 2026 · Traffic through August 2026' not in s
p.write_text(s)
report={'refreshed':'2026-11-16','method':'Hostname exactly matches getahandicap.usga.org; site total sessions, exact page path + query string / and /payment; weighted bounce=1-sum(engaged)/sum(sessions). Prior history preserved.','months':records,'octoberEngagementBreakFlagged':True,'published':False}
(r/'data/processed/getahandicap_traffic_2026-11-16.json').write_text(json.dumps(report,indent=2)+'\n');(r/'reports/getahandicap_traffic_2026-11-16.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copy2('/tmp/install_gah_traffic.py',r/'scripts/install_gah_traffic_2026_11_16.py')
preview=(r/'scripts/serve_local_review.py').read_text();exec(preview[:preview.index('class Handler')])
print(json.dumps(records,indent=2))
