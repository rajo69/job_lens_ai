# Job Lens AI - Career Co-Pilot

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

Job Lens AI is an end-to-end, AI-driven web application designed to help users analyze their job market fit and automate interview preparation. The tool scrapes real-time job postings, performs a deep resume-to-job-description comparison using large language models, and provides users with a comprehensive analysis package including a match score, tailored resume content, and a custom-generated cover letter.

**[➡️ View the Live Application Here]([http://your-live-app-link.com](https://joblensai-1.streamlit.app/))** *(Replace with your actual deployment link)*

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
