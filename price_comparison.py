import random

def compare_prices(product, price):
    # This is a mock implementation. In a real-world scenario, you would integrate
    # with a price comparison API or scrape e-commerce websites for actual data.
    alternatives = [
        {"name": f"{product} - Alternative 1", "price": price * 0.9},
        {"name": f"{product} - Alternative 2", "price": price * 0.95},
        {"name": f"{product} - Alternative 3", "price": price * 1.05},
    ]
    return sorted(alternatives, key=lambda x: x['price'])
