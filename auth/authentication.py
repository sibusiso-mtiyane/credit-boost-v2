import streamlit as st
from typing import Optional, Dict
from .users import UserDatabase, User, ROLE_PERMISSIONS

class AuthenticationManager:
    """Manages user authentication and session state"""
    
    def __init__(self):
        self.user_db = UserDatabase()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize authentication session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.permissions = None
    
    def login_page(self) -> bool:
        """Render login page and handle authentication"""
        st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h1 style='color: #164DF2;'>🔐 Credit Profile Manager</h1>
            <p style='color: #6D6D6D;'>Please login to access the system</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if self.authenticate(username, password):
                        st.success(f"Welcome, {st.session_state.user.full_name}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            # Demo credentials
            with st.expander("Demo Credentials"):
                st.write("""
                **Admin User:**
                - Username: `admin`
                - Password: `admin123`
                - Role: Administrator (full access)
                
                **Manager User:**
                - Username: `manager1`
                - Password: `manager123`
                - Role: Manager (can edit/delete, limited subscribers)
                
                **Analyst User:**
                - Username: `analyst1`
                - Password: `analyst123`
                - Role: Analyst (view only, limited subscribers)
                
                **Viewer User:**
                - Username: `viewer1`
                - Password: `viewer123`
                - Role: Viewer (read-only, limited subscribers)
                """)
        
        return st.session_state.authenticated
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        user = self.user_db.authenticate(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user = user
            st.session_state.permissions = ROLE_PERMISSIONS.get(user.role, {})
            return True
        return False
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.permissions = None
        st.rerun()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.authenticated
    
    def get_current_user(self) -> Optional[User]:
        """Get current authenticated user"""
        return st.session_state.user
    
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission"""
        if not st.session_state.permissions:
            return False
        return st.session_state.permissions.get(permission, False)
    
    def get_user_subscriber_ids(self) -> list:
        """Get subscriber IDs that current user can access"""
        user = self.get_current_user()
        if user and user.subscriber_ids:
            return user.subscriber_ids
        return []
    
    def can_access_subscriber(self, subscriber_id: str) -> bool:
        """Check if user can access data for specific subscriber"""
        user = self.get_current_user()
        if not user:
            return False
        
        # Admin can access everything
        if user.role == 'admin':
            return True
        
        # Check if subscriber_id is in user's allowed list
        return subscriber_id in user.subscriber_ids
    
    def render_top_right_user_info(self):
        """Render user information in top right corner"""
        user = self.get_current_user()
        if user:
            # Create custom HTML for top-right user info
            st.markdown(f"""
            <style>
            .user-info-top-right {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 999999;
                background: white;
                padding: 10px 15px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .user-info-content {{
                display: flex;
                flex-direction: column;
                align-items: flex-end;
            }}
            .user-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #164DF2, #3DF1DF);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 18px;
            }}
            .user-name {{
                font-weight: 600;
                color: #164DF2;
                font-size: 14px;
            }}
            .user-role {{
                color: #6D6D6D;
                font-size: 12px;
            }}
            .logout-btn {{
                background: #FF6B6B;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 12px;
                margin-top: 5px;
            }}
            .logout-btn:hover {{
                background: #FF5252;
            }}
            </style>
            
            <div class="user-info-top-right">
                <div class="user-avatar">
                    {user.full_name[0].upper() if user.full_name else user.username[0].upper()}
                </div>
                <div class="user-info-content">
                    <div class="user-name">{user.full_name}</div>
                    <div class="user-role">{user.role.capitalize()}</div>
                    <button class="logout-btn" onclick="window.location.href='?logout=true'">Logout</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Handle logout via query parameter
            if st.query_params.get("logout"):
                self.logout()