"""User dashboard and analytics API module."""
import json
import logging
from datetime import datetime, date, timedelta
from database import get_db_connection
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for user dashboard data and analytics."""
    
    def __init__(self, db_path='audiobook.db'):
        self.db_path = db_path
    
    def get_user_dashboard_data(self, user_id: int) -> Dict:
        """Get comprehensive dashboard data for a user."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Get user info with subscription details
            cursor.execute('''
                SELECT u.id, u.email, u.display_name, u.subscription_tier, 
                       u.created_at, u.last_login, u.is_active,
                       sl.monthly_conversions, sl.words_per_month, sl.max_file_size_mb,
                       sl.voice_options, sl.features
                FROM users u
                LEFT JOIN subscription_limits sl ON u.subscription_tier = sl.tier
                WHERE u.id = ?
            ''', (user_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return {'success': False, 'error': 'User not found'}
            
            user_data = dict(user_row)
            
            # Get user usage statistics
            cursor.execute('''
                SELECT words_used_this_month, conversions_this_month,
                       total_conversions, total_words_converted,
                       current_month_start, last_reset_date
                FROM user_usage WHERE user_id = ?
            ''', (user_id,))
            
            usage_row = cursor.fetchone()
            usage_data = dict(usage_row) if usage_row else self._create_default_usage(user_id)
            
            # Check if monthly reset is needed
            current_month_start = date.today().replace(day=1)
            if usage_data['current_month_start'] != current_month_start.isoformat():
                self._reset_monthly_usage(user_id, current_month_start)
                usage_data['words_used_this_month'] = 0
                usage_data['conversions_this_month'] = 0
                usage_data['current_month_start'] = current_month_start.isoformat()
            
            # Get recent conversions
            recent_conversions = self._get_recent_conversions(user_id, limit=10)
            
            # Get usage statistics
            usage_stats = self._calculate_usage_statistics(user_id)
            
            # Build dashboard response
            dashboard_data = {
                'success': True,
                'user': {
                    'id': user_data['id'],
                    'email': user_data['email'],
                    'display_name': user_data['display_name'],
                    'subscription_tier': user_data['subscription_tier'],
                    'member_since': user_data['created_at'],
                    'last_login': user_data['last_login'],
                    'is_active': bool(user_data['is_active'])
                },
                'subscription': {
                    'tier': user_data['subscription_tier'],
                    'monthly_conversions_limit': user_data['monthly_conversions'],
                    'words_per_month_limit': user_data['words_per_month'],
                    'max_file_size_mb': user_data['max_file_size_mb'],
                    'voice_options': json.loads(user_data['voice_options']) if user_data['voice_options'] else [],
                    'features': json.loads(user_data['features']) if user_data['features'] else {}
                },
                'usage': {
                    'current_month': {
                        'words_used': usage_data['words_used_this_month'],
                        'conversions_used': usage_data['conversions_this_month'],
                        'words_remaining': self._calculate_words_remaining(usage_data, user_data),
                        'conversions_remaining': self._calculate_conversions_remaining(usage_data, user_data)
                    },
                    'lifetime': {
                        'total_conversions': usage_data['total_conversions'],
                        'total_words_converted': usage_data['total_words_converted']
                    },
                    'month_start': usage_data['current_month_start']
                },
                'recent_conversions': recent_conversions,
                'statistics': usage_stats
            }
            
            conn.close()
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {e}")
            return {'success': False, 'error': 'Failed to load dashboard data'}
    
    def get_user_conversions(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict:
        """Get paginated user conversions with details."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get conversions with pagination
            cursor.execute('''
                SELECT id, job_id, original_filename, file_type, file_size,
                       word_count, voice_used, processing_time, status,
                       created_at, download_count, last_downloaded
                FROM conversions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, per_page, offset))
            
            conversions = []
            for row in cursor.fetchall():
                conversion = dict(row)
                conversion['download_url'] = f'/download/{conversion["job_id"]}'
                conversion['file_size_mb'] = round(conversion['file_size'] / (1024 * 1024), 2) if conversion['file_size'] else 0
                conversions.append(conversion)
            
            # Get total count
            cursor.execute('SELECT COUNT(*) as count FROM conversions WHERE user_id = ?', (user_id,))
            total_count = cursor.fetchone()['count']
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page
            
            conn.close()
            
            return {
                'success': True,
                'conversions': conversions,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting conversions for user {user_id}: {e}")
            return {'success': False, 'error': 'Failed to load conversions'}
    
    def get_usage_analytics(self, user_id: int, days: int = 30) -> Dict:
        """Get detailed usage analytics for a user."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get conversions in date range
            cursor.execute('''
                SELECT created_at, word_count, voice_used, processing_time, file_type
                FROM conversions
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at ASC
            ''', (user_id, start_date.isoformat()))
            
            conversions = [dict(row) for row in cursor.fetchall()]
            
            # Calculate analytics
            analytics = {
                'success': True,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_conversions': len(conversions),
                    'total_words': sum(c['word_count'] or 0 for c in conversions),
                    'total_processing_time': sum(c['processing_time'] or 0 for c in conversions),
                    'average_words_per_conversion': 0,
                    'average_processing_time': 0
                },
                'by_voice': {},
                'by_file_type': {},
                'daily_activity': [],
                'efficiency_score': 0
            }
            
            if conversions:
                analytics['summary']['average_words_per_conversion'] = analytics['summary']['total_words'] // len(conversions)
                analytics['summary']['average_processing_time'] = analytics['summary']['total_processing_time'] // len(conversions)
                
                # Group by voice
                voice_stats = {}
                for conv in conversions:
                    voice = conv['voice_used'] or 'unknown'
                    if voice not in voice_stats:
                        voice_stats[voice] = {'count': 0, 'words': 0}
                    voice_stats[voice]['count'] += 1
                    voice_stats[voice]['words'] += conv['word_count'] or 0
                analytics['by_voice'] = voice_stats
                
                # Group by file type
                file_type_stats = {}
                for conv in conversions:
                    file_type = conv['file_type'] or 'unknown'
                    if file_type not in file_type_stats:
                        file_type_stats[file_type] = {'count': 0, 'words': 0}
                    file_type_stats[file_type]['count'] += 1
                    file_type_stats[file_type]['words'] += conv['word_count'] or 0
                analytics['by_file_type'] = file_type_stats
                
                # Calculate efficiency score
                analytics['efficiency_score'] = self._calculate_efficiency_score(conversions)
            
            conn.close()
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for user {user_id}: {e}")
            return {'success': False, 'error': 'Failed to load analytics'}
    
    def check_usage_limits(self, user_id: int, estimated_words: int = 0) -> Dict:
        """Check if user can perform a conversion based on their limits."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Get user tier and limits
            cursor.execute('''
                SELECT u.subscription_tier, uu.words_used_this_month, uu.conversions_this_month,
                       sl.monthly_conversions, sl.words_per_month, sl.max_file_size_mb
                FROM users u
                JOIN user_usage uu ON u.id = uu.user_id
                JOIN subscription_limits sl ON u.subscription_tier = sl.tier
                WHERE u.id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': 'User not found'}
            
            data = dict(row)
            tier = data['subscription_tier']
            words_used = data['words_used_this_month']
            conversions_used = data['conversions_this_month']
            word_limit = data['words_per_month']
            conversion_limit = data['monthly_conversions']
            
            # Check limits (-1 means unlimited)
            can_convert = True
            reasons = []
            
            if word_limit > 0 and (words_used + estimated_words) > word_limit:
                can_convert = False
                reasons.append(f'Word limit would be exceeded ({words_used + estimated_words}/{word_limit})')
            
            if conversion_limit > 0 and conversions_used >= conversion_limit:
                can_convert = False
                reasons.append(f'Monthly conversion limit reached ({conversions_used}/{conversion_limit})')
            
            conn.close()
            
            return {
                'success': True,
                'can_convert': can_convert,
                'reasons': reasons,
                'current_usage': {
                    'words_used': words_used,
                    'conversions_used': conversions_used,
                    'word_limit': word_limit if word_limit > 0 else 'unlimited',
                    'conversion_limit': conversion_limit if conversion_limit > 0 else 'unlimited'
                },
                'tier': tier,
                'limits_approaching': {
                    'words': word_limit > 0 and (words_used / word_limit) > 0.8,
                    'conversions': conversion_limit > 0 and (conversions_used / conversion_limit) > 0.8
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {e}")
            return {'success': False, 'error': 'Failed to check usage limits'}
    
    def update_user_usage(self, user_id: int, word_count: int) -> bool:
        """Update user usage after a successful conversion."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Update usage counters
            cursor.execute('''
                UPDATE user_usage
                SET words_used_this_month = words_used_this_month + ?,
                    conversions_this_month = conversions_this_month + 1,
                    total_conversions = total_conversions + 1,
                    total_words_converted = total_words_converted + ?
                WHERE user_id = ?
            ''', (word_count, word_count, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usage updated for user {user_id}: +{word_count} words")
            return True
            
        except Exception as e:
            logger.error(f"Error updating usage for user {user_id}: {e}")
            return False
    
    def _get_recent_conversions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent conversions for dashboard display."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT job_id, original_filename, file_type, word_count,
                       voice_used, status, created_at, processing_time
                FROM conversions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            conversions = []
            for row in cursor.fetchall():
                conv = dict(row)
                conv['download_url'] = f'/download/{conv["job_id"]}'
                conversions.append(conv)
            
            conn.close()
            return conversions
            
        except Exception as e:
            logger.error(f"Error getting recent conversions: {e}")
            return []
    
    def _calculate_usage_statistics(self, user_id: int) -> Dict:
        """Calculate various usage statistics."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Get user creation date for account age
            cursor.execute('SELECT created_at FROM users WHERE id = ?', (user_id,))
            user_row = cursor.fetchone()
            
            # Get conversion stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_conversions,
                    AVG(word_count) as avg_words_per_conversion,
                    AVG(processing_time) as avg_processing_time,
                    MIN(created_at) as first_conversion,
                    MAX(created_at) as last_conversion
                FROM conversions WHERE user_id = ?
            ''', (user_id,))
            
            stats_row = cursor.fetchone()
            stats = dict(stats_row) if stats_row else {}
            
            # Calculate account age in days
            account_age_days = 0
            if user_row and user_row['created_at']:
                created_date = datetime.fromisoformat(user_row['created_at'])
                account_age_days = (datetime.now() - created_date).days
            
            # Calculate conversion frequency
            conversion_frequency = 0
            if account_age_days > 0 and stats.get('total_conversions', 0) > 0:
                conversion_frequency = stats['total_conversions'] / account_age_days
            
            conn.close()
            
            return {
                'account_age_days': account_age_days,
                'total_conversions': stats.get('total_conversions', 0),
                'avg_words_per_conversion': int(stats.get('avg_words_per_conversion', 0) or 0),
                'avg_processing_time': int(stats.get('avg_processing_time', 0) or 0),
                'conversion_frequency': round(conversion_frequency, 3),
                'first_conversion': stats.get('first_conversion'),
                'last_conversion': stats.get('last_conversion')
            }
            
        except Exception as e:
            logger.error(f"Error calculating usage statistics: {e}")
            return {}
    
    def _calculate_words_remaining(self, usage_data: Dict, user_data: Dict) -> int:
        """Calculate words remaining for current month."""
        word_limit = user_data['words_per_month']
        if word_limit <= 0:  # Unlimited
            return -1
        return max(0, word_limit - usage_data['words_used_this_month'])
    
    def _calculate_conversions_remaining(self, usage_data: Dict, user_data: Dict) -> int:
        """Calculate conversions remaining for current month."""
        conversion_limit = user_data['monthly_conversions']
        if conversion_limit <= 0:  # Unlimited
            return -1
        return max(0, conversion_limit - usage_data['conversions_this_month'])
    
    def _calculate_efficiency_score(self, conversions: List[Dict]) -> int:
        """Calculate user efficiency score based on usage patterns."""
        if not conversions:
            return 0
        
        score = 0
        
        # Points for consistency (regular usage)
        if len(conversions) >= 5:
            score += 20
        elif len(conversions) >= 2:
            score += 10
        
        # Points for processing efficiency (shorter processing times)
        avg_processing_time = sum(c['processing_time'] or 0 for c in conversions) / len(conversions)
        if avg_processing_time < 30:  # Less than 30 seconds average
            score += 30
        elif avg_processing_time < 60:
            score += 20
        elif avg_processing_time < 120:
            score += 10
        
        # Points for file diversity
        file_types = set(c['file_type'] for c in conversions if c['file_type'])
        score += min(len(file_types) * 15, 45)  # Max 45 points for diversity
        
        return min(score, 100)  # Cap at 100
    
    def _create_default_usage(self, user_id: int) -> Dict:
        """Create default usage record if it doesn't exist."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            current_month_start = date.today().replace(day=1)
            cursor.execute('''
                INSERT OR IGNORE INTO user_usage 
                (user_id, current_month_start)
                VALUES (?, ?)
            ''', (user_id, current_month_start))
            
            conn.commit()
            conn.close()
            
            return {
                'words_used_this_month': 0,
                'conversions_this_month': 0,
                'total_conversions': 0,
                'total_words_converted': 0,
                'current_month_start': current_month_start.isoformat(),
                'last_reset_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating default usage: {e}")
            return {}
    
    def _reset_monthly_usage(self, user_id: int, month_start: date) -> None:
        """Reset monthly usage counters."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_usage
                SET words_used_this_month = 0,
                    conversions_this_month = 0,
                    current_month_start = ?,
                    last_reset_date = ?
                WHERE user_id = ?
            ''', (month_start.isoformat(), datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Monthly usage reset for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error resetting monthly usage: {e}")

# Global dashboard service instance
dashboard_service = None

def get_dashboard_service():
    """Get the global dashboard service instance."""
    global dashboard_service
    if dashboard_service is None:
        dashboard_service = DashboardService()
    return dashboard_service