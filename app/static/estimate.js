const form=document.getElementById('estimateForm');
if(form){
 const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(n||0);
 let timer;
 async function update(){
  const fd=new FormData(form); const names=['material_cost','labor_cost','subcontractor_cost','permit_cost','disposal_cost','equipment_cost','delivery_cost','other_direct_cost','target_gross_margin'];
  const payload={}; names.forEach(n=>payload[n]=Number(fd.get(n)||0));
  const r=await fetch('/api/pricing',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); if(!r.ok)return;
  const d=await r.json(); document.getElementById('sellPrice').textContent=money(d.sell_price); document.getElementById('tax').textContent=money(d.material_tax); document.getElementById('direct').textContent=money(d.total_direct_cost); document.getElementById('profit').textContent=money(d.gross_profit); document.getElementById('marginOut').textContent=Math.round(d.gross_margin*100)+'%';
 }
 form.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(update,120)}); update();
}
