import os
from fastapi import FastAPI, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from app.services.enricher import enrich_company_data
from app.services.pdf_generator import generate_pdf_report
from app.services.email_sender import send_email_with_report
from app.services.google_integration import log_to_sheets, upload_to_drive

app = FastAPI(title="SimplifIQ Lead Intake Prototype")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

class LeadData(BaseModel):
    name: str
    email: str
    company_name: str
    website_url: HttpUrl

def process_lead_workflow(name: str, email: str, company_name: str, website_url: str):
    """
    Orchestrates the entire automated workflow without human intervention.
    """
    try:
        # 1. Enrich company data
        print(f"[*] Enriching data for {company_name} ({website_url})...")
        enriched_data = enrich_company_data(website_url, company_name)
        
        # 2. Generate personalized PDF report
        print(f"[*] Generating PDF report for {company_name}...")
        pdf_path = generate_pdf_report(name, company_name, enriched_data)
        
        # 3. Send email to prospect
        print(f"[*] Sending email to {email}...")
        email_sent = send_email_with_report(name, email, company_name, pdf_path)
        
        # 4. (Bonus) Log to Google Sheets
        print(f"[*] Logging to Google Sheets...")
        log_status = "Success" if email_sent else "Email Failed"
        log_to_sheets(name, email, company_name, log_status)
        
        # 5. (Bonus) Archiving to Google Drive
        print(f"[*] Archiving PDF to Google Drive...")
        upload_to_drive(pdf_path, f"{company_name}_Audit_Report.pdf")
        
        print(f"[+] Workflow completed successfully for {email}")
        
    except Exception as e:
        print(f"[!] Workflow failed for {email}: {str(e)}")
        # In a production system, we'd add proper logging/alerting here
        log_to_sheets(name, email, company_name, f"Failed: {str(e)[:50]}")


@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    """Serves the lead capture form."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/submit")
async def submit_lead(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    company_name: str = Form(...),
    website_url: str = Form(...)
):
    """
    Captures lead info, validates, and triggers the background workflow.
    """
    # Validation is implicitly handled by FastAPI Form typing, but we can add more robust checks
    if not name or not email or not company_name or not website_url:
        return JSONResponse(status_code=400, content={"error": "All fields are required."})
        
    # Trigger background task for the workflow so the user doesn't wait
    background_tasks.add_task(
        process_lead_workflow, 
        name, 
        email, 
        company_name, 
        website_url
    )
    
    return {"message": "Lead received successfully! We are generating your personalized report and will email it shortly."}

