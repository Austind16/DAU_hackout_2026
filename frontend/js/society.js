/* ================= SOCIETY SELECT ================= */
function renderSocieties(){
  const wrap = document.getElementById('society-list');
  wrap.innerHTML = SOCIETIES.map(s=>`
    <div class="card society-card ${s.name==='Green Valley Society' && state.society==='Green Valley Society' ? 'selected':''}" id="soc-${s.name.replace(/\s/g,'')}">
      <h3>${s.name}</h3>
      <div class="faint">${s.dist}</div>
      <div class="society-stats">
        <div class="stat"><b>${s.sellers}</b> nearby energy sellers</div>
        <div class="stat"><b>${s.buyers}</b> active buyers</div>
        <div class="stat"><b>${s.available}</b> available now</div>
      </div>
      <button class="btn btn-primary" onclick="selectSociety('${s.name}')">Select Society</button>
    </div>
  `).join('');
}

function selectSociety(name){
  state.society = name;
  state.selectedHouseId = null;
  document.getElementById('map-society-name').textContent = name;
  renderHouseGrid();
  hideFlow();
  document.getElementById('map-side').innerHTML = `
    <div class="card" style="text-align:center; color:var(--text-faint); padding:40px 20px;">
      Tap a gold house to see its available solar energy.
    </div>`;
  if(state.role==='sell'){
    showPage('page-sell');
  } else {
    showPage('page-map');
  }
}
