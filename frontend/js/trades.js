/* ================= TRADE HISTORY =================
   TODO: swap state.trades for Api.getTrades(userId) once trades.py
   is wired up, so this page reflects real settled trades.
*/
function renderTrades(){
  const wrap = document.getElementById('trades-list');
  if(state.trades.length===0){ wrap.innerHTML = '<div class="faint">No trades yet.</div>'; return; }
  wrap.innerHTML = state.trades.slice().reverse().map(t=>`
    <div class="sum-row">
      <span>${t.id} · ${t.type} — ${t.detail}<br><span class="faint">${t.time}</span></span>
      <b>${t.amount}</b>
    </div>
  `).join('');
}
