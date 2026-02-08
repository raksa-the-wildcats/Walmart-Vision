import sqlite3
from datetime import datetime
import pandas as pd

class ReceiptDatabase:
    def __init__(self, db_name="receipts.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                date TEXT,
                subtotal REAL,
                tax REAL,
                total REAL,
                transaction_id TEXT,
                image_path TEXT,
                created_at TEXT,
                raw_ocr_text TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_receipt(self, store_name, date, subtotal, tax, total, 
                    transaction_id=None, image_path=None, raw_ocr_text=None):
        """Add a new receipt to the database"""
        try:
            print(f"[DEBUG] Attempting to save receipt:")
            print(f"  Store: {store_name}")
            print(f"  Date: {date}")
            print(f"  Total: {total}")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO receipts (store_name, date, subtotal, tax, total, 
                                    transaction_id, image_path, created_at, raw_ocr_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (store_name, date, subtotal, tax, total, transaction_id, 
                  image_path, created_at, raw_ocr_text))
            
            receipt_id = cursor.lastrowid
            conn.commit()
            
            print(f"[DEBUG] Receipt saved successfully with ID: {receipt_id}")
            
            # Verify it was actually saved
            cursor.execute("SELECT COUNT(*) FROM receipts WHERE id = ?", (receipt_id,))
            count = cursor.fetchone()[0]
            print(f"[DEBUG] Verification - Receipt exists in DB: {count > 0}")
            
            conn.close()
            
            return receipt_id
            
        except Exception as e:
            print(f"[ERROR] Failed to save receipt: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_all_receipts(self):
        """Get all receipts as a pandas DataFrame"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM receipts ORDER BY date DESC", conn)
        conn.close()
        return df
    
    def get_spending_summary(self):
        """Get spending summary by store"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT 
                store_name,
                COUNT(*) as num_receipts,
                SUM(total) as total_spent,
                SUM(tax) as total_tax,
                AVG(total) as avg_spent
            FROM receipts
            GROUP BY store_name
            ORDER BY total_spent DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def delete_receipt(self, receipt_id):
        """Delete a receipt by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
        conn.commit()
        conn.close()