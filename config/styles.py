# import streamlit as st

# def apply_custom_styles():
#     """Apply custom CSS styles for the entire app"""
#     st.markdown("""
#     <style>
#     /* Import Raleway font */
#     @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;500;600;700;800&display=swap');

#     .main {
#             background-color: #3DF1DF !important; /* <--- ADD THIS */
#         }
                                   
#     /* Main app container - FULL WIDTH */
#     .main .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#         padding-left: 2rem;
#         padding-right: 2rem;
#         max-width: 100% !important;
#         width: 100% !important;
#     }
    
#     /* Remove any max-width constraints */
#     .st-emotion-cache-1y4p8pa {
#         max-width: 100% !important;
#         padding-left: 2rem !important;
#         padding-right: 2rem !important;
#     }
    
#     /* Make data editor use full width */
#     .stDataEditor {
#         width: 100% !important;
#     }
    
#     /* Ensure all content containers use full width */
#     .element-container {
#         max-width: 100% !important;
#     }
    
#     /* Sidebar styling */
#     section[data-testid="stSidebar"] {
#         background-color: #164DF2;
#         color: #FFFFFF;
#         min-width: 300px !important;
#     }
    
#     /* Sidebar text color */
#     section[data-testid="stSidebar"] * {
#         color: #FFFFFF !important;
#     }
    
#     /* Headers - Raleway Bold */
#     h1, h2, h3, .main-header {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 700 !important;
#         color: #1C1C1C !important;
#         margin-bottom: 0.5rem !important;
#     }
    
#     h1 {
#         font-size: 2.5rem !important;
#     }
    
#     h2 {
#         font-size: 2rem !important;
#     }
    
#     h3 {
#         font-size: 1.5rem !important;
#     }
    
#     /* Small headers - uppercase */
#     .small-header {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 700 !important;
#         text-transform: uppercase;
#         color: #1C1C1C !important;
#         letter-spacing: 1px;
#         margin-bottom: 0.5rem !important;
#     }
    
#     /* Body text - Raleway Regular/Light */
#     body, .body-text {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 400;
#         color: #1C1C1C;
#     }
    
#     .light-text {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 300;
#         color: #6D6D6D;
#     }
    
#     /* Buttons - Primary (Blue) */
#     .stButton button {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 600;
#         border-radius: 8px;
#         border: none;
#         transition: all 0.3s ease;
#     }
    
#     .stButton button:first-child {
#         background-color: #164DF2 !important;
#         color: #FFFFFF !important;
#     }
    
#     .stButton button:first-child:hover {
#         background-color: #0D3BC9 !important;
#         transform: translateY(-2px);
#         box-shadow: 0 4px 12px rgba(22, 77, 242, 0.3);
#     }
    
#     /* Secondary Buttons (Cyan) */
#     div[data-testid="stButton"] button[kind="secondary"] {
#         background-color: #3DF1DF !important;
#         color: #1C1C1C !important;
#         border: none !important;
#     }
    
#     div[data-testid="stButton"] button[kind="secondary"]:hover {
#         background-color: #2AD9C8 !important;
#         transform: translateY(-2px);
#         box-shadow: 0 4px 12px rgba(61, 241, 223, 0.3);
#     }
    
#     /* Metric cards */
#     [data-testid="metric-container"] {
#         border: 1px solid #F0F0F0;
#         border-radius: 12px;
#         padding: 15px;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.1);
#         margin: 5px;
#     }
    
#     [data-testid="metric-label"] {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 600;
#         color: #6D6D6D !important;
#         font-size: 0.9rem;
#     }
    
#     [data-testid="metric-value"] {
#         font-family: 'Raleway', sans-serif;
#         font-weight: 700;
#         color: #164DF2 !important;
#         font-size: 1.8rem;
#     }
    
#     /* Data editor styling - make it wider */
#     .stDataEditor {
#         width: 100% !important;
#         min-width: 100% !important;
#     }
    
#     .dataframe {
#         font-family: 'Raleway', sans-serif;
#         width: 100% !important;
#     }
    
#     /* Input fields */
#     .stTextInput input, .stSelectbox select, .stNumberInput input {
#         font-family: 'Raleway', sans-serif;
#         border-radius: 6px;
#         border: 1px solid #D1D1D1;
#     }
    
#     /* Success messages */
#     .stAlert [data-testid="stMarkdownContainer"] {
#         font-family: 'Raleway', sans-serif;
#     }
    
#     /* Divider styling */
#     hr {
#         border: none;
#         height: 2px;
#         background: linear-gradient(90deg, #164DF2, #3DF1DF);
#         margin: 1rem 0;
#     }
    
#     /* Custom colored elements */
#     .blue-accent {
#         color: #164DF2;
#     }
    
#     .cyan-accent {
#         color: #3DF1DF;
#     }
    
#     .magenta-accent {
#         color: #FF27D7;
#     }
    
#     .orange-accent {
#         color: #FFA030;
#     }
    
#     /* Sidebar section styling */
#     .sidebar-section {
#         background-color: rgba(255, 255, 255, 0.1);
#         border-radius: 12px;
#         padding: 15px;
#         margin: 10px 0;
#     }
    
#     /* Custom badge for subscriber ID */
#     .subscriber-badge {
#         background-color: #3DF1DF;
#         color: #1C1C1C;
#         padding: 4px 8px;
#         border-radius: 12px;
#         font-size: 0.8rem;
#         font-weight: 600;
#     }
    
#     /* Reduce margins in streamlit containers */
#     .stContainer {
#         padding: 0.5rem !important;
#     }
    
#     .element-container {
#         margin-bottom: 0.5rem !important;
#     }
    
#     /* Make columns tighter */
#     .row-widget.stColumns {
#         margin-bottom: 0.5rem !important;
#     }
    
#     /* Reduce padding in expandable containers */
#     .streamlit-expanderHeader {
#         padding: 0.5rem 1rem !important;
#     }
    
#     /* Custom CSS for data editor to be wider */
#     div[data-testid="stDataEditorRoot"] {
#         width: 100% !important;
#         min-width: 100% !important;
#     }
    
#     /* Reduce spacing in markdown elements */
#     .stMarkdown {
#         margin-bottom: 0.25rem !important;
#     }
    
#     /* Tighten up the layout */
#     .st-emotion-cache-1y4p8pa {
#         padding: 1rem 1rem !important;
#     }
    
#     /* Make the main content area use more screen space */
#     .st-emotion-cache-1v0mbdj {
#         width: 100% !important;
#     }
    
#      /*Added to ensure that the expander blends in to sidebar*/           
#     .st-emotion-cache-1lsfsc6 {
#         position: relative;
#         display: flex;
#         width: 100%;
#         min-width: 0px;
#         overflow: hidden;
#         font-size: inherit;
#         color: #FFFFFF !important;
#         padding: 0.25rem 0.75rem;
#         min-height: calc(-2px + 2.5rem);
#         -webkit-box-align: center;
#         align-items: center;
#         cursor: pointer;
#         list-style-type: none;
#         background-color: transparent;
#         transition: cubic-bezier(0.23, 1, 0.32, 1), background-color 150ms;
#     }

#     /* Reduce margins around the app */
#     #MainMenu {
#         visibility: hidden;
#     }
    
#     footer {
#         visibility: hidden;
#     }
    
#     /* Header spacing reduction */
#     .st-emotion-cache-10trblm {
#         margin-bottom: 0.25rem !important;
#     }
    
#     /* Login page specific styling */
#     .login-container {
#         max-width: 400px;
#         margin: 0 auto;
#         padding: 2rem;
#         background: white;
#         border-radius: 15px;
#         box-shadow: 0 10px 30px rgba(0,0,0,0.1);
#     }
    
#     /* User info in sidebar */
#     .user-info {
#         padding: 1rem;
#         background: rgba(255, 255, 255, 0.1);
#         border-radius: 10px;
#         margin-top: 1rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)

