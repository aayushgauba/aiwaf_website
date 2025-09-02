# DigitalOcean Deployment Guide

## Files for Deployment

1. **wsgi.py** - WSGI entry point
2. **Procfile** - Process definition (`web: python wsgi.py`)
3. **requirements.txt** - Python dependencies
4. **runtime.txt** - Python version specification
5. **.do/app.yaml** - DigitalOcean App Platform configuration

## Environment Variables

Set the following environment variable in your DigitalOcean app:
- `PORT`: Will be automatically set by the platform (usually 8080)

## Deployment Steps

1. Push your code to GitHub
2. Create a new app in DigitalOcean App Platform
3. Connect your GitHub repository
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
