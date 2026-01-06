import streamlit as st
from components.utils import render_delete_section
from auth.permissions import RowLevelSecurity

def render_sidebar(manager, auth_manager):
    """Render the sidebar with search and actions"""
    with st.sidebar:
        st.header("Customer Search")
        
        # Get user permissions
        user = auth_manager.get_current_user()
        user_subscriber_ids = user.subscriber_ids if user else []
        is_admin = user.role == 'admin' if user else False
        
        # Filter customer IDs based on user access
        all_customers = manager.get_all_customer_ids()
        accessible_customers = RowLevelSecurity.filter_customer_ids(
            all_customers, 
            st.session_state.data, 
            user_subscriber_ids
        )
        
        if accessible_customers:
            if 'customer_search' not in st.session_state:
                st.session_state.customer_search = ""
            
            search_term = st.text_input(
                "Search Customer ID:",
                value=st.session_state.customer_search,
                placeholder="Type to search..."
            )
            
            st.session_state.customer_search = search_term
            
            # Filter customers based on search term and permissions
            if search_term:
                filtered_customers = [cust for cust in accessible_customers 
                                    if search_term.upper() in cust.upper()]
            else:
                filtered_customers = accessible_customers
            
            if filtered_customers:
                selected_customer = st.selectbox(
                    "Select Customer:",
                    options=filtered_customers,
                    index=_get_customer_index(filtered_customers)
                )
                
                if selected_customer != st.session_state.get('current_customer_id'):
                    st.session_state.current_customer_id = selected_customer
                    st.rerun()
                
                if search_term:
                    st.caption(f"Found {len(filtered_customers)} matching customer(s)")
                else:
                    st.caption(f"Accessible customers: {len(filtered_customers)}/{len(all_customers)}")
            else:
                st.warning("No customers found matching your search")
                if st.button("Clear Search"):
                    st.session_state.customer_search = ""
                    st.rerun()
        else:
            st.warning("No customer data available for your access level")
        
        st.header("Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            disabled = len(st.session_state.undo_stack) == 0 or not auth_manager.has_permission('can_edit')
            if st.button("↶ Undo", use_container_width=True, disabled=disabled):
                manager.undo()
        
        with col2:
            disabled = len(st.session_state.redo_stack) == 0 or not auth_manager.has_permission('can_edit')
            if st.button("↷ Redo", use_container_width=True, disabled=disabled):
                manager.redo()
        
        if st.session_state.get('current_customer_id') and auth_manager.has_permission('can_edit'):
            if st.button("➕ Add New Row", use_container_width=True):
                manager.add_new_row(st.session_state.current_customer_id, user_subscriber_ids[0] if user_subscriber_ids else 'SUB001')
                st.rerun()
        
        # Delete Section - Only show if user has delete permission
        if (st.session_state.current_customer_id and 
            auth_manager.has_permission('can_delete')):
            render_delete_section(manager, st.session_state.current_customer_id, auth_manager)
        
        st.header("Data Management")
        
        st.caption(f"Undo stack: {len(st.session_state.undo_stack)}")
        st.caption(f"Redo stack: {len(st.session_state.redo_stack)}")
        
        # Export button - Only show if user has export permission
        if auth_manager.has_permission('can_export'):
            if st.button("📥 Export Data", use_container_width=True):
                # Filter data based on user permissions before export
                export_data = st.session_state.data
                if not is_admin and 'subscriber_id' in export_data.columns:
                    export_data = RowLevelSecurity.filter_data_by_subscriber(
                        export_data, 
                        user_subscriber_ids
                    )
                
                csv = export_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="credit_profiles.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    return st.session_state.get('current_customer_id')

def _get_customer_index(filtered_customers):
    """Get the index of the current customer in filtered list"""
    current_customer = st.session_state.get('current_customer_id')
    if not current_customer or current_customer not in filtered_customers:
        return 0
    return filtered_customers.index(current_customer)