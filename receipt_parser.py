import re
from datetime import datetime

class ReceiptParser:
    def __init__(self):
        pass
    
    def parse_walmart_receipt(self, ocr_text):
        """
        Parse Walmart receipt text and extract key information
        Returns: dict with extracted data
        """
        result = {
            'store_name': None,
            'date': None,
            'subtotal': None,
            'tax': None,
            'total': None,
            'transaction_id': None
        }
        
        # Extract store name
        if 'walmart' in ocr_text.lower():
            result['store_name'] = 'Walmart'
        
        # Extract date (various formats)
        # Format: MM/DD/YYYY or MM-DD-YYYY
        date_patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # M/D/YY or MM/DD/YY
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, ocr_text)
            if date_match:
                result['date'] = date_match.group(1)
                break
        
        # Extract subtotal
        subtotal_patterns = [
            r'SUBTOTAL\s*\$?(\d+\.?\d*)',
            r'SUB[\s-]?TOTAL\s*\$?(\d+\.?\d*)',
        ]
        
        for pattern in subtotal_patterns:
            subtotal_match = re.search(pattern, ocr_text, re.IGNORECASE)
            if subtotal_match:
                result['subtotal'] = float(subtotal_match.group(1))
                break
        
        # Extract tax
        tax_patterns = [
            r'TAX\s*\$?(\d+\.?\d*)',
            r'SALES TAX\s*\$?(\d+\.?\d*)',
        ]
        
        for pattern in tax_patterns:
            tax_match = re.search(pattern, ocr_text, re.IGNORECASE)
            if tax_match:
                result['tax'] = float(tax_match.group(1))
                break
        
        # Extract total (make sure we don't match SUBTOTAL)
        total_patterns = [
            r'(?<!SUB)TOTAL\s*\$?(\d+\.?\d*)',  # Negative lookbehind to exclude SUBTOTAL
            r'\bTOTAL\s*\$?(\d+\.?\d*)',  # Word boundary approach
            r'AMOUNT DUE\s*\$?(\d+\.?\d*)',
        ]
        
        for pattern in total_patterns:
            total_match = re.search(pattern, ocr_text, re.IGNORECASE)
            if total_match:
                result['total'] = float(total_match.group(1))
                break
        
        # Extract transaction ID
        trans_patterns = [
            r'TRANS(?:ACTION)?\s*ID\s*[-:]?\s*([A-Z0-9]+)',
            r'TRANS\s*ID\s*[-:]?\s*([A-Z0-9]+)',
        ]
        
        for pattern in trans_patterns:
            trans_match = re.search(pattern, ocr_text, re.IGNORECASE)
            if trans_match:
                result['transaction_id'] = trans_match.group(1)
                break
        
        return result
    
    def parse_generic_receipt(self, ocr_text):
        """
        Generic parser for any receipt
        Falls back to this if store-specific parser fails
        """
        # For MVP, I'll just use the Walmart parser
        return self.parse_walmart_receipt(ocr_text)
    
    def validate_parsed_data(self, parsed_data):
        """
        Validate that essential fields were extracted
        Returns: (is_valid, missing_fields)
        """
        required_fields = ['store_name', 'date', 'total']
        missing = [field for field in required_fields if not parsed_data.get(field)]
        
        is_valid = len(missing) == 0
        return is_valid, missing