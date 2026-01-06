import streamlit as st
from auth.permissions import RowLevelSecurity

def render_delete_section(manager, customer_id, auth_manager=None):
    """Render the delete row section in sidebar with permission checks"""
    customer_data = manager.get_customer_data(customer_id)
    
    if not customer_data.empty and len(customer_data) > 0:
        # Check if user has delete permission
        if auth_manager and not auth_manager.has_permission('can_delete'):
            st.warning("You don't have permission to delete records.")
            return
        
        # Filter data based on user's subscriber access
        if auth_manager:
            user = auth_manager.get_current_user()
            if user and user.role != 'admin':
                user_subscriber_ids = user.subscriber_ids
                customer_data = RowLevelSecurity.filter_data_by_subscriber(
                    customer_data, 
                    user_subscriber_ids
                )
        
        if len(customer_data) > 0:
            st.header("Delete Rows")
            
            row_options = [
                f"Row {i+1}: {row['product_type']} - {row['account_number']}" 
                for i, row in customer_data.iterrows()
            ]
            
            selected_row = st.selectbox(
                "Select row to delete:",
                options=row_options,
                key=f"delete_selector_{customer_id}"
            )
            
            if selected_row:
                row_index = int(selected_row.split(":")[0].replace("Row ", "")) - 1
                selected_data = customer_data.iloc[row_index]
                
                st.write("**Selected Row Details:**")
                st.write(f"Product: {selected_data['product_type']}")
                st.write(f"Account: {selected_data['account_number']}")
                st.write(f"Current Balance: ${selected_data['current_balance']:,.2f}")
                st.write(f"Last Payment: {selected_data['last_payment_date']}")
                st.write(f"Status: {selected_data['current_status']}")
                st.write(f"Subscriber: {selected_data['subscriber_id']}")
            
            if st.button("🗑️ Delete Selected Row", type="secondary", use_container_width=True,
                        key=f"delete_button_{customer_id}"):
                row_index = int(selected_row.split(":")[0].replace("Row ", "")) - 1
                if manager.delete_row(customer_id, row_index):
                    st.rerun()