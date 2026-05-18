import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from urllib.parse import urlparse

def get_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def scrape_website(url: str) -> str:
    """Scrapes the visible text from the given website URL."""
    try:
        # Add scheme if missing
        if not url.startswith("http"):
            url = "https://" + url
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        # Get text and clean it up
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit to first 3000 chars to avoid token limits for basic scraping
        return text[:3000]
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

def enrich_company_data(website_url: str, company_name: str) -> dict:
    """
    Orchestrates the enrichment process:
    1. Scrape website content
    2. Use Gemini AI to generate insights and audit notes
    """
    domain = get_domain(website_url)
    website_text = scrape_website(website_url)
    
    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Using fallback mock data.")
        return get_mock_enrichment_data(company_name)
        
    genai.configure(api_key=api_key)
    
    # Choose model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert business analyst and consultant. I have scraped some content from the website of a company named "{company_name}" (domain: {domain}).
    
    Website content:
    {website_text if website_text else "No content could be scraped. Please deduce what you can from the company name and domain."}
    
    Based on this information, provide a structured analysis in plain text (no markdown formatting symbols like ** or ##, just use capital letters for headers and dashes for bullet points) to be included in an audit report. 
    
    Provide the following sections:
    
    SUMMARY
    (A brief 2-3 sentence overview of what the company does and its value proposition)
    
    KEY STRENGTHS
    - (Strength 1)
    - (Strength 2)
    
    AREAS FOR IMPROVEMENT
    - (Area 1)
    - (Area 2)
    
    RECOMMENDED NEXT STEPS
    - (Step 1)
    - (Step 2)
    """
    
    try:
        response = model.generate_content(prompt)
        ai_text = response.text
        
        # Parse the AI response into a dictionary for the PDF generator
        sections = parse_ai_response(ai_text)
        return sections
        
    except Exception as e:
        print(f"Gemini API failed: {e}")
        return get_mock_enrichment_data(company_name)

def parse_ai_response(text: str) -> dict:
    """Simple parser to split the AI text into sections."""
    data = {
        "summary": "No summary provided.",
        "strengths": "No strengths identified.",
        "improvements": "No areas identified.",
        "next_steps": "No next steps provided."
    }
    
    # Very rudimentary parsing based on expected headers
    import re
    
    # Split by known headers
    parts = re.split(r'(SUMMARY|KEY STRENGTHS|AREAS FOR IMPROVEMENT|RECOMMENDED NEXT STEPS)', text, flags=re.IGNORECASE)
    
    current_key = None
    for part in parts:
        part_clean = part.strip()
        if part_clean.upper() == "SUMMARY":
            current_key = "summary"
        elif part_clean.upper() == "KEY STRENGTHS":
            current_key = "strengths"
        elif part_clean.upper() == "AREAS FOR IMPROVEMENT":
            current_key = "improvements"
        elif part_clean.upper() == "RECOMMENDED NEXT STEPS":
            current_key = "next_steps"
        elif current_key and part_clean:
            data[current_key] = part_clean
            current_key = None
            
    return data

def get_mock_enrichment_data(company_name: str) -> dict:
    """Fallback data if scraping/AI fails."""
    return {
        "summary": f"{company_name} appears to be an innovative company in its sector, focusing on delivering value to its clients.",
        "strengths": "- Strong brand presence\n- Clear product offerings",
        "improvements": "- Website load speed optimization\n- Clearer call-to-actions on the homepage",
        "next_steps": "- Schedule a technical audit\n- Review conversion funnels"
    }
