#!/usr/bin/env python3
"""
Production startup script for DigitalOcean deployment.
This script forces production mode and uses direct database connection.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_production_environment():
    """Configure environment for production deployment"""
    
    # Force production settings
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Check if we have required database variables
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your DigitalOcean App Platform environment variables.")
        sys.exit(1)
    
    # Build DATABASE_URL if not provided
    if not os.environ.get('DATABASE_URL'):
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT', '3306')
        db_name = os.environ.get('DB_NAME')
        
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        os.environ['DATABASE_URL'] = database_url
        print(f"✅ Built DATABASE_URL from components")
    
    # Remove SSH configuration to force direct connection
    ssh_vars = ['SSH_HOST', 'SSH_USERNAME', 'SSH_PASSWORD']
    for var in ssh_vars:
        if var in os.environ:
            del os.environ[var]
            print(f"Removed {var} for production mode")
    
    print("🚀 Production environment configured")
    print(f"Database Host: {os.environ.get('DB_HOST')}")
    print(f"Database Name: {os.environ.get('DB_NAME')}")

if __name__ == '__main__':
    print("Starting AIWAF Documentation in Production Mode...")
    
    # Setup production environment
    setup_production_environment()
    
    # Import and run the Flask app
    from app import app
    
    # Get port from environment (DigitalOcean provides this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Starting server on port {port}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )