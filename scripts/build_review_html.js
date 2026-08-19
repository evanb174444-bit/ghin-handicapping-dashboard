#!/usr/bin/env node
"use strict";
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const sourceHtml = fs.readFileSync(path.join(root, "index.html"), "utf8");
const css = fs.readFileSync(path.join(root, "assets", "styles.css"), "utf8");
let js = fs.readFileSync(path.join(root, "assets", "app.js"), "utf8");
const data = fs.readFileSync(path.join(root, "data", "processed", "mock_metrics.json"), "utf8")
  .replace(/<\/script/gi, "<\\/script");

js = js.replace(
  /async function init\(\)\{try\{const response=await fetch\("data\/processed\/mock_metrics\.json"\);if\(!response\.ok\)throw new Error\(`HTTP \$\{response\.status\}`\);const data=await response\.json\(\);records=data\.records;meta=data\.meta;setupFilters\(\);render\(\)\}catch\(error\)\{console\.error\(error\);\$\("app"\)\.innerHTML=`<div class="empty"><h3>Dashboard data could not be loaded<\/h3><p>Serve this folder over HTTP \(for example, <code>python3 -m http\.server<\/code>\) and refresh\.<\/p><\/div>`\}\}/,
  'function init(){try{const data=JSON.parse(document.getElementById("embeddedDashboardData").textContent);records=data.records;meta=data.meta;setupFilters();render()}catch(error){console.error(error);$("app").innerHTML=`<div class="empty"><h3>Dashboard data could not be loaded</h3></div>`}}'
);

if (js.includes('fetch("data/processed/mock_metrics.json")')) {
  throw new Error("Could not replace external data loader");
}

const bundled = sourceHtml
  .replace('<link rel="stylesheet" href="assets/styles.css">', `<style>\n${css}\n</style>`)
  .replace('<script src="assets/app.js"></script>', `<script id="embeddedDashboardData" type="application/json">${data}</script>\n<script>\n${js}\n</script>`);

fs.writeFileSync(path.join(root, "Handicapping and GHIN Dashboard.html"), bundled);
console.log("Built Handicapping and GHIN Dashboard.html");
