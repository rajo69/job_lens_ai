# app.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
import PyPDF2
import os
import groq
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
from streamlit.web.server.server import Server

# --- NEW: Firebase Admin SDK Imports ---
import firebase_admin
from firebase_admin import credentials, firestore

# --- App Configuration ---
st.set_page_config(page_title="Job Lens AI - Career Co-Pilot", layout="wide")

# --- NEW: Firebase Initialization ---
try:
    firebase_creds = dict(st.secrets.firebase_service_account)
    firebase_creds["private_key"] = firebase_creds["private_key"].replace('\\n', '\n')
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred)
except ValueError:
    pass

db = firestore.client()

# --- All Helper & Scraping Functions (UNCHANGED) ---
@st.cache_data
def parse_time_posted(time_text):
    if not time_text: return None
    num_match = re.search(r'\d+', time_text)
    if not num_match: return None
    num = int(num_match.group(0))
    time_text = time_text.lower()
    if 'second' in time_text or 'minute' in time_text or 'hour' in time_text: return 0
    elif 'day' in time_text: return num * 24
    elif 'week' in time_text: return num * 7 * 24
    elif 'month' in time_text: return num * 30 * 24
    else: return None

@st.cache_data
def parse_num_applicants(applicant_text):
    if not applicant_text: return None
    num_match = re.search(r'\d+', applicant_text)
    if num_match: return int(num_match.group(0))
    else: return None

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages: text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def fetch_job_details(job_id):
    try:
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        job_response = requests.get(job_url, timeout=15)
        job_response.raise_for_status()
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        salary_raw = None
        try:
            insights = job_soup.find_all("li", {"class": "job-details-jobs-unified-top-card__job-insight"})
            for insight in insights:
                if "💰" in insight.get_text():
                    salary_raw = insight.find("span").text.strip()
                    break
        except: pass
        job_post = {
            'job_id': job_id, 'job_link': f"https://www.linkedin.com/jobs/view/{job_id}",
            'job_title': job_soup.find("h2", {"class":"top-card-layout__title"}).text.strip() if job_soup.find("h2", {"class":"top-card-layout__title"}) else "N/A",
            'company_name': job_soup.find("a", {"class": "topcard__org-name-link"}).text.strip() if job_soup.find("a", {"class": "topcard__org-name-link"}) else "N/A",
            'salary': salary_raw,
            'job_desc': job_soup.find("div", {"class": "show-more-less-html__markup"}).get_text(separator="\n").strip() if job_soup.find("div", {"class": "show-more-less-html__markup"}) else "",
            'hours_posted': parse_time_posted(job_soup.find("span", {"class": "posted-time-ago__text"}).text.strip() if job_soup.find("span", {"class": "posted-time-ago__text"}) else None),
            'applicants_count': parse_num_applicants(job_soup.find("span", {"class": "num-applicants__caption"}).text.strip() if job_soup.find("span", {"class": "num-applicants__caption"}) else None)
        }
        return job_post
    except requests.exceptions.RequestException:
        return None

def run_linkedin_scraper(title, location, num_pages):
    # This function remains unchanged, it already uses parallel processing well.
    id_list, start, count = [], 0, 0
    status_text = st.empty()
    progress_bar = st.progress(0, text="Scraping progress")
    status_text.text("Part 1/2: Collecting Job IDs...")
    while count < num_pages:
        list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
        try:
            response = requests.get(list_url, timeout=10)
            response.raise_for_status()
            list_soup = BeautifulSoup(response.text, "html.parser")
            page_jobs = list_soup.find_all("li")
            if not page_jobs: break
            for job in page_jobs:
                job_id = job.find("div", {"class": "base-card"}).get("data-entity-urn", "").split(":")[-1]
                if job_id and job_id not in id_list: id_list.append(job_id)
            count += 1
            start += 25
            status_text.text(f"Part 1/2: Collecting Job IDs... Found {len(id_list)} IDs across {count} page(s).")
            progress_bar.progress(count / num_pages)
            time.sleep(random.uniform(0.5, 1.5))
        except requests.exceptions.RequestException as e:
            st.warning(f"Failed to fetch a job list page. Stopping ID collection. Error: {e}")
            break
    if not id_list: return None
    job_list = []
    total_ids = len(id_list)
    status_text.text(f"Part 2/2: Scraping details for {total_ids} jobs...")
    progress_bar.progress(0)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_id = {executor.submit(fetch_job_details, job_id): job_id for job_id in id_list}
        for i, future in enumerate(as_completed(future_to_id)):
            result = future.result()
            if result: job_list.append(result)
            progress = (i + 1) / total_ids
            status_text.text(f"Part 2/2: Scraping details... Job {i+1}/{total_ids}")
            progress_bar.progress(progress)
    status_text.empty()
    progress_bar.empty()
    return pd.DataFrame(job_list) if job_list else None

def escape_latex(text: str) -> str:
    if not isinstance(text, str): return ""
    return text.replace('\\', r'\textbackslash{}').replace('{', r'\{').replace('}', r'\}').replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('~', r'\textasciitilde{}').replace('^', r'\textasciicircum{}')

def run_deep_analysis(client, job_desc, resume_text):
    # This function remains unchanged, it now returns a status for error handling.
    latex_template = r"""\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{a4paper, total={170mm,257mm}, left=20mm, top=20mm}
\usepackage{enumitem}
\setlist[itemize]{leftmargin=*}
\linespread{1.15}
\begin{document}
%s
\end{document}
"""
    prompt = f"""You are an expert career coach and LaTeX resume formatter... (rest of prompt is unchanged)"""
    last_exception = None
    for attempt in range(2):
        try:
            response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "You are a career coach. Respond with a single, valid JSON object and nothing else."}, {"role": "user", "content": prompt}], temperature=0.4, timeout=90.0)
            analysis_json = json.loads(response.choices[0].message.content)
            resume_content = analysis_json.get('updated_resume_content', 'Error: Content not generated.')
            cover_letter_content = analysis_json.get('cover_letter_content', 'Error: Content not generated.')
            analysis_json['updated_resume_latex'] = latex_template % escape_latex(resume_content)
            analysis_json['cover_letter_latex'] = latex_template % escape_latex(cover_letter_content)
            analysis_json['status'] = 'success'
            return analysis_json
        except Exception as e:
            last_exception = e
            time.sleep(1)
    return {"status": "error", "match_analysis": f"An error occurred during analysis after multiple retries. Details: {str(last_exception)}"}

# --- Credit System & User Functions (UNCHANGED) ---
DEFAULT_CREDIT_LIMIT = 50
def get_user_ip():
    try:
        session_info = Server.get_current()._get_session_info_for_client(None)
        if session_info: return session_info.ws.request.remote_ip
    except Exception: return "local_user"
    return "unknown_user"
def get_user_data(ip):
    user_ref = db.collection('users').document(ip)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict(); user_data.setdefault("credit_limit", DEFAULT_CREDIT_LIMIT); return user_data
    else:
        default_data = {"credits_used": 0, "credit_limit": DEFAULT_CREDIT_LIMIT, "last_seen": datetime.now().isoformat()}
        user_ref.set(default_data); return default_data
@firestore.transactional
def update_user_credits_transactional(transaction, user_ref, credits_to_add):
    snapshot = user_ref.get(transaction=transaction)
    new_credits_used = snapshot.get('credits_used') + credits_to_add
    transaction.update(user_ref, {'credits_used': new_credits_used, 'last_seen': datetime.now().isoformat()})
def update_user_credits(ip, credits_to_add):
    if credits_to_add > 0:
        user_ref = db.collection('users').document(ip); update_user_credits_transactional(db.transaction(), user_ref, credits_to_add)
def get_all_user_data_for_admin():
    docs = db.collection('users').stream()
    return [{'ip': doc.id, **doc.to_dict()} for doc in docs]
def save_admin_credit_changes(edited_df):
    batch = db.batch()
    for _, row in edited_df.iterrows():
        user_ref = db.collection('users').document(row["ip"])
        batch.update(user_ref, {"credits_used": int(row["credits_used"]), "credit_limit": int(row["credit_limit"])})
    batch.commit()

# --- App State Initialization ---
try: api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError): api_key = None
user_ip = get_user_ip()
user_data = get_user_data(user_ip)
credits_left = user_data.get("credit_limit", DEFAULT_CREDIT_LIMIT) - user_data.get("credits_used", 0)

# --- MODIFIED: reset_flow now clears new dynamic analysis keys ---
def reset_flow():
    keys_to_delete = ['scraped_df', 'successful_analyses', 'failed_analyses', 'analysis_running', 'jobs_to_analyze']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

# --- NEW: Helper function to display results to avoid code duplication ---
def display_result_in_container(container, result):
    if result['analysis']['status'] == 'success':
        with container.expander(f"**{result['job_title']}** at {result['company_name']}", expanded=True):
            st.metric("Resume Match Score", f"{result['analysis'].get('resume_match_score', 0)}%")
            st.write("**Match Analysis:**")
            st.write(result['analysis'].get('match_analysis', 'N/A'))
            tab1, tab2 = st.tabs(["Tailored Resume (LaTeX)", "Cover Letter (LaTeX)"])
            with tab1: st.code(result['analysis'].get('updated_resume_latex', 'Error'), language='latex')
            with tab2: st.code(result['analysis'].get('cover_letter_latex', 'Error'), language='latex')
    else: # status == 'error'
        with container.expander(f"⚠️ **{result['job_title']}** at {result['company_name']}", expanded=True):
            st.error(f"**Reason for failure:** {result['analysis'].get('match_analysis', 'Unknown error.')}")

# --- Main App UI ---
st.title("🤖 Job Lens AI - Career Co-Pilot")

# Sidebar remains the same
with st.sidebar:
    st.header("📝 Your Resume")
    st.write("Upload your resume to enable the AI-powered deep analysis features.")
    resume_option = st.radio("Resume Input Method:", ("Paste Text", "Upload File"), key="resume_option", on_change=reset_flow)
    if resume_option == "Paste Text":
        resume_text_input = st.text_area("Paste your resume content here:", height=300, key="resume_paste", on_change=reset_flow)
        if resume_text_input: st.session_state['resume_text'] = resume_text_input
    else:
        uploaded_file = st.file_uploader("Upload Resume", type=['txt', 'pdf'], key="upload", on_change=reset_flow)
        if uploaded_file: st.session_state['resume_text'] = read_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else uploaded_file.getvalue().decode("utf-8")
    
    if 'resume_text' in st.session_state and st.session_state.get('resume_text'):
        st.success("✅ Resume Loaded & Ready for Analysis")
    else:
        st.warning("Resume must be provided to analyze jobs.")
    
    st.markdown("---")
    st.header("⚙️ Credits & Admin")
    st.info(f"**Analysis Credits: {max(0, credits_left)}** / {user_data.get('credit_limit')}")
    st.caption("Initial search is free. Analysis costs 1 credit per job.")
    is_admin = st.query_params.get("admin") == "true"
    if is_admin:
        with st.expander("👑 Admin Panel"):
            user_list = get_all_user_data_for_admin()
            if user_list:
                df = pd.DataFrame(user_list)[['ip', 'credits_used', 'credit_limit', 'last_seen']]
                edited_df = st.data_editor(df, column_config={"ip": st.column_config.TextColumn("User IP", disabled=True), "credits_used": st.column_config.NumberColumn("Credits Used", min_value=0, step=1), "credit_limit": st.column_config.NumberColumn("Credit Limit", min_value=0, step=1), "last_seen": st.column_config.TextColumn("Last Seen", disabled=True)}, num_rows="dynamic", use_container_width=True)
                if st.button("Save Credit Changes"):
                    save_admin_credit_changes(edited_df)
                    st.success("User credits saved to Firestore!"); time.sleep(1); st.rerun()
            else: st.write("No user data found in Firestore.")

# --- MAJOR REFACTOR: This is the new application flow logic ---

# STATE 1: Initial job scraping
if 'scraped_df' not in st.session_state and 'analysis_running' not in st.session_state:
    st.header("Step 1: Find Job Opportunities")
    st.write("Perform a quick, free search to find jobs. You can select which ones to analyze in the next step.")
    with st.form("scrape_form"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1: title_input = st.text_input("Job Title", "Data Scientist")
        with col2: location_input = st.text_input("Location", "USA")
        with col3: pages_to_scrape = st.number_input("# Pages to Scan", 1, 10, 1)
        submitted = st.form_submit_button("Find Jobs", type="primary")

    if submitted:
        df = run_linkedin_scraper(title_input, location_input, pages_to_scrape)
        if df is not None and not df.empty:
            df.insert(0, "Select", False); st.session_state.scraped_df = df; st.rerun()
        else:
            st.error("Scraping did not return any data. Please try different keywords.")

# STATE 2: Job selection for analysis
elif 'scraped_df' in st.session_state:
    st.header("Step 2: Select Jobs for Deep Analysis")
    st.write("Check the box for up to 3 jobs you want to analyze. This will use your credits.")
    
    df = st.session_state['scraped_df']
    edited_df = st.data_editor(df, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn(required=True), "job_id": None}, disabled=df.columns.drop("Select"))
    
    selected_jobs = edited_df[edited_df.Select]
    num_selected = len(selected_jobs)

    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        if num_selected > 3: st.error("Please select a maximum of 3 jobs.")
        elif num_selected > credits_left: st.error(f"You selected {num_selected} jobs, but only have {credits_left} credits.")
        elif not st.session_state.get('resume_text'): st.warning("You must upload your resume in the sidebar before analyzing.")
    
    with col2:
        analyze_button_disabled = (num_selected == 0 or num_selected > 3 or not st.session_state.get('resume_text') or num_selected > credits_left)
        if st.button(f"Analyze {num_selected} Selected Jobs", type="primary", disabled=analyze_button_disabled):
            # NEW: Set up the session state for the live analysis page and rerun
            st.session_state.analysis_running = True
            st.session_state.jobs_to_analyze = selected_jobs.to_dict(orient='records')
            st.session_state.successful_analyses = []
            st.session_state.failed_analyses = []
            del st.session_state['scraped_df'] # Transition away from this page
            st.rerun()

# STATE 3: DYNAMIC ANALYSIS - This is the new "live" results page
elif st.session_state.get('analysis_running'):
    st.header("🔬 Analyzing Jobs...")
    st.write("Results will appear below as they are completed.")
    
    jobs_to_process = st.session_state.jobs_to_analyze
    num_jobs = len(jobs_to_process)
    
    # Create a placeholder for each job
    placeholders = {job['job_id']: st.empty() for job in jobs_to_process}
    for job_id, placeholder in placeholders.items():
        job_title = next((job['job_title'] for job in jobs_to_process if job['job_id'] == job_id), "Unknown Job")
        with placeholder.container():
            st.status(f"Pending analysis for: **{job_title}**", expanded=True)

    client = groq.Groq(api_key=api_key)
    successful_count = 0

    with ThreadPoolExecutor(max_workers=min(num_jobs, 8)) as executor:
        future_to_job = {executor.submit(run_deep_analysis, client, job['job_desc'], st.session_state['resume_text']): job for job in jobs_to_process}
        
        for future in as_completed(future_to_job):
            job_row = future_to_job[future]
            job_id = job_row['job_id']
            placeholder = placeholders[job_id]
            
            try:
                analysis_result = future.result()
                job_row['analysis'] = analysis_result
                
                # Update the specific job's placeholder with the result
                with placeholder.container():
                    display_result_in_container(st, job_row)

                if analysis_result.get('status') == 'success':
                    st.session_state.successful_analyses.append(job_row)
                    successful_count += 1
                else:
                    st.session_state.failed_analyses.append(job_row)
            except Exception as exc:
                job_row['analysis'] = {"status": "error", "match_analysis": f"Critical error: {exc}"}
                with placeholder.container():
                    display_result_in_container(st, job_row)
                st.session_state.failed_analyses.append(job_row)

    # All jobs are finished, finalize the process
    st.header("✅ Analysis Complete")
    st.info(f"{successful_count} of {num_jobs} jobs analyzed successfully.")
    if successful_count > 0:
        update_user_credits(user_ip, successful_count)
        st.success(f"Your credits have been updated.")
    
    # Clean up the 'running' state
    st.session_state.analysis_running = False
    st.button("Start New Search", on_click=reset_flow)

# STATE 4: Static results page (if user reloads or comes back)
else:
    st.header("✅ Analysis Results")
    successful_results = st.session_state.get('successful_analyses', [])
    failed_results = st.session_state.get('failed_analyses', [])
    
    if successful_results:
        st.info(f"{len(successful_results)} jobs were analyzed successfully.")
        for result in successful_results:
            display_result_in_container(st, result)
            
    if failed_results:
        st.warning(f"{len(failed_results)} jobs could not be analyzed.")
        for result in failed_results:
            display_result_in_container(st, result)

    st.button("Start New Search", on_click=reset_flow)