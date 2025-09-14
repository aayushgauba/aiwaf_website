"""
Simple SSH tunnel test for PythonAnywhere MySQL connection
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_ssh_tunnel():
    """Test SSH tunnel connection to PythonAnywhere"""
    
    try:
        import sshtunnel
        import paramiko
        import pymysql
        
        # Fix for paramiko compatibility issues
        try:
            # For newer paramiko versions
            if not hasattr(paramiko, 'DSSKey'):
                import paramiko.dss
                paramiko.DSSKey = paramiko.dss.DSSKey
        except (AttributeError, ImportError):
            # Alternative fix for paramiko compatibility
            pass
        
        # Get credentials from environment
        ssh_host = os.environ.get('SSH_HOST')
        ssh_username = os.environ.get('SSH_USERNAME')
        ssh_password = os.environ.get('SSH_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = int(os.environ.get('DB_PORT', 3306))
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_name = os.environ.get('DB_NAME')
        
        print("Testing SSH tunnel connection...")
        print(f"SSH Host: {ssh_host}")
        print(f"SSH Username: {ssh_username}")
        print(f"Database Host: {db_host}")
        print(f"Database Name: {db_name}")
        
        # Configure timeouts
        sshtunnel.SSH_TIMEOUT = 20.0
        sshtunnel.TUNNEL_TIMEOUT = 20.0
        
        with sshtunnel.SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(db_host, db_port),
            local_bind_address=('127.0.0.1', 0)
        ) as tunnel:
            print(f"✅ SSH tunnel established successfully!")
            print(f"Local port: {tunnel.local_bind_port}")
            
            # Test MySQL connection through tunnel
            print("Testing MySQL connection through tunnel...")
            connection = pymysql.connect(
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                print(f"✅ MySQL connection successful! Result: {result}")
            
            connection.close()
            print("🎉 All tests passed! Your SSH tunnel and MySQL connection are working.")
            
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install: pip install sshtunnel paramiko pymysql")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your SSH credentials in .env file")
        print("2. Verify you can SSH manually: ssh aayushgauba@ssh.pythonanywhere.com")
        print("3. Check if your PythonAnywhere account has SSH access enabled")
        print("4. Verify your MySQL database exists and credentials are correct")

if __name__ == '__main__':
    test_ssh_tunnel()