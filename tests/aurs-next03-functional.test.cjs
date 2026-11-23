/* AURS NEXT 03 - self-contained Node 18+ regression tests.
   Run after cloning the branch:
   node --test tests/aurs-next03-functional.test.cjs
   These are simulated DOM tests, not a real Chrome/Android layout or security penetration test.
*/
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'..','aurs-command-front-v2.html'),'utf8');
const js=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(js,'inline app script exists');

function setup(){
  class Element {
    constructor(tag,id){this.tagName=tag;this.id=id||'';this.children=[];this.events={};
      this.textContent='';this.value='';this.className='';this.style={};this.checked=false;this.open=false;}
    addEventListener(ev,fn){this.events[ev]=fn;}
    append(...items){this.children.push(...items);}
    replaceChildren(...items){this.children=items;}
    setAttribute(k,v){this[k]=v;}
    scrollIntoView(){}
    click(){return this.emit('click');}
    emit(ev,obj={preventDefault(){}}){return this.events[ev]?.(obj);}
  }
  const map=new Map();
  const document={
    getElementById(id){if(!map.has(id))map.set(id,new Element('div',id));return map.get(id);},
    createElement(tag){return new Element(tag);},
    createTextNode(str){const e=new Element('#text');e.textContent=str;return e;}
  };
  const persisted=new Map();
  const localStorage={getItem(k){return persisted.get(k)||null;},setItem(k,val){persisted.set(k,val);}};
  const navigator={clipboard:{writeText:async()=>{}}};
  const confirm=()=>true;
  const Blob=function(){};
  const URL={createObjectURL(){return 'blob:mock';},revokeObjectURL(){}};
  document.getElementById('prompt').textContent='NEXT दबाने पर';
  new Function('document','localStorage','navigator','confirm','Blob','URL',js)
    (document,localStorage,navigator,confirm,Blob,URL);
  const $=id=>document.getElementById(id);
  const persistedState=()=>JSON.parse(persisted.get('aurs-business-command-v2'));
  function create(data={}){
    $('newProject').click();
    const entry={name:'QA DEMO 01',brand:'SANTRAM INDUSTRIES',type:'Rhinestone / Hotfix',
      qty:'100',owner:'Production lead',due:'2026-12-01',stage:'costing',approval:'pending',
      dispatch:'not-ready',notes:'demo only',material:'10',labour:'5',shipping:'2',
      waste:'10',margin:'25',gst:'18',...data};
    for(const [k,v] of Object.entries(entry))$('p'+k).value=v;
    $('editor').emit('submit');
    return persistedState().projects[0];
  }
  function edit(changes){
    const article=$('projects').children[0];
    const button=article.children.find(e=>e.className==='row').children.find(e=>e.textContent==='संपादित');
    button.click();
    for(const [k,v] of Object.entries(changes))$('p'+k).value=v;
    $('editor').emit('submit');
  }
  return {$,create,edit,persistedState};
}
test('syntax and local-only content policy',()=>{
  assert.doesNotThrow(()=>new Function(js));
  assert.match(html,/connect-src 'none'/);
  assert.doesNotMatch(js,/\b(?:fetch|XMLHttpRequest|sendBeacon|WebSocket)\s*\(/);
  assert.match(html,/@media\(max-width:440px\)/);
  assert.match(html,/min-height:44px/);
});
test('initial controls render with no record',()=>{
  const a=setup();
  assert.match(a.$('projectCount').textContent,/0/);
  assert.match(a.$('selection').children[0].textContent,/अभी सक्रिय/);
});
test('valid record is stored; costing includes wastage + gross margin + manually selected GST',()=>{
  const a=setup(); a.create();a.$('next').click();
  const s=a.$('prompt').textContent;
  assert.match(s,/unit cost INR 18.00/);
  assert.match(s,/sale ex-GST INR 24.00/);
  assert.match(s,/sale incl-GST INR 28.32/);
  assert.match(s,/total incl-GST INR 2832.00/);
});
test('invalid calendar dates are removed and user input appears as text',()=>{
  const a=setup();const p=a.create({due:'2026-02-30',name:'<img src=x onerror=alert(1)> SAMPLE'});
  assert.equal(p.due,'');
  assert.match(a.$('selection').children[0].textContent,/^<img/);
});
test('unapproved production produces a blocker rather than release',()=>{
  const a=setup();a.create();a.edit({stage:'production'});a.$('next').click();
  assert.match(a.$('prompt').textContent,/उत्पादन रोकें/);
});
test('workflow edits leave a local, explicitly non-authoritative change trail',()=>{
  const a=setup();a.create();a.edit({stage:'approval',approval:'approved'});
  assert.ok(a.persistedState().events.some(e=>e.type==='approval-status-edited'));
  assert.ok(a.persistedState().events.some(e=>e.type==='stage-updated'));
});
test('file checklist edits are recorded locally',()=>{
  const a=setup();a.create();
  const label=a.$('fileChecks').children[0];const checkbox=label.children[0];
  checkbox.checked=true;checkbox.emit('change');
  assert.ok(a.persistedState().events.some(e=>e.type==='file-check-edited'));
});
test('brand switching clears active selection and old NEXT command',()=>{
  const a=setup();a.create();a.$('next').click();
  const brand=a.$('brands').children.find(b=>b.textContent==='STYNSPARK');
  brand.click();
  assert.match(a.$('selection').children[0].textContent,/अभी सक्रिय/);
  assert.match(a.$('prompt').textContent,/^NEXT दबाने/);
});
test('import rejects duplicate project IDs',async()=>{
  const a=setup();const p=a.create();
  const file=a.$('importFile');
  file.files=[{size:500,text:async()=>JSON.stringify({version:2,data:{
    brand:'SANTRAM INDUSTRIES',selected:p.id,projects:[p,p],events:[]}})}];
  await file.emit('change',{target:file});
  assert.match(a.$('feedback').textContent,/अमान्य/);
  assert.equal(a.persistedState().projects.length,1);
});
