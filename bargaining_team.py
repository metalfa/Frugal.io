import random
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BargainingTeam:
    def __init__(self):
        self.negotiators = [
            {"name": "Alice", "success_rate": 0.7, "max_discount": 0.15},
            {"name": "Bob", "success_rate": 0.6, "max_discount": 0.2},
            {"name": "Charlie", "success_rate": 0.8, "max_discount": 0.1},
        ]

    def negotiate_price(self, item, original_price):
        negotiator = random.choice(self.negotiators)
        logger.debug(f"Negotiator {negotiator['name']} is attempting to negotiate for {item}")

        if random.random() < negotiator['success_rate']:
            discount = random.uniform(0.05, negotiator['max_discount'])
            new_price = original_price * (1 - discount)
            savings = original_price - new_price
            logger.debug(f"Negotiation successful. New price: ${new_price:.2f}, Savings: ${savings:.2f}")
            return {
                "success": True,
                "negotiator": negotiator['name'],
                "original_price": original_price,
                "new_price": new_price,
                "savings": savings,
            }
        else:
            logger.debug("Negotiation unsuccessful")
            return {
                "success": False,
                "negotiator": negotiator['name'],
                "original_price": original_price,
            }

def negotiate_shopping_cart(items):
    team = BargainingTeam()
    results = []

    for item in items:
        result = team.negotiate_price(item['name'], item['price'])
        result['item'] = item['name']
        results.append(result)

    return results
