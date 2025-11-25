"""
Script to restart all questions in the Bhagavad Gita Q&A system.
This script sends each question to the /ask endpoint to ensure all questions are processed.
"""
import requests
import json
import time
from tqdm import tqdm
from gita_qa_pairs import QA_PAIRS

# Base URL of the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

def restart_all_questions():
    """Send each question to the /ask endpoint to restart processing."""
    results = []
    
    print(f"Starting to process {len(QA_PAIRS)} questions...")
    
    for qa in tqdm(QA_PAIRS, desc="Processing questions"):
        try:
            # Prepare the request data
            data = {"question": qa["question"]}
            
            # Send the request to the /ask endpoint
            response = requests.post(
                f"{BASE_URL}/ask",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result = {
                    "question": qa["question"],
                    "status": "success",
                    "response": response.json()
                }
            else:
                result = {
                    "question": qa["question"],
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
            results.append(result)
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.1)
            
        except Exception as e:
            result = {
                "question": qa["question"],
                "status": "exception",
                "error": str(e)
            }
            results.append(result)
            continue
    
    # Save the results to a file
    with open("question_restart_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print a summary
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    exception_count = sum(1 for r in results if r["status"] == "exception")
    
    print("\nProcessing complete!")
    print(f"Total questions: {len(results)}")
    print(f"Successfully processed: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Exceptions: {exception_count}")
    print(f"Results saved to: question_restart_results.json")

if __name__ == "__main__":
    restart_all_questions()
