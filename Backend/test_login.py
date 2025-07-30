#!/usr/bin/env python3
"""Test script to verify admin login credentials work"""

import os
import sys
from werkzeug.security import check_password_hash
import sqlite3

def test_admin_login():
    """Test if admin login credentials work"""
    try:
        # Connect directly to the database
        db_path = 'instance/sports_management.db'
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the admin user
        cursor.execute('SELECT username, _pw_hash FROM user WHERE username = ?', ('admin',))
        result = cursor.fetchone()
        
        if not result:
            print("❌ Admin user not found in database")
            return False
        
        username, password_hash = result
        
        # Test the expected password
        if check_password_hash(password_hash, 'admin123'):
            print("✅ AUTHENTICATION FIXED!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   Status: LOGIN SHOULD WORK")
            return True
        else:
            print("❌ Password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if test_admin_login():
        sys.exit(0)
    else:
        sys.exit(1)