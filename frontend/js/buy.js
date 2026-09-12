/* ================= BUY =================
   TODO: replace the local `state.houses[...].available -= qty` mutation
   and trade push with Api.createTrade(...) once trades.py is wired in
   (trade_execution.py will handle the real settlement server-side).
*/
function confirmPurchase(){
  const ctx = state.buyContext;
  const total = ctx.qty*ctx.price;
  const gridCost = ctx.qty*state.gridRetail;
  const saving = gridCost-total;
  state.tradeCounter++;
  const tradeId = 'TRD-'+state.tradeCounter;
  // update house availability
  state.houses[ctx.houseId].available = Math.max(0, state.houses[ctx.houseId].available - ctx.qty);
  renderHouseGrid();

  document.getElementById('bc-summary').textContent = `${ctx.qty.toFixed(1)} kWh purchased from ${ctx.houseId}`;
  document.getElementById('bc-total').textContent = `₹${total.toFixed(2)}`;
  document.getElementById('bc-savings').textContent = `₹${saving.toFixed(2)}`;
  document.getElementById('bc-tradeid').textContent = tradeId;
  const ts = new Date().toLocaleString();
  document.getElementById('bc-time').textContent = ts;

  state.trades.push({id:tradeId, type:'Purchase', detail:`${ctx.qty.toFixed(1)} kWh from ${ctx.houseId} · ${ctx.name}`, amount:`₹${total.toFixed(2)}`, time:ts});
  renderTrades();
  showPage('page-buy-confirmed');
}
