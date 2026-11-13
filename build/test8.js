const { chromium } = require('playwright');
const S='/tmp/claude-0/-home-claude/78bf741d-87e3-5321-ab17-c985254f55e2/scratchpad/';
(async()=>{ const b=await chromium.launch(); const errs=[]; const report=[];
 for(const [w,h,tag] of [[1440,900,'d'],[390,844,'m']]){
  const p=await b.newPage({viewport:{width:w,height:h}}); p.on('pageerror',e=>errs.push(e.message));
  for(const g of ['gk','g3','g5']){
   await p.goto('http://localhost:8765/index.html#'+g+'/'+({gk:'K.2E',g3:'3.4K',g5:'5.3K'})[g]); await p.waitForTimeout(400);
   for(const v of ['cal','les','std','perf','moves','grid']){
     if(!(await p.isVisible(`.tabs button[data-view="${v}"]`))) continue;
     await p.click(`.tabs button[data-view="${v}"]`); await p.waitForTimeout(250);
     if(v==='les') await p.evaluate(()=>document.querySelectorAll('#modlist details').forEach(d=>d.open=true));
     const clipped=await p.evaluate(()=>{ let n=0, ex=[]; document.querySelectorAll('.view.on *').forEach(el=>{ const cs=getComputedStyle(el); if(el.children.length===0 && el.textContent.trim().length>3 && cs.overflow!=='visible' && el.scrollWidth>el.clientWidth+1 && cs.display!=='none' && !el.closest('.gridwrap,.calwrap,.acrosswrap,table.ptab')){ n++; if(ex.length<3) ex.push(el.tagName+'.'+el.className+': '+el.textContent.trim().slice(0,40)); } if(cs.textOverflow==='ellipsis' && el.scrollWidth>el.clientWidth+1){ n++; ex.push('ELLIPSIS '+el.textContent.slice(0,40)); } }); return [n,ex]; });
     const ov=await p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
     report.push(`${tag} ${g} ${v} clipped=${clipped[0]} ${clipped[1].join(' | ')} pageOverflow=${ov}`);
     if(g==='g3'&&tag==='d') await p.screenshot({path:S+'w_'+v+'.png'});
     if(g==='g3'&&tag==='m'&&(v==='grid'||v==='cal')) await p.screenshot({path:S+'wm_'+v+'.png'});
   }
  }
  await p.close();
 }
 console.log(report.filter(r=>!/clipped=0 .*pageOverflow=0$/.test(r)).join('\n')||'all clean'); console.log(errs.join('\n')||'no errors'); await b.close(); })();
