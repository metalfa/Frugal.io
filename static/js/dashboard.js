document.addEventListener('DOMContentLoaded', function() {
    const expenseForm = document.getElementById('expense-form');
    const receiptForm = document.getElementById('receipt-form');
    const expensesList = document.getElementById('expenses');
    const totalSpentElement = document.getElementById('total-spent');
    const categoryBreakdownElement = document.getElementById('category-breakdown');
    const productSuggestionsElement = document.getElementById('product-suggestions');

    expenseForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const amount = document.getElementById('amount').value;
        const category = document.getElementById('category').value;
        const description = document.getElementById('description').value;

        fetch('/add_expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount, category, description }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Expense added successfully');
                expenseForm.reset();
                updateExpenses();
                updateAnalysis();
                updateSuggestions();
            } else {
                alert('Error adding expense');
            }
        });
    });

    receiptForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(receiptForm);

        fetch('/upload_receipt', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Receipt processed successfully');
                receiptForm.reset();
                updateExpenses();
                updateAnalysis();
                updateSuggestions();
            } else {
                alert('Error processing receipt: ' + data.message);
            }
        });
    });

    function updateExpenses() {
        fetch('/dashboard')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newExpensesList = doc.getElementById('expenses');
                expensesList.innerHTML = newExpensesList.innerHTML;
            });
    }

    function updateAnalysis() {
        fetch('/analyze_expenses')
            .then(response => response.json())
            .then(data => {
                totalSpentElement.textContent = `Total Spent: $${data.total_spent.toFixed(2)}`;
                
                let breakdownHtml = '<h3>Category Breakdown:</h3><ul>';
                for (const [category, amount] of Object.entries(data.category_breakdown)) {
                    breakdownHtml += `<li>${category}: $${amount.toFixed(2)}</li>`;
                }
                breakdownHtml += '</ul>';
                categoryBreakdownElement.innerHTML = breakdownHtml;
            });
    }

    function updateSuggestions() {
        fetch('/get_suggestions')
            .then(response => response.json())
            .then(suggestions => {
                let suggestionsHtml = '<ul>';
                suggestions.forEach(suggestion => {
                    suggestionsHtml += `<li>${suggestion}</li>`;
                });
                suggestionsHtml += '</ul>';
                productSuggestionsElement.innerHTML = suggestionsHtml;
            });
    }

    // Initial updates
    updateAnalysis();
    updateSuggestions();
});
