"""
Database connection manager with SSH tunnel support for PythonAnywhere
"""
import os
import sshtunnel
import MySQLdb
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        self.ssh_host = os.environ.get('SSH_HOST')
        self.ssh_username = os.environ.get('SSH_USERNAME')
        self.ssh_password = os.environ.get('SSH_PASSWORD')
        self.db_host = os.environ.get('DB_HOST')
        self.db_user = os.environ.get('DB_USER')
        self.db_password = os.environ.get('DB_PASSWORD')
        self.db_name = os.environ.get('DB_NAME')
        self.db_port = int(os.environ.get('DB_PORT', 3306))
        
        # Configure SSH tunnel timeouts
        sshtunnel.SSH_TIMEOUT = 10.0
        sshtunnel.TUNNEL_TIMEOUT = 10.0
    
    @contextmanager
    def get_connection(self):
        """Get database connection with SSH tunnel for local development"""
        if self.ssh_host and self.ssh_username and self.ssh_password:
            # Use SSH tunnel for local development
            with sshtunnel.SSHTunnelForwarder(
                self.ssh_host,
                ssh_username=self.ssh_username,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.db_host, self.db_port)
            ) as tunnel:
                connection = MySQLdb.connect(
                    user=self.db_user,
                    passwd=self.db_password,
                    host='127.0.0.1',
                    port=tunnel.local_bind_port,
                    db=self.db_name,
                )
                try:
                    yield connection
                finally:
                    connection.close()
        else:
            # Direct connection for production (no SSH tunnel needed)
            connection = MySQLdb.connect(
                user=self.db_user,
                passwd=self.db_password,
                host=self.db_host,
                port=self.db_port,
                db=self.db_name,
            )
            try:
                yield connection
            finally:
                connection.close()
    
    def get_sqlalchemy_url(self):
        """Get SQLAlchemy URL for Flask-SQLAlchemy"""
        if self.ssh_host and self.ssh_username and self.ssh_password:
            # For local development with SSH tunnel, we'll handle this differently
            # Return a placeholder URL and handle connection in app initialization
            return f'mysql://{self.db_user}:{self.db_password}@localhost/{self.db_name}'
        else:
            # Direct connection for production
            return f'mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

# Global database manager instance
db_manager = DatabaseManager()