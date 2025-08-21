"""Database initialization and management."""
import sqlite3
import json
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

def init_database(db_path='audiobook.db'):
    """Initialize the database with required tables."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                display_name VARCHAR(100),
                subscription_tier VARCHAR(20) DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create user_usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                words_used_this_month INTEGER DEFAULT 0,
                conversions_this_month INTEGER DEFAULT 0,
                total_conversions INTEGER DEFAULT 0,
                total_words_converted INTEGER DEFAULT 0,
                current_month_start DATE NOT NULL,
                last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create conversions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_id VARCHAR(255) UNIQUE NOT NULL,
                original_filename VARCHAR(255),
                file_type VARCHAR(10),
                file_size INTEGER,
                word_count INTEGER,
                voice_used VARCHAR(50),
                processing_time INTEGER,
                status VARCHAR(20) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                last_downloaded TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        
        # Create subscription_limits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_limits (
                tier VARCHAR(20) PRIMARY KEY,
                monthly_conversions INTEGER,
                words_per_month INTEGER,
                max_file_size_mb INTEGER,
                voice_options TEXT,
                features TEXT
            )
        ''')
        
        # Insert default subscription tiers
        subscription_tiers = [
            ('free', 3, 10000, 10, 
             '["basic"]', 
             '{"premium_voices": false, "batch_conversion": false}'),
            ('professional', -1, -1, 50, 
             '["basic", "premium", "coqui_xtts"]', 
             '{"premium_voices": true, "batch_conversion": true}'),
            ('enterprise', -1, -1, 100, 
             '["basic", "premium", "coqui_xtts", "openai"]', 
             '{"premium_voices": true, "batch_conversion": true, "api_access": true}')
        ]
        
        # Insert tiers if they don't exist
        for tier_data in subscription_tiers:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_limits 
                (tier, monthly_conversions, words_per_month, max_file_size_mb, voice_options, features)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', tier_data)
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON conversions (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversions_job_id ON conversions (job_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_usage_user_id ON user_usage (user_id)')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

def get_db_connection(db_path='audiobook.db'):
    """Get a database connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def create_user_usage_record(user_id, db_path='audiobook.db'):
    """Create initial usage record for a new user."""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Set current month start to first day of current month
        current_month_start = date.today().replace(day=1)
        
        cursor.execute('''
            INSERT INTO user_usage (user_id, current_month_start)
            VALUES (?, ?)
        ''', (user_id, current_month_start))
        
        conn.commit()
        logger.info(f"Usage record created for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to create usage record: {e}")
        raise
    finally:
        conn.close()

def migrate_existing_conversions(db_path='audiobook.db'):
    """Migrate existing conversion jobs to the new schema if needed."""
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Check if we need to migrate any existing data
        # This is a placeholder for future migration logic
        # For now, just ensure the table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversions'
        ''')
        
        if cursor.fetchone():
            logger.info("Conversions table already exists")
        else:
            logger.info("Conversions table created")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()