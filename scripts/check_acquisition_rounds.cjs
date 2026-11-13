const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=process.argv[2]||path.resolve(__dirname,'..');
const acquisition=JSON.parse(fs.readFileSync(path.join(root,'data/processed/acquisition.json'))),ngf=JSON.parse(fs.readFileSync(path.join(root,'data/processed/ngf_rounds_played.json')));
const context=vm.createContext({ACQUISITION_DATA:acquisition,NGF_ROUNDS_DATA:ngf,document:{addEventListener(){}},fmt:n=>n.toLocaleString('en-US'),esc:s=>String(s)});
vm.runInContext(fs.readFileSync(path.join(root,'scripts/acquisition_rounds_view.js'),'utf8'),context);
let checked=0;
for(const gcOnly of [false,true])for(const year of [2024,2025,2026])for(const mode of ['monthly','ytd']){
 vm.runInContext(`acquisitionRoundsGCOnly=${gcOnly}`,context);
 const history=(gcOnly?acquisition.gc.history:acquisition.history).aga.regular;
 const rows=vm.runInContext(`acquisitionRoundsRows(${year},'${mode}')`,context);
 for(const row of rows){
  const extract=y=>{const months=history[y].slice(mode==='ytd'?0:row.month-1,row.month);return months.some(n=>n==null)?null:months.reduce((a,b)=>a+b,0);};
  const current=extract(year),prior=extract(year-1),report=ngf.months.find(r=>r.month===row.key);
  assert.equal(row.current,current);assert.equal(row.prior,prior);
  if(current!=null)assert(Math.abs(row.ghin-(current/prior-1)*100)<1e-10);
  assert.equal(row.rounds,report?(mode==='ytd'?report.ytdYoy:report.monthlyYoy):null);
  if(row.gap!=null)assert.equal(row.gap,row.ghin-row.rounds);checked++;
 }
 const markup=vm.runInContext(`acquisitionRoundsYear=${year};acquisitionRoundsMode='${mode}';acquisitionRoundsPage()`,context);
 assert(markup.includes('nr-data" open'));assert(!markup.includes('score entries'));
 const values=rows.flatMap(r=>[r.ghin,r.rounds]).filter(n=>n!=null),step=Math.max(...values)-Math.min(...values)>30?10:5,low=Math.min(-10,Math.floor(Math.min(0,...values)/step)*step),high=Math.max(20,Math.ceil(Math.max(0,...values)/step)*step);
 assert(values.every(v=>v>=low&&v<=high));
}
vm.runInContext("acquisitionRoundsGCOnly=false",context);
const rows=vm.runInContext("acquisitionRoundsRows(2026,'ytd')",context),common=rows.filter(r=>r.rounds!=null&&r.ghin!=null).at(-1);
assert.equal(common.month,9);assert.equal(common.current,acquisition.history.aga.regular[2026].slice(0,9).reduce((a,b)=>a+b,0));assert.equal(common.prior,acquisition.history.aga.regular[2025].slice(0,9).reduce((a,b)=>a+b,0));assert.equal(rows[9].rounds,null);assert.equal(rows[10].current,null);
vm.runInContext("acquisitionRoundsGCOnly=true",context);
const gcCommon=vm.runInContext("acquisitionRoundsRows(2026,'ytd')",context)[8];
assert.equal(gcCommon.current,131165);assert.equal(gcCommon.prior,135242);assert.equal(gcCommon.rounds,common.rounds);
console.log(JSON.stringify({gcCurrentAcquisition:gcCommon.current,gcPriorAcquisition:gcCommon.prior,gcAcquisitionYoy:gcCommon.ghin,checkedRows:checked,latestCommonMonth:common.key,currentAcquisition:common.current,priorAcquisition:common.prior,acquisitionYoy:common.ghin,ngfYoy:common.rounds,missingDataNotZero:true,axisContainsAllValues:true,style:'shared Scores comparison CSS',published:false}));
