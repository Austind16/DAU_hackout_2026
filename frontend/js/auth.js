/* ================= LOGIN =================
   TODO: replace login()'s direct showPage() call with a real
   auth request once Supabase Auth is wired up (see README
   "Not yet wired up" section) — e.g. Api call + storing a
   session token before moving to the inquiry page.
*/
function setAuthTab(mode){
  state.authMode = mode;
  document.getElementById('tab-login').classList.toggle('active', mode==='login');
  document.getElementById('tab-signup').classList.toggle('active', mode==='signup');
  document.getElementById('form-login').classList.toggle('hidden', mode!=='login');
  document.getElementById('form-signup').classList.toggle('hidden', mode!=='signup');
}

function login(){
  showPage('page-inquiry');
}
