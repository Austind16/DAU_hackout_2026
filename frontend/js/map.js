/* ================= SOCIETY MAP (3D SVG house grid) ================= */
function houseNodeSVG(id, cx, cy, h){
  const dx = cx-138, dy = cy-117;
  const kind = h ? h.color : 'muted';
  let wallFront='#132336', wallSide='#0C1827', accent='#1E354F', knob='#335478',
      roofSide='url(#mutedRoofSide)', roofFront='url(#mutedRoofFront)', eaves='#2E4C6D',
      nameColor='#738CA7', clickable=false, pv='', pill='', ping='';
  const name = h && h.name ? h.name : '';

  if(kind==='gold'){
    wallFront='#1C3149'; wallSide='#112133'; accent='#E08C36'; knob='#F2A65A';
    roofSide='url(#goldRoofSide)'; roofFront='url(#goldRoofFront)'; eaves='#F5AF67';
    nameColor='#D1D5DB'; clickable=true;
    pv = `<polygon points="129,74 114,88 143,88 137,78" fill="url(#goldPV)" stroke="#F2A65A" stroke-width="0.9" opacity="0.95"/>
      <line x1="121" y1="81" x2="140" y2="81" stroke="#F2A65A" stroke-width="0.7" opacity="0.85"/>
      <line x1="128" y1="74" x2="128" y2="88" stroke="#F2A65A" stroke-width="0.7" opacity="0.7"/>
      <line x1="135" y1="77" x2="135" y2="88" stroke="#F2A65A" stroke-width="0.7" opacity="0.7"/>`;
    pill = `<g filter="url(#glow-gold)"><rect x="111" y="48" width="48" height="16" rx="8" fill="#F2A65A" stroke="#FFFFFF" stroke-width="0.8"/></g>
      <text x="135" y="59.5" text-anchor="middle" fill="#141416" font-size="9.5" font-family="'Space Grotesk',sans-serif" font-weight="700">${h.available.toFixed(1)} kWh</text>`;
  } else if(kind==='cyan'){
    wallFront='#163652'; wallSide='#0D2439'; accent='#4FC3E8'; knob='#4FC3E8';
    roofSide='url(#cyanRoofSide)'; roofFront='url(#cyanRoofFront)'; eaves='#6DE0FF';
    nameColor='#738CA7';
    pill = `<g filter="url(#glow-cyan)"><rect x="114" y="48" width="42" height="16" rx="8" fill="#0C253B" stroke="#4FC3E8" stroke-width="1.3"/></g>
      <text x="135" y="59.5" text-anchor="middle" fill="#4FC3E8" font-size="10" font-family="'Space Grotesk',sans-serif" font-weight="700">YOU</text>`;
    ping = `<circle cx="162" cy="76" r="5" fill="#F0563B"/><circle cx="162" cy="76" r="9" fill="#F0563B" opacity="0.4" class="pulse-ring"/>`;
  } else if(kind==='red'){
    ping = `<circle cx="162" cy="76" r="5" fill="#F0563B"/><circle cx="162" cy="76" r="9" fill="#F0563B" opacity="0.4" class="pulse-ring"/>`;
  }

  return `<g class="house-node ${clickable?'':'disabled'} ${state.selectedHouseId===id?'selected-house':''}" data-id="${id}"
      transform="translate(${dx},${dy})" ${clickable?`onclick="openHouse('${id}')"`:''}>
    <ellipse cx="138" cy="117" rx="33" ry="9" fill="#000000" opacity="0.6"/>
    <polygon points="147,92 159,85 159,107 147,114" fill="${wallSide}" stroke="${accent}" stroke-width="1.1" stroke-linejoin="round"/>
    <rect x="111" y="92" width="36" height="22" rx="2.5" fill="${wallFront}" stroke="${accent}" stroke-width="1.3"/>
    <rect x="126" y="101" width="9" height="13" rx="1.5" fill="#0A1624" stroke="${accent}" stroke-width="0.8"/>
    <circle cx="133" cy="108" r="0.8" fill="${knob}" opacity="0.8"/>
    <rect x="115" y="96" width="8" height="7" rx="1" fill="#0A1624" stroke="${accent}" stroke-width="0.75"/>
    <line x1="119" y1="96" x2="119" y2="103" stroke="${accent}" stroke-width="0.6"/>
    <line x1="115" y1="99.5" x2="123" y2="99.5" stroke="${accent}" stroke-width="0.6"/>
    <line x1="151" y1="94" x2="156" y2="91" stroke="${accent}" stroke-width="0.8" opacity="0.7"/>
    <line x1="151" y1="99" x2="156" y2="96" stroke="${accent}" stroke-width="0.8" opacity="0.7"/>
    <polygon points="129,70 142,64 162,82 149,90" fill="${roofSide}" stroke="${eaves}" stroke-width="1.2" stroke-linejoin="round"/>
    <polygon points="129,70 108,90 149,90" fill="${roofFront}" stroke="${eaves}" stroke-width="1.4" stroke-linejoin="round"/>
    <line x1="129" y1="70" x2="142" y2="64" stroke="#FFF" stroke-width="1" opacity="0.6" stroke-linecap="round"/>
    <line x1="108" y1="90" x2="149" y2="90" stroke="${eaves}" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="149" y1="90" x2="162" y2="82" stroke="${eaves}" stroke-width="1.5" stroke-linecap="round"/>
    ${pv}
    ${pill}
    ${ping}
    <text x="135" y="130" text-anchor="middle" fill="#FFFFFF" font-size="11" font-family="'Space Grotesk',sans-serif" font-weight="700">${id}</text>
    <text x="135" y="140" text-anchor="middle" fill="${nameColor}" font-size="8.5" font-family="Inter, sans-serif">${name}</text>
  </g>`;
}

function renderHouseGrid(){
  // glass card backings
  const cardsGroup = document.getElementById('glass-cards');
  let cardsHtml = '';
  BLOCKS.forEach((b, r)=>{
    for(let n=1;n<=ROWS;n++){
      const id = b+n;
      const h = state.houses[id];
      const active = h && (h.color==='gold' || h.color==='cyan');
      cardsHtml += `<g id="glass-cell-${id}">
        <rect x="${CARD_X[n-1]}" y="${CARD_Y[r]}" width="96" height="104" rx="16"
          fill="url(#${active?'glassCardActiveGrad':'glassCardGrad'})" stroke="rgba(255,255,255,0.08)" stroke-width="1" filter="url(#card-soft-shadow)"/>
        <rect x="${CARD_X[n-1]+1}" y="${CARD_Y[r]+1}" width="94" height="102" rx="15" fill="none"
          stroke="${h && h.color==='gold' ? 'rgba(240,168,60,0.15)' : 'rgba(255,255,255,0.02)'}" stroke-width="1"/>
      </g>`;
    }
  });
  cardsGroup.innerHTML = cardsHtml;

  // junction dots
  const dotsGroup = document.getElementById('junction-dots');
  let dotsHtml = '';
  JY.forEach(y=> JX.forEach(x=> dotsHtml += `<circle cx="${x}" cy="${y}" r="2.8"/>`));
  dotsGroup.innerHTML = dotsHtml;

  // house nodes
  const nodesGroup = document.getElementById('house-nodes');
  let nodesHtml = '';
  BLOCKS.forEach((b, r)=>{
    for(let n=1;n<=ROWS;n++){
      const id = b+n;
      nodesHtml += houseNodeSVG(id, COL_X[n-1], ROW_Y[r], state.houses[id]);
    }
  });
  nodesGroup.innerHTML = nodesHtml;
}

function flowPathFor(fromId, toId){
  const [fr, fc] = [BLOCKS.indexOf(fromId[0]), parseInt(fromId[1])-1];
  const [tr, tc] = [BLOCKS.indexOf(toId[0]), parseInt(toId[1])-1];
  const sx=JX[fc], sy=JY[fr], ux=JX[tc], uy=JY[tr];
  return `M ${sx} ${sy} L ${ux} ${sy} L ${ux} ${uy}`;
}

function showFlow(sellerId){
  const d = flowPathFor(sellerId, state.userHouse);
  ['flow-underlay','flow-base','flow-anim','flow-pulse'].forEach(pid=>document.getElementById(pid).setAttribute('d', d));
  document.getElementById('active-flow-group').style.opacity = 1;
}

function hideFlow(){
  document.getElementById('active-flow-group').style.opacity = 0;
}

function openHouse(id){
  state.currentHouseId = id;
  state.selectedHouseId = id;
  renderHouseGrid();
  showFlow(id);
  const h = state.houses[id];
  const savings = ((state.gridRetail - h.price)/state.gridRetail*100).toFixed(1);
  document.getElementById('map-side').innerHTML = `
    <div class="card house-detail">
      <div class="hd-top">
        <div class="hd-avatar">${h.name.split(' ').map(w=>w[0]).join('')}</div>
        <div><div class="hd-name">${id} · ${h.name.split(' ')[0]}</div></div>
      </div>
      <div class="hd-tag">Solar surplus available</div>
      <div class="kv-grid">
        <div><div class="kv-label">Available</div><div class="kv-val gold">${h.available.toFixed(1)} kWh</div></div>
        <div><div class="kv-label">Price</div><div class="kv-val">₹${h.price.toFixed(2)} / kWh</div></div>
        <div><div class="kv-label">Grid rate</div><div class="kv-val">₹${state.gridRetail.toFixed(2)} / kWh</div></div>
        <div><div class="kv-label">Savings</div><div class="kv-val green">${savings}%</div></div>
      </div>
      <button class="btn btn-primary btn-full" onclick="viewEnergy('${id}')">View Energy</button>
    </div>
  `;
}

function viewEnergy(id){
  state.currentHouseId = id;
  const h = state.houses[id];
  state.need = Math.min(5.0, h.available);
  document.getElementById('rec-house-id').textContent = id;
  document.getElementById('rec-house-name').textContent = h.name;
  document.getElementById('rec-capacity').textContent = h.capacity;
  document.getElementById('rec-available').textContent = h.available.toFixed(1)+' kWh';
  document.getElementById('rec-p2p-price').textContent = '₹'+h.price.toFixed(2)+'/kWh';
  document.getElementById('rec-grid-price').textContent = '₹'+state.gridRetail.toFixed(2)+'/kWh';
  document.getElementById('qty-max-label').textContent = h.available.toFixed(1);
  updateQtyDisplay();
  computeRecommendation();
  showPage('page-recommend');
}
