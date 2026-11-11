/* Verificación del cálculo y las interacciones sin instalar dependencias. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../dashboard/running_dashboard.html'),'utf8');
const payload=JSON.parse(html.match(/<script id="running-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const nodes=new Map();
class Element{
 constructor(id=''){this.id=id;this.value='';this.dataset={};this.style={};this.children=[];this.events={};this.open=false;this._html='';this.firstChild={textContent:''};this.parentNode={classList:{add(){}}};}
 set innerHTML(s){this._html=s;this.children=[];for(const m of s.matchAll(/<button data-year="([^"]+)"/g)){const el=new Element();el.dataset.year=m[1];this.children.push(el);}}
 get innerHTML(){return this._html;}
 setAttribute(k,v){this[k]=v;}
 removeAttribute(k){delete this[k];}
 addEventListener(k,fn){this.events[k]=fn;}
 append(el){this.children.push(el);}
 insertBefore(el){this.children.push(el);}
 replaceChildren(){this.children=[];this._html='';}
 querySelector(sel){return new Element(sel);}
 closest(){return {insertBefore(){}};}
 focus(){}
 click(){this.clicked=true;}
 showModal(){this.open=true;}
 close(){this.open=false;}
}
function get(id){if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id);}
get('running-data').textContent=JSON.stringify(payload);get('pageSize').value='10';
const configs=[];class Chart{constructor(canvas,config){this.config=config;configs.push(config);}destroy(){}resize(){}}
let blob;
const views=['resumen','analisis','objetivos','marcas','historial'].map(view=>{const el=new Element();el.dataset.view=view;return el;});
const routes=views.map(v=>{const el=new Element();el.dataset.route=v.dataset.view;return el;});
const context=vm.createContext({console,location:{hash:'#resumen'},document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:s=>s==='[data-view]'?views:s==='[data-route]'?routes:[],documentElement:{dataset:{theme:'light'}}},window:{Chart,addEventListener:()=>{}},Chart,getComputedStyle:()=>({getPropertyValue:()=> '#aaaaaa'}),URL:{createObjectURL:b=>{blob=b;return 'blob:test';},revokeObjectURL:()=>{}},Blob,setTimeout:fn=>fn()});
const run=s=>vm.runInContext(s,context);
run(script);
const snapshot=()=>JSON.parse(run('JSON.stringify({count:state.rows.length,km:sum(state.rows,"distance_km"),comparable:state.comparable,days:state.dayCount})'));
const all=payload.activities,exterior=all.filter(r=>r.modalidad==='running'),cinta=all.filter(r=>r.modalidad==='treadmill_running');
assert.equal(snapshot().count,exterior.length);assert.equal(snapshot().comparable,false);
assert.ok(Math.abs(snapshot().km-exterior.reduce((s,r)=>s+r.distance_km,0))<1e-7);
assert.equal(run('durationWords(722101)'),'200 h 35 min');
assert.equal(run('durationWords(3599)'),'0 h 59 min');
assert.ok(!html.includes('<footer>'));assert.ok(!html.includes('V4 · LIMA'));assert.ok(!html.includes('<div class="side-foot">'));
const monthly=configs.find(c=>c.data.datasets[0]?.label==='Volumen mensual');
assert.equal(monthly.options.scales.y.grid.display,false);assert.equal(monthly.plugins[0].id,'monthValues');
const volumes=monthly.data.datasets[0].data,mean=volumes.reduce((a,b)=>a+b,0)/volumes.length;
assert.ok(monthly.data.datasets[1].data.every(v=>Math.abs(v-mean)<1e-9));
assert.ok(monthly.data.datasets[0].backgroundColor.some(c=>c==='#426b55'));
assert.ok(!/\.record:nth-child\(4n\+1\)/.test(html));
assert.ok(html.includes('.record:hover'));assert.ok(html.includes('.filterbar{position:relative;top:auto;z-index:1}'));
const initialCharts=[...configs];
for(const c of initialCharts){
 assert.equal(c.options.scales.x.grid.display,false);assert.equal(c.options.scales.y.grid.display,false);
 assert.equal(c.plugins[0].id,'monthValues');
 if(c.type!=='scatter'&&c.data.datasets.some(d=>(d.type||c.type)==='bar'))assert.ok(c.data.datasets.some(d=>/Media/.test(d.label)));
}
const drawn=[];monthly.plugins[0].afterDatasetsDraw({ctx:{save(){},restore(){},fillText:(...args)=>drawn.push(args)},data:monthly.data,getDatasetMeta:()=>({data:volumes.map((v,i)=>({x:i*50,y:100-v}))})});
assert.equal(drawn.length,volumes.filter(v=>v!==0).length);
const sparseDrawn=[];
monthly.plugins[0].afterDatasetsDraw({ctx:{save(){},restore(){},fillText:(...args)=>sparseDrawn.push(args)},data:{datasets:[{label:'Volumen',data:[0,null,21.1,0,21.2]}]},getDatasetMeta:()=>({data:[0,1,2,3,4].map(i=>({x:i*50,y:100}))})});
assert.equal(sparseDrawn.length,2);assert.ok(sparseDrawn.every(([label])=>label!=='0,0'));
assert.ok(run('weekLabel("2025-12-29")').startsWith('Semana 1 · 29/12/2025–04/01/2026'));
run('state.weekSelection="2026-10-26";renderCharts()');
const selectedWeek=configs.at(-1);assert.ok(selectedWeek);
assert.ok(!html.includes('Margen media/maratón y récords'));
assert.ok(!html.includes('id="tolerance"'));
get('years').events.click({target:{dataset:{year:'2026'}}});
assert.equal(get('from').value,'2026-01-01');assert.equal(get('to').value,'2026-12-31');
assert.equal(snapshot().count,exterior.filter(r=>r.fecha_local.startsWith('2026')).length);
get('reset').onclick();
for(const view of ['analisis','objetivos','marcas','historial','resumen']){run(`showPage('${view}')`);assert.equal(views.filter(v=>!v.hidden).length,1);assert.equal(views.find(v=>!v.hidden).dataset.view,view);}
assert.equal(run('RECORD_DISTANCES.length'),8);
assert.equal(run('bestTime([],42.195,null)'),null);
assert.equal(run('bestTime([{distance_km:5,pace_sec_km:300,fastestSplit_5000:1400}],5,"fastestSplit_5000").seconds'),1400);
get('goalName').value='Mi primer reto';get('goalMetric').value='km';get('goalTarget').value='100';get('goalFrom').value='2026-01-01';get('goalTo').value='2026-12-31';get('goalType').value='running';
get('goalForm').onsubmit({preventDefault(){}});assert.equal(run('GOALS.length'),1);
assert.ok(run('goalProgress(GOALS[0]).value')>0);assert.ok(get('goalList').innerHTML.includes('Mi primer reto'));
run('editGoal(1)');get('goalTarget').value='200';get('goalForm').onsubmit({preventDefault(){}});assert.equal(run('GOALS[0].target'),200);assert.equal(run('GOALS.length'),1);
assert.throws(()=>run('validateGoal({...GOALS[0],from:"2026-02-30"})'));
assert.throws(()=>run('validateGoal({...GOALS[0],target:-1})'));
assert.equal(run('goalProgress({...GOALS[0],metric:"time",target:42.195,seconds:1000,from:"2023-01-01",to:"2023-01-02"}).value'),null);
get('newRace').onclick();assert.equal(get('goalMetric').value,'race');
get('goalName').value='Media de primavera';get('goalTarget').value='21.0975';get('goalFrom').value='2027-01-01';get('goalTo').value='2027-04-15';get('goalType').value='running';get('raceLocation').value='Madrid';
get('goalForm').onsubmit({preventDefault(){}});assert.equal(run('GOALS.length'),2);
assert.equal(run('GOALS[1].metric'),'race');assert.equal(run('GOALS[1].location'),'Madrid');
assert.equal(run('goalProgress(GOALS[1]).achieved'),false);assert.ok(get('raceList').innerHTML.includes('Media de primavera'));
assert.equal(run('goalProgress({...GOALS[1],completed:true}).percent'),100);
const runRow=exterior[0];
assert.equal(run(`goalProgress({...GOALS[1],target:${runRow.distance_km},from:'${runRow.fecha_local.slice(0,10)}',to:'${runRow.fecha_local.slice(0,10)}'}).matched`),true);
assert.equal(run(`goalProgress({...GOALS[1],target:${runRow.distance_km},seconds:1,from:'${runRow.fecha_local.slice(0,10)}',to:'${runRow.fecha_local.slice(0,10)}'}).achieved`),false);
// Un clic normal cambia a un único año y sincroniza ambas fechas.
get('years').events.click({target:{dataset:{year:'2025'}}});
assert.equal(get('from').value,'2025-01-01');assert.equal(get('to').value,'2025-12-31');
assert.equal(snapshot().count,exterior.filter(r=>r.fecha_local.startsWith('2025')).length);
assert.equal(snapshot().days,365);
get('years').events.click({target:{dataset:{year:'2024'}}});
assert.equal(get('from').value,'2024-01-01');assert.equal(get('to').value,'2024-12-31');assert.equal(snapshot().days,366);
get('years').events.click({target:{dataset:{year:'2025'}}});
assert.equal(get('from').value,'2025-01-01');assert.equal(get('to').value,'2025-12-31');
assert.equal(snapshot().count,exterior.filter(r=>r.fecha_local.startsWith('2025')).length);
get('years').events.click({target:{dataset:{year:'all'}}});
assert.equal(get('from').value,payload.meta.from.slice(0,10));assert.equal(get('to').value,payload.meta.to.slice(0,10));
assert.equal(snapshot().count,exterior.length);
get('reset').onclick();assert.ok(!html.includes('id="multiYear"'));
assert.ok(get('heroVisual').innerHTML.includes('días con carrera'));
assert.ok(!get('kpis').innerHTML.includes('<svg')); 
assert.equal(run('pace(359.9)'),'6:00');assert.equal(run('pace(null)'),'—');assert.equal(run('days("2024-03-31","2024-03-30")'),1);
assert.ok(configs.length>=18);assert.ok(configs.find(c=>c.options.scales.y.reverse));
assert.equal(configs.find(c=>c.data.datasets.some(d=>d.label==='Tendencia · Exterior')).options.scales.x.type,'linear');
get('type').value='treadmill_running';run('update()');assert.equal(snapshot().count,cinta.length);
assert.equal(run('sum(state.rows,"elevationGain")'),null);
get('type').value='all';run('update()');assert.equal(snapshot().count,all.length);
get('from').value='2026-10-01';get('to').value='2026-10-31';run('update()');assert.equal(snapshot().days,31);assert.equal(snapshot().comparable,true);
const oct=all.filter(r=>r.fecha_local>='2026-10-01'&&r.fecha_local<'2026-11-01');assert.equal(snapshot().count,oct.length);
assert.equal(run('state.previous.length'),all.filter(r=>r.fecha_local>='2026-08-31'&&r.fecha_local<'2026-10-01').length);
get('from').value='2023-07-02';get('to').value='2026-11-05';run('state.years=new Set(["2023","2026"]);update()');assert.equal(snapshot().comparable,false);
run('state.years=new Set();update()');assert.equal(snapshot().count,0);assert.ok(get('tableBody').innerHTML.includes('No hay carreras'));
get('from').value='2026-11-05';get('to').value='2023-07-02';run('update()');assert.equal(snapshot().count,0);assert.equal(get('filterError').hidden,false);
get('reset').onclick();assert.equal(snapshot().count,exterior.length);
run('state.category=0;update()');assert.equal(snapshot().count,exterior.filter(r=>r.distance_km<5).length);
run('state.category=4;update()');assert.equal(snapshot().count,exterior.filter(r=>Math.abs(r.distance_km-21.0975)<=21.0975*.02).length);
get('reset').onclick();get('search').value='no existe esta carrera';get('search').oninput();assert.ok(get('pageInfo').textContent.startsWith('0 resultados'));
get('search').value='';run('state.sort="distance_km";state.direction=-1;state.page=999;renderTable()');assert.ok(!get('pageInfo').textContent.includes('999'));assert.equal(get('next').disabled,true);
run(`openDetail(${JSON.stringify(all[0].activityId)})`);assert.equal(get('detail').open,true);get('closeDetail').onclick();assert.equal(get('detail').open,false);
(async()=>{
 get('saveGoals').onclick();const saved=JSON.parse(await blob.text());assert.equal(saved.version,1);assert.equal(saved.goals[0].target,200);
 const input={files:[{text:async()=>JSON.stringify(saved)}],value:'goals.json'};
 run('GOALS=[]');await get('loadGoals').onchange({target:input});assert.equal(run('GOALS.length'),2);assert.equal(run('GOALS[0].target'),200);assert.equal(run('GOALS[1].metric'),'race');
 await get('loadGoals').onchange({target:{files:[{text:async()=>'{"version":1,"goals":[{}]}'}],value:'bad.json'}});
 assert.equal(run('GOALS.length'),2);assert.ok(get('goalStatus').textContent.startsWith('No se pudo cargar'));
 run('exportCSV()');assert.ok(blob instanceof Blob);const text=await blob.text();
 assert.equal(text.split('\r\n').length,exterior.length+1);assert.ok(text.includes('Ritmo (/km)'));
 console.log('OK: año 2026 y fechas, 5 páginas, objetivos crear/editar/guardar/cargar/validar, 8 distancias, datos reales, gráficos, tabla y CSV.');
})().catch(e=>{console.error(e);process.exitCode=1;});
