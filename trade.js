/* APOXY Global Trade Desk — browser-local operations module.
   No external network calls, no fabricated suppliers, no message sending.
   Data remains in this browser until exported. */
(()=>{
'use strict';
const KEY='apoxy_global_trade_desk_v1';
const blank=()=>({buyers:[],suppliers:[],quotes:[],orders:[],tasks:[]});
let data=load();
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const uid=p=>p+'-'+Date.now().toString(36).toUpperCase()+'-'+Math.random().toString(36).slice(2,6).toUpperCase();
function load(){try{const d=JSON.parse(localStorage.getItem(KEY)||'{}');return {...blank(),...d}}catch{return blank()}}
function save(){localStorage.setItem(KEY,JSON.stringify(data));render()}
function note(msg){if(typeof window.toast==='function')window.toast(msg);else alert(msg)}
function obj(form){return Object.fromEntries(new FormData(form).entries())}
function download(name,body,type='application/json'){const a=document.createElement('a'),u=URL.createObjectURL(new Blob([body],{type}));a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1000)}
function money(n,c='INR'){try{return new Intl.NumberFormat(undefined,{style:'currency',currency:c,maximumFractionDigits:2}).format(Number(n)||0)}catch{return (Number(n)||0).toFixed(2)+' '+c}}
function render(){
 const count=(id,n)=>{const e=$(id);if(e)e.textContent=n};
 count('#tradeBuyerCount',data.buyers.length);count('#tradeSupplierCount',data.suppliers.length);count('#tradeQuoteCount',data.quotes.length);count('#tradeOrderCount',data.orders.filter(x=>!['Delivered','Cancelled'].includes(x.status)).length);
 renderBuyers();renderSuppliers();renderQuotes();renderOrders();renderTasks();
}
function rows(id,html,empty,cols){const e=$(id);if(e)e.innerHTML=html||'<tr><td colspan="'+cols+'" class="muted">'+empty+'</td></tr>'}
function renderBuyers(){const q=($('#tradeBuyerSearch')?.value||'').toLowerCase();rows('#tradeBuyerRows',data.buyers.filter(x=>JSON.stringify(x).toLowerCase().includes(q)).map(x=>'<tr><td><b>'+esc(x.name)+'</b><br>'+esc(x.country)+'<br><small>'+esc(x.email)+' '+esc(x.phone)+'</small></td><td>'+esc(x.product)+'<br><span class="pill">'+esc(x.status)+'</span></td><td>'+esc(x.followup||'No date')+'<br><button class="btn secondary" data-bstatus="'+x.id+'">Update status</button> <button class="btn danger" data-bdel="'+x.id+'">Delete</button></td></tr>').join(''),'No buyer leads yet. Add a real prospect.',3);
 $('#tradeBuyerRows')?.querySelectorAll('[data-bdel]').forEach(b=>b.onclick=()=>remove('buyers',b.dataset.bdel));
 $('#tradeBuyerRows')?.querySelectorAll('[data-bstatus]').forEach(b=>b.onclick=()=>{const x=data.buyers.find(v=>v.id===b.dataset.bstatus);const s=prompt('New buyer status',x.status);if(s!==null){x.status=s;save()}});
}
function renderSuppliers(){const q=($('#tradeSupplierSearch')?.value||'').toLowerCase();rows('#tradeSupplierRows',data.suppliers.filter(x=>JSON.stringify(x).toLowerCase().includes(q)).map(x=>'<tr><td><b>'+esc(x.name)+'</b><br>'+esc(x.location)+'<br><small>'+esc(x.email)+' '+esc(x.phone)+'</small></td><td>'+esc(x.product)+'<br>MOQ: '+esc(x.moq||'—')+'<br>'+money(x.cost||0,'INR')+'/unit (entered)</td><td><span class="pill">'+esc(x.verification)+'</span><br><button class="btn danger" data-sdel="'+x.id+'">Delete</button></td></tr>').join(''),'No supplier records. Add only businesses you have independently checked.',3);
 $('#tradeSupplierRows')?.querySelectorAll('[data-sdel]').forEach(b=>b.onclick=()=>remove('suppliers',b.dataset.sdel));
}
function renderQuotes(){rows('#tradeQuoteRows',data.quotes.map(x=>'<tr><td><b>'+esc(x.buyer)+'</b><br>'+esc(x.product)+'</td><td>'+Number(x.qty).toLocaleString()+'</td><td>'+money(x.unitPrice,x.currency)+'</td></tr>').join(''),'No saved quotations.',3)}
function renderOrders(){rows('#tradeOrderRows',data.orders.map(x=>'<tr><td><b>'+esc(x.po)+'</b><br>'+esc(x.buyer)+'<br>'+esc(x.product)+'</td><td>'+money(x.value,'INR')+'<br>'+esc(x.payment)+'</td><td><span class="pill">'+esc(x.status)+'</span><br>'+esc(x.due||'No due date')+'<br><button class="btn secondary" data-odel="'+x.id+'">Delete</button></td></tr>').join(''),'No confirmed orders recorded.',3);$('#tradeOrderRows')?.querySelectorAll('[data-odel]').forEach(b=>b.onclick=()=>remove('orders',b.dataset.odel))}
function renderTasks(){rows('#tradeTaskRows',data.tasks.map(x=>'<tr><td>'+esc(x.title)+'<br>'+esc(x.company)+'</td><td>'+esc(x.date||'No date')+'<br>'+esc(x.priority)+'</td><td>'+(x.done?'<b>Completed</b>':'<button class="btn secondary" data-tdone="'+x.id+'">Mark done</button>')+' <button class="btn danger" data-tdel="'+x.id+'">Delete</button></td></tr>').join(''),'No follow-ups scheduled.',3);$('#tradeTaskRows')?.querySelectorAll('[data-tdone]').forEach(b=>b.onclick=()=>{const t=data.tasks.find(x=>x.id===b.dataset.tdone);if(t)t.done=true;save()});$('#tradeTaskRows')?.querySelectorAll('[data-tdel]').forEach(b=>b.onclick=()=>remove('tasks',b.dataset.tdel))}
function remove(k,id){if(confirm('Delete this record?')){data[k]=data[k].filter(x=>x.id!==id);save()}}
$('#tradeBuyerForm')?.addEventListener('submit',e=>{e.preventDefault();const x=obj(e.currentTarget);data.buyers.unshift({id:uid('BUY'),...x,createdAt:new Date().toISOString()});e.currentTarget.reset();save();note('Buyer lead saved on this device. No message sent.')});
$('#tradeSupplierForm')?.addEventListener('submit',e=>{e.preventDefault();const x=obj(e.currentTarget);data.suppliers.unshift({id:uid('SUP'),...x,createdAt:new Date().toISOString()});e.currentTarget.reset();save();note('Supplier record saved. Verification is not automatic.')});
$('#tradeQuoteForm')?.addEventListener('submit',e=>{e.preventDefault();const x=obj(e.currentTarget),qty=Math.max(1,Number(x.qty)||1),currency=x.currency||'INR',landed=(Number(x.unitCost||0)+Number(x.pack||0))*qty+Number(x.freight||0)+Number(x.other||0),margin=Math.min(90,Math.max(0,Number(x.margin)||0))/100,total=landed/(1-margin),unit=total/qty,profit=total-landed;
 const q={id:uid('QUO'),buyer:x.buyer,product:x.product,qty,currency,landed,total,unitPrice:unit,profit,margin:x.margin,createdAt:new Date().toISOString()};data.quotes.unshift(q);
 $('#tradeQuoteResult').innerHTML='<h3>Saved quotation estimate</h3><div class="stats-grid"><div class="stat-card"><span class="muted">Landed cost</span><strong>'+money(landed,currency)+'</strong></div><div class="stat-card"><span class="muted">Suggested unit price</span><strong>'+money(unit,currency)+'</strong></div><div class="stat-card"><span class="muted">Total quote</span><strong>'+money(total,currency)+'</strong></div><div class="stat-card"><span class="muted">Gross profit</span><strong>'+money(profit,currency)+'</strong></div></div><p class="muted">Estimate only. Taxes, customs duty, FX conversion, bank charges, platform fees, insurance and unentered costs are excluded. This is gross margin on selling price, not net profit.</p>';save();note('Quotation estimate saved locally. Review all costs before sending.')});
$('#tradeOrderForm')?.addEventListener('submit',e=>{e.preventDefault();const x=obj(e.currentTarget);data.orders.unshift({id:uid('ORD'),...x,createdAt:new Date().toISOString()});e.currentTarget.reset();save();note('Order record saved locally. No PO/payment/shipment was processed.')});
$('#tradeTaskForm')?.addEventListener('submit',e=>{e.preventDefault();const x=obj(e.currentTarget);data.tasks.unshift({id:uid('TASK'),...x,done:false,createdAt:new Date().toISOString()});e.currentTarget.reset();save();note('Follow-up saved locally.')});
$('#tradeBuyerSearch')?.addEventListener('input',renderBuyers);$('#tradeSupplierSearch')?.addEventListener('input',renderSuppliers);
document.querySelectorAll('[data-trade-tab]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-trade-tab]').forEach(x=>{x.classList.toggle('primary',x===b);x.classList.toggle('secondary',x!==b)});document.querySelectorAll('.trade-panel').forEach(x=>x.classList.toggle('active',x.id==='trade-'+b.dataset.tradeTab))}));
$('#tradeExport')?.addEventListener('click',()=>download('APOXY_GLOBAL_TRADE_BACKUP_'+new Date().toISOString().slice(0,10)+'.json',JSON.stringify({version:1,exportedAt:new Date().toISOString(),data},null,2)));
$('#tradeImport')?.addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{const x=JSON.parse(await file.text()),d=x.data||x;if(!['buyers','suppliers','quotes','orders','tasks'].every(k=>Array.isArray(d[k])))throw Error('Invalid APOXY trade backup');if(!confirm('Replace all current Global Trade Desk records with this backup?'))return;data=d;save();note('Trade backup imported on this device.')}catch(err){note('Import failed: '+err.message)}finally{e.target.value=''}});
document.querySelectorAll('[data-page="trade"],[data-go="trade"]').forEach(b=>b.addEventListener('click',render));
render();
})();
