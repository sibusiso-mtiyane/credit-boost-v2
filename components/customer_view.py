import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def render_customer_view(manager, customer_id, auth_manager=None):
    """Render the main customer view with data and statistics"""
    customer_data = manager.get_customer_data(customer_id)
    
    if not customer_data.empty:
        _render_customer_header(customer_id, len(customer_data))
        _render_editable_table(manager, customer_id, customer_data, auth_manager)
        _render_summary_statistics(customer_data)
        _render_credit_score_dashboard(customer_data, customer_id, auth_manager)
    else:
        _render_no_data_view(manager, customer_id, auth_manager)

def render_welcome_screen(manager, auth_manager=None):
    """Render the welcome screen when no customer is selected"""
    st.info("👆 Search for a customer in the sidebar to view their credit profile")
    
    _render_available_customers(manager, auth_manager)
    _render_dataset_overview(manager, auth_manager)

def _render_customer_header(customer_id, product_count):
    """Render the customer header section"""
    st.header(f"Credit Profile for: {customer_id}")
    st.write(f"**Total Products:** {product_count}")

def _render_editable_table(manager, customer_id, customer_data, auth_manager=None):
    """Render the editable data table with permission checks"""
    st.subheader("Edit Customer Data")
    
    # Check if user has edit permission
    can_edit = True
    if auth_manager:
        can_edit = auth_manager.has_permission('can_edit')
    
    edited_df = st.data_editor(
        customer_data,
        key=f"customer_editor_{customer_id}",
        num_rows="fixed",
        use_container_width=True,
        column_config=_get_column_config(),
        hide_index=True,
        disabled=not can_edit  # Disable editing if user doesn't have permission
    )
    
    # Save changes button - only show if user has edit permission
    if can_edit:
        if st.button("💾 Save Changes", type="primary", key=f"save_{customer_id}"):
            if not edited_df.equals(customer_data):
                manager.update_customer_data(customer_id, edited_df, auth_manager)
                st.rerun()
            else:
                st.info("No changes detected")
    else:
        st.info("📝 Read-only mode: You don't have permission to edit data")

def _get_column_config():
    """Get the column configuration for the data editor"""
    return {
        "customer_id": st.column_config.TextColumn("Customer ID", disabled=True),
        "product_type": st.column_config.SelectboxColumn(
            "Product Type",
            options=["Credit Card", "Personal Loan", "Mortgage", "Auto Loan", "Business Loan", "New Product"],
            required=True
        ),
        "account_number": st.column_config.TextColumn("Account Number", required=True),
        "opening_date": st.column_config.DateColumn("Opening Date", format="YYYY-MM-DD", required=True),
        "last_payment_date": st.column_config.DateColumn("Last Payment Date", format="YYYY-MM-DD", required=True),
        "opening_balance": st.column_config.NumberColumn("Opening Balance", format="$%d", min_value=0, required=True),
        "credit_limit": st.column_config.NumberColumn("Credit Limit", format="$%d", min_value=0, required=True),
        "monthly_instalment": st.column_config.NumberColumn("Monthly Instalment", format="$%d", min_value=0, required=True),
        "loan_term": st.column_config.NumberColumn("Loan Term (months)", min_value=1, max_value=600, step=1, required=True),
        "current_balance": st.column_config.NumberColumn("Current Balance", format="$%d", min_value=0, required=True),
        "current_status": st.column_config.SelectboxColumn(
            "Current Status",
            options=["Active", "Closed", "Pending", "Delinquent", "Default", "Written Off"],
            required=True
        ),
        "balance_overdue": st.column_config.NumberColumn("Balance Overdue", format="$%d", min_value=0, required=True),
        "subscriber_id": st.column_config.SelectboxColumn(
            "Subscriber ID",
            options=["SUB001", "SUB002", "SUB003", "SUB004", "SUB005"],
            required=True
        )
    }

def _render_summary_statistics(customer_data):
    """Render the summary statistics section"""
    st.subheader("Summary Statistics")
    
    if len(customer_data) > 0:
        # First row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_credit_limit = customer_data['credit_limit'].sum()
            st.metric("Total Credit Limit", f"${total_credit_limit:,.2f}")
        
        with col2:
            total_current_balance = customer_data['current_balance'].sum()
            st.metric("Total Current Balance", f"${total_current_balance:,.2f}")
        
        with col3:
            total_overdue = customer_data['balance_overdue'].sum()
            st.metric("Total Overdue", f"${total_overdue:,.2f}")
        
        with col4:
            active_products = len(customer_data[customer_data['current_status'] == 'Active'])
            st.metric("Active Products", active_products)
        
        # Second row
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            total_monthly_instalment = customer_data['monthly_instalment'].sum()
            st.metric("Total Monthly Instalment", f"${total_monthly_instalment:,.2f}")
        
        with col6:
            utilization = (total_current_balance / total_credit_limit * 100) if total_credit_limit > 0 else 0
            st.metric("Utilization Rate", f"{utilization:.1f}%")
        
        with col7:
            overdue_ratio = (total_overdue / total_current_balance * 100) if total_current_balance > 0 else 0
            st.metric("Overdue Ratio", f"{overdue_ratio:.1f}%")
        
        with col8:
            unique_subscribers = customer_data['subscriber_id'].nunique()
            st.metric("Credit Providers", unique_subscribers)
        
        # Payment statistics
        _render_payment_statistics(customer_data)

def _render_payment_statistics(customer_data):
    """Render payment-related statistics"""
    if len(customer_data) > 0:
        today = datetime.now().date()
        
        if customer_data['last_payment_date'].dtype == 'object':
            customer_data['last_payment_date'] = pd.to_datetime(customer_data['last_payment_date']).dt.date
        
        customer_data['days_since_last_payment'] = customer_data['last_payment_date'].apply(
            lambda x: (today - x).days if pd.notnull(x) else None
        )
        
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            active_accounts = customer_data[customer_data['current_status'] == 'Active']
            if not active_accounts.empty and 'days_since_last_payment' in active_accounts.columns:
                valid_days = active_accounts['days_since_last_payment'].dropna()
                if not valid_days.empty:
                    avg_days_since_payment = valid_days.mean()
                    st.metric("Avg Days Since Payment", f"{avg_days_since_payment:.0f} days")
                else:
                    st.metric("Avg Days Since Payment", "N/A")
            else:
                st.metric("Avg Days Since Payment", "N/A")
        
        with col10:
            most_recent_payment = customer_data['last_payment_date'].max()
            if pd.notnull(most_recent_payment):
                st.metric("Most Recent Payment", most_recent_payment.strftime('%Y-%m-%d'))
            else:
                st.metric("Most Recent Payment", "N/A")
        
        with col11:
            if 'days_since_last_payment' in customer_data.columns:
                recent_payments = len(customer_data[
                    (customer_data['days_since_last_payment'] <= 30) & 
                    (customer_data['days_since_last_payment'].notna())
                ])
                st.metric("Recent Payments (≤30 days)", recent_payments)
            else:
                st.metric("Recent Payments (≤30 days)", 0)
        
        with col12:
            if 'days_since_last_payment' in customer_data.columns:
                overdue_payments = len(customer_data[
                    (customer_data['days_since_last_payment'] > 30) & 
                    (customer_data['days_since_last_payment'].notna())
                ])
                st.metric("Overdue Payments (>30 days)", overdue_payments)
            else:
                st.metric("Overdue Payments (>30 days)", 0)

def _render_credit_score_dashboard(customer_data, customer_id, auth_manager=None):
    """Render the comprehensive credit score dashboard with permission checks"""
    st.markdown("---")
    st.header("📊 Credit Score Dashboard")
    
    # Check if user has simulation permission
    can_simulate = True
    if auth_manager:
        can_simulate = auth_manager.has_permission('can_simulate')
    
    # Calculate current credit score
    current_score, current_components = _calculate_credit_score(customer_data)
    
    # Initialize session state for historical data and target score
    if f'score_history_{customer_id}' not in st.session_state:
        st.session_state[f'score_history_{customer_id}'] = _generate_score_history(customer_id)
    if f'target_score_{customer_id}' not in st.session_state:
        st.session_state[f'target_score_{customer_id}'] = 80
    
    # Dashboard layout - only show simulation tabs if user has permission
    if can_simulate:
        tab1, tab2, tab3, tab4 = st.tabs(["Current Score", "Score Trends", "Score Simulation", "Improvement Plan"])
        
        with tab1:
            _render_current_score_tab(current_score, current_components, customer_id)
        
        with tab2:
            _render_score_trends_tab(customer_id, current_score, current_components)
        
        with tab3:
            _render_score_simulation_tab(current_components, customer_id)
        
        with tab4:
            _render_improvement_plan_tab(current_components, customer_id)
    else:
        tab1, tab2 = st.tabs(["Current Score", "Score Trends"])
        
        with tab1:
            _render_current_score_tab(current_score, current_components, customer_id)
        
        with tab2:
            _render_score_trends_tab(customer_id, current_score, current_components)
        
        st.info("🎯 Score simulation features are only available for users with simulation permissions.")

def _render_current_score_tab(current_score, current_components, customer_id):
    """Render the current score tab"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        _render_credit_score_gauge(current_score)
        
        # Quick stats
        st.subheader("Quick Stats")
        total_possible = sum(comp["max_points"] for comp in current_components)
        percentage = (current_score / total_possible) * 100
        
        st.metric("Overall Score", f"{current_score}/{total_possible}")
        st.metric("Percentage", f"{percentage:.1f}%")
        st.metric("Score Category", _get_score_category(current_score))
    
    with col2:
        st.subheader("Component Breakdown")
        
        # Create a bar chart for component scores
        fig = go.Figure()
        
        components = [comp["name"] for comp in current_components]
        current_points = [comp["points"] for comp in current_components]
        max_points = [comp["max_points"] for comp in current_components]
        
        # Add current points
        fig.add_trace(go.Bar(
            name='Current Points',
            x=components,
            y=current_points,
            marker_color='#164DF2'
        ))
        
        # Add max possible points
        fig.add_trace(go.Bar(
            name='Max Possible',
            x=components,
            y=max_points,
            marker_color='#3DF1DF',
            opacity=0.3
        ))
        
        fig.update_layout(
            title="Score Components - Current vs Maximum",
            barmode='overlay',
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def _render_score_trends_tab(customer_id, current_score, current_components):
    """Render the score trends and waterfall analysis tab"""
    st.subheader("📈 Score Trend Analysis")
    
    # Get historical data
    history = st.session_state[f'score_history_{customer_id}']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score trend over time
        fig = px.line(
            history, 
            x='date', 
            y='score',
            title='Credit Score Trend Over Time',
            markers=True
        )
        fig.update_layout(height=400)
        fig.add_hline(y=current_score, line_dash="dash", line_color="red", 
                     annotation_text="Current Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Waterfall chart for last period change
        if len(history) > 1:
            _render_waterfall_chart(history, current_components)
        else:
            st.info("Not enough historical data for waterfall analysis")

def _render_waterfall_chart(history, current_components):
    """Render waterfall chart showing score changes"""
    # Get the last two scores for comparison
    previous_score = history.iloc[-2]['score']
    current_score = history.iloc[-1]['score']
    
    # Simulate component changes (in real scenario, you'd have historical component data)
    component_changes = []
    for comp in current_components:
        change = np.random.randint(-5, 10)  # Simulated change
        component_changes.append({
            'component': comp['name'],
            'change': change,
            'direction': 'increase' if change > 0 else 'decrease'
        })
    
    # Create waterfall data
    measures = ["relative"] * len(component_changes) + ["total"]
    y = [change['change'] for change in component_changes] + [current_score - previous_score]
    x = [change['component'] for change in component_changes] + ["Final Score"]
    
    fig = go.Figure(go.Waterfall(
        name="Score Changes",
        orientation="v",
        measure=measures,
        x=x,
        y=y,
        textposition="outside",
        text=[f"+{val}" if val > 0 else str(val) for val in y[:-1]] + [f"{y[-1]:+.0f}"],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=f"Score Change Analysis: {previous_score} → {current_score}",
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_score_simulation_tab(current_components, customer_id):
    """Render the score simulation tab"""
    st.subheader("🎯 Score Simulation")
    st.write("Adjust the components below to see how they affect your credit score:")
    
    # Initialize session state for simulated components
    if f'simulated_components_{customer_id}' not in st.session_state:
        st.session_state[f'simulated_components_{customer_id}'] = current_components.copy()
    
    simulated_components = st.session_state[f'simulated_components_{customer_id}']
    
    # Target score input
    target_score = st.slider(
        "Set Target Score",
        min_value=0,
        max_value=100,
        value=st.session_state[f'target_score_{customer_id}'],
        key=f"target_slider_{customer_id}"
    )
    st.session_state[f'target_score_{customer_id}'] = target_score
    
    # Component sliders
    col1, col2 = st.columns(2)
    
    updated_components = []
    with col1:
        for i, comp in enumerate(current_components[:3]):
            new_points = st.slider(
                f"{comp['name']}",
                min_value=0,
                max_value=comp["max_points"],
                value=comp["points"],
                key=f"sim_{customer_id}_{i}"
            )
            updated_comp = comp.copy()
            updated_comp["points"] = new_points
            updated_components.append(updated_comp)
    
    with col2:
        for i, comp in enumerate(current_components[3:], 3):
            new_points = st.slider(
                f"{comp['name']}",
                min_value=0,
                max_value=comp["max_points"],
                value=comp["points"],
                key=f"sim_{customer_id}_{i}"
            )
            updated_comp = comp.copy()
            updated_comp["points"] = new_points
            updated_components.append(updated_comp)
    
    # Calculate simulated score
    simulated_score = sum(comp["points"] for comp in updated_components)
    st.session_state[f'simulated_components_{customer_id}'] = updated_components
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_score = sum(comp["points"] for comp in current_components)
        st.metric("Current Score", current_score)
    
    with col2:
        st.metric("Simulated Score", simulated_score, delta=simulated_score - current_score)
    
    with col3:
        st.metric("Target Score", target_score, delta=simulated_score - target_score)
    
    # Progress towards target
    progress = min((simulated_score / target_score) * 100, 100) if target_score > 0 else 0
    st.progress(progress / 100)
    st.write(f"Progress towards target: {progress:.1f}%")
    
    # Reset button
    if st.button("Reset to Current Values"):
        st.session_state[f'simulated_components_{customer_id}'] = current_components.copy()
        st.rerun()

def _render_improvement_plan_tab(current_components, customer_id):
    """Render the improvement plan tab"""
    st.subheader("📋 Personalized Improvement Plan")
    
    target_score = st.session_state[f'target_score_{customer_id}']
    simulated_components = st.session_state[f'simulated_components_{customer_id}']
    current_score = sum(comp["points"] for comp in current_components)
    simulated_score = sum(comp["points"] for comp in simulated_components)
    
    # Calculate improvement needed
    improvement_needed = target_score - current_score
    
    if improvement_needed <= 0:
        st.success("🎉 You've already reached your target score!")
        return
    
    st.write(f"To reach your target score of **{target_score}**, you need **{improvement_needed}** additional points.")
    
    # Generate improvement recommendations
    recommendations = _generate_improvement_recommendations(current_components, target_score)
    
    st.subheader("Recommended Actions")
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"#{i}: {rec['component']} (+{rec['potential_points']} points)"):
            st.write(f"**Current:** {rec['current_state']}")
            st.write(f"**Target:** {rec['target_state']}")
            st.write(f"**Action Steps:**")
            for step in rec['action_steps']:
                st.write(f"• {step}")
            
            # Progress indicator
            progress = min((rec['current_points'] / rec['target_points']) * 100, 100)
            st.write(f"**Progress:** {progress:.1f}%")
            st.progress(progress / 100)

def _generate_improvement_recommendations(current_components, target_score):
    """Generate personalized improvement recommendations"""
    recommendations = []
    
    for comp in current_components:
        potential_improvement = comp["max_points"] - comp["points"]
        
        if potential_improvement > 0:
            recommendation = {
                'component': comp['name'],
                'current_points': comp['points'],
                'target_points': comp['max_points'],
                'potential_points': potential_improvement,
                'current_state': comp['description'],
                'target_state': _get_target_description(comp['name']),
                'action_steps': _get_action_steps(comp['name'], comp['points'], comp['max_points'])
            }
            recommendations.append(recommendation)
    
    # Sort by potential impact (highest first)
    recommendations.sort(key=lambda x: x['potential_points'], reverse=True)
    
    return recommendations[:3]  # Return top 3 recommendations

def _get_target_description(component_name):
    """Get target description for each component"""
    targets = {
        "Credit Utilization": "Keep utilization below 30%",
        "Payment History": "Make payments within 15 days",
        "Credit Mix": "Maintain 3+ different credit products",
        "Account Age & Activity": "Keep 3+ active accounts",
        "Overdue Behavior": "Eliminate all overdue amounts"
    }
    return targets.get(component_name, "Reach maximum points")

def _get_action_steps(component_name, current_points, max_points):
    """Get actionable steps for improvement"""
    if component_name == "Credit Utilization":
        return [
            "Pay down credit card balances below 30% of limits",
            "Request credit limit increases on existing cards",
            "Avoid maxing out any single credit card"
        ]
    elif component_name == "Payment History":
        return [
            "Set up automatic payments for all accounts",
            "Make payments at least 15 days before due date",
            "Contact lenders immediately if you anticipate late payments"
        ]
    elif component_name == "Credit Mix":
        return [
            "Consider adding a different type of credit product",
            "Maintain a healthy mix of revolving and installment credit",
            "Don't open too many new accounts at once"
        ]
    elif component_name == "Account Age & Activity":
        return [
            "Keep old accounts open to maintain credit history",
            "Use credit cards regularly but responsibly",
            "Avoid closing your oldest credit accounts"
        ]
    elif component_name == "Overdue Behavior":
        return [
            "Pay off all overdue amounts immediately",
            "Contact lenders to negotiate payment plans if needed",
            "Set up payment reminders to avoid future late payments"
        ]
    return ["Consult with a financial advisor for personalized guidance"]

def _generate_score_history(customer_id, periods=12):
    """Generate mock historical score data"""
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='M')
    base_score = 65  # Starting score
    
    history = []
    current_score = base_score
    for date in dates:
        # Simulate some variation
        change = np.random.randint(-5, 8)
        current_score = max(0, min(100, current_score + change))
        history.append({
            'date': date,
            'score': current_score,
            'customer_id': customer_id
        })
    
    return pd.DataFrame(history)

def _calculate_credit_score(customer_data):
    """Calculate credit score based on customer data"""
    total_credit_limit = customer_data['credit_limit'].sum()
    total_current_balance = customer_data['current_balance'].sum()
    total_overdue = customer_data['balance_overdue'].sum()
    active_products = len(customer_data[customer_data['current_status'] == 'Active'])
    
    # Calculate utilization rate
    utilization = (total_current_balance / total_credit_limit * 100) if total_credit_limit > 0 else 0
    
    # Calculate days since last payment (for active accounts)
    today = datetime.now().date()
    if customer_data['last_payment_date'].dtype == 'object':
        customer_data['last_payment_date'] = pd.to_datetime(customer_data['last_payment_date']).dt.date
    
    active_accounts = customer_data[customer_data['current_status'] == 'Active']
    if not active_accounts.empty:
        active_accounts['days_since_last_payment'] = active_accounts['last_payment_date'].apply(
            lambda x: (today - x).days if pd.notnull(x) else 90
        )
        avg_days_since_payment = active_accounts['days_since_last_payment'].mean()
    else:
        avg_days_since_payment = 90
    
    # Score components
    score_components = [
        {
            "name": "Credit Utilization",
            "points": _calculate_utilization_points(utilization),
            "max_points": 40,
            "description": f"Utilization: {utilization:.1f}%"
        },
        {
            "name": "Payment History",
            "points": _calculate_payment_points(avg_days_since_payment),
            "max_points": 25,
            "description": f"Avg days since payment: {avg_days_since_payment:.0f}"
        },
        {
            "name": "Credit Mix",
            "points": _calculate_credit_mix_points(customer_data),
            "max_points": 20,
            "description": f"Product types: {customer_data['product_type'].nunique()}"
        },
        {
            "name": "Account Age & Activity",
            "points": _calculate_account_age_points(customer_data),
            "max_points": 10,
            "description": f"Active accounts: {active_products}"
        },
        {
            "name": "Overdue Behavior",
            "points": _calculate_overdue_points(total_overdue, total_current_balance),
            "max_points": 5,
            "description": f"Overdue ratio: {(total_overdue/total_current_balance*100) if total_current_balance > 0 else 0:.1f}%"
        }
    ]
    
    total_score = sum(component["points"] for component in score_components)
    
    return total_score, score_components

def _calculate_utilization_points(utilization):
    """Calculate points for credit utilization"""
    if utilization <= 10:
        return 40
    elif utilization <= 30:
        return 35
    elif utilization <= 50:
        return 25
    elif utilization <= 75:
        return 15
    else:
        return 5

def _calculate_payment_points(avg_days):
    """Calculate points for payment history"""
    if avg_days <= 15:
        return 25
    elif avg_days <= 30:
        return 20
    elif avg_days <= 45:
        return 15
    elif avg_days <= 60:
        return 10
    else:
        return 5

def _calculate_credit_mix_points(customer_data):
    """Calculate points for credit mix diversity"""
    unique_products = customer_data['product_type'].nunique()
    if unique_products >= 4:
        return 20
    elif unique_products >= 3:
        return 15
    elif unique_products >= 2:
        return 10
    else:
        return 5

def _calculate_account_age_points(customer_data):
    """Calculate points for account age and activity"""
    active_accounts = len(customer_data[customer_data['current_status'] == 'Active'])
    if active_accounts >= 4:
        return 10
    elif active_accounts >= 3:
        return 8
    elif active_accounts >= 2:
        return 6
    else:
        return 4

def _calculate_overdue_points(total_overdue, total_balance):
    """Calculate points for overdue behavior"""
    overdue_ratio = (total_overdue / total_balance * 100) if total_balance > 0 else 0
    if overdue_ratio == 0:
        return 5
    elif overdue_ratio <= 5:
        return 4
    elif overdue_ratio <= 10:
        return 3
    elif overdue_ratio <= 20:
        return 2
    else:
        return 1

def _render_credit_score_gauge(score):
    """Render the credit score gauge"""
    # Determine score category and color
    if score >= 90:
        category = "Excellent"
        color = "#00FF00"
    elif score >= 75:
        category = "Good"
        color = "#90EE90"
    elif score >= 60:
        category = "Fair"
        color = "#FFA500"
    elif score >= 40:
        category = "Poor"
        color = "#FF6B6B"
    else:
        category = "Very Poor"
        color = "#FF0000"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 3px solid {color};">
        <h1 style="margin: 0; color: {color}; font-size: 4rem; font-weight: bold;">{score}</h1>
        <h3 style="margin: 0; color: {color};">{category}</h3>
        <p style="margin: 5px 0 0 0; color: #6c757d;">Credit Score</p>
    </div>
    """, unsafe_allow_html=True)

def _get_score_category(score):
    """Get score category"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Poor"
    else:
        return "Very Poor"

def _render_no_data_view(manager, customer_id, auth_manager=None):
    """Render view when no customer data is found"""
    st.warning(f"No records found for customer ID: {customer_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add First Product for This Customer", key=f"add_first_{customer_id}"):
            # Get subscriber ID from current user if available
            subscriber_id = 'SUB001'
            if auth_manager:
                user = auth_manager.get_current_user()
                if user and user.subscriber_ids:
                    subscriber_id = user.subscriber_ids[0]
            
            manager.add_new_row(customer_id, subscriber_id)
            st.rerun()
    with col2:
        if st.button("🔍 Search Different Customer", key=f"search_diff_{customer_id}"):
            st.session_state.current_customer_id = None
            st.session_state.customer_search = ""
            st.rerun()

def _render_available_customers(manager, auth_manager=None):
    """Render the available customers section"""
    st.subheader("Available Customers")
    unique_customers = manager.get_all_customer_ids()
    
    if len(unique_customers) > 0:
        cols = st.columns(3)
        for i, customer in enumerate(unique_customers[:6]):
            with cols[i % 3]:
                if st.button(f"{customer}", use_container_width=True, key=f"cust_btn_{customer}"):
                    st.session_state.current_customer_id = customer
                    st.session_state.customer_search = customer
                    st.rerun()

def _render_dataset_overview(manager, auth_manager=None):
    """Render the dataset overview section"""
    st.subheader("Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(manager.get_all_customer_ids()))
    
    with col2:
        st.metric("Total Products", len(st.session_state.data))
    
    with col3:
        active_count = len(st.session_state.data[st.session_state.data['current_status'] == 'Active'])
        st.metric("Active Products", active_count)
    
    with col4:
        total_credit = st.session_state.data['credit_limit'].sum()
        st.metric("Total Credit Limit", f"${total_credit:,.0f}")