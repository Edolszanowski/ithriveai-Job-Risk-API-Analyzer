"""
Job Title Autocomplete Demo
This script demonstrates the job title autocomplete functionality.
"""

import streamlit as st
from job_title_autocomplete import job_title_autocomplete, load_job_titles_from_db

st.title("Job Title Autocomplete Demo")

st.markdown("""
This demo shows how the job title autocomplete functionality works.
Type in the search box below to see matching job titles.
""")

# Get all job titles for display
job_titles = load_job_titles_from_db()

# Display stats about available job titles
st.subheader("Job Title Database Stats")
st.write(f"Total job titles available: {len(job_titles)}")

primary_titles = [job for job in job_titles if job.get("is_primary")]
st.write(f"Primary BLS job titles: {len(primary_titles)}")
st.write(f"Alternative job titles: {len(job_titles) - len(primary_titles)}")

# Show the autocomplete in action
st.subheader("Try the Autocomplete")

# Create the autocomplete input
selected_job = job_title_autocomplete(
    label="Enter a job title",
    key="demo_autocomplete",
    placeholder="Start typing a job title...",
    help="Type a job title to see matching suggestions"
)

# Show the selected job
if selected_job:
    st.write(f"You selected: **{selected_job}**")
    
    # Find the corresponding job data
    matching_job = next((job for job in job_titles if job["title"].lower() == selected_job.lower()), None)
    
    if matching_job:
        st.write(f"SOC Code: {matching_job['soc_code']}")
        st.write(f"Is primary BLS title: {'Yes' if matching_job.get('is_primary') else 'No'}")
    else:
        st.write("This job title doesn't exist in our database yet.")

# Show sample job titles
st.subheader("Sample Available Job Titles")
sample_size = min(20, len(job_titles))
sample_jobs = job_titles[:sample_size]

st.write("Here are some sample job titles available in the autocomplete:")
for job in sample_jobs:
    primary_indicator = "✓" if job.get("is_primary") else ""
    st.write(f"{job['title']} {primary_indicator} ({job['soc_code']})")