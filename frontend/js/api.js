/* ================= API LAYER =================
   Thin wrappers around your FastAPI backend
   (app/main.py + app/routers/*). Nothing in the UI calls
   fetch() directly — it all goes through here, so swapping
   mock state for live data later means editing this file only.

   Currently unused: the rest of the app still runs on the
   mock `state` object in state.js. Wire a screen up by calling
   the matching function below instead of reading from `state`.
*/
const API_BASE = window.GRID_LOCAL_API_BASE || 'http://localhost:8000/api';

async function apiRequest(path, options = {}){
  const res = await fetch(`${API_BASE}${path}`, {
    headers:{ 'Content-Type':'application/json', ...(options.headers||{}) },
    ...options
  });
  if(!res.ok){
    const text = await res.text().catch(()=> '');
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }
  return res.status === 204 ? null : res.json();
}

/* ---- Users (app/routers/users.py) ---- */
const Api = {
  getUsers: () => apiRequest('/users'),
  getUser: (id) => apiRequest(`/users/${id}`),
  createUser: (payload) => apiRequest('/users', { method:'POST', body:JSON.stringify(payload) }),

  /* ---- Meter readings (app/routers/meters.py) ---- */
  getMeterReadings: (houseId) => apiRequest(`/meters?house_id=${encodeURIComponent(houseId)}`),

  /* ---- Listings (app/routers/listings.py) — surplus energy for sale ---- */
  getListings: (societyId) => apiRequest(`/listings?society_id=${encodeURIComponent(societyId)}`),
  createListing: (payload) => apiRequest('/listings', { method:'POST', body:JSON.stringify(payload) }),

  /* ---- Trades (app/routers/trades.py) ---- */
  getTrades: (userId) => apiRequest(`/trades?user_id=${encodeURIComponent(userId)}`),
  createTrade: (payload) => apiRequest('/trades', { method:'POST', body:JSON.stringify(payload) }),

  /* ---- Grid status (app/routers/grid_status.py) — outage / retail price ---- */
  getGridStatus: (societyId) => apiRequest(`/grid-status?society_id=${encodeURIComponent(societyId)}`),

  /* ---- Forecast (services/forecasting.py, per README "next steps") ---- */
  getForecast: (userId) => apiRequest(`/users/${userId}/forecast`)
};
