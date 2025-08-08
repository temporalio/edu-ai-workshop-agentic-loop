import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import OPENAI_API_KEY
from litellm import completion, ModelResponse

# PDF generation imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def llm_call(prompt: str, model: str = "openai/gpt-4o") -> ModelResponse:
    response = completion(
        model=model,
        messages=[{"content": prompt, "role": "user"}]
    )
    return response

def create_pdf(content: str, filename: str = "research_report.pdf"):
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    # Build the content
    story = []
    
    # Add title
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Add the main content
    # Split content into paragraphs and format each one
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():  # Only add non-empty paragraphs
            p = Paragraph(para.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
    
    doc.build(story)
    return filename

print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

# Get prompt from command line argument or use default
if len(sys.argv) > 1:
    prompt = sys.argv[1]
elif not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

print("\nPART 1: Getting research report from OpenAI. Please wait...")

try:
    # Make the API call
    result = llm_call(prompt)
    
    # Extract the response content
    response_content = result["choices"][0]["message"]["content"]
    
    print("Research complete!")
    print("Now demonstrating normal execution fragility:")
    print("Press Ctrl+C within the next 15 seconds to simulate a process crash.")
    print("Then restart the script to see how you lose all progress...")
    
    # Long pause to allow killing the process
    for i in range(15, 0, -1):
        print(f"Continuing in {i} seconds... (Press Ctrl+C to kill process)")
        time.sleep(1)
    
except Exception as e:
    print(f"Error: {e}")

# PART 2: CREATE PDF DOCUMENT
print("\nPART 2: Creating PDF Document")

try:
    if 'response_content' in locals() and response_content:
        print("Now generating your PDF with your research...")
        
        # Create the PDF
        pdf_filename = create_pdf(response_content, "research_report.pdf")
        
        print(f"SUCCESS! PDF created: {pdf_filename}")
    else:
        print("No research content available to create PDF.")
        
except Exception as e:
    print(f"Error: {e}")