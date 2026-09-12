/* ================= QUANTITY + AI RECOMMENDATION =================
   computeRecommendation() is a client-side stand-in for the
   backend's services/matching_engine.py + pricing_engine.py.
   Swap the local `candidates` sort for a call to
   Api.getListings()/a future /api/match endpoint once that's ready.
*/
function changeQty(delta){
  const h = state.houses[state.currentHouseId];
  let v = state.need + delta;
  v = Math.max(0.5, Math.min(h.available, v));
  state.need = Math.round(v*10)/10;
  updateQtyDisplay();
  computeRecommendation();
}

function updateQtyDisplay(){
  document.getElementById('qty-display').textContent = state.need.toFixed(1);
}

function computeRecommendation(){
  const userBlock = state.houses[state.userHouse].block;
  const need = state.need;
  const candidates = Object.entries(state.houses)
    .filter(([id,h])=>h.color==='gold' && h.available >= need)
    .map(([id,h])=>({id, ...h, blockDist: blockDistance(userBlock, h.block)}));
  candidates.sort((a,b)=>{
    if(a.blockDist !== b.blockDist) return a.blockDist - b.blockDist;
    if(a.price !== b.price) return a.price - b.price;
    return a.available - b.available;
  });
  const best = candidates[0] || {id:state.currentHouseId, ...state.houses[state.currentHouseId]};
  state.recommendedId = best.id;
  const sameBlock = best.blockDist === 0;
  const cost = need*best.price;
  const gridCost = need*state.gridRetail;
  const saving = gridCost-cost;

  document.getElementById('ai-explanation').textContent =
    `You need approximately ${need.toFixed(1)} kWh. House ${best.id} is the best option because it has `+
    `${best.available.toFixed(1)} kWh available`+
    (sameBlock ? ', is in your block,' : ', is nearby,')+
    ` and offers a lower price than the grid.`;
  document.getElementById('ai-seller').textContent = `${best.id} · ${best.name}`;
  document.getElementById('ai-available').textContent = `${best.available.toFixed(1)} kWh`;
  document.getElementById('ai-need').textContent = `${need.toFixed(1)} kWh`;
  document.getElementById('ai-saving').textContent = `₹${saving.toFixed(2)}`;
}

function chooseRecommended(){
  const best = state.houses[state.recommendedId];
  const need = state.need;
  state.buyContext = {
    houseId: state.recommendedId, name: best.name, price: best.price,
    available: best.available, qty: need
  };
  document.getElementById('buy-seller').textContent = `${state.recommendedId} · ${best.name}`;
  document.getElementById('buy-available').textContent = `${best.available.toFixed(1)} kWh`;
  document.getElementById('buy-qty').textContent = `${need.toFixed(1)} kWh`;
  document.getElementById('buy-price').textContent = `₹${best.price.toFixed(2)}/kWh`;
  const total = need*best.price;
  const gridCost = need*state.gridRetail;
  document.getElementById('buy-gridcost').textContent = `₹${gridCost.toFixed(2)}`;
  document.getElementById('buy-total').textContent = `₹${total.toFixed(2)}`;
  document.getElementById('buy-save').textContent = `₹${(gridCost-total).toFixed(2)}`;
  showPage('page-buy');
}
