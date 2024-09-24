document.addEventListener('DOMContentLoaded', function() {
    const expenseForm = document.getElementById('expense-form');
    const receiptForm = document.getElementById('receipt-form');
    const shoppingCartForm = document.getElementById('shopping-cart-form');
    const expensesList = document.getElementById('expenses');
    const totalSpentElement = document.getElementById('total-spent');
    const categoryBreakdownElement = document.getElementById('category-breakdown');
    const productSuggestionsElement = document.getElementById('product-suggestions');
    const shoppingCartItemsElement = document.getElementById('shopping-cart-items');
    const shoppingCartSuggestionsElement = document.getElementById('shopping-cart-suggestions');

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

    shoppingCartForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(shoppingCartForm);

        fetch('/upload_shopping_cart', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('Shopping cart analysis response:', data);
            if (data.success) {
                alert('Shopping cart analyzed successfully');
                shoppingCartForm.reset();
                displayShoppingCartAnalysis(data.items, data.suggestions);
            } else {
                console.error('Error analyzing shopping cart:', data.message);
                alert('Error analyzing shopping cart: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('An error occurred while analyzing the shopping cart. Please try again.');
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

    function displayShoppingCartAnalysis(items, suggestions) {
        console.log('Items:', items);
        console.log('Suggestions:', suggestions);

        let itemsHtml = '<h3>Shopping Cart Items:</h3><ul>';
        if (items && items.length > 0) {
            items.forEach(item => {
                console.log('Processing item:', item);
                if (item && item.name && item.price !== undefined) {
                    itemsHtml += `<li>${item.name}: $${item.price.toFixed(2)}</li>`;
                } else {
                    console.warn('Invalid item:', item);
                }
            });
        } else {
            console.warn('No items found in the shopping cart');
            itemsHtml += '<li>No items found in the shopping cart.</li>';
        }
        itemsHtml += '</ul>';
        
        let suggestionsHtml = '<h3>Alternative Suggestions:</h3><ul>';
        if (suggestions && suggestions.length > 0) {
            suggestions.forEach(suggestion => {
                console.log('Processing suggestion:', suggestion);
                if (suggestion && suggestion.original_item && suggestion.alternative_item) {
                    suggestionsHtml += `<li>
                        <strong>${suggestion.original_item}</strong> ($${suggestion.original_price.toFixed(2)})
                        <br>Alternative: ${suggestion.alternative_item} ($${suggestion.alternative_price.toFixed(2)})
                        <br>Potential Savings: $${(suggestion.original_price - suggestion.alternative_price).toFixed(2)}
                    </li>`;
                } else {
                    console.warn('Invalid suggestion:', suggestion);
                }
            });
        } else {
            console.warn('No alternative suggestions available');
            suggestionsHtml += '<li>No alternative suggestions available.</li>';
        }
        suggestionsHtml += '</ul>';

        if (shoppingCartItemsElement) {
            shoppingCartItemsElement.innerHTML = itemsHtml;
        } else {
            console.error('shoppingCartItemsElement not found');
        }

        if (shoppingCartSuggestionsElement) {
            shoppingCartSuggestionsElement.innerHTML = suggestionsHtml;
        } else {
            console.error('shoppingCartSuggestionsElement not found');
        }
    }

    updateAnalysis();
    updateSuggestions();
});