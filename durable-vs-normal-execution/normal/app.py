## Part 1, does not have students create a JSON format
import os
import sys
import time
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import OPENAI_API_KEY
from litellm import completion, ModelResponse

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
    doc = SimpleDocTemplate(filename, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    story = []
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 12))
    
    doc.build(story)
    return filename

print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ").strip()

if len(sys.argv) > 1:
    prompt = sys.argv[1]
elif not prompt:
    prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
    print(f"No prompt entered. Using default: {prompt}")

print("\nPART 1: Getting research report from OpenAI. Please wait...")

try:
    result = llm_call(prompt)
    
    response_content = result["choices"][0]["message"]["content"]
    
    print("Research complete!")
    
    # # Output research response in JSON format to console
    # research_data = {
    #     "prompt": prompt,
    #     "research": response_content
    # }
    
    # print("\nResearch JSON Output:")
    # print(json.dumps(research_data, indent=2, ensure_ascii=False))
    
    # print("\nNow demonstrating normal execution fragility:")
    # print("Press Ctrl+C within the next 15 seconds to simulate a process crash.")
    # print("Then restart the script to see how you lose all progress...")
    
    # Long pause to allow killing the process
    for i in range(15, 0, -1):
        print(f"Continuing in {i} seconds... (Press Ctrl+C to kill process)")
        time.sleep(1)
    
except Exception as e:
    print(f"Error: {e}")

print("\nPART 2: Creating PDF Document")

try:
    if 'response_content' in locals() and response_content:
        print("Now generating your PDF with your research...")
        
        pdf_filename = create_pdf(response_content, "research_report.pdf")
        print(f"SUCCESS! PDF created: {pdf_filename}")
    else:
        print("No research content available to create PDF.")
        
except Exception as e:
    print(f"Error: {e}")