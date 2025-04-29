#!/usr/bin/env python
import sys
import os
import subprocess
from dotenv import load_dotenv
from market_research_agent.crew import MarketResearchAgentCrew


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
        'company': "Flipkart"
    }

    print("🚀 Running the Crew...")
    result = MarketResearchAgentCrew().crew().kickoff(inputs=inputs)

    markdown_file = "report.md"
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
        raise Exception(f"An error occurred while replaying the crew: {e}")\


if __name__ == "__main__":
    import sys
    # Make sure .env file exists in project root directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if not os.path.exists(dotenv_path):
        print(f"Warning: .env file not found at {dotenv_path}")
        print("Make sure you have created a .env file with EXA_API_KEY=your_key_here in the project root directory")
    company = sys.argv[1]
    run(company)
