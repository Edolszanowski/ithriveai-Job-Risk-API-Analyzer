import streamlit as st
import psycopg2
from urllib.parse import urlparse, urlunparse # For cleaner password masking

st.set_page_config(layout="wide")
st.title("Supabase Connection Test (Basic)")

DATABASE_URL = None
st.subheader("Secrets Retrieval:")
try:
    DATABASE_URL = st.secrets["DATABASE_URL"]
    st.info("✅ DATABASE_URL found in Streamlit secrets.")

    # Mask password for display
    try:
        parsed_url = urlparse(DATABASE_URL)
        display_netloc = parsed_url.netloc
        if parsed_url.password:
            display_netloc = display_netloc.replace(parsed_url.password, "********")
        
        masked_url_for_display = urlunparse(
            (parsed_url.scheme,
             display_netloc,
             parsed_url.path,
             parsed_url.params,
             parsed_url.query,
             parsed_url.fragment)
        )
        st.write(f"Attempting to connect with (password masked): {masked_url_for_display}")
    except Exception as parse_mask_e:
        st.warning(f"Could not parse/mask DATABASE_URL for display: {parse_mask_e}. Will proceed with raw secret if available.")
        st.write("DATABASE_URL value (from secrets) will be used directly for connection.")

except KeyError:
    st.error("❌ DATABASE_URL not found in Streamlit secrets! Please ensure it is set correctly in your Streamlit Cloud app settings.")
    st.stop() # Stop execution if secret is missing
except Exception as e:
    st.error(f"❌ Error accessing Streamlit secrets: {e}")
    st.stop() # Stop execution

if DATABASE_URL:
    conn = None
    st.subheader("Database Connection Attempt:")
    try:
        st.write(f"Attempting to connect to Supabase using port {urlparse(DATABASE_URL).port or 'default'}...")
        conn = psycopg2.connect(DATABASE_URL)
        st.success("✅ Successfully connected to Supabase!")

        cur = conn.cursor()
        
        st.write("Executing a simple query (SELECT version())...")
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        if db_version:
            st.info(f"Database version: {db_version[0]}")
        else:
            st.warning("Could not retrieve database version.")

        st.write("Checking for 'job_searches' table (if applicable)...")
        # Adjust schema if your table is not in 'public'
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'job_searches');")
        table_exists_row = cur.fetchone()
        if table_exists_row and table_exists_row[0]:
            st.success("✅ 'job_searches' table exists in the 'public' schema.")
        else:
            st.warning("⚠️ 'job_searches' table does NOT exist in the 'public' schema (or query failed).")

        cur.close()

    except psycopg2.OperationalError as e:
        st.error("❌ OperationalError: Failed to connect to Supabase.")
        st.error(f"Details: {e}")
        st.error("Troubleshooting for 'Cannot assign requested address' (often with IPv6):")
        st.error("1. This likely indicates an issue with the Streamlit Cloud environment's ability to make outgoing IPv6 connections to your specific Supabase host.")
        st.error("2. Confirm your Supabase host is primarily/only resolving to IPv6 (e.g., via local `nslookup`). Your previous test showed this.")
        st.error("3. Ensure your Supabase Project's Network Restrictions are fully open (e.g., 'Allow all IP addresses' or 0.0.0.0/0).")
        st.error("4. Contact Streamlit Support/Community with these findings, including the error message and that your host is IPv6.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            st.info("Database connection closed.")
else:
    # This part should ideally not be reached if st.stop() was called earlier due to missing secret
    st.error("Critical error: DATABASE_URL was not available after secret retrieval block.")
