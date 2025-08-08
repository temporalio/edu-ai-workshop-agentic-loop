import os
import sys

from temporalio import activity
from temporalio.exceptions import ApplicationError

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import OPENAI_API_KEY
from litellm import completion

# PDF generation imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class GenerateReportActivities:

    @activity.defn
    async def perform_research(self, prompt: str, model: str = "openai/gpt-4o") -> str:
        response = completion(
            model=model,
            messages=[{"content": prompt, "role": "user"}]
        )
        
        research_response = response["choices"][0]["message"]["content"]
        return research_response

    @activity.defn
    async def create_pdf_activity(self, content: str, filename: str = "research_pdf.pdf") -> str:
        # Get current attempt number from Temporal
        attempt = activity.info().attempt
        
        # Fail the first 2 attempts to demonstrate retries
        if attempt <= 2:
            raise ApplicationError(f"PDF creation failed - demonstrating Temporal retries!")
        
        print("Creating PDF document...")
        
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
        
        print(f"SUCCESS! PDF created: {filename}")
        return filename