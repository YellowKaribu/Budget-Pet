let currentPage = 1;
const itemsPerPage = 10;
let allTransactions = [];

function renderPage(page) {
  const container = document.getElementById('transactions');
  container.innerHTML = '';

  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const pageData = allTransactions.slice(start, end);

  if (pageData.length === 0) {
    container.textContent = 'Нет транзакций для отображения.';
    return;
  }

  const table = document.createElement('table');
  table.className = 'balance_table';

  // Заголовки
  const thead = document.createElement('thead');
  thead.innerHTML = `
    <tr>
      <th>ID</th>
      <th>Дата</th>
      <th>Тип</th>
      <th>Сумма</th>
      <th>Комментарий</th>
      <th>Категория</th>
      <th>Налог</th>
      <th>Действия</th>
    </tr>
  `;
  table.appendChild(thead);

  // Строки данных
  const tbody = document.createElement('tbody');
  pageData.forEach(transaction => {
  let rawDate = transaction.operation_date;
  if (rawDate.includes(',')) {
    rawDate = rawDate.split(',')[1].trim();
  }
  const dateStr = rawDate.split(':').slice(0, 2).join(':');

  // Добавляем смайлик по типу операции
  let typeText = '';
  if (transaction.operation_type.startsWith('income')) {
    typeText = '💰 ' + transaction.operation_type;
  } else if (transaction.operation_type.startsWith('expense')) {
    typeText = '🛒 ' + transaction.operation_type;
  } else {
    typeText = transaction.operation_type;
  }

  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${transaction.id}</td>
    <td>${dateStr}</td>
    <td>${typeText}</td>
    <td>${transaction.operation_amount}</td>
    <td>${transaction.operation_comment || '—'}</td>
    <td>${transaction.operation_category || '—'}</td>
    <td>${transaction.operation_tax_status || '—'}</td>
    <td>
      <button class="edit-btn" data-id="${transaction.id}">✏️</button>
      <button class="delete-btn" data-id="${transaction.id}">🗑️</button>
    </td>
  `;

  // Класс для покраски строк
  if (transaction.operation_type.startsWith('income')) {
    row.classList.add('income');
  } else if (transaction.operation_type.startsWith('expense')) {
    row.classList.add('expense');
  }

  tbody.appendChild(row);
});


  table.appendChild(tbody);
  container.appendChild(table);

  updatePaginationControls();
}





function updatePaginationControls() {
  const totalPages = Math.ceil(allTransactions.length / itemsPerPage);
  const controls = document.getElementById('pagination-controls');
  controls.innerHTML = '';

  const prevBtn = document.createElement('button');
  prevBtn.textContent = '← Назад';
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => {
    currentPage--;
    renderPage(currentPage);
  };
  controls.appendChild(prevBtn);

  const pageInfo = document.createElement('span');
  pageInfo.textContent = ` Страница ${currentPage} из ${totalPages} `;
  controls.appendChild(pageInfo);

  const nextBtn = document.createElement('button');
  nextBtn.textContent = 'Вперёд →';
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => {
    currentPage++;
    renderPage(currentPage);
  };
  controls.appendChild(nextBtn);
}

async function fetch_and_render_transactions_log() {
  try {
    let response = await fetch('/transactions.jsonl');
    if (!response.ok) throw new Error('Ошибка запроса');
    let data = await response.json();

    data.sort((a, b) => {
      const diff = new Date(b.operation_date).getTime() - new Date(a.operation_date).getTime();
      if (diff !== 0) return diff;
      return b.id - a.id;
    });

    allTransactions = data;
    renderPage(currentPage);
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();
  fetch_and_render_transactions_log();
});
