"""
Job Title Autocomplete Module

This module provides autocomplete functionality for job title searches,
suggesting BLS job titles as users type.
"""

import os
import json
import streamlit as st
from sqlalchemy import create_engine, text
from typing import List, Dict, Any

# Cache for storing job titles to minimize database queries
@st.cache_data(ttl=3600)
def load_job_titles_from_db():
    """
    Load all job titles from the database.
    Results are cached for one hour to reduce database load.
    
    Returns:
        List of dictionaries with job titles and SOC codes
    """
    # Get database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL environment variable not set - using fallback job titles")
        return load_fallback_job_titles()
    
    try:
        # Connection parameters for reliable connection
        connect_args = {
            "connect_timeout": 5,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
            "sslmode": 'require'
        }
        
        # Create engine
        engine = create_engine(
            database_url, 
            connect_args=connect_args,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        # Query job titles from database
        with engine.connect() as conn:
            # Get all job titles
            query = text("""
                SELECT j.title, j.soc_code, j.is_primary 
                FROM job_titles j
                ORDER BY j.is_primary DESC, j.title
            """)
            result = conn.execute(query)
            job_titles = [{"title": row[0], "soc_code": row[1], "is_primary": row[2]} for row in result]
            
            return job_titles
            
    except Exception as e:
        print(f"Error loading job titles from database: {str(e)}")
        return load_fallback_job_titles()

def load_fallback_job_titles():
    """
    Load a sample list of job titles when database is not available.
    """
    return [
        {"title": "Software Developer", "soc_code": "15-1252", "is_primary": True},
        {"title": "Software Engineer", "soc_code": "15-1252", "is_primary": False},
        {"title": "Web Developer", "soc_code": "15-1254", "is_primary": True},
        {"title": "Registered Nurse", "soc_code": "29-1141", "is_primary": True},
        {"title": "Nurse", "soc_code": "29-1141", "is_primary": False},
        {"title": "Teacher", "soc_code": "25-2021", "is_primary": False},
        {"title": "Elementary School Teacher", "soc_code": "25-2021", "is_primary": True},
        {"title": "Lawyer", "soc_code": "23-1011", "is_primary": True},
        {"title": "Attorney", "soc_code": "23-1011", "is_primary": False},
        {"title": "Accountant", "soc_code": "13-2011", "is_primary": True},
        {"title": "Architect", "soc_code": "17-1011", "is_primary": True},
        {"title": "Doctor", "soc_code": "29-1215", "is_primary": False},
        {"title": "Physician", "soc_code": "29-1215", "is_primary": True},
        {"title": "Project Manager", "soc_code": "11-3021", "is_primary": True},
        {"title": "Product Manager", "soc_code": "11-2021", "is_primary": True},
        {"title": "Data Scientist", "soc_code": "15-2051", "is_primary": True},
        {"title": "Data Analyst", "soc_code": "15-2041", "is_primary": True}
    ]

def search_job_titles(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for job titles matching a query string.
    
    Args:
        query: Search string
        limit: Maximum number of results to return
        
    Returns:
        List of matching job titles
    """
    job_titles = load_job_titles_from_db()
    
    # If query is empty, return popular or primary job titles
    if not query:
        # Return primary titles first, then limit
        primary_titles = [job for job in job_titles if job.get("is_primary")]
        return primary_titles[:limit]
    
    # Normalize query for case-insensitive search
    query_lower = query.lower()
    
    # Find exact title matches first
    exact_matches = [job for job in job_titles if job["title"].lower() == query_lower]
    
    # Find titles that start with the query
    starts_with_matches = [job for job in job_titles 
                         if job["title"].lower().startswith(query_lower) 
                         and job not in exact_matches]
    
    # Find titles that contain the query
    contains_matches = [job for job in job_titles 
                      if query_lower in job["title"].lower() 
                      and job not in exact_matches
                      and job not in starts_with_matches]
    
    # Combine results, prioritizing exact matches, then starts-with, then contains
    results = exact_matches + starts_with_matches + contains_matches
    
    # Return limited results
    return results[:limit]

def job_title_autocomplete(label: str, key: str = "", value: str = "", placeholder: str = "Search for a job title...", help: str = ""):
    """
    Create a job title autocomplete input field.
    
    Args:
        label: Label for the input field
        key: Unique key for Streamlit session state
        value: Default value
        placeholder: Placeholder text
        help: Help text
        
    Returns:
        Selected job title
    """
    # Create unique keys if not provided
    if key == "":
        key = f"job_search_{id(label)}"
    
    input_key = f"{key}_input"
    selection_key = f"{key}_selection"
    
    # Initialize session state
    if input_key not in st.session_state:
        st.session_state[input_key] = value
        
    if selection_key not in st.session_state:
        st.session_state[selection_key] = None
    
    # Create text input for search
    query = st.text_input(
        label=label,
        value=st.session_state[input_key],
        placeholder=placeholder,
        help=help,
        key=input_key
    )
    
    # Search for matching job titles
    if query:
        matches = search_job_titles(query)
        
        if matches:
            # Display matches in a dropdown
            selected_index = st.selectbox(
                "Select a job title:",
                options=range(len(matches)),
                format_func=lambda i: matches[i]["title"],
                key=f"{key}_dropdown"
            )
            
            selected_job = matches[selected_index]["title"]
            
            # Update selection when user clicks button
            if st.button("Use this job title", key=f"{key}_button"):
                # Store the selection in session state for retrieval on next run
                st.session_state[selection_key] = selected_job
                # Return the selected job directly
                return selected_job
                
            return selected_job
        else:
            st.info("No matching job titles found. Try a different search term.")
            return query
    
    return query