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

  pageData.forEach(transaction => {
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
