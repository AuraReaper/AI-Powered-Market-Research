from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import subprocess
from dotenv import load_dotenv
from datetime import datetime

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


def convert_md_to_pdf(markdown_path):
	"""
	Converts a markdown file to PDF using Quarto CLI.
	"""
	if not os.path.exists(markdown_path):
		raise FileNotFoundError(f"Markdown file not found at: {markdown_path}")

	subprocess.run(["quarto", "render", markdown_path, "--to", "pdf"], check=True)


@app.post("/generate/")
async def generate_docs(payload: InputPayload):
	try:
		company = payload.company.strip()
		if not company:
			raise HTTPException(status_code=400, detail="Company name is required.")

		inputs = {"company": company}
		markdown_filename = f"{company}.md"
		pdf_filename = f"{company}.pdf"
		markdown_path = os.path.join(OUTPUT_DIR, markdown_filename)
		pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

		# Run the crew
		crew_output = MarketResearchAgentCrew().crew().kickoff(inputs=inputs)

		# for task_output in crew_output.tasks_output:
		# 	print("====== TASK OUTPUT ======")
		# 	print("type:", type(task_output))
		# 	print("keys:", dir(task_output))
		# 	print("raw:", task_output.raw)

		outputs = [
			f"##{task_output.raw}"
			for task_output in crew_output.tasks_output
		]

		# Save the markdown result
		with open(markdown_path, "w") as f:
			f.write("\n\n".join(outputs))


		# Convert to PDF
		convert_md_to_pdf(markdown_path)

		return {
			"message": "Files generated successfully.",
			"markdown_url": f"/download/md/{company}",
			"pdf_url": f"/download/pdf/{company}"
		}

	except subprocess.CalledProcessError as e:
		raise HTTPException(status_code=500, detail=f"PDF conversion failed: {e}")
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/md/{company}")
async def download_markdown(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.md")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="Markdown file not found.")
	return FileResponse(path, filename=f"{company}.md", media_type='text/markdown')


@app.get("/download/pdf/{company}")
async def download_pdf(company: str):
	path = os.path.join(OUTPUT_DIR, f"{company}.pdf")
	if not os.path.exists(path):
		raise HTTPException(status_code=404, detail="PDF file not found.")
	return FileResponse(path, filename=f"{company}.pdf", media_type='application/pdf')
