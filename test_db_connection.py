import streamlit as st
import psycopg2
import os

st.set_page_config(layout="wide")
st.title("Supabase Connection Test")

# Try to get the DATABASE_URL from Streamlit secrets
DATABASE_URL = None
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
    st.info("DATABASE_URL found in Streamlit secrets.")
except KeyError:
    st.error("DATABASE_URL not found in Streamlit secrets!")
    st.stop()
except Exception as e:
    st.error(f"Error accessing Streamlit secrets: {e}")
    st.stop()

if DATABASE_URL:
    # Mask the password for display
    try:
        # A bit of a hacky way to mask password for display
        # Assumes format postgresql://username:password@host:port/database
        parts = DATABASE_URL.split('@')
        creds_part = parts[0].split(':')
        masked_url = f"{creds_part[0]}:{creds_part[1]}//********@{parts[1]}"
        st.write(f"Attempting to connect with URL (password masked): {masked_url}")
    except Exception:
        st.write("Attempting to connect with the configured DATABASE_URL (unable to parse for masking).")


    conn = None
    try:
        st.write("Attempting to connect to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        st.success("Successfully connected to Supabase!")

        cur = conn.cursor()
        
        st.subheader("Checking 'job_searches' table:")
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'job_searches');")
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            st.success("'job_searches' table exists.")
            cur.execute("SELECT * FROM job_searches ORDER BY timestamp DESC LIMIT 5;")
            rows = cur.fetchall()
            st.write(f"Found {len(rows)} recent records in 'job_searches':")
            for row in rows:
                st.write(row)
        else:
            st.warning("'job_searches' table does NOT exist.")
            st.write("Consider running your setup_db.py script or creating it manually in Supabase.")

        cur.close()

    except psycopg2.OperationalError as e:
        st.error(f"OperationalError: Failed to connect to Supabase.")
        st.error(f"Details: {e}")
        st.error("Troubleshooting steps:")
        st.error("1. Double-check your DATABASE_URL in Streamlit secrets. Ensure host, port (try 6543), username, password, and db name are correct.")
        st.error("2. Check Supabase project status and ensure the database is running.")
        st.error("3. Check Supabase network restrictions (Project Settings -> Database -> Network Restrictions). For testing, you might temporarily allow all IPs if it's restricted.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            st.info("Database connection closed.")
else:
    st.error("DATABASE_URL is not set. Cannot perform connection test.")
