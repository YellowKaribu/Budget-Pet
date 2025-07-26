window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();

  setupToggleOptions();
  setupFormSubmitHandler();
});

function setupToggleOptions() {
  const incomeRadio = document.getElementById("income");
  const expenseRadio = document.getElementById("expense");
  const incomeFromIP = document.getElementById("tax_status");
  const categorySelect = document.getElementById("categorySelect");
  const incomeLabel = incomeRadio?.closest('.toggle-option');
  const expenseLabel = expenseRadio?.closest('.toggle-option');

  if (!incomeRadio || !expenseRadio || !incomeFromIP || !categorySelect || !incomeLabel || !expenseLabel) return;

  function updateFieldStates() {
    if (incomeRadio.checked) {
      incomeFromIP.disabled = false;
      categorySelect.disabled = true;
      incomeLabel.classList.add('selected');
      expenseLabel.classList.remove('selected');
    } else if (expenseRadio.checked) {
      incomeFromIP.disabled = true;
      categorySelect.disabled = false;
      incomeLabel.classList.remove('selected');
      expenseLabel.classList.add('selected');
    } else {
      incomeFromIP.disabled = true;
      categorySelect.disabled = true;
      incomeLabel.classList.remove('selected');
      expenseLabel.classList.remove('selected');
    }
  }

  incomeRadio.addEventListener("change", updateFieldStates);
  expenseRadio.addEventListener("change", updateFieldStates);

  updateFieldStates();
}

function setupFormSubmitHandler() {
  const form = document.getElementById('operation-form');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const dateInput = form.operation_date;
    const dateValue = dateInput.value ? dateInput.value : null;

    const data = {
      operation_date: dateValue,
      type: form.type.value,
      tax_status: form.tax_status.value,
      category: form.category.value,
      amount: form.amount.value,
      comment: form.comment.value
    };

    try {
      const response = await fetch('/new_operation.json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        alert('Операция успешно добавлена');
        form.reset();
      } else {
        alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
      }
    } catch (error) {
      alert('Ошибка сети или сервера');
      console.error(error);
    }
  });
}

