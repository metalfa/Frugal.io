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

        # Check if the file exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None

        # Open the image using Pillow
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Error opening image: {str(e)}")
            return None

        # Use pytesseract to extract text from the image
        logger.debug("Extracting text from image using pytesseract")
        try:
            text = pytesseract.image_to_string(image)
            logger.debug(f"Extracted text from image:\n{text}")
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return None

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
        match = re.search(r'(.+?)\s+\$?(\d+\.\d{2})(?:\s+|$)', line)
        if match:
            item_name = match.group(1).strip()
            price = float(match.group(2))

            items.append({"name": item_name, "price": price})
            logger.debug(f"Matched item: {item_name}, price: ${price:.2f}")
        else:
            logger.debug(f"No match found for line: {line}")

    logger.debug(f"Extracted items: {items}")
    return items

def suggest_alternatives(items):
    logger.debug("Generating alternative suggestions")
    suggestions = []
    for item in items:
        suggestion = {
            "original_item": item["name"],
            "original_price": item["price"],
            "alternative_item": f"Alternative for {item['name']}",
            "alternative_price": item["price"] * 0.9  # 10% cheaper alternative
        }
        suggestions.append(suggestion)
        logger.debug(f"Generated suggestion: {suggestion}")
    return suggestions
