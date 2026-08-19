#!/usr/bin/env node
"use strict";
const fs=require("fs"),path=require("path");
const file=path.join(__dirname,"..","data","processed","mock_metrics.json"),data=JSON.parse(fs.readFileSync(file,"utf8"));
const errors=[],seen=new Set(),required=["reportPeriod","year","month","associationId","membershipType","clubType","accessType","gender","activeGolfers","scoresGhin"];
for(const [i,r] of data.records.entries()){
  for(const k of required)if(r[k]===undefined||r[k]===null)errors.push(`Record ${i}: missing ${k}`);
  const key=[r.reportPeriod,r.associationId,r.membershipType,r.clubType,r.accessType,r.gender].join("|");if(seen.has(key))errors.push(`Duplicate grain: ${key}`);seen.add(key);
  if(r.month<1||r.month>12)errors.push(`Record ${i}: invalid month`);
  for(const [k,v] of Object.entries(r))if((typeof v==="number")&&(!Number.isFinite(v)||v<0))errors.push(`Record ${i}: invalid ${k}`);
  if(Math.abs(r.appScores+r.webScores+r.kioskScores-r.scoresGhin)>2)errors.push(`Record ${i}: channels do not reconcile`);
  if(Math.abs(r.totalScorePosts+r.holeByHolePosts+r.holeStatsPosts-r.scoresGhin)>2)errors.push(`Record ${i}: score types do not reconcile`);
}
if(data.records.length!==5376)errors.push(`Expected 5376 records, found ${data.records.length}`);
if(errors.length){console.error(errors.slice(0,30).join("\n"));process.exit(1)}
console.log(`PASS: ${data.records.length} unique records; required fields, dates, nonnegative metrics, channel totals and score-entry totals validated.`);
