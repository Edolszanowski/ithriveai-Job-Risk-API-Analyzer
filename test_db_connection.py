import streamlit as st
import os
from sqlalchemy import create_engine, text
import pandas as pd

st.title("Database Connection Test")

# Get the DATABASE_URL from environment variables or secrets
database_url = st.secrets.get("DATABASE_URL") if hasattr(st, "secrets") else os.environ.get("DATABASE_URL")

if not database_url:
    st.error("No DATABASE_URL found in environment or secrets")
else:
    # Mask the password for display
    masked_url = database_url.replace("://postgres:", "://postgres:****@") if "://postgres:" in database_url else database_url
    st.info(f"Testing connection to: {masked_url}")
    
    try:
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            st.success("✅ Successfully connected to database!")
            
            # Check if job_searches table exists
            try:
                result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'job_searches')"))
                table_exists = result.scalar()
                
                if table_exists:
                    st.success("✅ Found 'job_searches' table")
                    
                    # Get count of records
                    count_query = text("SELECT COUNT(*) FROM job_searches")
                    count_result = connection.execute(count_query)
                    count = count_result.scalar()
                    
                    st.write(f"Total job searches in database: {count}")
                    
                    # Get recent records
                    query = text("SELECT job_title, timestamp, year_1_risk, year_5_risk FROM job_searches ORDER BY timestamp DESC LIMIT 5")
                    result = connection.execute(query)
                    recent_searches = [dict(row) for row in result]
                    
                    if recent_searches:
                        st.write("Recent job searches:")
                        st.dataframe(pd.DataFrame(recent_searches))
                    else:
                        st.info("No job searches found in the database yet")
                else:
                    st.warning("⚠️ 'job_searches' table does not exist yet")
                    st.info("The table will be created when you perform your first search")
                    
                    # Create the table
                    st.write("Would you like to create the table now?")
                    if st.button("Create job_searches table"):
                        create_table_sql = """
                        CREATE TABLE IF NOT EXISTS job_searches (
                            id SERIAL PRIMARY KEY,
                            job_title VARCHAR(255) NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            year_1_risk FLOAT,
                            year_5_risk FLOAT,
                            risk_category VARCHAR(50),
                            job_category VARCHAR(50)
                        );
                        """
                        connection.execute(text(create_table_sql))
                        st.success("Table created successfully!")
            except Exception as e:
                st.error(f"Error checking tables: {str(e)}")
                
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        st.info("Make sure your DATABASE_URL is correctly formatted and the database is accessible")

st.markdown("---")
st.info("This is a test page to verify your database connection. You can safely add this to your GitHub repository.")