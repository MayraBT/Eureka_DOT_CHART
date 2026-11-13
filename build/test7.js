const { chromium } = require('playwright');
(async()=>{ const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1440,height:900}}); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8765/index.html#g3/3.4K'); await p.waitForTimeout(500);
 await p.evaluate(()=>{ document.querySelectorAll('#detail details.sec').forEach(d=>d.open=d.dataset.sec==='STAAR performance'); });
 const s=await p.$('#detail details.sec[data-sec="STAAR performance"]'); await s.scrollIntoViewIfNeeded(); await p.waitForTimeout(200);
 await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/dist_std.png'});
 await p.click('.tabs button[data-view="perf"]'); await p.check('#pBelow'); await p.waitForTimeout(300);
 const n=await p.evaluate(()=>document.querySelectorAll('#ptab tbody tr').length);
 await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/dist_perf.png'});
 const counts={}; for(const g of ['g3','g4','g5']){ await p.selectOption('#courseSel',g); await p.waitForTimeout(300); await p.click('.tabs button[data-view="perf"]'); await p.check('#pBelow'); await p.waitForTimeout(200); counts[g]=await p.evaluate(()=>[document.querySelectorAll('#ptab tbody tr').length]); }
 console.log('below rows g3',n,counts,errs); await b.close(); })();
