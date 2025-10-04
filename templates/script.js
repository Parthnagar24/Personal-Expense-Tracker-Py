const form = document.getElementById("expense-form");
const amountInput = document.getElementById("amount");
const dateInput = document.getElementById("date");
const noteInput = document.getElementById("note");
const categoryInput = document.getElementById("category");
const expenseTableBody = document.getElementById("expense-table-body");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const expenseIdInput = document.getElementById("expense-id");
const messageArea = document.getElementById("message-area");

// Initial load of expenses
document.addEventListener("DOMContentLoaded", fetchExpenses);

async function fetchExpenses() {
  try {
    const response = await fetch("/api/expenses");
    if (!response.ok) throw new Error("Failed to fetch expenses");
    const expenses = await response.json();
    renderExpenses(expenses);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function renderExpenses(expenses) {
  expenseTableBody.innerHTML = "";
  if (expenses.length === 0) {
    expenseTableBody.innerHTML =
      '<tr><td colspan="5">No expenses recorded yet.</td></tr>';
    return;
  }
  expenses.forEach((expense) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${expense.date}</td>
      <td>$${expense.amount.toFixed(2)}</td>
      <td>${expense.category}</td>
      <td>${expense.note}</td>
      <td class="actions">
        <button class="update-btn" onclick="prepareUpdate(${
          expense.id
        })">Update</button>
        <button class="delete-btn" onclick="deleteExpense(${
          expense.id
        })">Delete</button>
      </td>
    `;
    expenseTableBody.appendChild(row);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const expenseId = expenseIdInput.value;
  const expenseData = {
    amount: amountInput.value,
    date: dateInput.value,
    note: noteInput.value,
    category: categoryInput.value || "Uncategorized",
  };

  try {
    let response;
    if (expenseId) {
      response = await fetch(`/api/expenses/${expenseId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(expenseData),
      });
    } else {
      response = await fetch("/api/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(expenseData),
      });
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    form.reset();
    cancelUpdate();
    await fetchExpenses();
    showMessage("Expense saved successfully!", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

async function deleteExpense(id) {
  if (!confirm("Are you sure you want to delete this expense?")) return;
  try {
    const response = await fetch(`/api/expenses/${id}`, { method: "DELETE" });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    await fetchExpenses();
    showMessage("Expense deleted successfully!", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function prepareUpdate(id) {
  const response = await fetch("/api/expenses");
  const expenses = await response.json();
  const expense = expenses.find((exp) => exp.id === id);

  if (expense) {
    expenseIdInput.value = expense.id;
    amountInput.value = expense.amount;
    dateInput.value = expense.date;
    noteInput.value = expense.note;
    categoryInput.value = expense.category;

    submitBtn.textContent = "Update Expense";
    cancelBtn.style.display = "inline-block";
  }
}

cancelBtn.addEventListener("click", cancelUpdate);

function cancelUpdate() {
  form.reset();
  expenseIdInput.value = "";
  submitBtn.textContent = "Add Expense";
  cancelBtn.style.display = "none";
}

function showMessage(message, type) {
  messageArea.textContent = message;
  messageArea.className = `message ${type}`;
  messageArea.style.display = "block";
  setTimeout(() => {
    messageArea.style.display = "none";
  }, 3000);
}
