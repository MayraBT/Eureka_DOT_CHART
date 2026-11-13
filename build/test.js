const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch(); const errs=[];
  const p=await b.newPage({viewport:{width:1440,height:900}});
  p.on('pageerror',e=>errs.push('PAGEERR '+e.message)); p.on('console',m=>{ if(m.type()==='error') errs.push('CONSOLE '+m.text()); });
  const url='http://localhost:8765/index.html';
  for(const g of ['g3','g4','g5']){
    await p.goto(url+'#'+g); await p.waitForTimeout(600);
    for(const v of ['cal','les','std','perf','moves','grid']){
      await p.click(`.tabs button[data-view="${v}"]`); await p.waitForTimeout(200);
    }
  }
  await p.goto(url+'#g3/3.4K'); await p.waitForTimeout(500);
  await p.click('#detail .secbar button[data-a="1"]').catch(e=>errs.push('no secbar'));
  await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/std.png',fullPage:false});
  await p.click('.tabs button[data-view="cal"]'); await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/cal.png'});
  await p.click('.tabs button[data-view="les"]'); await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/les.png'});
  await p.click('.tabs button[data-view="grid"]'); await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/grid.png'});
  await p.click('.tabs button[data-view="perf"]'); await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/perf.png'});
  await p.click('.tabs button[data-view="moves"]'); await p.waitForTimeout(300);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/moves.png'});
  // help
  await p.click('#helpOpen'); await p.waitForTimeout(200);
  await p.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/help.png'});
  await p.keyboard.press('Escape');
  // phone
  const m=await b.newPage({viewport:{width:390,height:844}});
  m.on('pageerror',e=>errs.push('M PAGEERR '+e.message));
  for(const g of ['g3','g4','g5']){ await m.goto(url+'#'+g+'/'+({g3:'3.3H',g4:'4.3D',g5:'5.3K'})[g]); await m.waitForTimeout(500);
    const ov=await m.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth); if(ov>1) errs.push(g+' phone overflow '+ov); }
  await m.screenshot({path:'/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/phone.png'});
  // broken images
  const imgs=await p.evaluate(()=>{ const out=[]; for(const [c,a] of Object.entries(PERF)) for(const d of a) out.push(d.img); return out; });
  console.log('items',imgs.length);
  console.log(errs.join('\n')||'no errors');
  await b.close();
})();
