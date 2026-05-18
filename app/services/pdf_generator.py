import os
from fpdf import FPDF
from datetime import datetime

class AuditReportPDF(FPDF):
    def __init__(self, company_name):
        super().__init__()
        self.company_name = company_name

    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Colors
        self.set_text_color(79, 70, 229) # Primary color matches UI
        # Title
        self.cell(0, 10, 'SimplifIQ Strategy Audit', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Prepared exclusively for {self.company_name}', 0, 1, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(name: str, company_name: str, enriched_data: dict) -> str:
    """
    Generates a personalized PDF report.
    Returns the file path to the generated PDF.
    """
    pdf = AuditReportPDF(company_name)
    pdf.add_page()
    
    # Date
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'R')
    pdf.ln(5)

    # Greeting
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Hello {name},", 0, 1, 'L')
    pdf.ln(2)
    
    # Intro
    pdf.set_font('Arial', '', 11)
    intro_text = (f"Thank you for your interest. Based on our initial review of {company_name}, "
                  "we have compiled this brief strategic audit. This report highlights key observations "
                  "and potential areas for growth.")
    pdf.multi_cell(0, 7, intro_text)
    pdf.ln(10)

    # Helper function for sections
    def add_section(title, content):
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(79, 70, 229)
        pdf.cell(0, 10, title, 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        # Replace literal \n with actual newlines if present, remove problematic characters
        clean_content = str(content).replace('\r', '').encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, clean_content)
        pdf.ln(8)

    # Add Enriched Data Sections
    add_section("1. Company Overview & Market Position", enriched_data.get('overview', 'Information pending.'))
    add_section("2. Technical & UX Assessment", enriched_data.get('ux', 'Information pending.'))
    add_section("3. Actionable Growth Opportunities", enriched_data.get('growth', 'Information pending.'))
    add_section("4. Identified Gaps & Risk Factors", enriched_data.get('risks', 'Information pending.'))

    # Outro
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 7, "This is an automated analysis generated to demonstrate our contextual understanding of your business. We look forward to a deeper discussion.")

    # Save PDF to /tmp (required for Vercel Serverless Functions)
    reports_dir = "/tmp"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create safe filename
    safe_company = "".join([c for c in company_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    filename = f"{safe_company.replace(' ', '_')}_Audit.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    pdf.output(filepath)
    return filepath
