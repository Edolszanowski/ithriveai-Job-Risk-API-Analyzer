"""
Add High-Risk Jobs to Database

This script identifies jobs with high AI displacement risk (>10% over 5 years)
and ensures they are properly represented in the database with complete
analysis data.
"""

import os
import time
import psycopg2
import streamlit as st
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Database connection
def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            st.error("Database URL not found in environment variables")
            return None
            
        # Parse the URL to replace 'postgres://' with 'postgresql://' if needed
        parsed = urlparse(database_url)
        if parsed.scheme == 'postgres':
            postgresql_url = database_url.replace('postgres://', 'postgresql://', 1)
        else:
            postgresql_url = database_url
            
        engine = create_engine(postgresql_url)
        return engine
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def find_high_risk_jobs(min_risk_percentage=10):
    """
    Find all jobs with AI risk greater than the specified percentage over 5 years.
    Returns a list of job data dictionaries.
    """
    engine = get_db_connection()
    if not engine:
        return []
        
    query = text("""
        SELECT 
            o.code AS soc_code,
            o.title AS job_title,
            o.major_group_code,
            o.current_employment,
            o.projected_employment,
            o.percent_change,
            o.annual_job_openings,
            o.median_annual_wage,
            r.year_1_risk,
            r.year_5_risk,
            r.risk_category,
            r.risk_factors,
            r.protective_factors,
            r.analysis
        FROM 
            soc_detailed_occupations o
        JOIN 
            ai_risk_assessments r ON o.code = r.soc_code
        WHERE 
            r.year_5_risk > :min_risk
        ORDER BY 
            r.year_5_risk DESC
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"min_risk": min_risk_percentage})
            high_risk_jobs = []
            for row in result:
                # Convert SQLAlchemy Row to dictionary
                job_dict = {}
                for column, value in zip(result.keys(), row):
                    job_dict[column] = value
                high_risk_jobs.append(job_dict)
            
        return high_risk_jobs
    except Exception as e:
        st.error(f"Error querying high-risk jobs: {e}")
        return []

def ensure_job_titles_exist(high_risk_jobs):
    """
    Make sure all high-risk jobs are properly added to the job_titles table
    for autocomplete functionality.
    """
    engine = get_db_connection()
    if not engine:
        return False
        
    jobs_added = 0
    
    for job in high_risk_jobs:
        soc_code = job['soc_code']
        title = job['job_title']
        
        # Check if job title already exists
        check_query = text("""
            SELECT COUNT(*) FROM job_titles 
            WHERE soc_code = :soc_code AND title = :title
        """)
        
        try:
            with engine.connect() as conn:
                result = conn.execute(check_query, {"soc_code": soc_code, "title": title})
                if result.scalar() == 0:
                    # Safely insert without ON CONFLICT clause
                    insert_query = text("""
                        INSERT INTO job_titles (soc_code, title, is_primary)
                        VALUES (:soc_code, :title, 1)
                    """)
                    conn.execute(insert_query, {"soc_code": soc_code, "title": title})
                    jobs_added += 1
        except Exception as e:
            st.error(f"Error adding job title {title}: {e}")
    
    return jobs_added

def add_common_job_variants(high_risk_jobs):
    """
    Add common variants of job titles to improve search functionality.
    """
    engine = get_db_connection()
    if not engine:
        return False
        
    variants_added = 0
    
    # Dictionary of common job title variations
    variations = {
        "Data Entry Keyers": ["Data Entry Clerk", "Data Entry Specialist", "Data Entry Operator"],
        "Bookkeeping, Accounting, and Auditing Clerks": ["Bookkeeper", "Accounting Clerk", "Auditing Clerk"],
        "Executive Secretaries and Executive Administrative Assistants": ["Executive Assistant", "Administrative Assistant", "Executive Secretary"],
        "First-Line Supervisors of Office and Administrative Support Workers": ["Office Manager", "Administrative Supervisor", "Office Supervisor"],
        "Customer Service Representatives": ["Customer Service Agent", "Customer Support Representative", "Customer Care Representative"],
        "Assemblers and Fabricators, All Other": ["Assembly Worker", "Manufacturing Assembler", "Production Assembler"],
        "Inspectors, Testers, Sorters, Samplers, and Weighers": ["Quality Inspector", "Quality Control Technician", "QA Tester"],
        "Cashiers": ["Checkout Clerk", "Retail Cashier", "Sales Cashier"],
        "Sales Representatives, Wholesale and Manufacturing": ["Sales Rep", "Account Representative", "B2B Sales Representative"],
        "Retail Salespersons": ["Retail Sales Associate", "Sales Consultant", "Retail Sales Advisor"],
        "Securities, Commodities, and Financial Services Sales Agents": ["Financial Advisor", "Stockbroker", "Investment Sales Agent"],
        "Management Analysts": ["Business Analyst", "Consultant", "Business Consultant"],
        "Financial Analysts": ["Investment Analyst", "Finance Analyst", "Financial Advisor"]
    }
    
    for job in high_risk_jobs:
        soc_code = job['soc_code']
        title = job['job_title']
        
        # Check if this job has variations defined
        if title in variations:
            for variant in variations[title]:
                # First check if variant already exists
                check_query = text("""
                    SELECT COUNT(*) FROM job_titles 
                    WHERE soc_code = :soc_code AND title = :variant
                """)
                
                try:
                    with engine.connect() as conn:
                        result = conn.execute(check_query, {"soc_code": soc_code, "variant": variant})
                        if result.scalar() == 0:
                            # Safely insert without ON CONFLICT clause
                            insert_query = text("""
                                INSERT INTO job_titles (soc_code, title, is_primary)
                                VALUES (:soc_code, :variant, 0)
                            """)
                            conn.execute(insert_query, {"soc_code": soc_code, "variant": variant})
                            variants_added += 1
                except Exception as e:
                    st.error(f"Error adding job variant {variant}: {e}")
    
    return variants_added

def main():
    st.title("High-Risk Jobs Database Update")
    
    st.write("This tool identifies jobs with significant AI displacement risk (>10% over 5 years) and ensures they are properly added to our database.")
    
    min_risk = st.slider("Minimum Risk Percentage", min_value=10, max_value=90, value=10, step=5)
    
    if st.button("Run Update"):
        with st.spinner("Finding high-risk jobs..."):
            high_risk_jobs = find_high_risk_jobs(min_risk)
            
            if not high_risk_jobs:
                st.error("No jobs found or database connection error.")
                return
                
            st.success(f"Found {len(high_risk_jobs)} jobs with >={min_risk}% AI displacement risk over 5 years.")
            
            # Show the jobs in a table
            st.write("High-Risk Jobs:")
            job_data = [{
                "Job Title": job["job_title"],
                "5-Year Risk %": job["year_5_risk"],
                "Risk Category": job["risk_category"],
                "SOC Code": job["soc_code"]
            } for job in high_risk_jobs]
            
            st.table(job_data)
            
            # Ensure all jobs are in the database
            with st.spinner("Adding missing job titles to database..."):
                jobs_added = ensure_job_titles_exist(high_risk_jobs)
                st.success(f"Added {jobs_added} new job titles to the database.")
            
            # Add common variants
            with st.spinner("Adding common job title variants..."):
                variants_added = add_common_job_variants(high_risk_jobs)
                st.success(f"Added {variants_added} job title variants to improve search.")
            
            st.info("Database update complete! The autocomplete feature will now include all these high-risk jobs.")

if __name__ == "__main__":
    main()