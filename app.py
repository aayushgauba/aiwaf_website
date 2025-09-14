from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import pymysql

# Install PyMySQL as MySQL driver for SQLAlchemy
pymysql.install_as_MySQLdb()

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration with SSH tunnel support
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Determine environment mode
ssh_host = os.environ.get('SSH_HOST')
flask_env = os.environ.get('FLASK_ENV', 'production')
is_development = flask_env == 'development' and ssh_host

print(f"Environment: {flask_env}")
print(f"SSH Host configured: {'Yes' if ssh_host else 'No'}")
print(f"Running in: {'Development (SSH Tunnel)' if is_development else 'Production (Direct Connection)'}")

if is_development:
    # Local development with SSH tunnel - skip SQLAlchemy initialization
    # It will be handled by run_tunnel.py after tunnel is established
    print("Skipping database initialization - will be handled by SSH tunnel script")
    db = None
else:
    # Production - direct connection using environment variables
    print("Initializing database for production...")
    
    # Try DATABASE_URL first (for platforms like DigitalOcean)
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Build from individual components from .env
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT', '3306')
        db_name = os.environ.get('DB_NAME')
        
        if not all([db_user, db_password, db_host, db_name]):
            raise ValueError("Missing required database environment variables. Please check your .env file.")
        
        database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    print(f"Database URL configured: {database_url.split('://')[0]}://[user]:[password]@{database_url.split('@')[1]}")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy for production
    db = SQLAlchemy(app)

# Database Models (will be properly defined after SSH tunnel initialization)
def define_models():
    """Define database models - called after SQLAlchemy initialization"""
    global PageView, UserFeedback, DownloadStats
    
    class PageView(db.Model):
        """Track page views for analytics"""
        id = db.Column(db.Integer, primary_key=True)
        page_path = db.Column(db.String(255), nullable=False)
        user_ip = db.Column(db.String(45))  # IPv6 compatible
        user_agent = db.Column(db.Text)
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    class UserFeedback(db.Model):
        """Store user feedback on documentation"""
        id = db.Column(db.Integer, primary_key=True)
        page_path = db.Column(db.String(255), nullable=False)
        rating = db.Column(db.Integer)  # 1-5 rating
        comment = db.Column(db.Text)
        email = db.Column(db.String(120))  # Optional contact
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    class DownloadStats(db.Model):
        """Track AIWAF downloads and installations"""
        id = db.Column(db.Integer, primary_key=True)
        framework = db.Column(db.String(50), nullable=False)  # django, flask, etc.
        version = db.Column(db.String(20))
        user_ip = db.Column(db.String(45))
        country = db.Column(db.String(2))  # Country code
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    return PageView, UserFeedback, DownloadStats

# Initialize models if not in SSH tunnel mode
if db is not None:
    PageView, UserFeedback, DownloadStats = define_models()
else:
    # Will be defined later by tunnel runner
    PageView, UserFeedback, DownloadStats = None, None, None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/health')
def health():
    try:
        if db is None:
            db_status = "not initialized (SSH tunnel mode)"
        else:
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy", 
        "message": "AIWAF Documentation is running",
        "database": db_status
    })

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/docs/<framework>')
def framework_docs(framework):
    return render_template(f'docs_{framework}.html')

@app.route('/docs/<framework>/<page>')
def doc_page(framework, page):
    return render_template(f'docs_{framework}_{page}.html')

# Initialize database tables
if __name__ == '__main__':
    # Use the same environment detection logic
    ssh_host = os.environ.get('SSH_HOST')
    flask_env = os.environ.get('FLASK_ENV', 'production')
    is_development = flask_env == 'development' and ssh_host
    
    if not is_development and db is not None:
        # Production mode - initialize database
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as e:
                print(f"❌ Database initialization error: {e}")
    elif is_development:
        print("Development mode - database initialization will be handled by tunnel runner")
    else:
        print("Warning: Database not initialized (db is None)")

    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask app on port {port} (debug: {debug_mode})")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
