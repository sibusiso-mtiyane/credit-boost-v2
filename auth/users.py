import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class User:
    """User class representing an authenticated user"""
    def __init__(self, username: str, password_hash: str, role: str, 
                 subscriber_ids: List[str], full_name: str = "", email: str = ""):
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'manager', 'analyst', 'viewer'
        self.subscriber_ids = subscriber_ids  # List of subscriber IDs user can access
        self.full_name = full_name
        self.email = email
        self.created_at = datetime.now()
        self.last_login = None
        
    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'subscriber_ids': self.subscriber_ids,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        user = cls(
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            subscriber_ids=data['subscriber_ids'],
            full_name=data.get('full_name', ''),
            email=data.get('email', '')
        )
        if 'created_at' in data:
            user.created_at = datetime.fromisoformat(data['created_at'])
        if 'last_login' in data and data['last_login']:
            user.last_login = datetime.fromisoformat(data['last_login'])
        return user

class UserDatabase:
    """Simple user database stored in JSON file"""
    def __init__(self, db_path: str = "users.json"):
        self.db_path = db_path
        self.users = self._load_users()
        
    def _load_users(self) -> Dict[str, User]:
        """Load users from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    return {username: User.from_dict(user_data) 
                           for username, user_data in data.items()}
            except:
                pass
        return self._create_default_users()
    
    def _create_default_users(self) -> Dict[str, User]:
        """Create default users if no database exists"""
        default_users = {
            'admin': User(
                username='admin',
                password_hash=self._hash_password('admin123'),
                role='admin',
                subscriber_ids=['SUB001', 'SUB002', 'SUB003', 'SUB004', 'SUB005'],
                full_name='System Administrator',
                email='admin@creditprofile.com'
            ),
            'manager1': User(
                username='manager1',
                password_hash=self._hash_password('manager123'),
                role='manager',
                subscriber_ids=['SUB001', 'SUB002'],
                full_name='Credit Manager 1',
                email='manager1@creditprofile.com'
            ),
            'analyst1': User(
                username='analyst1',
                password_hash=self._hash_password('analyst123'),
                role='analyst',
                subscriber_ids=['SUB001'],
                full_name='Credit Analyst 1',
                email='analyst1@creditprofile.com'
            ),
            'viewer1': User(
                username='viewer1',
                password_hash=self._hash_password('viewer123'),
                role='viewer',
                subscriber_ids=['SUB001'],
                full_name='Data Viewer 1',
                email='viewer1@creditprofile.com'
            )
        }
        self._save_users(default_users)
        return default_users
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _save_users(self, users: Dict[str, User]):
        """Save users to JSON file"""
        data = {username: user.to_dict() for username, user in users.items()}
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.users.get(username)
        if user and user.password_hash == self._hash_password(password):
            user.last_login = datetime.now()
            self._save_users(self.users)
            return user
        return None
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def add_user(self, user: User):
        """Add new user"""
        self.users[user.username] = user
        self._save_users(self.users)
    
    def update_user(self, username: str, **kwargs):
        """Update user properties"""
        if username in self.users:
            user = self.users[username]
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self._save_users(self.users)
    
    def delete_user(self, username: str):
        """Delete user"""
        if username in self.users and username != 'admin':  # Prevent deleting admin
            del self.users[username]
            self._save_users(self.users)
            return True
        return False
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())

# User role permissions
ROLE_PERMISSIONS = {
    'admin': {
        'can_view_all': True,
        'can_edit': True,
        'can_delete': True,
        'can_add_users': True,
        'can_manage_users': True,
        'can_export': True,
        'can_simulate': True
    },
    'manager': {
        'can_view_all': False,
        'can_edit': True,
        'can_delete': True,
        'can_add_users': False,
        'can_manage_users': False,
        'can_export': True,
        'can_simulate': True
    },
    'analyst': {
        'can_view_all': False,
        'can_edit': False,
        'can_delete': False,
        'can_add_users': False,
        'can_manage_users': False,
        'can_export': True,
        'can_simulate': True
    },
    'viewer': {
        'can_view_all': False,
        'can_edit': False,
        'can_delete': False,
        'can_add_users': False,
        'can_manage_users': False,
        'can_export': False,
        'can_simulate': False
    }
}