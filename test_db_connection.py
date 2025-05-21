import streamlit as st
import psycopg2
import os # Not strictly needed now
import socket # Import socket module
from urllib.parse import urlparse, urlunparse # To manipulate the URL

st.set_page_config(layout="wide")
st.title("Supabase Connection Test")

# ... (your TEST_MESSAGE secret test if you still have it) ...

st.subheader("DATABASE_URL Test:")
DATABASE_URL_FROM_SECRETS = None
try:
    DATABASE_URL_FROM_SECRETS = st.secrets["DATABASE_URL"]
    st.info("✅ DATABASE_URL found in Streamlit secrets.")
except KeyError:
    st.error("❌ DATABASE_URL not found in Streamlit secrets! Please ensure it is set correctly.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error accessing Streamlit secrets: {e}")
    st.stop()

if DATABASE_URL_FROM_SECRETS:
    effective_db_url = DATABASE_URL_FROM_SECRETS
    try:
        st.write(f"Original DATABASE_URL from secrets: {DATABASE_URL_FROM_SECRETS}")
        parsed_url = urlparse(DATABASE_URL_FROM_SECRETS)
        hostname = parsed_url.hostname

        if hostname:
            st.write(f"Attempting to resolve hostname '{hostname}' to IPv4...")
            try:
                # Get IPv4 address info for the hostname
                # AF_INET specifies IPv4
                addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
                ipv4_address = addr_info[0][4][0] # Extract the IPv4 string
                st.success(f"Resolved '{hostname}' to IPv4: {ipv4_address}")

                # Reconstruct the URL with the IPv4 address
                # This replaces the hostname in the netloc part of the URL
                new_netloc = f"{parsed_url.username}:{parsed_url.password}@{ipv4_address}:{parsed_url.port}"
                if not parsed_url.username and not parsed_url.password: # Handle case with no user/pass in URL (unlikely for DB)
                     new_netloc = f"{ipv4_address}:{parsed_url.port}"
                elif not parsed_url.password: # Handle case with username but no pass
                     new_netloc = f"{parsed_url.username}@{ipv4_address}:{parsed_url.port}"


                modified_url_parts = list(parsed_url)
                modified_url_parts[1] = new_netloc # Index 1 is netloc
                effective_db_url = urlunparse(modified_url_parts)
                st.write(f"Attempting to connect with IPv4-resolved URL: {effective_db_url.replace(parsed_url.password, '********') if parsed_url.password else effective_db_url}")

            except socket.gaierror as e:
                st.warning(f"Could not resolve hostname '{hostname}' to IPv4: {e}. Will proceed with original URL.")
            except Exception as e:
                st.warning(f"Error during IPv4 resolution or URL reconstruction: {e}. Will proceed with original URL.")
        else:
            st.warning("Could not parse hostname from DATABASE_URL. Proceeding with original URL.")

    except Exception as e:
        st.warning(f"Could not parse DATABASE_URL for IPv4 resolution: {e}. Proceeding with original URL.")


    # Mask the password for display (using the potentially modified URL)
    try:
        # A bit of a hacky way to mask password for display
        _parsed_display_url = urlparse(effective_db_url)
        _display_netloc = _parsed_display_url.netloc
        if _parsed_display_url.password:
            _display_netloc = _display_netloc.replace(_parsed_display_url.password, "********")

        masked_url_for_display = urlunparse(
            (_parsed_display_url.scheme,
             _display_netloc,
             _parsed_display_url.path,
             _parsed_display_url.params,
             _parsed_display_url.query,
             _parsed_display_url.fragment)
        )
        st.write(f"Final URL for connection (password masked): {masked_url_for_display}")
    except Exception:
        st.write("Attempting to connect with the configured DATABASE_URL (unable to parse for masking).")


    conn = None
    try:
        st.write("Attempting to connect to Supabase...")
        conn = psycopg2.connect(effective_db_url) # Use the potentially IPv4-resolved URL
        st.success("✅ Successfully connected to Supabase!")
        # ... (rest of your connection test logic: check table, fetch rows etc.) ...
        cur = conn.cursor()
        st.subheader("Checking 'job_searches' table:")
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'job_searches');")
        table_exists_row = cur.fetchone()
        if table_exists_row and table_exists_row[0]:
            st.success("✅ 'job_searches' table exists.")
            # ... (your code to fetch and display rows) ...
        else:
            st.warning("⚠️ 'job_searches' table does NOT exist in the 'public' schema.")
        cur.close()

    except psycopg2.OperationalError as e:
        st.error(f"❌ OperationalError: Failed to connect to Supabase.")
        st.error(f"Details: {e}")
        # ... (your troubleshooting steps) ...
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            st.info("Database connection closed.")
else:
    st.error("DATABASE_URL is not set. Cannot perform connection test.")
