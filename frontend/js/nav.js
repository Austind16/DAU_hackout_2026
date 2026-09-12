/* ================= NAV / STEP BAR ================= */
let currentPageId = 'page-login';

function renderSteps(){
  const bar = document.getElementById('steps');
  const flow = FLOWS[state.role] || FLOWS.buy;
  bar.innerHTML = flow.map((id,i)=>{
    const cls = id===currentPageId ? 'step active' : 'step done';
    return `<div class="${cls}" onclick="jumpTo('${id}')">${STEP_LABELS[id]}</div>` + (i<flow.length-1 ? '<span class="step-sep">›</span>' : '');
  }).join('');
  const pill = document.getElementById('role-pill');
  if(state.role==='both'){ pill.classList.remove('hidden'); pill.textContent='Buyer & Seller'; }
  else if(state.role==='sell'){ pill.classList.remove('hidden'); pill.textContent='Solar Seller'; }
  else { pill.classList.remove('hidden'); pill.textContent='Buyer'; }
}

function jumpTo(id){
  // only allow jumping to steps already reachable
  showPage(id);
}

function showPage(id){
  document.querySelectorAll('.page').forEach(p=>p.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
  currentPageId = id;
  const topbar = document.getElementById('topbar');
  if(id==='page-login'){ topbar.classList.add('hidden'); }
  else { topbar.classList.remove('hidden'); renderSteps(); }
  window.scrollTo({top:0, behavior:'smooth'});
}
