window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance();
});

async function fetch_and_render_balance() {
  try {
    let response = await fetch('/budget_state.json');
    if (!response.ok) throw new Error('Ошибка запроса');
    let data = await response.json();
    document.getElementById('reserve_state').textContent = `${data.reserve || 0}`;
    document.getElementById('available_funds_state').textContent = `${data.available_funds || 0}`;
    document.getElementById('rent_state').textContent = `${data.rent || 0}`;
    document.getElementById('taxes_state').textContent = `${data.taxes || 0}`;
  } catch (error) {
    console.error('Ошибка:', error);
  }
}
