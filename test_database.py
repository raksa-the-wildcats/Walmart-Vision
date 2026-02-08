"""
Test script to verify database is working correctly

"""

from database import ReceiptDatabase
import os
import sqlite3

print("Testing Receipt Database...")
print("=" * 50)

# Initialize database
db = ReceiptDatabase()

print(f"\n1. Database file: {db.db_name}")
print(f"2. Database exists: {os.path.exists(db.db_name)}")
print(f"3. Database size: {os.path.getsize(db.db_name) if os.path.exists(db.db_name) else 0} bytes")

# Check table structure
print("\n4. Checking database structure...")
conn = sqlite3.connect(db.db_name)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='receipts'")
result = cursor.fetchone()
if result:
    print("   Table 'receipts' exists:")
    print(f"   {result[0]}")
else:
    print("   ⚠️ WARNING: Table 'receipts' does not exist!")
conn.close()

# Add a test receipt
print("\n5. Adding test receipt...")
try:
    receipt_id = db.add_receipt(
        store_name="Test Store",
        date="02/07/2026",
        subtotal=100.00,
        tax=8.25,
        total=108.25,
        transaction_id="TEST123"
    )
    print(f"   ✅ Receipt ID: {receipt_id}")
except Exception as e:
    print(f"   ❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

# Get all receipts
print("\n6. Retrieving all receipts...")
receipts = db.get_all_receipts()
print(f"   Number of receipts: {len(receipts)}")

if len(receipts) > 0:
    print("\n7. Receipt data:")
    print(receipts)
    
    print("\n8. Spending summary:")
    summary = db.get_spending_summary()
    print(summary)
    
    # Direct SQL query
    print("\n9. Direct SQL query:")
    conn = sqlite3.connect(db.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, store_name, date, total FROM receipts")
    rows = cursor.fetchall()
    for row in rows:
        print(f"   ID: {row[0]}, Store: {row[1]}, Date: {row[2]}, Total: ${row[3]}")
    conn.close()
else:
    print("\n   ⚠️ WARNING: No receipts found in database!")
    
    # Try direct query
    print("\n   Trying direct SQL query...")
    conn = sqlite3.connect(db.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM receipts")
    count = cursor.fetchone()[0]
    print(f"   Direct count from SQL: {count}")
    conn.close()

print("\n" + "=" * 50)
print("Test complete!")