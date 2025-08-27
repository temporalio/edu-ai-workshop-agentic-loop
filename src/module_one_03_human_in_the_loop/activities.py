import os
import sys
from pathlib import Path
from typing import cast

from temporalio import activity
from temporalio.exceptions import ApplicationError

sys.path.append(str(Path(__file__).parent.parent.parent))

from config import OPENAI_API_KEY
from litellm import completion
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class GenerateReportActivities:
    @activity.defn
    async def perform_research(self, prompt: str, model: str = "openai/gpt-4o") -> str:
        response = completion(model=model, messages=[{"content": prompt, "role": "user"}])

        return cast("str", response["choices"][0]["message"]["content"])

    @activity.defn
    async def create_pdf_activity(self, content: str, filename: str = "research_pdf.pdf") -> str:
        attempt = activity.info().attempt
        if attempt <= 2:
            raise ApplicationError("PDF creation failed - demonstrating Temporal retries!")

        doc = SimpleDocTemplate(filename, pagesize=letter)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30, alignment=1)

        story: list[Flowable] = []
        title = Paragraph("Research Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        paragraphs = content.split("\n\n")
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip(), styles["Normal"])
                story.append(p)
                story.append(Spacer(1, 12))

        doc.build(story)

        print(f"SUCCESS! PDF created: {filename}")
        return filename
