Of course. Here is the complete, raw Markdown code for the `README.md` file. You can copy and paste this directly into a file named `README.md` in your project's root directory.

```markdown
# Job Lens AI - Career Co-Pilot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

Job Lens AI is an end-to-end, AI-driven web application designed to help users analyze their job market fit and automate interview preparation. The tool scrapes real-time job postings, performs a deep resume-to-job-description comparison using large language models, and provides users with a comprehensive analysis package including a match score, tailored resume content, and a custom-generated cover letter.

**[➡️ View the Live Application Here](http://your-live-app-link.com)** *(Replace with your actual deployment link)*

## ✨ Key Features

*   **🌐 Real-Time Job Scraping**: Fetches live job postings directly from LinkedIn using a keyword and location search.
*   **🧠 Intelligent Resume Analysis**: Leverages the Groq API (running Llama 3.1) to perform a deep semantic comparison between a user's resume and a job description.
*   **📊 Comprehensive Feedback**: Delivers a detailed analysis including:
    *   A **resume match percentage** and ATS score.
    *   A rewritten, **tailored resume** with bullet points optimized for the target job.
    *   A professionally crafted **cover letter**.
*   **⚡ Scalable & Performant Backend**: Implements multithreading for parallel API requests to both LinkedIn and the Groq API, minimizing user latency during scraping and analysis.
*   **☁️ Secure Cloud Integration**: Utilizes Google Firebase (Firestore) to manage a user credit system and persist user data in a secure, scalable cloud environment.
*   **👤 Frictionless User Onboarding**: Employs IP-based authentication to manage user sessions and credits without requiring a traditional login, reducing user friction.
*   **👑 Admin Dashboard**: A protected admin panel allows for monitoring user activity and managing credit allocations directly from the UI.

## ⚙️ Tech Stack

| Category         | Technology / Library                                                              |
| ---------------- | --------------------------------------------------------------------------------- |
| **Frontend**     | Streamlit                                                                         |
| **Backend / AI** | Python, Groq API (Llama 3.1), Langchain (Concept), `concurrent.futures` (Multithreading) |
| **Data Scraping**| Requests, BeautifulSoup4                                                          |
| **Database**     | Google Cloud Firestore                                                            |
| **Languages**    | Python, SQL (used by Firebase), LaTeX (for document generation)                   |
| **Deployment**   | Streamlit Community Cloud (or any platform supporting Python apps)                |

## 🚀 How It Works

The application operates in a simple, multi-step flow designed for an intuitive user experience.

1.  **Find Jobs**: The user enters a job title and location. The application scrapes LinkedIn for relevant job postings and displays them in a clean, interactive table.
2.  **Upload Resume & Select**: The user uploads their resume (PDF or TXT) or pastes the content directly. They then select up to 3 jobs from the scraped list for analysis.
3.  **Run AI Analysis**: The app sends the resume and each selected job description to the Groq API. The backend processes these requests in parallel. The UI updates in real-time, showing the status of each job analysis as it completes.
4.  **Review & Download**: Completed analyses are displayed with the match score, tailored advice, and the generated LaTeX code for the updated resume and cover letter.

## 🛠️ Setup and Local Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

*   Python 3.9+
*   Git

### 2. Clone the Repository

```bash
git clone https://github.com/rajo69/ai-career-navigator.git
cd ai-career-navigator
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

You will need a `requirements.txt` file. Create one with the following content:
```txt
streamlit
requests
beautifulsoup4
PyPDF2
pandas
groq
firebase-admin
```
Then, install the libraries:
```bash
pip install -r requirements.txt
```

### 5. Configure Secrets

This application requires API keys for Groq and a service account for Google Firebase. Streamlit's built-in secrets management is used to handle these securely.

Create a file at `/.streamlit/secrets.toml` and paste the following content, replacing the placeholder values with your actual credentials.

```toml
# /.streamlit/secrets.toml

# Groq Cloud API Key
GROQ_API_KEY = "gsk_YourGroqApiKeyHere"

# Firebase Service Account Credentials
# Get this from your Firebase project settings > Service accounts > Generate new private key
[firebase_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----\nYourPrivateKeyHere\n-----END PRIVATE KEY-----\n"""
client_email = "your-client-email@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email.iam.gserviceaccount.com"
```

**Note:** When pasting the `private_key` from your Firebase JSON file, ensure it is enclosed in triple quotes and that newline characters (`\n`) are preserved, as shown in the template.

### 6. Run the Application

Once the dependencies are installed and secrets are configured, run the Streamlit app from your terminal:

```bash
streamlit run app.py
```

The application should now be running and accessible at `http://localhost:8501`.

## 📂 Project Structure

```
.
├── .streamlit/
│   └── secrets.toml      # <-- IMPORTANT: Store API keys and credentials here
├── app.py                # Main Streamlit application logic
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

## 📈 Future Improvements

*   **Expanded Job Board Support**: Integrate scrapers for other popular job boards like Indeed, Glassdoor, and Otta.
*   **Advanced User Accounts**: Move from IP-based sessions to a full-fledged authentication system (e.g., OAuth with Google/LinkedIn) to allow users to save their analysis history.
*   **Interactive Dashboard**: Add a dashboard for users to track their application progress and view analytics on their job search.
*   **Direct PDF/DOCX Generation**: Convert the generated LaTeX into downloadable PDF or DOCX files directly within the app.

## 📄 License

This project is licensed under the MIT License.

---

**Built by Rajarshi Nandi**

*   [LinkedIn](https://linkedin.com/in/rajarshi-nandi)
*   [GitHub](https://github.com/rajo69)

```
