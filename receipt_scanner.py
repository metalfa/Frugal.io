import os
from PIL import Image
import pytesseract
import re
from datetime import datetime

def scan_receipt(image_path):
    try:
        # Open the image using Pillow
        image = Image.open(image_path)
        
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image)
        
        # Process the extracted text to identify expense information
        amount = extract_amount(text)
        date = extract_date(text)
        merchant = extract_merchant(text)
        
        return {
            'amount': amount,
            'date': date,
            'merchant': merchant
        }
    except Exception as e:
        print(f"Error scanning receipt: {str(e)}")
        return None

def extract_amount(text):
    # Use regex to find a dollar amount in the text
    amount_match = re.search(r'\$?\d+\.\d{2}', text)
    if amount_match:
        return float(amount_match.group().replace('$', ''))
    return None

def extract_date(text):
    # Use regex to find a date in the text (assuming format MM/DD/YYYY or similar)
    date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
    if date_match:
        try:
            return datetime.strptime(date_match.group(), '%m/%d/%Y').date()
        except ValueError:
            pass
    return None

def extract_merchant(text):
    # Assuming the merchant name is on the first line of the receipt
    lines = text.split('\n')
    if lines:
        return lines[0].strip()
    return None
