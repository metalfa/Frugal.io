from collections import Counter

def get_suggestions(expenses):
    # This is a simple implementation. In a real-world scenario, you would use
    # more advanced machine learning techniques for better suggestions.
    categories = [expense.category for expense in expenses]
    most_common = Counter(categories).most_common(3)
    
    suggestions = [
        f"Based on your spending habits, you might be interested in deals on {category}"
        for category, _ in most_common
    ]
    return suggestions
