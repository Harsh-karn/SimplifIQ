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
    You are a top-tier Management Consultant and Growth Strategist. I have scraped some content from the website of a company named "{company_name}" (domain: {domain}).
    
    Website content:
    {website_text if website_text else "No content could be scraped. Please deduce what you can from the company name and domain."}
    
    Based on this information, provide a highly precise, detail-oriented, and professional strategic analysis in plain text (do NOT use markdown symbols like ** or ##, just use capital letters for headers and standard dashes for bullet points) to be included in an audit report.
    
    Your tone must be authoritative, data-driven, and highly customized to their industry.
    
    Provide EXACTLY the following 4 sections, with detailed paragraphs and multiple bullet points where appropriate:
    
    COMPANY OVERVIEW & MARKET POSITION
    (Provide a detailed 1-2 paragraph analysis of their core value proposition, target audience, and positioning within their specific industry.)
    
    TECHNICAL & UX ASSESSMENT
    (Analyze their apparent digital presence, messaging clarity, and user experience based on the scraped content. Provide specific observations.)
    
    ACTIONABLE GROWTH OPPORTUNITIES
    - (Highly specific opportunity 1 related to their product/service)
    - (Highly specific opportunity 2 related to marketing or conversion)
    - (Highly specific opportunity 3 related to expansion or optimization)
    
    IDENTIFIED GAPS & RISK FACTORS
    - (Risk 1 based on industry standards)
    - (Risk 2 based on missing information or messaging gaps)
    """
    
    try:
        response = model.generate_content(prompt)
        ai_text = response.text
        return parse_ai_response(ai_text)
        
    except Exception as e:
        print(f"\n[!] Gemini API failed during generation: {e}\n")
        return get_mock_enrichment_data(company_name, domain)

def parse_ai_response(text: str) -> dict:
    """Simple parser to split the AI text into sections."""
    data = {
        "overview": "Information pending full analysis.",
        "ux": "Information pending technical review.",
        "growth": "- Pending strategic review",
        "risks": "- Pending risk assessment"
    }
    
    import re
    # Split by known headers
    parts = re.split(r'(COMPANY OVERVIEW & MARKET POSITION|TECHNICAL & UX ASSESSMENT|ACTIONABLE GROWTH OPPORTUNITIES|IDENTIFIED GAPS & RISK FACTORS)', text, flags=re.IGNORECASE)
    
    current_key = None
    for part in parts:
        part_clean = part.strip()
        header_check = part_clean.upper()
        
        if "COMPANY OVERVIEW" in header_check:
            current_key = "overview"
        elif "UX ASSESSMENT" in header_check:
            current_key = "ux"
        elif "GROWTH OPPORTUNITIES" in header_check:
            current_key = "growth"
        elif "RISK FACTORS" in header_check:
            current_key = "risks"
        elif current_key and part_clean:
            data[current_key] = part_clean
            current_key = None
            
    return data

def get_mock_enrichment_data(company_name: str, domain: str) -> dict:
    """Detailed fallback data if scraping/AI fails."""
    return {
        "overview": f"{company_name} is operating in a competitive digital landscape. Based on the domain architecture ({domain}), the business targets a modern consumer base seeking streamlined solutions. The core value proposition appears centered on delivering specialized services, though there is significant room to capture additional market share through tighter vertical integration and clearer competitive differentiation.",
        "ux": "The digital touchpoints suggest a functional approach to user acquisition, but the narrative flow lacks the required friction-reduction to maximize conversion rates. The hero messaging could be heavily optimized for clarity, and the primary call-to-action (CTA) pathways require A/B testing to establish a stronger psychological trigger for the end user.",
        "growth": "- Implement aggressive retargeting campaigns focusing on middle-of-funnel users who abandon the initial conversion step.\n- Deploy an automated lead-nurturing sequence that addresses the specific pain points of your highest-LTV customer segment.\n- Overhaul the landing page architecture to prioritize social proof and quantifiable outcomes above the fold.",
        "risks": "- Over-reliance on generic messaging which dilutes the brand's unique selling proposition (USP).\n- Potential high bounce rates due to lack of immediate clarity in the primary hero section.\n- Missed opportunities in capturing top-of-funnel intent due to an absence of high-value lead magnets."
    }
