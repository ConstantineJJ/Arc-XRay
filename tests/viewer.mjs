import {chromium} from 'playwright';
import {execFileSync} from 'node:child_process';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';

const python=process.env.ARC_XRAY_PYTHON || 'python';
const out=resolve('.test-output');await mkdir(out,{recursive:true});
for(const [project,dir]of [['python-service','python'],['typescript-service','typescript']])
 execFileSync(python,['-B','arc-xray.py','audit','examples/'+project,'--out',out+'/'+dir],{stdio:'pipe'});
const edge='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const browser=await chromium.launch({headless:true,...(process.env.ARC_XRAY_BROWSER?{executablePath:process.env.ARC_XRAY_BROWSER}:existsSync(edge)?{executablePath:edge}:{})});
const checks=[],errors=[];const check=(name,fn)=>{assert.ok(fn,name);checks.push(name);};
const page=await browser.newPage({viewport:{width:1920,height:1080},acceptDownloads:true});
page.on('pageerror',e=>errors.push(e.message));const remote=[];page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url());});
try {
 await page.goto(pathToFileURL(out+'/python/index.html').href);await page.waitForSelector('.node');
 check('offline graph renders',await page.locator('.node').count()>0);check('no remote dependencies',remote.length===0);
 const source=JSON.parse(await readFile(out+'/python/atlas.json','utf8'));
 check('complete initial graph within default bounds',await page.locator('.node').count()===source.views[0].nodes.length);
 await page.locator('.node').first().click();await page.locator('#inspector details:has(pre) summary').first().click();check('source inspector and hash',await page.locator('#inspector').innerText().then(s=>s.includes('SHA-256')));
 const colors=await page.locator('.edge').evaluateAll(es=>es.map(e=>e.getAttribute('stroke')));check('arrows have multiple colors',new Set(colors).size>1);
 await page.locator('.connection').first().focus();await page.keyboard.press('Enter');check('edge inspector',await page.locator('#inspector .relation').count()===2);
 const old=await page.evaluate(()=>ArcXRay.state.scale);await page.locator('#plus').click();check('zoom changes scale',await page.evaluate(()=>ArcXRay.state.scale)>old);
 const canvas=await page.locator('#canvas').boundingBox();const oldX=await page.evaluate(()=>ArcXRay.state.x);await page.mouse.move(canvas.x+canvas.width-20,canvas.y+canvas.height-20);await page.mouse.down();await page.mouse.move(canvas.x+canvas.width-80,canvas.y+canvas.height-50);await page.mouse.up();check('pan moves viewport',await page.evaluate(()=>ArcXRay.state.x)!==oldX);
 await page.locator('#tree').click();check('tree layout switches',await page.evaluate(()=>ArcXRay.state.layout)==='tree');
 const tree=await page.evaluate(()=>({ids:ArcXRay.visible,primary:ArcXRay.primaryEdges,edges:ArcXRay.data.edges}));const parents=new Set();for(const id of tree.primary){const e=tree.edges.find(e=>e.id===id);assert.ok(!parents.has(e.target));parents.add(e.target);}check('tree has at most one main parent',true);
 await page.locator('#options summary').click();await page.locator('#cross').uncheck();check('cross edges can be hidden',await page.locator('.connection.cross').count()===0);await page.locator('#cross').check();
 await page.locator('#collapse').click();check('groups collapse',await page.locator('.node').count()<source.views[0].nodes.length);await page.locator('#expand').click();
 await page.locator('#font').selectOption('1.4');check('independent font setting',await page.evaluate(()=>ArcXRay.state.font)===1.4);
 await page.locator('#confidence').selectOption('inference');check('evidence filter',await page.evaluate(()=>ArcXRay.visible.every(id=>ArcXRay.data.nodes.find(n=>n.id===id)?.status==='inference')));await page.locator('#reset').click();
 await page.locator('#language').selectOption('ru');check('Russian controls',await page.locator('#review').innerText()==='Риски и несоответствия');
 await page.locator('#search').fill('service.py');check('global search returns matches',await page.locator('#search-results button').count()>0);await page.locator('#search-results button').first().click();check('search result opens source card',await page.locator('#inspector h2').innerText()==='service.py');
 await page.locator('#review').click();check('review findings rendered',await page.locator('.finding').count()===source.findings.length);
 await page.locator('.finding button').nth(1).click();check('single finding log',await page.locator('#log-items input:checked').count()===1);await page.locator('dialog form button').click();
 await page.locator('#inspector>button').first().click();check('bulk finding log',await page.locator('#log-items input:checked').count()===source.findings.length);
 await page.locator('#log-format').selectOption('json');await page.locator('#log-dialog>details summary').click();check('log JSON source evidence',await page.locator('#log-preview').innerText().then(s=>JSON.parse(s).records.every(r=>r.source_evidence.length)));
 await page.evaluate(()=>{window.__saved='';window.showSaveFilePicker=async()=>({name:'findings.json',createWritable:async()=>({write:async value=>window.__saved=value,close:async()=>{}})});document.querySelector('#save-log').hidden=false;});
 await page.locator('#save-log').click();check('native save writer receives valid log',await page.evaluate(()=>JSON.parse(window.__saved).records.length)===source.findings.length);
 await page.evaluate(()=>{window.showSaveFilePicker=async()=>{throw new DOMException('Cancelled','AbortError');};});await page.locator('#save-log').click();check('picker cancellation handled',await page.locator('#save-status').innerText().then(s=>s.includes('отменено')));
 await page.evaluate(()=>{document.querySelector('#download-log').hidden=false;});const downloadPromise=page.waitForEvent('download');await page.locator('#download-log').click();const downloaded=await downloadPromise;const stream=await downloaded.createReadStream();const chunks=[];for await(const chunk of stream)chunks.push(chunk);check('browser downloads actual JSON bytes',JSON.parse(Buffer.concat(chunks).toString()).records.length===source.findings.length);await page.locator('dialog form button').click();
 await page.locator('#map').click();await page.locator('#options summary').click();await page.locator('#reset').click();await page.locator('#fullscreen').click();check('canvas mode hides auxiliary panels',!(await page.locator('#sidebar').isVisible())&&!(await page.locator('#inspector').isVisible())&&!(await page.locator('#toolbar').isVisible()));await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.fullscreenElement&&!ArcXRay.state.fullscreen&&!ArcXRay.state.fullscreenPending);check('fullscreen exit restores panels',await page.locator('#sidebar').isVisible());
 await page.locator('#coverage').click();check('coverage and limits visible',await page.locator('#inspector').innerText().then(s=>s.includes('lexical')));
 const flow=source.views.find(v=>v.category==='workflow');await page.locator(`[data-view="${flow.id}"]`).click();check('execution view is connected',await page.locator('.connection').count()>0);
 await page.locator('[data-view="system"]').click();await page.locator('#language').selectOption('en');
 await page.screenshot({path:out+'/atlas-fhd.png'});
 for(const size of [{width:3840,height:2160},{width:1440,height:900},{width:768,height:1024},{width:375,height:812},{width:320,height:700}]){await page.setViewportSize(size);await page.waitForTimeout(80);check('responsive '+size.width,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));}
 await page.setViewportSize({width:1440,height:900});await page.goto(pathToFileURL(out+'/typescript/index.html').href);await page.waitForSelector('.node');check('TypeScript project renders',await page.evaluate(()=>ArcXRay.data.coverage.languages.TypeScript)===3);
 // The host preview receives the exact same autonomous HTML, not another renderer.
 const canonicalHtml=await readFile(out+'/python/index.html','utf8');
 await page.goto('about:blank');await page.setContent('<iframe id="app" style="width:1200px;height:750px;border:0"></iframe>');
 await page.locator('#app').evaluate((iframe,html)=>iframe.srcdoc=html,canonicalHtml);
 const frame=page.frameLocator('#app');await frame.locator('.node').first().waitFor();
 check('same HTML renders in host-style preview',await frame.locator('.node').count()===source.views[0].nodes.length);
 check('preview has identical full architecture model',await frame.locator('body').evaluate(()=>JSON.stringify(ArcXRay.data))===JSON.stringify(source));
 check('canonical blue UI in preview',await frame.locator('body').evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--bg').trim())==='#182338');
 await frame.locator('.node').first().click();await frame.locator('#inspector details:has(pre) summary').first().click();check('preview source inspection',await frame.locator('#inspector').innerText().then(s=>s.includes('SHA-256')));
 await page.screenshot({path:out+'/atlas-preview-host.png'});
 const large=structuredClone(source);large.nodes=Array.from({length:180},(_,i)=>({...source.nodes[0],id:'large-'+i,group:'modules',label:'Component '+i}));large.edges=[];large.views=[{id:'system',title:'Large project',description:'Synthetic coverage fixture',nodes:large.nodes.map(n=>n.id),edges:[]}];
 await frame.locator('body').evaluate((_,data)=>ArcXRay.loadAtlas(data),large);
 check('large graph groups all nodes without truncation',await frame.locator('body').evaluate(()=>ArcXRay.data.nodes.length)===180 && (await frame.locator('#counts').innerText()).includes('180 / 180'));
 await frame.locator('#options summary').click();await frame.locator('#expand').click();check('all grouped components can be expanded',await frame.locator('.node').count()===180);
 check('no browser script errors',errors.length===0);
 await writeFile(out+'/browser-verification.json',JSON.stringify({status:'PASS',checks,errors,remoteRequests:remote,hostAcceptance:'Same canonical HTML/model verified in an iframe preview without MCP; actual Chat host invocation remains separate.'},null,2));
 console.log(JSON.stringify({status:'PASS',checks:checks.length,errors}));
} finally {await browser.close();}
