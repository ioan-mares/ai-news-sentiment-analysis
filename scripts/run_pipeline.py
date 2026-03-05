# scripts/run_pipeline.py
import subprocess
import os
import sys

# Define absolute paths to ensure it works in Crontab
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_BIN = sys.executable # Uses the current Conda environment python

def run_step(script_name):
    script_path = os.path.join(PROJECT_DIR, "scripts", script_name)
    print(f"--- Running {script_name} ---")
    result = subprocess.run([PYTHON_BIN, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Error in {script_name}")
        return False
    return True

def main():
    # Step 1: Ingest news (RSS)
    if run_step("get_news_bot.py"):
        # Step 2: Analyze with Llama 3.1
        run_step("analyze_news.py")
        print("\n✅ Pipeline execution finished successfully.")

if __name__ == "__main__":
    main()