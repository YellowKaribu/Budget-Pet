window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();

  const form = document.getElementById('statistics-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const filters = collectFilters();
    const resultDiv = document.getElementById('statistics-result');
    resultDiv.innerHTML = '<p>Загрузка...</p>';

    try {
      const response = await fetch('/api/statistics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
    });
      if (!response.ok) throw new Error('Ошибка запроса');

      const data = await response.json();
      console.log("received data", data);
      renderStatistics(data);
    } catch (error) {
      resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${error.message}</p>`;
    }
  });
});

function collectFilters() {
  const startDate = document.getElementById('start-date').value;
  const endDate = document.getElementById('end-date').value;

  const types = Array.from(document.querySelectorAll('input[name="type"]:checked'))
    .map(cb => cb.value);

  const categories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
    .map(cb => cb.value);

  return { start_date: startDate, end_date: endDate, types, categories };
}

function renderStatistics(data) {
  const resultDiv = document.getElementById('statistics-result');
  if (!data || !data.summary || data.summary.length === 0) {
    resultDiv.innerHTML = '<p>Нет данных для отображения.</p>';
    return;
  }
  // общая сумма
  let totalRow = '';
  if (data.total !== undefined) {
    totalRow = `
      <tr style="font-weight: bold; background-color: #3b3f92; color: white;">
        <td>Общая сумма</td>
        <td>${data.total}</td>
      </tr>
    `;
  }

  let html = `
    <table class="balance_table">
      <thead>
        <tr>
          <th>Категория</th>
          <th>Сумма</th>
        </tr>
      </thead>
      <tbody>
      ${totalRow}
  `;

  for (const row of data.summary) {
    html += `<tr><td>${row.category}</td><td>${row.total}</td></tr>`;
  }

  html += '</tbody></table>';
  resultDiv.innerHTML = html;
}
