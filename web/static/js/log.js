async function fetch_and_render_transactions_log() {
  try {
    let response = await fetch('/transactions.jsonl');
    if (!response.ok) throw new Error('Ошибка запроса');
    let data = await response.json();

    const container = document.getElementById('transactions');
    container.innerHTML = ''; // очистить

    if (data.length === 0) {
      container.textContent = 'Нет транзакций для отображения.';
      return;
    }

    data.forEach(transaction => {
      const p = document.createElement('p');
      p.className = 'transaction';
      if (transaction.operation_type.startsWith('income')) p.classList.add('income');

      p.textContent = `ID: ${transaction.id}, Дата: ${transaction.operation_date}, Тип: ${transaction.operation_type}, Сумма: ${transaction.operation_amount}, Комментарий: ${transaction.operation_comment || 'Нет комментария'}`;

      if (transaction.operation_type === 'expense') {
        p.textContent += `, Категория: ${transaction.operation_category || 'Нет категории'}`;
      } else {
        p.textContent += `, Налоговый статус: ${transaction.operation_tax_status || 'Нет статуса'}`;
      }

      container.appendChild(p);
    });
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

// Вызов сразу при загрузке DOM:
window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();
  fetch_and_render_transactions_log();  // вызываем без кнопки
});

