window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();
});

async function fetch_and_render_balance_sidebar() {
  try {
    let response = await fetch('/budget_state.json');
    if (!response.ok) throw new Error('Ошибка запроса');
    let data = await response.json();
    const balance = data.balance;
    document.getElementById('reserve_state_sidebar').textContent = balance.reserve ?? '0.00';
    document.getElementById('available_funds_state_sidebar').textContent = balance.available_funds ?? '0.00';
    document.getElementById('rent_state_sidebar').textContent = balance.rent ?? '0.00';
    document.getElementById('taxes_state_sidebar').textContent = balance.taxes ?? '0.00';
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

