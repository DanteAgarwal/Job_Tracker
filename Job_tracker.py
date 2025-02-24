import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Database setup
conn = sqlite3.connect("job_tracker.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_applied TEXT,
                company_name TEXT,
                job_title TEXT,
                location TEXT,
                job_link TEXT,
                status TEXT,
                follow_up_date TEXT,
                interview_date TEXT,
                recruiter_contact TEXT,
                networking_contact TEXT,
                notes TEXT,
                priority TEXT)''')
conn.commit()

# Streamlit UI
st.title("📊 Job Application Tracker")

# Sidebar Navigation
menu = ["Add Job Application", "View & Update Applications", "Analytics Dashboard"]
choice = st.sidebar.selectbox("Select Option", menu)

if choice == "Add Job Application":
    st.subheader("➕ Add New Job Application")
    with st.form("job_form"):
        date_applied = st.date_input("Date Applied", datetime.today())
        company_name = st.text_input("Company Name")
        job_title = st.text_input("Job Title")
        location = st.text_input("Location")
        job_link = st.text_input("Job Posting Link")
        status = st.selectbox("Application Status", ["Applied", "Interview Scheduled", "Offer Received", "Rejected", "Ghosted"])
        follow_up_date = st.date_input("Follow-up Date", datetime.today() + timedelta(days=7))
        interview_date = st.date_input("Interview Date", None)
        recruiter_contact = st.text_input("Recruiter Contact")
        networking_contact = st.text_input("Networking Contact")
        notes = st.text_area("Notes")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submit_button = st.form_submit_button("Save Application")

        if submit_button:
            c.execute("INSERT INTO jobs (date_applied, company_name, job_title, location, job_link, status, follow_up_date, interview_date, recruiter_contact, networking_contact, notes, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (date_applied, company_name, job_title, location, job_link, status, follow_up_date, interview_date, recruiter_contact, networking_contact, notes, priority))
            conn.commit()
            st.success(f"Job application for {job_title} at {company_name} added successfully!")

elif choice == "View & Update Applications":
    st.subheader("📂 View & Manage Applications")
    df = pd.read_sql("SELECT * FROM jobs", conn)
    if not df.empty:
        st.dataframe(df)

        # Update and Delete Functionality
        st.subheader("Update or Delete Application")
        application_id = st.number_input("Enter Application ID to Update/Delete", min_value=1)
        if st.button("Load Application"):
            application = pd.read_sql(f"SELECT * FROM jobs WHERE id = {application_id}", conn)
            if not application.empty:
                st.write(application)
                with st.form("update_form"):
                    new_status = st.selectbox("Update Status", ["Applied", "Interview Scheduled", "Offer Received", "Rejected", "Ghosted"], index=["Applied", "Interview Scheduled", "Offer Received", "Rejected", "Ghosted"].index(application['status'][0]))
                    new_follow_up_date = st.date_input("Update Follow-up Date", datetime.strptime(application['follow_up_date'][0], '%Y-%m-%d'))
                    new_interview_date = st.date_input("Update Interview Date", datetime.strptime(application['interview_date'][0], '%Y-%m-%d') if application['interview_date'][0] else None)
                    new_notes = st.text_area("Update Notes", application['notes'][0])
                    update_button = st.form_submit_button("Update Application")
                    delete_button = st.form_submit_button("Delete Application")

                    if update_button:
                        c.execute("UPDATE jobs SET status = ?, follow_up_date = ?, interview_date = ?, notes = ? WHERE id = ?",
                                  (new_status, new_follow_up_date, new_interview_date, new_notes, application_id))
                        conn.commit()
                        st.success("Application updated successfully!")

                    if delete_button:
                        c.execute("DELETE FROM jobs WHERE id = ?", (application_id,))
                        conn.commit()
                        st.success("Application deleted successfully!")
            else:
                st.warning("No application found with the given ID.")
    else:
        st.warning("No applications found. Start adding now!")

elif choice == "Analytics Dashboard":
    st.subheader("📊 Job Application Insights")
    df = pd.read_sql("SELECT * FROM jobs", conn)
    if not df.empty:
        st.write(f"Total Applications: {len(df)}")
        st.write(f"Interviews Scheduled: {len(df[df['status'] == 'Interview Scheduled'])}")
        st.write(f"Offers Received: {len(df[df['status'] == 'Offer Received'])}")
    else:
        st.warning("No applications yet! Add some to see insights.")
