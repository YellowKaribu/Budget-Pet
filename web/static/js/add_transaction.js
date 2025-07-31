window.addEventListener('DOMContentLoaded', () => {
  fetch_and_render_balance_sidebar();

  setupToggleOptions();
  setupFormSubmitHandler();
});

function setupToggleOptions() {
  const incomeRadio = document.getElementById("income");
  const expenseRadio = document.getElementById("expense");
  const incomeFromIP = document.getElementById("tax_rate");
  const categorySelect = document.getElementById("category");
  const incomeLabel = incomeRadio?.closest('.toggle-option');
  const expenseLabel = expenseRadio?.closest('.toggle-option');

  if (!incomeRadio || !expenseRadio || !incomeFromIP || !categorySelect || !incomeLabel || !expenseLabel) return;

  function updateFieldStates() {
    if (incomeRadio.checked) {
      incomeFromIP.disabled = false;
      incomeLabel.classList.add('selected');
      expenseLabel.classList.remove('selected');
    } else if (expenseRadio.checked) {
      incomeFromIP.disabled = true;
      incomeLabel.classList.remove('selected');
      expenseLabel.classList.add('selected');
    } else {
      incomeFromIP.disabled = true;
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

    const dateInput = form.date;
    const dateValue = dateInput.value ? dateInput.value : null;

    const data = {
      date: dateValue,
      type: form.type.value,
      tax_rate: form.tax_rate.disabled ? 0 : Number(form.tax_rate.value),
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

