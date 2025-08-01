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
    // Обработка даты
    const date = new Date(transaction.operation_date);
    const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    let typeText = '';
    if (transaction.operation_type.startsWith('income')) {
      typeText = '💰 ' + transaction.operation_type;
    } else if (transaction.operation_type.startsWith('expense')) {
      typeText = '🛒 ' + transaction.operation_type;
    } else {
      typeText = transaction.operation_type;
    }

    const maxCommentLength = 11; 
    const comment = transaction.operation_comment || '—';
    const displayComment = comment.length > maxCommentLength
      ? comment.slice(0, maxCommentLength) + '...'
      : comment;

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${transaction.id}</td>
      <td>${dateStr}</td>
      <td>${typeText}</td>
      <td>${transaction.operation_amount}</td>
      <td class="comment" title="${comment.replace(/"/g, '&quot;')}">${displayComment}</td>
      <td>${transaction.operation_category || '—'}</td>
      <td>${transaction.operation_tax_rate || '—'}</td>
      <td>
        <button class="edit-btn" data-id="${transaction.id}" data-transaction='${JSON.stringify(transaction)}'>✏️</button>
        <button class="delete-btn" data-id="${transaction.id}">🗑️</button>
      </td>
    `;

    if (transaction.operation_type.startsWith('income')) {
      row.classList.add('income');
    } else if (transaction.operation_type.startsWith('expense')) {
      row.classList.add('expense');
    }

    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  container.appendChild(table);

  attachButtonHandlers();
  updatePaginationControls();
}

function attachButtonHandlers() {
  document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-id');
      if (confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
        try {
          const response = await fetch(`/delete_operation/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });
          const result = await response.json();
          if (result.ok) {
            alert('Транзакция удалена!');
            await fetch_and_render_transactions_log();
          } else {
            alert(`Ошибка: ${result.error}`);
          }
        } catch (error) {
          alert(`Ошибка: ${error}`);
        }
      }
    });
  });

  document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', () => {
      const transaction = JSON.parse(button.getAttribute('data-transaction'));
      showEditModal(transaction);
    });
  });
}

function showEditModal(transaction) {
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.innerHTML = `
    <div class="modal-content">
      <span class="close-btn">&times;</span>
      <h2>Редактировать транзакцию #${transaction.id}</h2>
      <form id="edit-transaction-form">
        <label>Дата и время:
          <input type="datetime-local" name="operation_date" value="${new Date(transaction.operation_date).toISOString().slice(0, 16)}" required>
        </label>
        <label>Тип:
          <select name="operation_type" required>
            <option value="income" ${transaction.operation_type === 'income' ? 'selected' : ''}>Доход</option>
            <option value="expense" ${transaction.operation_type === 'expense' ? 'selected' : ''}>Расход</option>
          </select>
        </label>
        <label>Сумма:
          <input type="number" name="operation_amount" step="0.01" value="${transaction.operation_amount}" required>
        </label>
        <label>Категория (для расходов):
          <select name="operation_category">
            <option value="Доход" ${!transaction.operation_category ? 'selected' : ''}>Доход</option>
            <option value="Еда" ${transaction.operation_category === 1 ? 'selected' : ''}>Еда</option>
            <option value="Коммуналка" ${transaction.operation_category === 2 ? 'selected' : ''}>Коммуналка</option>
            <option value="Лекарства" ${transaction.operation_category === 3 ? 'selected' : ''}>Лекарства</option>
            <option value="Развлечения" ${transaction.operation_category === 4 ? 'selected' : ''}>Развлечения</option>
            <option value="Прочее" ${transaction.operation_category === 5 ? 'selected' : ''}>Прочее</option>
          </select>
        </label>
        <label>Комментарий:
          <input type="text" name="operation_comment" value="${transaction.operation_comment || ''}">
        </label>
        <label>Налог:
          <input type="number" name="operation_tax_rate" step="0.01" value="${transaction.operation_tax_rate}" required>
        </label>
        </label>
        <button type="submit">Сохранить</button>
      </form>
    </div>
  `;
  document.body.appendChild(modal);

  const form = modal.querySelector('#edit-transaction-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = {
      operation_date: formData.get('operation_date'),
      operation_type: formData.get('operation_type'),
      operation_amount: parseFloat(formData.get('operation_amount')),
      operation_category: formData.get('operation_category') || null,
      operation_comment: formData.get('operation_comment') || null,
      operation_tax_rate: formData.get('operation_tax_rate')
    };

    try {
      console.log('off')
  const response = await fetch(`/edit_operation.json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: transaction.id,
      date: data.operation_date,
      type: data.operation_type,
      amount: data.operation_amount,
      category: data.operation_category,
      tax_rate: data.operation_tax_rate,
      comment: data.operation_comment
    })
  });

  const result = await response.json();

  if (result.status === 'success') {
    alert('Транзакция обновлена!');
    modal.remove();
    await fetch_and_render_transactions_log();
  } else {
    alert(`Ошибка: ${result.error}`);
  }
} catch (error) {
  alert(`Ошибка: ${error}`);
}

  });

  modal.querySelector('.close-btn').addEventListener('click', () => {
    modal.remove();
  });
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
  fetch_and_render_transactions_log();
});