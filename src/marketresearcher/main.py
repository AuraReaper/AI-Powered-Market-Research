#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from crew import Marketresearcher
import traceback
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file from project root (two levels up from src/marketresearcher)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

print(f"🔑 Loading environment variables from: {env_path}")
print(f"✅ API Keys loaded: GEMINI={'✓' if os.getenv('GEMINI_API_KEY') else '✗'}, GROQ={'✓' if os.getenv('GROQ_API_KEY') else '✗'}, SERPER={'✓' if os.getenv('SERPER_API_KEY') else '✗'}")

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(company_name: str):
    """
    Run the crew.
    """
    inputs = {
        'company': company_name
    }
    
    try:
        Marketresearcher().crew().kickoff(inputs=inputs)
    except Exception as e:
        print("❌ Error during CrewAI execution:")
        traceback.print_exc()  # shows full stack trace
        print(f"\nException Message: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Marketresearcher().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Marketresearcher().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Marketresearcher().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py run <company_name>")
        print("  python main.py train <company_name> <iterations> <filename>")
        print("  python main.py test <company_name> <iterations> <model_name>")
        print("  python main.py replay <task_id>")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "run":
            run(sys.argv[2])

        elif command == "train":
            train()

        elif command == "test":
            test()

        elif command == "replay":
            replay()

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except IndexError:
        print("⚠️ Missing arguments for command.")
        sys.exit(1)
