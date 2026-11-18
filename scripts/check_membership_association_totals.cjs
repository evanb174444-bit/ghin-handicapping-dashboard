const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),r='/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard';
const read=n=>JSON.parse(fs.readFileSync(r+'/data/processed/'+n+'.json'));
const ctx=vm.createContext({MEMBERSHIP_ASSOCIATION_DATA:read('membership_associations'),MEMBERSHIP_CLUB_DATA:read('membership_clubs'),MEMBERSHIP_ASSOCIATION_UNIQUE_PATTERNS:read('membership_association_unique_patterns'),membershipPopulation:'all',document:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(r+'/scripts/membership_associations_view.js','utf8'),ctx);
const expected=read('international_totals');
for(const scope of ['all','aga','international'])for(const population of ['all','regular','junior']){ctx.membershipPopulation=population;ctx.rows=ctx.MEMBERSHIP_ASSOCIATION_DATA.scopes[scope][population];const t=vm.runInContext('membershipAssociationTotals(rows)',ctx);assert.equal(t.activeGolfers,expected.scopes[scope][population].uniqueGolfers);assert.equal(t.memberships,expected.scopes[scope][population].memberships);}
ctx.membershipPopulation='all';ctx.rows=ctx.MEMBERSHIP_ASSOCIATION_DATA.scopes.aga.all.filter(x=>x.region==='West');const totals=vm.runInContext('membershipAssociationTotals(rows)',ctx),baseline=JSON.parse(fs.readFileSync(r+'/reports/membership_association_totals_validation.json')).westRawRecordChecks;
for(const [key,value] of Object.entries(baseline))assert(Math.abs(totals[key]-value)<1e-8,key+': '+totals[key]+' != '+value);
assert(totals.activeGolfers<ctx.rows.reduce((s,x)=>s+x.activeGolfers,0));ctx.rows=[];assert.equal(vm.runInContext('membershipAssociationTotals(rows).activeGolfers',ctx),0);assert.equal(vm.runInContext('membershipAssociationTotals(rows).averageAge',ctx),null);
console.log('PASS: totals match all nine scope/population snapshots; every West metric independently matches private records, with cross-association deduplication and empty selections verified.');
