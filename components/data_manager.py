import streamlit as st
import pandas as pd
from datetime import datetime

class CreditProfileManager:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'data' not in st.session_state:
            st.session_state.data = self.load_sample_data()
        
        if 'undo_stack' not in st.session_state:
            st.session_state.undo_stack = []
        
        if 'redo_stack' not in st.session_state:
            st.session_state.redo_stack = []
        
        if 'current_customer_id' not in st.session_state:
            st.session_state.current_customer_id = None
        
        if 'edited_rows' not in st.session_state:
            st.session_state.edited_rows = set()
    
    def load_sample_data(self):
        """Load sample data with subscriber IDs"""
        sample_data = {
            'customer_id': ['CUST001', 'CUST001', 'CUST002', 'CUST001', 'CUST003', 'CUST004', 'CUST005'],
            'product_type': ['Credit Card', 'Personal Loan', 'Mortgage', 'Auto Loan', 'Credit Card', 'Business Loan', 'Personal Loan'],
            'account_number': ['CC12345', 'PL67890', 'MTG54321', 'AL98765', 'CC11111', 'BL22222', 'PL33333'],
            'opening_date': ['2022-01-15', '2022-03-20', '2021-11-10', '2023-02-05', '2022-12-15', '2023-01-10', '2023-03-15'],
            'last_payment_date': ['2024-01-15', '2024-01-10', '2024-01-05', '2023-12-15', '2024-01-12', '2024-01-08', '2023-12-20'],
            'opening_balance': [0, 10000, 250000, 15000, 0, 50000, 8000],
            'credit_limit': [5000, 10000, 250000, 15000, 3000, 50000, 8000],
            'monthly_instalment': [150, 320, 1850, 450, 90, 1200, 280],
            'loan_term': [36, 36, 360, 36, 24, 48, 36],
            'current_balance': [1200, 4500, 185000, 0, 800, 12000, 3500],
            'current_status': ['Active', 'Active', 'Active', 'Closed', 'Active', 'Active', 'Pending'],
            'balance_overdue': [0, 0, 0, 0, 150, 0, 0],
            'subscriber_id': ['SUB001', 'SUB002', 'SUB001', 'SUB003', 'SUB002', 'SUB001', 'SUB003']
        }
        df = pd.DataFrame(sample_data)
        df['opening_date'] = pd.to_datetime(df['opening_date']).dt.date
        df['last_payment_date'] = pd.to_datetime(df['last_payment_date']).dt.date
        return df
    
    def get_all_customer_ids(self):
        """Get all unique customer IDs for the dropdown"""
        return sorted(st.session_state.data['customer_id'].unique())
    
    def add_new_row(self, customer_id, subscriber_id='SUB001'):
        """Add a new row for the customer with subscriber ID"""
        self.save_state()
        
        new_row = {
            'customer_id': customer_id,
            'product_type': 'New Product',
            'account_number': f'NEW{len(st.session_state.data) + 1}',
            'opening_date': datetime.now().date(),
            'last_payment_date': datetime.now().date(),
            'opening_balance': 0,
            'credit_limit': 0,
            'monthly_instalment': 0,
            'loan_term': 12,
            'current_balance': 0,
            'current_status': 'Active',
            'balance_overdue': 0,
            'subscriber_id': subscriber_id
        }
        
        new_df = pd.DataFrame([new_row])
        st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)
        st.success(f"Added new row for customer {customer_id}")
    
    # NEW METHOD: Delete row with permission checks
    def delete_row(self, customer_id, row_index, auth_manager=None):
        """Delete a specific row with permission checks"""
        self.save_state()
        
        customer_data = self.get_customer_data(customer_id)
        if 0 <= row_index < len(customer_data):
            # Get the actual index in the main dataframe
            actual_index = st.session_state.data[
                (st.session_state.data['customer_id'] == customer_id)
            ].index[row_index]
            
            # Check if user has permission to delete this specific row
            if auth_manager:
                user = auth_manager.get_current_user()
                if user and user.role != 'admin':
                    # Check if the row belongs to a subscriber the user can access
                    if 'subscriber_id' in st.session_state.data.columns:
                        row_subscriber_id = st.session_state.data.at[actual_index, 'subscriber_id']
                        if row_subscriber_id not in user.subscriber_ids:
                            st.error("You don't have permission to delete this record.")
                            return False
            
            st.session_state.data = st.session_state.data.drop(actual_index).reset_index(drop=True)
            st.success("Row deleted successfully")
            return True
        else:
            st.error("Invalid row index")
            return False
    
    # NEW METHOD: Update data with permission checks
    def update_customer_data(self, customer_id, edited_df, auth_manager=None):
        """Update customer data based on edits with permission checks"""
        self.save_state()
        
        customer_indices = st.session_state.data[
            st.session_state.data['customer_id'] == customer_id
        ].index
        
        for i, (idx, new_row) in enumerate(edited_df.iterrows()):
            if i < len(customer_indices):
                actual_index = customer_indices[i]
                
                # Check if user has permission to edit this specific row
                if auth_manager:
                    user = auth_manager.get_current_user()
                    if user and user.role != 'admin':
                        # Check if the row belongs to a subscriber the user can access
                        if 'subscriber_id' in st.session_state.data.columns:
                            row_subscriber_id = st.session_state.data.at[actual_index, 'subscriber_id']
                            if row_subscriber_id not in user.subscriber_ids:
                                st.error(f"You don't have permission to edit row {i+1}.")
                                continue
                
                for col in edited_df.columns:
                    st.session_state.data.at[actual_index, col] = new_row[col]
        
        st.success("Changes saved successfully!")
    
    # NEW METHOD: Save state for undo/redo
    def save_state(self):
        """Save current state to undo stack"""
        if 'data' in st.session_state:
            st.session_state.undo_stack.append(st.session_state.data.copy())
            st.session_state.redo_stack.clear()
    
    # NEW METHOD: Undo
    def undo(self):
        """Undo the last action"""
        if st.session_state.undo_stack:
            st.session_state.redo_stack.append(st.session_state.data.copy())
            st.session_state.data = st.session_state.undo_stack.pop()
            st.rerun()
    
    # NEW METHOD: Redo
    def redo(self):
        """Redo the last undone action"""
        if st.session_state.redo_stack:
            st.session_state.undo_stack.append(st.session_state.data.copy())
            st.session_state.data = st.session_state.redo_stack.pop()
            st.rerun()
    
    # NEW METHOD: Get customer data
    def get_customer_data(self, customer_id):
        """Get all records for a specific customer"""
        customer_data = st.session_state.data[
            st.session_state.data['customer_id'] == customer_id
        ].reset_index(drop=True)
        return customer_data
    
    # NEW METHOD: Search customer IDs
    def search_customer_ids(self, search_term):
        """Search for customer IDs that match the search term"""
        all_customers = self.get_all_customer_ids()
        if search_term:
            return [cust for cust in all_customers if search_term.upper() in cust.upper()]
        return all_customers