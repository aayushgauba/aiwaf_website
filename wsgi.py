import os
from app import app

# This is the WSGI entry point for production servers like gunicorn
application = app

if __name__ == "__main__":
    # Get port from environment variable for deployment platforms
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
