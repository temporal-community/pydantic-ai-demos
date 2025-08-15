from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.durable_exec.temporal import TemporalAgent

from pydantic_demos.workflows.pdf_generation_activity import (
    PDFGenerationResult,
    StylingOptions,
    generate_pdf,
)


class PDFReportData(BaseModel):
    """Result from PDF generation"""

    success: bool
    """Whether PDF generation was successful"""

    formatting_notes: str
    """Notes about the formatting decisions made"""

    pdf_file_path: str | None = None
    """Path to the generated PDF file"""

    error_message: str | None = None
    """Error message if PDF generation failed"""


PDF_GENERATION_PROMPT = """
You are a PDF formatting specialist tasked with converting markdown research reports 
into professionally formatted PDF documents. You will be provided with markdown content 
that needs to be converted to PDF format.

Your responsibilities:
1. Analyze the markdown content structure
2. Determine appropriate title and styling options
3. Call the PDF generation tool with the content and formatting preferences
4. Return confirmation of successful PDF generation along with formatting notes and the PDF file path

Focus on creating clean, professional-looking PDFs that are easy to read and well-structured. 
Use appropriate styling for headers, paragraphs, lists, and code blocks.

IMPORTANT: When the PDF generation is successful, you must include the pdf_file_path from the 
tool response in your output. Set success to true and include the file path returned by the tool.
"""


agent = Agent(
    "gpt-4o-mini",
    instructions=PDF_GENERATION_PROMPT,
    name="pdf-generator-agent",
    output_type=PDFReportData,
)


@agent.tool
async def generate_pdf_tool(
    ctx: RunContext,
    markdown_content: str,
    title: str = "Research Report",
    font_size: int | None = None,
    primary_color: str | None = None,
) -> PDFGenerationResult:
    """
    Generate a PDF from markdown content with specified styling options.

    Args:
        markdown_content: The markdown content to convert to PDF
        title: Title for the PDF document
        font_size: Optional custom font size
        primary_color: Optional custom primary color

    Returns:
        PDFGenerationResult with file path and success status
    """
    styling_options = None
    if font_size or primary_color:
        styling_options = StylingOptions(
            font_size=font_size,
            primary_color=primary_color,
        )

    # Call the actual Temporal activity
    return await generate_pdf(markdown_content, title, styling_options)


temporal_agent = TemporalAgent(agent)
