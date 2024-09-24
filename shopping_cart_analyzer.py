import os
from PIL import Image
import pytesseract
import re
from flask import current_app
import logging
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def analyze_shopping_cart(image_path):
    try:
        logger.debug(f"Analyzing shopping cart image: {image_path}")
        
        # Open the image using Pillow
        image = Image.open(image_path)
        
        # Use pytesseract to extract text from the image
        logger.debug("Extracting text from image using pytesseract")
        text = pytesseract.image_to_string(image)
        logger.debug(f"Extracted text: {text}")
        
        # Process the extracted text to identify items and prices
        items = extract_items(text)
        
        logger.debug(f"Extracted items: {items}")
        return items
    except Exception as e:
        logger.error(f"Error analyzing shopping cart: {str(e)}")
        return None

def extract_items(text):
    # Split the text into lines
    lines = text.split('\n')
    
    items = []
    for line in lines:
        # Skip empty lines
        if not line.strip():
            logger.debug(f"Skipping empty line")
            continue
        
        # Use regex to find item name and price
        match = re.search(r'(.+?)\s+\$?(\d+\.\d{2})', line)
        if match:
            item_name = match.group(1).strip()
            price = float(match.group(2))
            
            # Skip the subtotal line
            if "subtotal" not in item_name.lower():
                items.append({"name": item_name, "price": price})
                logger.debug(f"Matched item: {item_name}, price: ${price:.2f}")
        else:
            logger.debug(f"No match found for line: {line}")
    
    logger.debug(f"Extracted items: {items}")
    return items

# Small database of alternative products
alternative_products = {
    "Milk": [
        {"name": "Organic Milk", "price": 4.99},
        {"name": "Soy Milk", "price": 3.99},
        {"name": "Almond Milk", "price": 3.49},
    ],
    "Bread": [
        {"name": "Whole Grain Bread", "price": 3.99},
        {"name": "Gluten-Free Bread", "price": 5.99},
        {"name": "Sourdough Bread", "price": 4.49},
    ],
    "Eggs": [
        {"name": "Free-Range Eggs", "price": 5.99},
        {"name": "Organic Eggs", "price": 6.49},
        {"name": "Quail Eggs", "price": 7.99},
    ],
    "Default": [
        {"name": "Generic Alternative 1", "price": 0},
        {"name": "Generic Alternative 2", "price": 0},
        {"name": "Generic Alternative 3", "price": 0},
    ]
}

def suggest_alternatives(items):
    suggestions = []
    for item in items:
        original_name = item["name"]
        original_price = item["price"]
        
        # Find matching category or use default
        category = next((cat for cat in alternative_products.keys() if cat.lower() in original_name.lower()), "Default")
        alternatives = alternative_products[category]
        
        # Select a random alternative
        alternative = random.choice(alternatives)
        alternative_name = alternative["name"]
        
        # If using default category, adjust the price
        if category == "Default":
            alternative_price = round(original_price * random.uniform(0.8, 0.95), 2)
        else:
            alternative_price = alternative["price"]
        
        suggestion = {
            "original_item": original_name,
            "original_price": original_price,
            "alternative_item": alternative_name,
            "alternative_price": alternative_price
        }
        suggestions.append(suggestion)
        logger.debug(f"Generated suggestion: {suggestion}")
    
    logger.debug(f"All generated suggestions: {suggestions}")
    return suggestions
