#!/usr/bin/env node
"use strict";
const fs=require("fs"),path=require("path");
const output=path.join(__dirname,"..","data","processed","mock_metrics.json");
const associations=[
  ["FSGA","Florida State Golf Association",.19],["NCGA","Northern California Golf Association",.18],
  ["SCGA","Southern California Golf Association",.17],["MASS","Mass Golf",.11],
  ["TGA","Texas Golf Association",.14],["GAP","Golf Association of Philadelphia",.10],
  ["CGA","Colorado Golf Association",.11]
];
const membershipTypes=[["REGULAR","Regular",.84],["JUNIOR","Junior",.16]],clubTypes=[["TYPE_1","Type 1",.28],["TYPE_2","Type 2",.24],["TYPE_3","Type 3",.26],["GC_CLUBS","GC Clubs",.22]],accessTypes=[["PUBLIC","Public",.64],["PRIVATE","Private",.36]],genders=[["MALE","Male",.77],["FEMALE","Female",.23]];
const providers=["GHIN","Golf Genius","The Grint","New Start","Mobile ForeTees","AdminEscape","Other"],providerShare=[.69,.105,.07,.045,.035,.025,.03];
function hash(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return(h>>>0)/4294967295}
const records=[];
for(const year of [2025,2026])for(let month=1;month<=12;month++)for(const [associationId,,af] of associations)for(const [membershipType,,mf] of membershipTypes)for(const [clubType,,cf] of clubTypes)for(const [accessType,,xf] of accessTypes)for(const [gender,,gf] of genders){
  const key=[year,month,associationId,membershipType,clubType,accessType,gender].join("|");
  const noise=.965+hash(key)*.07,season=1+Math.sin((month-3)/12*Math.PI*2)*.045,growth=year===2026?1.052:1;
  const activeGolfers=Math.round(3340000*af*mf*cf*xf*gf*noise*growth*season);
  const ghinActiveGolfers=Math.round(activeGolfers*(.885+hash(key+"g")*.045));
  const scoreRate=(1.17+month*.075)*(1+Math.sin((month-2)/12*Math.PI*2)*.22);
  const scoresGhin=Math.round(ghinActiveGolfers*scoreRate),scoresAga=Math.round(scoresGhin*(1.055+hash(key+"a")*.025));
  const appShare=.77+hash(key+"app")*.10,webShare=.075+hash(key+"web")*.025,kioskShare=Math.max(0,1-appShare-webShare);
  const gpsSubscribers=Math.round(activeGolfers*(.068+(month/12)*.018+hash(key+"gps")*.018));
  const activeAppUsers=Math.round(activeGolfers*(.56+hash(key+"users")*.16)),repeatUsers=Math.round(activeAppUsers*(.61+hash(key+"repeat")*.13));
  const providerScores={};providers.forEach((p,i)=>providerScores[p]=Math.round(scoresAga*providerShare[i]));
  records.push({reportPeriod:`${year}-${String(month).padStart(2,"0")}`,year,month,associationId,membershipType,clubType,accessType,gender,activeGolfers,ghinActiveGolfers,scoresAga,scoresGhin,appScores:Math.round(scoresGhin*appShare),webScores:Math.round(scoresGhin*webShare),kioskScores:Math.round(scoresGhin*kioskShare),totalScorePosts:Math.round(scoresGhin*.48),holeByHolePosts:Math.round(scoresGhin*.34),holeStatsPosts:Math.round(scoresGhin*.18),gpsSubscribers,gpsUpgrades:Math.round(gpsSubscribers*.058),gpsRenewals:Math.round(gpsSubscribers*.71),activeAppUsers,repeatUsers,providerScores});
}
const dimensions={associationId:[["ALL","All Associations"],...associations.map(x=>x.slice(0,2))],membershipType:[["ALL","All Membership Types"],...membershipTypes.map(x=>x.slice(0,2))],clubType:[["ALL","All Club Types"],...clubTypes.map(x=>x.slice(0,2))],accessType:[["ALL","All Access Types"],...accessTypes.map(x=>x.slice(0,2))],gender:[["ALL","All Genders"],...genders.map(x=>x.slice(0,2))]};
for(const key of Object.keys(dimensions))dimensions[key]=dimensions[key].map(([id,label])=>({id,label}));
fs.writeFileSync(output,JSON.stringify({meta:{generatedAt:new Date().toISOString(),mockData:true,grain:"report period x association x membership type x club type x access type x gender",months:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],providers,dimensions},records},null,2)+"\n");
console.log(`Generated ${records.length} records at ${output}`);
