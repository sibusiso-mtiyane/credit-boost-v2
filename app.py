import streamlit as st
# from config.styles import apply_custom_styles
from components.sidebar import render_sidebar
from components.customer_view import render_customer_view, render_welcome_screen
from components.data_manager import CreditProfileManager
from auth.authentication import AuthenticationManager
from auth.permissions import RowLevelSecurity


def load_css(file_name):
    with open(file_name) as f:
        # st.html is the modern (2026) way to inject style tags
        st.html(f"<style>{f.read()}</style>")

# Call this at the very beginning of your app
load_css("assets/style.css")

# SET PAGE CONFIG HERE - AT THE VERY TOP
st.set_page_config(
    page_title="Credit Profile Manager",
    page_icon="💳",
    layout="wide",  # <-- ADD THIS LINE
    initial_sidebar_state="expanded"  # You can also add this if you want
)

def main():
    # Apply custom styles
    # apply_custom_styles()
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager()
    
    # Check authentication
    if not auth_manager.is_authenticated():
        if auth_manager.login_page():
            st.rerun()
        return
    
    # User is authenticated - show main app
    _render_authenticated_app(auth_manager)

def _render_authenticated_app(auth_manager):
    """Render the main app for authenticated users"""
    # Initialize data manager
    manager = CreditProfileManager()
    
    # Apply row-level security filtering
    user_subscriber_ids = auth_manager.get_user_subscriber_ids()
    is_admin = auth_manager.get_current_user().role == 'admin'
    
    # Filter data based on user permissions
    if not is_admin and 'subscriber_id' in st.session_state.data.columns:
        original_count = len(st.session_state.data)
        st.session_state.data = RowLevelSecurity.filter_data_by_subscriber(
            st.session_state.data, 
            user_subscriber_ids
        )
        filtered_count = len(st.session_state.data)
        
        # Show access info (only show once per session)
        if f'access_info_shown_{auth_manager.get_current_user().username}' not in st.session_state:
            if filtered_count < original_count:
                st.info(f"📊 Showing {filtered_count} of {original_count} records based on your access permissions.")
            st.session_state[f'access_info_shown_{auth_manager.get_current_user().username}'] = True
    
    # # Render user info in top right corner
    # auth_manager.render_top_right_user_info()
    
    # # Render main header with user info
    # user = auth_manager.get_current_user()
    # st.markdown(f"""
    # <div style='text-align: center; margin-bottom: 2rem;'>
    #     <h1 style='color: #164DF2; margin-bottom: 0.5rem;'>💳 CREDIT PROFILE MANAGER</h1>
    #     <div style='color: #6D6D6D; font-family: Raleway; font-weight: 300;'>
    #         Comprehensive Credit Portfolio Management System
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Render sidebar and get current customer ID
    current_customer_id = render_sidebar(manager, auth_manager)
    
    # Render main content based on customer selection
    if current_customer_id:
        render_customer_view(manager, current_customer_id, auth_manager)
    else:
        render_welcome_screen(manager, auth_manager)

if __name__ == "__main__":
    main()