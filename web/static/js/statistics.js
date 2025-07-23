window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();
});

document.getElementById('refresh_balance').onclick = () => {
  fetch_and_render_balance_sidebar();
};

async function fetch_and_render_balance_sidebar() {
  try {
    let response = await fetch('/budget_state.json');
    if (!response.ok) throw new Error('Ошибка запроса');
    let data = await response.json();
    document.getElementById('reserve_state_sidebar').textContent = `${data.reserve || 0}`;
    document.getElementById('available_funds_state_sidebar').textContent = `${data.available_funds || 0}`;
    document.getElementById('rent_state_sidebar').textContent = `${data.rent || 0}`;
    document.getElementById('taxes_state_sidebar').textContent = `${data.taxes || 0}`;
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

