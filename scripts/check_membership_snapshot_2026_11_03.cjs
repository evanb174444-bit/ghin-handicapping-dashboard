const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root='/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard',dir=root+'/data/processed/refresh-2026-11-03';const read=n=>JSON.parse(fs.readFileSync(dir+'/'+n+'.json','utf8'));
const ctx={MEMBERSHIP_INTERSECTIONS:read('membership_intersections'),MEMBERSHIP_INDEX_STATS:null,membershipPopulation:'all',document:{addEventListener:()=>{}}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(root+'/scripts/membership_explorer.js','utf8'),ctx);
const counts=read('international_totals').scopes.aga;
for(const pop of ['all','regular','junior']){const r=ctx.membershipExplorerResult({},pop,'membershipType');assert.equal(r.total,counts[pop].memberships);assert.equal(r.unique,counts[pop].uniqueGolfers);assert.equal(r.additional,counts[pop].additionalMemberships);assert.equal(r.groups.reduce((n,g)=>n+g.total,0),r.total);}
const r=ctx.membershipExplorerResult({association:['53','1'],gender:['Female']},'all','association');const expected=read('validation').filteredExplorerCheck;assert.equal(r.total,expected.total);assert.equal(r.unique,expected.unique);assert.equal(r.nh,expected.nh);
ctx.MEMBERSHIP_INDEX_STATS=read('membership_index_stats');const exact=ctx.membershipExplorerResult({},'all','membershipType');assert.equal(exact.indexStats.n,ctx.MEMBERSHIP_INDEX_STATS.meta.validGolfers);assert(Number.isFinite(exact.indexStats.mean));assert(Number.isFinite(exact.indexStats.median));
assert.equal(ctx.MEMBERSHIP_INDEX_STATS.meta.conflictingGolfersExcluded,0,'Conflicting Index values require investigation');
console.log(JSON.stringify({pass:true,explorerPopulations:3,combinedFilter:'female NCGA+Metropolitan',index:exact.indexStats},null,2));
