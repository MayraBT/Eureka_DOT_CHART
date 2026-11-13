const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8765/index.html'); await p.waitForTimeout(400);
 const v1=await p.evaluate(()=>document.querySelector('.view.on').id);
 await p.click('.tabs button[data-view="cal"]'); await p.selectOption('#courseSel','g4'); await p.waitForTimeout(400);
 const v2=await p.evaluate(()=>document.querySelector('.view.on').id);
 console.log(v1,v2,errs); await b.close(); })();
