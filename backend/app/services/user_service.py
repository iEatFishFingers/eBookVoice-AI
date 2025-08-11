"""
User Management Service
Handles user operations with Supabase database
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from supabase import create_client, Client

class UserManager:
    """
    User management without Firebase
    Stores user data in Supabase PostgreSQL database
    """
    
    def __init__(self, config):
        self.supabase: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_KEY  # Use service key for admin operations
        )
    
    def create_or_update_user(self, google_user_info: Dict) -> Dict:
        """
        Idempotent user creation/update
        
        Why idempotent? Google OAuth can be called multiple times,
        we don't want to create duplicate users or fail on existing users.
        """
        google_id = google_user_info.get('sub')  # 'sub' is the stable Google ID
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        picture = google_user_info.get('picture')
        
        # Try to find existing user
        existing_user = self.supabase.table('users').select('*').eq('google_id', google_id).execute()
        
        if existing_user.data:
            # Update existing user (handle profile changes)
            updated_user = self.supabase.table('users').update({
                'name': name,
                'picture_url': picture,
                'updated_at': 'now()'
            }).eq('google_id', google_id).execute()
            
            return updated_user.data[0]
        else:
            # Create new user
            new_user = self.supabase.table('users').insert({
                'google_id': google_id,
                'email': email,
                'name': name,
                'picture_url': picture
            }).execute()
            
            return new_user.data[0]
    
    def get_user_by_google_id(self, google_id: str) -> Optional[Dict]:
        """Get user by Google ID"""
        result = self.supabase.table('users').select('*').eq('google_id', google_id).execute()
        return result.data[0] if result.data else None
    
    def update_storage_usage(self, user_id: str, bytes_used: int) -> bool:
        """
        Update user's storage usage for quota management
        
        Why track storage? 
        - Enforce free tier limits
        - Plan monetization strategy
        - Prevent abuse
        """
        try:
            self.supabase.table('users').update({
                'storage_used_bytes': bytes_used
            }).eq('id', user_id).execute()
            return True
        except Exception:
            return False
    
    def check_storage_quota(self, user_id: str, additional_bytes: int) -> bool:
        """
        Check if user can upload additional data
        
        Business logic for quota enforcement
        """
        user = self.supabase.table('users').select('storage_used_bytes, subscription_type').eq('id', user_id).execute()
        
        if not user.data:
            return False
        
        current_usage = user.data[0]['storage_used_bytes'] or 0
        subscription = user.data[0]['subscription_type']
        
        # Define quotas based on subscription
        quotas = {
            'free': 100 * 1024 * 1024,      # 100MB for free users
            'premium': 10 * 1024 * 1024 * 1024,  # 10GB for premium
        }
        
        quota = quotas.get(subscription, quotas['free'])
        return (current_usage + additional_bytes) <= quota
    
    def add_audiobook(self, user_id: str, title: str, filename: str, storage_key: str, file_size: int = None) -> str:
        """
        Add audiobook record for user
        
        Returns:
            Audiobook ID
        """
        result = self.supabase.table('audiobooks').insert({
            'user_id': user_id,
            'title': title,
            'original_filename': filename,
            'storage_key': storage_key,
            'file_size': file_size
        }).execute()
        
        return result.data[0]['id']
    
    def get_user_audiobooks(self, user_id: str) -> List[Dict]:
        """Get all audiobooks for a user"""
        result = self.supabase.table('audiobooks').select(
            'id, title, original_filename, file_size, duration_seconds, status, created_at, completed_at'
        ).eq('user_id', user_id).order('created_at', desc=True).execute()
        
        audiobooks = []
        for row in result.data:
            audiobooks.append({
                'id': row['id'],
                'title': row['title'],
                'filename': row['original_filename'],
                'file_size': row['file_size'],
                'duration': row['duration_seconds'],
                'status': row['status'],
                'created_at': row['created_at'],
                'completed_at': row['completed_at']
            })
        
        return audiobooks
    
    def update_audiobook_status(self, audiobook_id: str, status: str, duration_seconds: int = None) -> bool:
        """Update audiobook processing status"""
        try:
            update_data = {'status': status}
            if duration_seconds:
                update_data['duration_seconds'] = duration_seconds
            if status == 'completed':
                update_data['completed_at'] = 'now()'
            
            self.supabase.table('audiobooks').update(update_data).eq('id', audiobook_id).execute()
            return True
        except Exception:
            return False