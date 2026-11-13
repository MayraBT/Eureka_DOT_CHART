const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch(); const errs=[]; const out=[];
  for(const view of ['std','les','cal','perf','moves','grid']){
    const p=await b.newPage({viewport:{width:1440,height:900}}); p.on('pageerror',e=>errs.push(view+': '+e.message));
    await p.goto('http://localhost:8765/index.html#g5/5.3K'); await p.waitForTimeout(500);
    await p.fill('#q','decimal'); await p.waitForTimeout(200); await p.fill('#q',''); await p.waitForTimeout(100);
    await p.goto('http://localhost:8765/index.html#g5/5.3K'); await p.waitForTimeout(400);
    // turn on lens + moves selection
    await p.evaluate(()=>{ setLens('5.3K'); openMoves('5.3K'); });
    await p.click(`.tabs button[data-view="${view}"]`); await p.waitForTimeout(200);
    await p.selectOption('#courseSel','g3'); await p.waitForTimeout(500);
    const st=await p.evaluate(()=>({sel,lens:!!lens,q:$('q').value,mv:mvSel,hash:location.hash,lensbar:!$('lensbar').hidden,detail:$('detail').textContent.slice(0,60),mvd:$('mvDetail').textContent.slice(0,40),hl:document.querySelectorAll('#modlist .lrow.hit').length,cal:$('calSel').textContent.slice(0,40)}));
    out.push(view+' '+JSON.stringify(st));
    await p.close();
  }
  console.log(out.join('\n')); console.log(errs.join('\n')||'no errors'); await b.close();
})();
