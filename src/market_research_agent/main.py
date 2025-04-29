#!/usr/bin/env python
import sys
import os
import subprocess
from market_research_agent.crew import MarketResearchAgentCrew

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def convert_md_to_pdf_with_quarto(markdown_path):
    """
    Converts a markdown file to PDF using Quarto CLI.
    """
    if not os.path.exists(markdown_path):
        print(f"Markdown file not found at: {markdown_path}")
        return

    try:
        subprocess.run(["quarto", "render", markdown_path, "--to", "pdf"], check=True)
        print(f"PDF successfully generated: {markdown_path.replace('.md', '.pdf')}")
    except subprocess.CalledProcessError as e:
        print(f"Quarto conversion failed:\n{e}")

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'Netflix'
    }

    print("🚀 Running the Crew...")
    result = MarketResearchAgentCrew().crew().kickoff(inputs=inputs)

    # Automatically convert markdown to PDF
    markdown_file = "report.md"  # adjust if using another filename
    print("Converting Markdown to PDF using Quarto...")
    convert_md_to_pdf_with_quarto(markdown_file)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        MarketResearchAgentCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MarketResearchAgentCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        MarketResearchAgentCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
