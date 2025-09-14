# DigitalOcean Deployment Guide with MySQL

## Files for Deployment

1. **wsgi.py** - WSGI entry point
2. **Procfile** - Process definition (`web: gunicorn --bind 0.0.0.0:$PORT wsgi:application`)
3. **requirements.txt** - Python dependencies (includes Flask-SQLAlchemy, PyMySQL)
4. **runtime.txt** - Python version specification
5. **.do/app.yaml** - DigitalOcean App Platform configuration with MySQL database
6. **.env.example** - Environment variables template

## Database Setup

The application now includes MySQL integration with the following features:
- **PageView tracking** - Analytics for documentation usage
- **UserFeedback** - Collect user feedback on documentation pages
- **DownloadStats** - Track AIWAF framework downloads

### Database Models
- `PageView` - Track page visits and user analytics
- `UserFeedback` - Store user ratings and comments
- `DownloadStats` - Monitor download statistics by framework

## Environment Variables

Required environment variables for your DigitalOcean app:
- `PORT`: Automatically set by the platform (usually 8080)
- `SECRET_KEY`: Set a secure secret key for Flask sessions

**Database Configuration (Option 1 - Recommended for Security):**
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password  
- `DB_HOST`: MySQL server hostname/IP
- `DB_PORT`: MySQL port (usually 3306)
- `DB_NAME`: Database name

**Database Configuration (Option 2 - Alternative):**
- `DATABASE_URL`: Full MySQL connection URL (if set, overrides individual components)

## Deployment Steps

1. **Prepare your repository**:
   - Ensure all files are committed to GitHub
   - Copy `.env.example` to `.env` and configure for local development
   - **Never commit your `.env` file with real credentials!**

2. **Create DigitalOcean App**:
   - Create a new app in DigitalOcean App Platform
   - Connect your GitHub repository
   - The app.yaml will automatically configure the web service

3. **Configure Environment Variables in DigitalOcean Dashboard**:
   - Set `SECRET_KEY` to a secure random string
   - Set database credentials: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
   - **OR** alternatively set `DATABASE_URL` with full connection string

4. **Database Setup**:
   - Ensure your external MySQL server allows connections from DigitalOcean
   - Database tables will be created automatically on first run
   - The `/health` endpoint will verify database connectivity
4. DigitalOcean will automatically detect the Python app and use the Procfile
5. The app will start using `python wsgi.py`

## Health Check

The app should respond on:
- Health check endpoint: `/` (homepage)
- Port: Whatever is set in the `PORT` environment variable

## Common Issues

1. **Module not found**: Ensure all dependencies are in requirements.txt
2. **Port binding**: The app binds to 0.0.0.0 and uses PORT environment variable
3. **WSGI issues**: Using simple Flask development server instead of gunicorn for simplicity
