from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import tempfile
from pathlib import Path
import json
import traceback
from typing import Optional
import re

from starlette.middleware.cors import CORSMiddleware

# Load your crew system
from src.market_research_agent.crew import MarketResearchAgentCrew

# Load env variables from root
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class InputPayload(BaseModel):
	company: str


class ErrorResponse(BaseModel):
	error_type: str
	message: str
	details: Optional[str] = None
	suggestions: Optional[list[str]] = None


class APIError:
	"""Custom error types for better frontend handling"""
	TOKEN_LIMIT = "token_limit_exceeded"
	API_QUOTA = "api_quota_exceeded"
	API_TIMEOUT = "api_timeout"
	INVALID_API_KEY = "invalid_api_key"
	NETWORK_ERROR = "network_error"
	PROCESSING_ERROR = "processing_error"
	PDF_CONVERSION_ERROR = "pdf_conversion_error"
	INVALID_INPUT = "invalid_input"
	SERVER_ERROR = "server_error"


def create_error_response(error_type: str, message: str, details: str = None, suggestions: list[str] = None) -> dict:
	"""Create standardized error response"""
	return {
		"error": True,
		"error_type": error_type,
		"message": message,
		"details": details,
		"suggestions": suggestions or []
	}


def analyze_error_message(error_str: str) -> tuple[str, str, list[str]]:
	"""Analyze error message and determine error type with suggestions"""
	error_lower = error_str.lower()
	
	# Token limit errors
	if any(keyword in error_lower for keyword in ['token', 'context length', 'maximum context', 'input too long']):
		return (
			APIError.TOKEN_LIMIT,
			"The request exceeded the maximum token limit for the AI model.",
			[
				"Try using a shorter company name or description",
				"Contact support if this persists with standard inputs",
				"Consider breaking down complex requests into smaller parts"
			]
		)
	
	# API quota/rate limit errors
	if any(keyword in error_lower for keyword in ['quota', 'rate limit', 'too many requests', 'limit exceeded']):
		return (
			APIError.API_QUOTA,
			"API quota or rate limit has been exceeded.",
			[
				"Please wait a few minutes and try again",
				"Consider upgrading your API plan for higher limits",
				"Try again during off-peak hours"
			]
		)
	
	# Authentication errors
	if any(keyword in error_lower for keyword in ['unauthorized', 'invalid api key', 'authentication', 'api key']):
		return (
			APIError.INVALID_API_KEY,
			"Invalid or missing API key configuration.",
			[
				"Check that your API keys are properly configured",
				"Verify that your API key is valid and not expired",
				"Contact your administrator to check API key permissions"
			]
		)
	
	# Timeout errors
	if any(keyword in error_lower for keyword in ['timeout', 'timed out', 'connection timeout']):
		return (
			APIError.API_TIMEOUT,
			"The request timed out while processing.",
			[
				"Please try again in a few moments",
				"Check your internet connection",
				"The AI service may be experiencing high demand"
			]
		)
	
	# Network/connection errors
	if any(keyword in error_lower for keyword in ['connection', 'network', 'unreachable', 'dns']):
		return (
			APIError.NETWORK_ERROR,
			"Network connection error occurred.",
			[
				"Check your internet connection",
				"Try again in a few minutes",
				"Contact support if the issue persists"
			]
		)
	
	# PDF conversion errors
	if any(keyword in error_lower for keyword in ['pdf', 'conversion', 'playwright', 'wkhtmltopdf']):
		return (
			APIError.PDF_CONVERSION_ERROR,
			"Error occurred during PDF generation.",
			[
				"Try downloading the HTML version instead",
				"The report was generated but PDF conversion failed",
				"Contact support if PDF generation is critical"
			]
		)
	
	# Default processing error
	return (
		APIError.PROCESSING_ERROR,
		"An error occurred while processing your request.",
		[
			"Please try again with a different company name",
			"Check that the company name is spelled correctly",
			"Contact support if the issue persists"
		]
	)


async def convert_html_to_pdf(html_content, output_path):
	"""
	Converts HTML content to PDF using playwright or puppeteer.
	"""
	try:
		# Using playwright for HTML to PDF conversion
		from playwright.async_api import async_playwright
		
		async with async_playwright() as p:
			browser = await p.chromium.launch()
			page = await browser.new_page()
			await page.set_content(html_content)
			await page.pdf(path=output_path, format='A4', print_background=True)
			await browser.close()
	except ImportError:
		# Fallback to wkhtmltopdf if playwright not available
		with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_html:
			tmp_html.write(html_content)
			tmp_html_path = tmp_html.name
		
		subprocess.run([
			'wkhtmltopdf',
			'--page-size', 'A4',
			'--margin-top', '0.75in',
			'--margin-right', '0.75in',
			'--margin-bottom', '0.75in',
			'--margin-left', '0.75in',
			'--encoding', 'UTF-8',
			'--enable-local-file-access',
			tmp_html_path,
			output_path
		], check=True)
		
		os.unlink(tmp_html_path)


@app.post("/generate/")
async def generate_docs(payload: InputPayload):
	try:
		company = payload.company.strip()
		if not company:
			error_response = create_error_response(
				APIError.INVALID_INPUT,
				"Company name is required.",
				suggestions=[
					"Please enter a valid company name",
					"Company name cannot be empty or just spaces"
				]
			)
			raise HTTPException(status_code=400, detail=error_response)
		
		# Validate company name length and format
		if len(company) > 100:
			error_response = create_error_response(
				APIError.INVALID_INPUT,
				"Company name is too long.",
				details=f"Company name length: {len(company)} characters (max: 100)",
				suggestions=[
					"Please use a shorter company name",
					"Use common abbreviations if necessary"
				]
			)
			raise HTTPException(status_code=400, detail=error_response)
		
		# Check for potentially problematic characters
		if re.search(r'[<>:"/\\|?*]', company):
			error_response = create_error_response(
				APIError.INVALID_INPUT,
				"Company name contains invalid characters.",
				details="Company name should not contain special file system characters",
				suggestions=[
					"Use only letters, numbers, spaces, and basic punctuation",
					"Remove characters like < > : \" / \\ | ? *"
				]
			)
			raise HTTPException(status_code=400, detail=error_response)

		inputs = {"company": company}
		markdown_filename = f"{company}.md"
		pdf_filename = f"{company}.pdf"
		markdown_path = os.path.join(OUTPUT_DIR, markdown_filename)

		html_filename = f"{company}.html"
		html_path = os.path.join(OUTPUT_DIR, html_filename)
		pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

		# Run the crew with detailed error handling
		try:
			crew_output = MarketResearchAgentCrew().crew().kickoff(inputs=inputs)
		except Exception as crew_error:
			# Analyze the crew execution error
			error_type, error_message, suggestions = analyze_error_message(str(crew_error))
			error_response = create_error_response(
				error_type,
				error_message,
				details=f"Error during AI processing: {str(crew_error)[:200]}...",
				suggestions=suggestions
			)
			raise HTTPException(status_code=500, detail=error_response)

		# The final task (final_proposal_compilation_task) generates the complete HTML report
		final_html_report = None
		
		# Extract the final HTML report from the output
		for task_output in crew_output.tasks_output:
			if hasattr(task_output, 'name') and 'final_proposal_compilation' in task_output.name:
				final_html_report = task_output.raw
				break
			# If name attribute doesn't exist, check if this is the last task (proposal writer)
			if task_output == crew_output.tasks_output[-1]:
				final_html_report = task_output.raw

		# Fallback: if no final report found, use the last task output
		if final_html_report is None:
			final_html_report = crew_output.tasks_output[-1].raw if crew_output.tasks_output else "No output generated"

		# Clean up the HTML content - remove markdown wrapper if present
		final_html_report = final_html_report.strip()
		
		# Remove markdown code block wrapper if present
		if final_html_report.startswith('```markdown'):
			final_html_report = final_html_report[11:]
		if final_html_report.startswith('```html'):
			final_html_report = final_html_report[7:]
		if final_html_report.startswith('```'):
			final_html_report = final_html_report[3:]
		if final_html_report.endswith('```'):
			final_html_report = final_html_report[:-3]
		
		final_html_report = final_html_report.strip()

		# Save the HTML result
		with open(html_path, "w", encoding='utf-8') as f:
			f.write(final_html_report)

		# Convert HTML to PDF with error handling
		try:
			await convert_html_to_pdf(final_html_report, pdf_path)
		except Exception as pdf_error:
			# If PDF conversion fails, still return success but note the PDF issue
			print(f"PDF conversion failed: {pdf_error}")
			# Remove the failed PDF file if it exists
			if os.path.exists(pdf_path):
				os.remove(pdf_path)
			# Return success but with PDF warning
			return {
				"message": "Report generated successfully, but PDF conversion failed.",
				"html_url": f"/download/html/{company}",
				"pdf_url": None,
				"warning": {
					"type": APIError.PDF_CONVERSION_ERROR,
					"message": "PDF generation failed but HTML report is available",
					"suggestions": [
						"Download the HTML version instead",
						"You can print the HTML to PDF using your browser"
					]
				}
			}

		return {
			"message": "Report generated successfully.",
			"html_url": f"/download/html/{company}",
			"pdf_url": f"/download/pdf/{company}",
			"success": True
		}

	except HTTPException:
		# Re-raise HTTP exceptions (they already have proper error formatting)
		raise
	except Exception as e:
		# Handle any other unexpected errors
		print(f"Unexpected error: {e}")
		print(f"Traceback: {traceback.format_exc()}")
		
		# Analyze the error and provide appropriate response
		error_type, error_message, suggestions = analyze_error_message(str(e))
		error_response = create_error_response(
			error_type,
			error_message,
			details=str(e)[:300] + "..." if len(str(e)) > 300 else str(e),
			suggestions=suggestions
		)
		raise HTTPException(status_code=500, detail=error_response)


@app.get("/download/md/{company}")
async def download_markdown(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.md")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="Markdown file not found.")
	return FileResponse(path, filename=f"{company}.md", media_type='text/markdown')


@app.get("/download/html/{company}")
async def download_html(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.html")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="HTML file not found.")
	return FileResponse(path, filename=f"{company}.html", media_type='text/html')


@app.get("/view/html/{company}")
async def view_html(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.html")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="HTML file not found.")
	
	with open(path, 'r', encoding='utf-8') as f:
		content = f.read()
	
	return HTMLResponse(content=content)


@app.get("/download/pdf/{company}")
async def download_pdf(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.pdf")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="PDF file not found.")
	return FileResponse(path, filename=f"{company}.pdf", media_type='application/pdf')
