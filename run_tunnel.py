"""
SSH Tunnel Flask App Runner for PythonAnywhere
This script establishes an SSH tunnel and then runs the Flask app
"""
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_with_ssh_tunnel():
    """Run Flask app with SSH tunnel for local development"""
    ssh_host = os.environ.get('SSH_HOST')
    
    if ssh_host:
        # Local development - use SSH tunnel
        print("Starting SSH tunnel for local development...")
        
        try:
            import sshtunnel
            import paramiko
            
            # Fix for paramiko compatibility issues with newer versions
            try:
                if not hasattr(paramiko, 'DSSKey'):
                    import paramiko.dss
                    paramiko.DSSKey = paramiko.dss.DSSKey
            except (AttributeError, ImportError):
                # Skip if fix not needed or not available
                pass
            
            ssh_username = os.environ.get('SSH_USERNAME')
            ssh_password = os.environ.get('SSH_PASSWORD')
            db_host = os.environ.get('DB_HOST')
            db_port = int(os.environ.get('DB_PORT', 3306))
            
            # Configure SSH tunnel timeouts
            sshtunnel.SSH_TIMEOUT = 20.0
            sshtunnel.TUNNEL_TIMEOUT = 20.0
            
            print(f"Connecting to SSH host: {ssh_host}")
            print(f"SSH Username: {ssh_username}")
            print(f"Database host: {db_host}")
            
            with sshtunnel.SSHTunnelForwarder(
                (ssh_host, 22),
                ssh_username=ssh_username,
                ssh_password=ssh_password,
                remote_bind_address=(db_host, db_port),
                local_bind_address=('127.0.0.1', 0)  # Let system choose available port
            ) as tunnel:
                print(f"SSH Tunnel established successfully!")
                print(f"Local port: {tunnel.local_bind_port}")
                print(f"Remote: {db_host}:{db_port}")
                
                # Import Flask app after tunnel is established
                from app import app, define_models
                
                # Update the database URL to use the tunnel
                db_user = os.environ.get('DB_USER')
                db_password = os.environ.get('DB_PASSWORD')
                db_name = os.environ.get('DB_NAME')
                
                tunnel_url = f'mysql+pymysql://{db_user}:{db_password}@127.0.0.1:{tunnel.local_bind_port}/{db_name}'
                print(f"Database URL: mysql+pymysql://{db_user}:***@127.0.0.1:{tunnel.local_bind_port}/{db_name}")
                
                # Wait a moment for tunnel to be fully established
                time.sleep(1)
                
                # Test direct PyMySQL connection first
                print("Testing direct PyMySQL connection through tunnel...")
                try:
                    import pymysql
                    test_conn = pymysql.connect(
                        host='127.0.0.1',
                        port=tunnel.local_bind_port,
                        user=db_user,
                        password=db_password,
                        database=db_name
                    )
                    with test_conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                    test_conn.close()
                    print("✅ Direct PyMySQL connection successful!")
                except Exception as e:
                    print(f"❌ Direct PyMySQL connection failed: {e}")
                    return
                
                # Now initialize SQLAlchemy with the tunnel URL
                print("Initializing SQLAlchemy with tunnel...")
                from flask_sqlalchemy import SQLAlchemy
                
                # Configure the app with tunnel database URL
                app.config['SQLALCHEMY_DATABASE_URI'] = tunnel_url
                app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
                
                # Initialize SQLAlchemy
                db = SQLAlchemy(app)
                
                # Update app's db reference
                import app as app_module
                app_module.db = db
                
                # Define models now that db is available
                with app.app_context():
                    PageView, UserFeedback, DownloadStats = define_models()
                    app_module.PageView = PageView
                    app_module.UserFeedback = UserFeedback
                    app_module.DownloadStats = DownloadStats
                    
                    # Create tables
                    try:
                        db.create_all()
                        print("✅ Database tables created successfully!")
                    except Exception as e:
                        print(f"❌ Error creating tables: {e}")
                        return
                
                # Run the Flask app
                port = int(os.environ.get('PORT', 5000))
                print(f"🚀 Starting Flask app on port {port}...")
                print(f"Access your app at: http://localhost:{port}")
                print(f"Database connected via tunnel on port {tunnel.local_bind_port}")
                app.run(host='0.0.0.0', port=port, debug=False)
                
        except ImportError as e:
            print(f"Import error: {e}")
            print("Please install required packages: pip install sshtunnel paramiko")
            sys.exit(1)
        except Exception as e:
            print(f"SSH Tunnel error: {e}")
            print("Troubleshooting tips:")
            print("1. Check your SSH credentials are correct")
            print("2. Verify PythonAnywhere allows SSH access")
            print("3. Try connecting manually: ssh aayushgauba@ssh.pythonanywhere.com")
            sys.exit(1)
    else:
        # Production - run normally
        print("No SSH configuration found, running in production mode...")
        from app import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_with_ssh_tunnel()