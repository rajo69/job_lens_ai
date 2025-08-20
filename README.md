# Job Lens AI — Career Co-Pilot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-app-%23FF4B4B.svg)
![Groq LLM](https://img.shields.io/badge/LLM-Groq%20(Llama%203.1)-purple.svg)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Job Lens AI** is an end-to-end, AI-driven web app that analyzes a candidate’s job-market fit and automates interview prep. It scrapes real job postings, performs deep resume↔JD comparison with LLMs, and returns a match score, tailored resume content (LaTeX-ready), and a custom cover letter. A credit system backed by Firebase enables simple usage limits and an admin dashboard for monitoring.

**👉 Live Demo:** **[Job Lens AI (Streamlit)](https://joblensai-1.streamlit.app/)**

---

## Table of Contents

- [Features](#features)
- [Skills & Keywords](#skills--keywords)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Clone & Install](#clone--install)
  - [Secrets & Environment](#secrets--environment)
  - [Run Locally](#run-locally)
- [Usage](#usage)
  - [User Flow](#user-flow)
  - [Admin Dashboard](#admin-dashboard)
- [Data Model & Credits](#data-model--credits)
- [Security & Privacy](#security--privacy)
- [Performance & Scalability](#performance--scalability)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [What to Highlight on Your Resume](#what-to-highlight-on-your-resume)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **🌐 Real-Time Job Scraping**
  - Pulls live postings from LinkedIn’s guest endpoints using keyword + location.
  - Extracts job metadata (title, company, salary when available, applicants, freshness).

- **🧠 Intelligent Resume Analysis (LLM)**
  - Groq API (Llama 3.1) computes semantic alignment between resume and JD.
  - Returns: **match score**, **ATS-style feedback**, **tailored resume content**, **custom cover letter**.
  - Outputs also returned as **LaTeX** snippets for clean PDF export.

- **⚡ Parallelized Backend**
  - Multithreaded scraping and inference with `ThreadPoolExecutor` for responsive UX.

- **☁️ Credit System & Persistence**
  - **Firebase Firestore** stores per-IP credits and activity.
  - **IP-based auth** avoids login friction for a low-barrier demo.

- **👑 Admin Dashboard**
  - Query param–gated panel (`?admin=true`) to monitor users and edit credit limits.

- **🧰 Streamlit UI/UX**
  - Real-time progress, status cards, expandable results, and code tabs for LaTeX output.

> **Legal note:** Scraping third-party sites may be subject to rate limits and Terms of Service. Use responsibly.

---

## Skills & Keywords

Web scraping • BeautifulSoup4 • Requests • Multithreading (ThreadPoolExecutor) • Streamlit • Groq API (Llama 3.1) • LLM prompting • JSON parsing • Caching • Error handling • Firebase Firestore • LaTeX • Data extraction • Parallel I/O

---

## Architecture

<img width="1536" height="1024" alt="Architecture" src="https://github.com/user-attachments/assets/5bbab0f0-fc5f-4516-abd7-06a320e38717" />

**Key flows**
1. User searches jobs → Streamlit scrapes LinkedIn guest pages.
2. User uploads/pastes resume → selects up to 3 jobs.
3. App dispatches parallel LLM calls to Groq.
4. Results render incrementally (match score, analysis, LaTeX resume/cover letter).
5. Credits are deducted and persisted in Firestore.

---

## Tech Stack

| Category           | Technology / Library |
|--------------------|----------------------|
| **Frontend**       | Streamlit            |
| **Backend / AI**   | Python, Groq API (Llama 3.1), `concurrent.futures` |
| **Scraping**       | `requests`, `beautifulsoup4` |
| **Persistence**    | Google Firebase (Firestore) |
| **Docs / Output**  | LaTeX (resume/cover letter export) |
| **Deployment**     | Streamlit Community Cloud (or any Python host) |

> Planned/Optional: LangChain for prompt/IO orchestration and tool abstractions.

---

## Getting Started

### Prerequisites
- Python **3.9+**
- Git
- Firebase project + **service account** credentials (JSON)
- Groq API key

### Clone & Install

```bash
git clone https://github.com/rajo69/ai-career-navigator.git
cd ai-career-navigator
python -m venv .venv && source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Secrets & Environment

This app expects **Streamlit secrets** for both Groq and Firebase.

Create **`.streamlit/secrets.toml`** at the project root:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"

[firebase_service_account]
type = "service_account"
project_id = "your-firebase-project-id"
private_key_id = "..."
# Note the escaped newlines:
private_key = "-----BEGIN PRIVATE KEY-----\nABC...XYZ=\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxx@your-firebase-project-id.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> The app reads `st.secrets["GROQ_API_KEY"]` and `st.secrets.firebase_service_account`.  
> In the code, the Firebase private key’s `\n` are normalized automatically.

### Run Locally

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

---

## Usage

### User Flow

1. **Find Jobs**  
   Enter a **Job Title** and **Location**, pick the number of pages to scan, and click **Find Jobs**.  
   Results show in an editable table with a **Select** checkbox.

2. **Upload Resume**  
   In the sidebar, **Paste Text** or **Upload PDF/TXT**. You’ll see a “✅ Resume Loaded” confirmation.

3. **Select & Analyze**  
   Choose up to **3** jobs (1 credit/job). Click **Analyze Selected Jobs**.  
   Each job’s analysis renders incrementally with:
   - **Resume match score** (metric)
   - **Match analysis** (ATS-style feedback)
   - **LaTeX tabs** for tailored resume and cover letter

4. **Review & Export**  
   Copy the LaTeX output into your resume/cover letter template to produce polished PDFs.

> **Note:** Initial search is free. Analyses consume credits.

### Admin Dashboard

Append `?admin=true` to the app URL to open the admin panel:

```
https://<your-app-url>/?admin=true
```

From there you can view/update:
- `credits_used`
- `credit_limit`
- `last_seen`

Click **Save Credit Changes** to persist in Firestore.

---

## Data Model & Credits

**Collection:** `users`  
**Document ID:** user IP address (via `Server.get_current()` in Streamlit)

**Fields**
- `credits_used` (**int**) — total analyses consumed
- `credit_limit` (**int**) — default **50** (configurable)
- `last_seen` (**ISO timestamp**)

**Credit Rules**
- **0** credits for job search (scraping only)
- **+1** credit per successfully analyzed job
- Credits update at the end of an analysis batch

---

## Security & Privacy

- **Authentication:** IP-based sessioning to remove login friction for demo purposes.  
  For production, consider OAuth (e.g., Google Sign-In) or email/password auth.

- **Secrets:** Keep all API keys in **Streamlit secrets** (never commit keys to git).

- **Data Stored:** Only minimal user meta in Firestore (IP as doc ID, credits, timestamps).  
  Resume text is processed in-memory for analysis; do not store PII unless you explicitly add that.

- **Scraping:** Respect robots.txt and site Terms of Service. Add backoffs, rate limits, and rotating headers/UA if extending scraping.

---

## Performance & Scalability

- **Parallelism:** Uses `ThreadPoolExecutor` for both job detail scraping and LLM analyses.  
- **Caching:** Streamlit `@st.cache_data` caches pure functions (e.g., parsing helpers) to save redundant work.
- **Latency:** Groq API calls run concurrently; UI updates progressively so users see results as they finish.
- **Throughput:** Increase `max_workers` carefully. Add retries and backoff for network reliability.  
- **State Isolation:** Streamlit `session_state` gates the 4 UI states (search → select → live analysis → results).

---

## Troubleshooting

- **No jobs returned:** Try fewer pages, broader keywords, or a different location. Scraping endpoints sometimes change.
- **PDF parsing failed:** Ensure the PDF has embedded text (not just images). Try uploading a TXT version.
- **Credits not updating:** Confirm Firestore rules allow read/write; check service account permissions.
- **Admin panel hidden:** Make sure the URL includes `?admin=true` exactly (lowercase).

---

## Roadmap

- Replace IP-based sessions with OAuth (Google Sign-In) and per-user history.
- Add **export to PDF** from LaTeX directly in-app.
- Integrate **LangChain** for prompt templates & structured output parsing.
- Expand sources beyond LinkedIn (e.g., Indeed, Greenhouse).
- Add **vector similarity** pre-screen (e.g., sentence-transformers) before LLM calls to reduce cost/latency.
- Implement **rate limiting** and retry/backoff policies for scraping.
- Containerize with Docker and add CI checks (ruff/black, mypy).

---

## What to Highlight on Your Resume

- Built an **end-to-end AI application** that ingests real job postings, performs **LLM-based resume matching**, and generates **LaTeX-ready** tailored resumes and cover letters.
- Designed a **parallelized pipeline** using Python `concurrent.futures` to reduce scraping and inference latency.
- Implemented a **serverless credit system** on **Firebase Firestore** with an **admin dashboard** for monitoring and quota management.
- Deployed a **responsive Streamlit UI** with progressive updates and robust error handling for production-like UX.

---

## Contributing

Contributions and feature requests are welcome!  
Open an issue to discuss major changes before submitting a PR.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

### Repo Pointers

- **Main app:** `app.py`  
- **Dependencies:** `requirements.txt`
