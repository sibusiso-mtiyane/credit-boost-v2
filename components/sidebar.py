import streamlit as st
from components.utils import render_delete_section
from auth.permissions import RowLevelSecurity

def render_sidebar(manager, auth_manager):
    """Render the sidebar with expandable sections"""
    
    st.markdown("""
    <style>

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F2A66, #164DF2);
        color: #FFFFFF !important;
    }

    /* Remove all expander borders and containers */
    /*div[data-testid="stExpander"],
    div[data-testid="stExpander"] > div,
    div[data-testid="stExpander"] > div > div {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        color: #FFFFFF !important;
    }*/
                
    div[data-testid="stExpander"],
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] summary {
    border: none !important;
    box-shadow: none !important;
    outline: none !important; /* Removes focus ring when clicked */
    background: transparent !important;
    }

    /* Expander header styling */
    div[data-testid="stExpander"] div[role="button"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        border-radius: 8px;
        padding: 0.6rem 0.75rem;
        margin-bottom: 0.25rem;
        transition: background 0.2s ease;
    }

    /* Hover state */
    div[data-testid="stExpander"] div[role="button"]:hover {
        background: rgba(255, 255, 255, 0.16) !important;
    }

    /* Target the expander chevron icon */
    div[data-testid="stExpander"] svg[data-testid="stExpanderToggleIcon"] {
        fill: transparent !important;         /* Makes the inside of the icon clear */
        stroke: white !important;              /* Adds the white outline */
        stroke-width: 2px !important;          /* Controls the thickness of the outline */
        color: transparent !important;         /* Ensures default color doesn't override */
    }

    /* Expanded content blends into sidebar */
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        background: transparent !important;
        padding-left: 0.25rem;
        color: white !important;
    }    
                
    /* Division line between sections */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
        margin: 0rem 0;
    }
    
    /* User info styling */
    .user-info-container {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 0.5rem;
        color: #FFFFFF !important;
    }
    
    .user-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 1rem;
        background: linear-gradient(135deg, #164DF2, #3DF1DF);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 28px;
        border: 3px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-name {
        font-weight: 600;
        color: #164DF2;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
        color: #FFFFFF !important;
    }
    
    .user-role {
        color: #6D6D6D;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.25rem;
        color: #FFFFFF !important;
    }
    
    .user-subscribers {
        font-size: 0.8rem;
        color: #6D6D6D;
        margin-top: 0.5rem;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state for expanded sections
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = {
            'search': False,  # Default collapsed
            'actions': False,  # Default collapsed
            'data_management': False  # Default collapsed
        }
    
    with st.sidebar:
        # Get user
        user = auth_manager.get_current_user()
        
        # USER INFO SECTION (Above all other sections)
        if user:
            # Get user's initials for avatar
            if user.full_name:
                initials = ''.join([name[0].upper() for name in user.full_name.split()[:2]])
            else:
                initials = user.username[0].upper()
            
            # Display user info
            st.markdown(f"""
            <div class="user-info-container">
                <div class="user-avatar">
                    {initials}
                </div>
                <div class="user-name">{user.full_name if user.full_name else user.username}</div>
                <div class="user-role">{user.role.capitalize()}</div>
                <div class="user-subscribers">
                    Access to {len(user.subscriber_ids)} subscriber(s)
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("User information not available")

        # Division line after user info
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # CUSTOMER SEARCH SECTION (Collapsible)
        search_expanded = st.session_state.sidebar_expanded['search']
        
        # Create an expander for customer search
        with st.expander("🔍 **CUSTOMER SEARCH**", expanded=False):
            if not search_expanded:
                # Update state when expander is opened
                st.session_state.sidebar_expanded['search'] = True
                st.rerun()
            
            # Get user permissions
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
                    placeholder="Type to search...",
                    key="search_input"
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
                        index=_get_customer_index(filtered_customers),
                        key="customer_select"
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
                    if st.button("Clear Search", key="clear_search"):
                        st.session_state.customer_search = ""
                        st.rerun()
            else:
                st.warning("No customer data available for your access level")
        
        # Division line between sections
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # ACTIONS SECTION (Collapsible)
        actions_expanded = st.session_state.sidebar_expanded['actions']
        
        with st.expander("⚡ **ACTIONS**", expanded=False):
            if not actions_expanded:
                # Update state when expander is opened
                st.session_state.sidebar_expanded['actions'] = True
                st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                disabled = len(st.session_state.undo_stack) == 0 or not auth_manager.has_permission('can_edit')
                if st.button("↶ Undo", 
                           key="undo_button",
                           disabled=disabled,
                           use_container_width=True):
                    manager.undo()
            
            with col2:
                disabled = len(st.session_state.redo_stack) == 0 or not auth_manager.has_permission('can_edit')
                if st.button("↷ Redo", 
                           key="redo_button",
                           disabled=disabled,
                           use_container_width=True):
                    manager.redo()
            
            if st.session_state.get('current_customer_id') and auth_manager.has_permission('can_edit'):
                if st.button("➕ Add New Row", 
                           key="add_row_button",
                           use_container_width=True):
                    manager.add_new_row(st.session_state.current_customer_id, 
                                      user.subscriber_ids[0] if user and user.subscriber_ids else 'SUB001')
                    st.rerun()
            
            # Delete Section - Only show if user has delete permission
            if (st.session_state.current_customer_id and 
                auth_manager.has_permission('can_delete')):
                render_delete_section(manager, st.session_state.current_customer_id, auth_manager)
        
        # Division line between sections
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # DATA MANAGEMENT SECTION (Collapsible)
        data_expanded = st.session_state.sidebar_expanded['data_management']
        
        with st.expander("📊 **DATA MANAGEMENT**", expanded=False):
            if not data_expanded:
                # Update state when expander is opened
                st.session_state.sidebar_expanded['data_management'] = True
                st.rerun()
            
            # Stack info
            st.caption(f"Undo stack: {len(st.session_state.undo_stack)}")
            st.caption(f"Redo stack: {len(st.session_state.redo_stack)}")
            
            # Export button - Only show if user has export permission
            if auth_manager.has_permission('can_export'):
                if st.button("📥 Export Data", 
                           key="export_button",
                           use_container_width=True):
                    # Filter data based on user permissions before export
                    export_data = st.session_state.data
                    if not is_admin and 'subscriber_id' in export_data.columns:
                        export_data = RowLevelSecurity.filter_data_by_subscriber(
                            export_data, 
                            user.subscriber_ids if user else []
                        )
                    
                    csv = export_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="credit_profiles.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_button"
                    )
            
            # Refresh data button
            if st.button("🔄 Refresh Data", 
                       key="refresh_button",
                       use_container_width=True):
                st.session_state.data = None
                st.rerun()

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        # # ADD LOGOUT BUTTON HERE
        # if st.button("Log out", icon=":material/logout:", use_container_width=True):
        #     st.logout() # Standard 2026 logout command

        # sidebar.py
        if st.button("Log out", icon=":material/logout:", use_container_width=True):
            st.logout()            # clear auth
            st.session_state.clear()  # optional: clear all session state
            st.rerun()             # force app.py to re-check authentication

    return st.session_state.get('current_customer_id')

def _get_customer_index(filtered_customers):
    """Get the index of the current customer in filtered list"""
    current_customer = st.session_state.get('current_customer_id')
    if not current_customer or current_customer not in filtered_customers:
        return 0
    return filtered_customers.index(current_customer)