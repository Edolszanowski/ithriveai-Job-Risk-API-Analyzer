"""
Database Refresh Module

This script performs a daily update of BLS statistics and refreshes the database
to keep it active and ensure data is current.

Run this script daily using a scheduled task or cron job.
"""

import os
import sys
import json
import time
import datetime
import random
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_refresh.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import BLS connector
import bls_connector

# Try to import database module - fall back gracefully if not available
try:
    from database import save_job_search, get_popular_searches, get_highest_risk_jobs, get_lowest_risk_jobs, get_recent_searches
    database_available = True
    logger.info("Database module loaded successfully")
except Exception as e:
    logger.error(f"Error loading database module: {str(e)}")
    database_available = False
    # Define stub functions to avoid unbound variable errors
    def save_job_search(job_title, risk_data):
        logger.info(f"Would save job search for '{job_title}' if database was available")
        return None
        
    def get_popular_searches(limit=5):
        logger.info(f"Would get popular searches if database was available")
        return []
        
    def get_highest_risk_jobs(limit=5):
        logger.info(f"Would get highest risk jobs if database was available")
        return []
        
    def get_lowest_risk_jobs(limit=5):
        logger.info(f"Would get lowest risk jobs if database was available")
        return []
        
    def get_recent_searches(limit=10):
        logger.info(f"Would get recent searches if database was available")
        return []

# List of key job titles to refresh - these are common searches that will keep our data fresh
KEY_JOB_TITLES = [
    "Software Developer",
    "Nurse",
    "Project Manager",
    "Teacher",
    "Data Analyst",
    "Marketing Manager",
    "Financial Analyst",
    "Graphic Designer",
    "Sales Representative",
    "Customer Service Representative"
]

def update_job_data(job_title: str) -> Dict[str, Any]:
    """
    Update data for a specific job title from BLS API
    
    Args:
        job_title: The job title to update
        
    Returns:
        Updated job data dictionary
    """
    logger.info(f"Updating data for {job_title}")
    
    try:
        # Get BLS data
        from job_api_integration import get_job_data
        job_data = get_job_data(job_title)
        
        # Save to database if available
        if database_available:
            try:
                save_job_search(job_title, {
                    'year_1_risk': job_data.get('risk_scores', {}).get('year_1', 0),
                    'year_5_risk': job_data.get('risk_scores', {}).get('year_5', 0),
                    'risk_category': job_data.get('risk_category', 'Unknown'),
                    'job_category': job_data.get('job_category', 'Unknown')
                })
                logger.info(f"Successfully saved {job_title} to database")
            except Exception as e:
                logger.error(f"Error saving {job_title} to database: {str(e)}")
        
        return job_data
    
    except Exception as e:
        logger.error(f"Error updating data for {job_title}: {str(e)}")
        return {"error": str(e)}

def check_and_update_refresh_timestamp():
    """Update the last refresh timestamp"""
    try:
        refresh_data = {"date": datetime.datetime.now().isoformat()}
        with open("last_refresh.json", "w") as f:
            json.dump(refresh_data, f)
        logger.info(f"Updated last refresh timestamp: {refresh_data['date']}")
    except Exception as e:
        logger.error(f"Error updating refresh timestamp: {str(e)}")

def perform_database_queries():
    """Perform various database queries to ensure the database stays active"""
    if not database_available:
        logger.warning("Database not available - skipping database queries")
        return
    
    try:
        # Execute various read operations to keep database active
        popular = get_popular_searches(5)
        logger.info(f"Popular searches: {len(popular)} retrieved")
        
        highest_risk = get_highest_risk_jobs(5)
        logger.info(f"Highest risk jobs: {len(highest_risk)} retrieved")
        
        lowest_risk = get_lowest_risk_jobs(5)
        logger.info(f"Lowest risk jobs: {len(lowest_risk)} retrieved")
        
        recent = get_recent_searches(10)
        logger.info(f"Recent searches: {len(recent)} retrieved")
    except Exception as e:
        logger.error(f"Error performing database queries: {str(e)}")

def main():
    """Main function to update job data and refresh database"""
    logger.info("Starting database refresh process")
    
    # Check BLS API connection
    api_key = os.environ.get('BLS_API_KEY')
    if not api_key:
        logger.error("BLS_API_KEY environment variable not set")
        return
    
    # Randomly select 2-4 jobs to update (to avoid hitting API limits)
    sample_size = min(random.randint(2, 4), len(KEY_JOB_TITLES))
    jobs_to_update = random.sample(KEY_JOB_TITLES, sample_size)
    
    logger.info(f"Selected {len(jobs_to_update)} jobs to update: {', '.join(jobs_to_update)}")
    
    # Update each selected job
    updated_jobs = []
    for job_title in jobs_to_update:
        try:
            job_data = update_job_data(job_title)
            updated_jobs.append(job_title)
        except Exception as e:
            logger.error(f"Failed to update {job_title}: {str(e)}")
        
        # Sleep briefly between API calls
        time.sleep(1)
    
    # Perform database queries
    perform_database_queries()
    
    # Update refresh timestamp
    check_and_update_refresh_timestamp()
    
    logger.info(f"Database refresh completed. Updated {len(updated_jobs)} jobs: {', '.join(updated_jobs)}")

if __name__ == "__main__":
    main()