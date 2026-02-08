import streamlit as st
from PIL import Image
import pandas as pd
from database import ReceiptDatabase
from ocr_processor import ReceiptOCR
from receipt_parser import ReceiptParser
import os

# Page configuration
st.set_page_config(
    page_title="Receipt Tracker",
    page_icon="🧾",
    layout="wide"
)

# Initialize components
def init_components():
    db = ReceiptDatabase()
    ocr = ReceiptOCR()
    parser = ReceiptParser()
    return db, ocr, parser

db, ocr, parser = init_components()

# Initialize session state
if 'ocr_text' not in st.session_state:
    st.session_state.ocr_text = None
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None

# Title and description
st.title("🧾 Receipt Tracker")
st.markdown("Upload receipt images to track your spending")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigation", ["Upload Receipt", "View Receipts", "Spending Summary"])

# Page: Upload Receipt
if page == "Upload Receipt":
    st.header("Upload a Receipt")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a receipt image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, width='stretch')
        
        with col2:
            st.subheader("Preprocessed Image")
            processed_img = ocr.get_processed_image(image)
            st.image(processed_img, width='stretch')
        
        # Process button
        if st.button("Extract Data", type="primary"):
            with st.spinner("Processing receipt..."):
                # Perform OCR
                ocr_text = ocr.extract_text(image)
                st.session_state.ocr_text = ocr_text  # Save to session state
                
                # Show raw OCR text in expander
                with st.expander("View Raw OCR Text"):
                    st.text(ocr_text)
                
                # Parse the receipt
                parsed_data = parser.parse_walmart_receipt(ocr_text)
                st.session_state.parsed_data = parsed_data  # Save to session state
                
                # Validate
                is_valid, missing_fields = parser.validate_parsed_data(parsed_data)
                
                if is_valid:
                    st.success("✅ Receipt data extracted successfully!")
                else:
                    st.warning(f"⚠️ Some fields are missing: {', '.join(missing_fields)}")
        
        # Display form if we have parsed data
        if st.session_state.parsed_data is not None:
            parsed_data = st.session_state.parsed_data
            
            # Display extracted data
            st.subheader("Extracted Data")
            
            # Create editable form
            with st.form("receipt_form"):
                store_name = st.text_input("Store Name", value=parsed_data.get('store_name', ''))
                date = st.text_input("Date", value=parsed_data.get('date', ''))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    subtotal = st.number_input("Subtotal ($)", 
                                              value=float(parsed_data.get('subtotal') or 0), 
                                              format="%.2f")
                with col2:
                    tax = st.number_input("Tax ($)", 
                                        value=float(parsed_data.get('tax') or 0), 
                                        format="%.2f")
                with col3:
                    total = st.number_input("Total ($)", 
                                          value=float(parsed_data.get('total') or 0), 
                                          format="%.2f")
                
                transaction_id = st.text_input("Transaction ID", 
                                              value=parsed_data.get('transaction_id', ''))
                
                # Submit button
                submitted = st.form_submit_button("Save to Database", type="primary")
                
                if submitted:
                    st.write("**[DEBUG] Form submitted!**")
                    st.write(f"Store: {store_name}")
                    st.write(f"Date: {date}")
                    st.write(f"Subtotal: {subtotal}")
                    st.write(f"Tax: {tax}")
                    st.write(f"Total: {total}")
                    st.write(f"Transaction ID: {transaction_id}")
                    
                    if store_name and date and total > 0:
                        try:
                            st.write("**[DEBUG] Validation passed, calling database...**")
                            # Save to database
                            receipt_id = db.add_receipt(
                                store_name=store_name,
                                date=date,
                                subtotal=subtotal,
                                tax=tax,
                                total=total,
                                transaction_id=transaction_id,
                                image_path=uploaded_file.name,
                                raw_ocr_text=st.session_state.ocr_text
                            )
                            st.success(f"✅ Receipt saved successfully! (ID: {receipt_id})")
                            st.balloons()
                            
                            # Verify immediately
                            st.write("**[DEBUG] Verifying save...**")
                            all_receipts = db.get_all_receipts()
                            st.write(f"Total receipts in database now: {len(all_receipts)}")
                            
                            # Clear session state
                            st.session_state.ocr_text = None
                            st.session_state.parsed_data = None
                            
                            # Add a note to check other pages
                            st.info("✅ Receipt saved! Navigate to 'View Receipts' or 'Spending Summary' to see your data!")
                            
                        except Exception as e:
                            st.error(f"❌ Error saving to database: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                    else:
                        st.error("❌ Please fill in required fields: Store Name, Date, and Total")
                        st.write(f"Validation failed: store_name={bool(store_name)}, date={bool(date)}, total>0={total > 0}")

# Page: View Receipts
elif page == "View Receipts":
    st.header("All Receipts")
    
    # Debug: Show database path
    with st.expander("🔍 Debug Info"):
        st.write(f"Database file: {db.db_name}")
        st.write(f"Database exists: {os.path.exists(db.db_name)}")
    
    receipts_df = db.get_all_receipts()
    
    if len(receipts_df) > 0:
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Receipts", len(receipts_df))
        with col2:
            st.metric("Total Spent", f"${receipts_df['total'].sum():.2f}")
        with col3:
            st.metric("Total Tax", f"${receipts_df['tax'].sum():.2f}")
        with col4:
            st.metric("Avg Per Receipt", f"${receipts_df['total'].mean():.2f}")
        
        st.divider()
        
        # Display table
        display_df = receipts_df[['id', 'store_name', 'date', 'subtotal', 'tax', 'total', 'transaction_id', 'created_at']]
        st.dataframe(display_df, width='stretch')
        
        # Option to delete receipts
        st.subheader("Delete Receipt")
        receipt_id_to_delete = st.number_input("Enter Receipt ID to delete", min_value=1, step=1)
        if st.button("Delete", type="secondary"):
            db.delete_receipt(receipt_id_to_delete)
            st.success(f"Receipt {receipt_id_to_delete} deleted!")
            st.rerun()
    else:
        st.info("No receipts found. Upload your first receipt!")

# Page: Spending Summary
elif page == "Spending Summary":
    st.header("Spending Summary by Store")
    
    # Debug: Show database path
    with st.expander("🔍 Debug Info"):
        st.write(f"Database file: {db.db_name}")
        all_receipts = db.get_all_receipts()
        st.write(f"Total receipts in database: {len(all_receipts)}")
    
    summary_df = db.get_spending_summary()
    
    if len(summary_df) > 0:
        # Display summary table
        st.dataframe(summary_df, width='stretch')
        
        # Visualizations
        st.subheader("Total Spending by Store")
        st.bar_chart(summary_df.set_index('store_name')['total_spent'])
        
        st.subheader("Number of Receipts by Store")
        st.bar_chart(summary_df.set_index('store_name')['num_receipts'])
        
    else:
        st.info("No spending data available yet. Upload some receipts!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("Receipt Tracker MVP - Track your spending from receipt images using OCR")