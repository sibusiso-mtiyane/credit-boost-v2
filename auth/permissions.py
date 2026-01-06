import pandas as pd
from typing import List, Optional
import streamlit as st

class RowLevelSecurity:
    """Manages row-level security based on subscriber_id"""
    
    @staticmethod
    def filter_data_by_subscriber(data: pd.DataFrame, subscriber_ids: List[str]) -> pd.DataFrame:
        """Filter dataframe to only include rows with allowed subscriber IDs"""
        if 'subscriber_id' in data.columns:
            filtered_data = data[data['subscriber_id'].isin(subscriber_ids)]
            return filtered_data.copy()
        return data
    
    @staticmethod
    def filter_customer_ids(customer_ids: List[str], data: pd.DataFrame, 
                           subscriber_ids: List[str]) -> List[str]:
        """Filter customer IDs to only include those from allowed subscribers"""
        if 'subscriber_id' not in data.columns:
            return customer_ids
        
        # Get unique customer IDs from allowed subscribers
        filtered_data = data[data['subscriber_id'].isin(subscriber_ids)]
        filtered_customers = filtered_data['customer_id'].unique().tolist()
        
        # Filter original list to only include allowed customers
        return [cid for cid in customer_ids if cid in filtered_customers]
    
    @staticmethod
    def validate_subscriber_access(subscriber_id: str, allowed_subscribers: List[str], 
                                 is_admin: bool = False) -> bool:
        """Validate if user can access data for specific subscriber"""
        if is_admin:
            return True
        return subscriber_id in allowed_subscribers
    
    @staticmethod
    def get_accessible_subscribers(data: pd.DataFrame, user_subscriber_ids: List[str], 
                                 is_admin: bool = False) -> List[str]:
        """Get list of subscribers that user can access from the data"""
        if 'subscriber_id' not in data.columns:
            return []
        
        all_subscribers = data['subscriber_id'].unique().tolist()
        if is_admin:
            return all_subscribers
        
        return [sub_id for sub_id in all_subscribers if sub_id in user_subscriber_ids]