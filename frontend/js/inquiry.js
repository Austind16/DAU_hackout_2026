/* ================= INQUIRY ================= */
function pick(field, value, el){
  state.inquiry[field] = value;
  const group = el.parentElement;
  [...group.children].forEach(c=>c.classList.remove('sel'));
  el.classList.add('sel');
}

function submitInquiry(){
  state.inquiry.area = document.getElementById('inq-area').value || 'Vastrapur';
  state.inquiry.city = document.getElementById('inq-city').value || 'Ahmedabad';
  state.inquiry.pin = document.getElementById('inq-pin').value || '380015';
  state.role = state.inquiry.goal || 'buy';
  renderSocieties();
  showPage('page-society');
}
