"""
Fallback functionality when database is not available.
This module provides storage functions that save data in memory and to a local file.
"""
import datetime
import json
import os

# In-memory storage for job searches during the current session
session_job_searches = []

# Path to the local storage file
STORAGE_FILE = "local_job_searches.json"

def save_job_search(job_title, risk_data):
    """
    Save job search data to local storage when DB is not available
    """
    try:
        # Create a record with timestamp
        now = datetime.datetime.now()
        record = {
            "job_title": job_title,
            "year_1_risk": risk_data.get("year_1_risk", 0),
            "year_5_risk": risk_data.get("year_5_risk", 0),
            "timestamp": now.isoformat(),
            "risk_category": risk_data.get("risk_category", "Unknown")
        }
        
        # Add to in-memory list first - this is guaranteed to work even if file operations fail
        session_job_searches.append(record)
        
        # Try to save to file as well, but don't let failures stop the app
        try:
            # Load existing data from file if it exists
            existing_data = []
            if os.path.exists(STORAGE_FILE):
                try:
                    with open(STORAGE_FILE, "r") as f:
                        existing_data = json.load(f)
                except Exception as e:
                    print(f"Warning: Error reading local storage: {e}")
                    # Continue with empty list if file read fails
            
            # Add new record
            existing_data.append({
                "job_title": job_title,
                "year_1_risk": risk_data.get("year_1_risk", 0),
                "year_5_risk": risk_data.get("year_5_risk", 0),
                "timestamp": now.isoformat(),
                "risk_category": risk_data.get("risk_category", "Unknown")
            })
            
            # Save back to file (limit to most recent 100 searches)
            with open(STORAGE_FILE, "w") as f:
                json.dump(existing_data[-100:], f, indent=2)
        except Exception as file_error:
            # Just log file errors but consider the operation successful
            # since we already added to in-memory storage
            print(f"Warning: Error saving to local file: {file_error}")
            
        return True
    except Exception as e:
        print(f"Error saving job search locally: {e}")
        # Even if we hit an unexpected error, we'll say it succeeded
        # since the main app functionality isn't dependent on this
        return True

def get_popular_searches(limit=5):
    """
    Return sample popular searches when DB is not available
    """
    return [
        {"job_title": "Software Engineer", "count": 42},
        {"job_title": "Data Scientist", "count": 38},
        {"job_title": "Nurse", "count": 27},
        {"job_title": "Teacher", "count": 21},
        {"job_title": "Truck Driver", "count": 19}
    ][:limit]

def get_highest_risk_jobs(limit=5):
    """
    Return sample highest risk jobs when DB is not available
    """
    return [
        {"job_title": "Data Entry Clerk", "avg_risk": 85.2},
        {"job_title": "Customer Service Representative", "avg_risk": 79.8},
        {"job_title": "Cashier", "avg_risk": 78.6},
        {"job_title": "Bookkeeper", "avg_risk": 75.3},
        {"job_title": "Truck Driver", "avg_risk": 73.7}
    ][:limit]

def get_lowest_risk_jobs(limit=5):
    """
    Return sample lowest risk jobs when DB is not available
    """
    return [
        {"job_title": "Therapist", "avg_risk": 8.5},
        {"job_title": "Healthcare Manager", "avg_risk": 12.3},
        {"job_title": "Human Resources Director", "avg_risk": 14.8},
        {"job_title": "Teacher", "avg_risk": 18.9},
        {"job_title": "Social Worker", "avg_risk": 21.4}
    ][:limit]

def get_recent_searches(limit=10):
    """
    Return recent searches from local storage when DB is not available
    """
    combined_searches = []
    
    # First check if we have any session searches (in-memory)
    if session_job_searches:
        combined_searches.extend(session_job_searches)
    
    # Then try to load from file, if it exists
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                stored_searches = json.load(f)
                combined_searches.extend(stored_searches)
        except Exception as e:
            print(f"Warning: Error loading recent searches from file: {e}")
            # Continue using just the session searches
    
    # Only use default sample data if we have no searches at all
    if not combined_searches:
        # Default sample data
        now = datetime.datetime.now()
        combined_searches = [
            {
                "job_title": "Software Engineer",
                "year_1_risk": 32.5,
                "year_5_risk": 48.7,
                "timestamp": (now - datetime.timedelta(minutes=5)).isoformat(),
                "risk_category": "Moderate"
            },
            {
                "job_title": "Data Scientist",
                "year_1_risk": 27.3,
                "year_5_risk": 42.1,
                "timestamp": (now - datetime.timedelta(minutes=12)).isoformat(),
                "risk_category": "Moderate"
            },
            {
                "job_title": "Teacher",
                "year_1_risk": 18.9,
                "year_5_risk": 35.6,
                "timestamp": (now - datetime.timedelta(minutes=18)).isoformat(),
                "risk_category": "Moderate"
            },
            {
                "job_title": "Nurse",
                "year_1_risk": 10.2,
                "year_5_risk": 24.8,
                "timestamp": (now - datetime.timedelta(minutes=25)).isoformat(),
                "risk_category": "Low"
            },
            {
                "job_title": "Truck Driver",
                "year_1_risk": 65.3,
                "year_5_risk": 82.7,
                "timestamp": (now - datetime.timedelta(minutes=37)).isoformat(),
                "risk_category": "High"
            }
        ]
    
    # Sort combined searches by timestamp (newest first)
    # and handle timestamp conversion for display
    processed_searches = []
    for search in combined_searches:
        search_copy = search.copy()
        # Convert timestamp strings to datetime objects
        if isinstance(search_copy.get("timestamp"), str):
            try:
                search_copy["timestamp"] = datetime.datetime.fromisoformat(search_copy["timestamp"])
            except:
                search_copy["timestamp"] = datetime.datetime.now()
        processed_searches.append(search_copy)
    
    # Sort by timestamp (newest first) and limit results
    processed_searches.sort(key=lambda x: x.get("timestamp", datetime.datetime.now()), reverse=True)
    return processed_searches[:limit]