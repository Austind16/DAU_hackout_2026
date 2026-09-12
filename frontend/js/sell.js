/* ================= SELL =================
   TODO: listSurplus() should call Api.createListing(...) (listings.py),
   and simulateRequest()/acceptRequest() stand in for a real incoming
   request once Supabase Realtime is wired up for live listing/trade
   updates (see README "Not yet wired up").
*/
function changeSellQty(delta){
  let v = state.sellQty + delta;
  v = Math.max(0.5, Math.min(state.sellSurplusTotal, v));
  state.sellQty = Math.round(v*10)/10;
  document.getElementById('sell-qty-display').textContent = state.sellQty.toFixed(1);
}

function listSurplus(){
  document.getElementById('live-qty').textContent = state.sellQty.toFixed(1)+' kWh';
  showPage('page-listing-live');
}

function simulateRequest(){
  const qty = Math.min(state.sellQty, 6.0);
  document.getElementById('req-qty').textContent = qty.toFixed(1)+' kWh';
  document.getElementById('req-surplus').textContent = state.sellSurplusTotal.toFixed(1)+' kWh';
  const total = qty*state.sellPrice;
  document.getElementById('req-total').textContent = '₹'+total.toFixed(2);
  state.pendingRequest = {qty, total};
  showPage('page-request');
}

function acceptRequest(){
  const req = state.pendingRequest;
  state.tradeCounter++;
  const tradeId = 'TRD-'+state.tradeCounter;
  state.sellSurplusTotal = Math.max(0, state.sellSurplusTotal - req.qty);
  document.getElementById('sell-surplus-total').textContent = state.sellSurplusTotal.toFixed(1)+' kWh';
  document.getElementById('ra-summary').textContent = `${req.qty.toFixed(1)} kWh has been allocated to B3.`;
  document.getElementById('ra-tradeid').textContent = tradeId;

  const ts = new Date().toLocaleString();
  state.trades.push({id:tradeId, type:'Sale', detail:`${req.qty.toFixed(1)} kWh sold to House B3`, amount:'₹'+req.total.toFixed(2), time:ts});
  renderTrades();
  showPage('page-request-accepted');
}

function declineRequest(){
  showPage('page-listing-live');
}
