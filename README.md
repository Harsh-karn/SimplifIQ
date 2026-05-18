<div align="center">
  <h1>SimplifIQ - AI Lead Intake Automation</h1>
  <p>A completely automated, serverless prototype that transforms simple lead captures into highly personalized, AI-driven strategy audits delivered instantly via email.</p>
  <a href="https://simplifiq.vercel.app/" target="_blank"><strong>🚀 View Live Demo on Vercel</strong></a>
  <br/><br/>
</div>

## 📌 Project Overview
Many businesses rely on lead intake forms, but follow-up processes are often highly manual. This project is a functional, end-to-end prototype designed to fully automate the top-of-funnel workflow. 

When a prospect submits their company details, this system instantly:
1. **Captures** and validates the lead data.
2. **Enriches** the data by intelligently scraping the provided website.
3. **Analyzes** the content using Google's Gemini LLM (acting as an expert Growth Consultant) to extract precise business insights.
4. **Generates** a beautifully formatted, customized PDF Strategic Audit.
5. **Delivers** the audit directly to the prospect's inbox via email.
6. **Archives (Bonus)** the lead data to Google Sheets and the PDF to Google Drive.

## 🏗 System Architecture & Tech Stack
Built for speed, maintainability, and scalability.

- **Backend:** `Python` + `FastAPI` 
- **AI / Enrichment:** `BeautifulSoup4` (Scraping) + `Google Gemini 1.5 Flash` (LLM Analysis)
- **PDF Engine:** `fpdf2` (chosen for zero OS-level dependencies, perfect for serverless).
- **Email Delivery:** Python's native `smtplib` via Gmail SMTP.
- **Serverless Deployment:** Fully configured for **Vercel** via `vercel.json` and `/tmp` filesystem handling.

## 🧠 Handling Real-World Edge Cases & Fallbacks
A production system must be resilient. This prototype demonstrates contextual problem solving:
- **Scraping Blockers:** If a website blocks the scraping attempt (e.g. 403 Forbidden), the LLM dynamically pivots to deduce business insights purely from the domain name and company name.
- **API Failures / Missing Keys:** If the Gemini API fails, rate-limits, or keys are missing, the system catches the exception and falls back to a highly detailed, professional mock-data payload. The end-user *always* receives a polished report.
- **Serverless Constraints:** Vercel freezes execution immediately after an HTTP response. Background tasks were migrated to synchronous execution specifically to guarantee the email delivery within serverless timeout windows, avoiding zombie processes.

## 🚀 Setup & Local Development

### 1. Prerequisites
- Python 3.8+
- [Google AI Studio API Key](https://aistudio.google.com/app/apikey)
- Gmail App Password

### 2. Installation
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Rename `.env.example` to `.env` and fill in the required keys:
```env
GEMINI_API_KEY=your_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
```

### 4. Run Locally
```bash
uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000` to test the workflow.

## ☁️ Deploying to Vercel
This project is configured out-of-the-box for Vercel Serverless Functions.
1. Push this repository to GitHub.
2. Import the project in Vercel.
3. Add your `.env` variables into the Vercel Dashboard Settings -> Environment Variables.
4. Click **Deploy**.

## ⚖️ Trade-offs & Future Improvements
Given this is a prototype, several calculated trade-offs were made:
- **Scraping:** Relies on basic HTTP requests. In production, a headless browser (like Playwright) would be required to render React/Vue SPAs before extracting text.
- **Prompt Engineering:** The current LLM output is parsed using RegEx. A production version would utilize *Structured Outputs* (JSON schemas) to absolutely guarantee the LLM response format.
- **Queuing:** Currently runs synchronously for Vercel compatibility. At scale, this would be decoupled using an event queue (e.g., Celery, Redis, or AWS SQS) so the web server returns a 202 Accepted instantly while a worker processes the PDF and email asynchronously.
