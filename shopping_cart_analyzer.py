import os
from PIL import Image
import pytesseract
import re
from flask import current_app
import logging

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
        
        return items
    except Exception as e:
        logger.error(f"Error analyzing shopping cart: {str(e)}")
        return None

def extract_items(text):
    # Split the text into lines
    lines = text.split('\n')
    
    items = []
    for line in lines:
        # Use regex to find item name and price
        match = re.search(r'(.*?)\s*\$?(\d+\.\d{2})', line)
        if match:
            item_name = match.group(1).strip()
            price = float(match.group(2))
            items.append({"name": item_name, "price": price})
    
    logger.debug(f"Extracted items: {items}")
    return items

def suggest_alternatives(items):
    # This is a placeholder function. In a real-world scenario, you would
    # integrate with a price comparison API or database to suggest alternatives.
    suggestions = []
    for item in items:
        suggestion = {
            "original_item": item["name"],
            "original_price": item["price"],
            "alternative_item": f"Alternative {item['name']}",
            "alternative_price": round(item["price"] * 0.9, 2)  # 10% cheaper as an example
        }
        suggestions.append(suggestion)
    logger.debug(f"Generated suggestions: {suggestions}")
    return suggestions
