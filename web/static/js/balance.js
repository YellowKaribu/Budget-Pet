window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance();

  document.getElementById('balance_form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
      reserve: parseFloat(document.getElementById('reserve_input').value),
      available_funds: parseFloat(document.getElementById('available_funds_input').value),
      rent: parseFloat(document.getElementById('rent_input').value),
      taxes: parseFloat(document.getElementById('taxes_input').value),
    };

    try {
      const response = await fetch('/update_balance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Ошибка обновления');

      // Обновим UI
      fetch_and_render_balance();
    } catch (error) {
      console.error('Ошибка при обновлении:', error);
    }
  });
});

async function fetch_and_render_balance() {
  try {
    const response = await fetch('/budget_state.json');
    if (!response.ok) throw new Error('Ошибка запроса');

    const data = await response.json();
    const balance = data.balance;

    document.getElementById('reserve_state').textContent = balance.reserve ?? '0.00';
    document.getElementById('available_funds_state').textContent = balance.available_funds ?? '0.00';
    document.getElementById('rent_state').textContent = balance.rent ?? '0.00';
    document.getElementById('taxes_state').textContent = balance.taxes ?? '0.00';

    document.getElementById('reserve_input').value = balance.reserve ?? '0.00';
    document.getElementById('available_funds_input').value = balance.available_funds ?? '0.00';
    document.getElementById('rent_input').value = balance.rent ?? '0.00';
    document.getElementById('taxes_input').value = balance.taxes ?? '0.00';
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

