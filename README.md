# SimplifIQ Lead Intake Prototype

This is a working prototype for an automated lead intake workflow. It captures potential client information, enriches the data using web scraping and AI, generates a personalized strategic audit report as a PDF, and automatically emails it to the prospect.

## Architecture & System Design

The system is built using **Python** and **FastAPI** to handle web requests and orchestrate background processing.

1.  **Frontend/Form Capture**: A lightweight HTML page built with Jinja2 and Tailwind-style vanilla CSS. It accepts the user's information asynchronously to prevent page reloading.
2.  **API Gateway**: A FastAPI backend receives the form submission, validates the inputs, and kicks off the background workflow using `FastAPI.BackgroundTasks`. This ensures an immediate response to the client ("Success! Generating your report...") without waiting for the slow LLM, PDF generation, or Email sending operations.
3.  **Data Enrichment Service (`enricher.py`)**: 
    *   **Scraping**: Uses `requests` and `BeautifulSoup` to scrape the visible text of the prospect's company website.
    *   **AI Insights**: Uses the **Google Gemini API** (`gemini-1.5-flash`) to analyze the scraped content and generate a structured audit containing a summary, key strengths, areas for improvement, and next steps.
4.  **PDF Generation Service (`pdf_generator.py`)**: Uses the `fpdf2` library to create a clean, professional, and branded PDF document integrating the AI-generated insights.
5.  **Email Service (`email_sender.py`)**: Connects via SMTP (e.g., Gmail) to send a personalized email to the prospect with the generated PDF attached.
6.  **Google Integration Service (`google_integration.py`)**: Handles the **Bonus Requirements** by logging lead data into Google Sheets and archiving the generated PDF to Google Drive via the `google-api-python-client`.

## Fallbacks and Real-World Scenarios Handled

*   **Scraping Failures or Token Limits**: If the website blocks scraping or the URL is invalid, the text is bypassed. The prompt specifically instructs the AI to deduce what it can from the domain name and company name alone. If the Gemini API fails entirely or no API key is provided, a robust mock data fallback is utilized.
*   **Asynchronous Background Processing**: Web requests don't time out while waiting for AI generation and email sending.
*   **Missing Integrations**: The system checks for the presence of API keys, `.env` variables, and Google `credentials.json` files. If any of these are missing, it gracefully skips that particular step (e.g., skips uploading to Drive) while continuing the core flow, ensuring the user gets their email if possible.

## Setup Instructions

### 1. Prerequisites

*   Python 3.8+
*   Google Gemini API Key
*   An Email account with an App Password (for SMTP)
*   (Optional) Google Cloud Service Account JSON file for Sheets/Drive bonus features.

### 2. Installation

1.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Fill in the `.env` file with your credentials:
    *   `GEMINI_API_KEY`: Your Gemini API Key from Google AI Studio.
    *   `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Your email server details (e.g., for Gmail, use an App Password).
    *   `SENDER_EMAIL`: The email address the reports will be sent from.
    *   **(Bonus)** `GOOGLE_SHEET_ID` and `GOOGLE_DRIVE_FOLDER_ID`: For the Google Sheets and Drive integrations.
3.  **(Bonus)** Place your Google Service Account key file in the root directory and name it `credentials.json`. 

### 4. Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be available at: http://127.0.0.1:8000

## Limitations & Trade-offs

1.  **Web Scraping**: Simple HTTP requests with `BeautifulSoup` are used for speed and simplicity. In a production environment, many modern websites (SPAs built in React/Vue) require a headless browser (like Playwright or Selenium) to fully render the DOM before scraping text.
2.  **PDF Layout Engine**: `fpdf2` is fast and doesn't require system-level dependencies (like `wkhtmltopdf` does), making it highly portable. However, building complex layouts with `fpdf2` is imperative and can be tedious. A production system might utilize HTML-to-PDF generators for more sophisticated, data-driven report designs.
3.  **LLM Prompting**: The current parsing logic for the LLM response relies on regex headers. A more robust implementation would use Structured Outputs (like Gemini's `response_schema` or function calling) to guarantee the LLM returns pure JSON data.
4.  **Error Recovery**: The current implementation logs errors to stdout and optionally to Google Sheets. In production, a task queue like Celery or a workflow engine like Temporal would provide automated retries for transient API failures.
