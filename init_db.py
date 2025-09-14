#!/usr/bin/env python3
"""
Database initialization script for AIWAF Documentation Website
Run this script to create database tables and initial data
"""

from app import app, db, PageView, UserFeedback, DownloadStats
from datetime import datetime

def init_database():
    """Initialize database tables and create sample data"""
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        # Check if tables are empty and add sample data
        if PageView.query.count() == 0:
            print("Adding sample page view data...")
            sample_views = [
                PageView(page_path='/', user_ip='127.0.0.1', user_agent='Sample Browser'),
                PageView(page_path='/docs', user_ip='127.0.0.1', user_agent='Sample Browser'),
                PageView(page_path='/docs/django', user_ip='127.0.0.1', user_agent='Sample Browser'),
            ]
            
            for view in sample_views:
                db.session.add(view)
        
        if UserFeedback.query.count() == 0:
            print("Adding sample feedback data...")
            sample_feedback = UserFeedback(
                page_path='/docs/django/installation',
                rating=5,
                comment='Great documentation! Very helpful.',
                email='user@example.com'
            )
            db.session.add(sample_feedback)
        
        if DownloadStats.query.count() == 0:
            print("Adding sample download stats...")
            sample_download = DownloadStats(
                framework='django',
                version='1.0.0',
                user_ip='127.0.0.1',
                country='US'
            )
            db.session.add(sample_download)
        
        # Commit all changes
        db.session.commit()
        print("Database initialization completed successfully!")
        
        # Print table counts
        print(f"PageView records: {PageView.query.count()}")
        print(f"UserFeedback records: {UserFeedback.query.count()}")
        print(f"DownloadStats records: {DownloadStats.query.count()}")

if __name__ == '__main__':
    init_database()