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

# Check if we're using SSH tunnel (local development) or direct connection (production)
ssh_host = os.environ.get('SSH_HOST')
if ssh_host:
    # Local development with SSH tunnel - skip SQLAlchemy initialization
    # It will be handled by run_tunnel.py after tunnel is established
    db = None
else:
    # Production - direct connection
    db_user = os.environ.get('DB_USER', 'username')
    db_password = os.environ.get('DB_PASSWORD', 'password')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'aiwaf_docs')
    
    # If DATABASE_URL is provided, use it directly
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Initialize SQLAlchemy only for production
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
    # Only initialize database when running directly (not through tunnel)
    ssh_host = os.environ.get('SSH_HOST')
    if not ssh_host:
        # No SSH tunnel - safe to initialize database
        with app.app_context():
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as e:
                print(f"Database initialization error: {e}")
    else:
        print("SSH tunnel detected - skipping database initialization (will be handled by tunnel runner)")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
