"""
Test Script for Bhagavad Gita Q&A System with 200 Questions

This script tests the application with 200 questions about the Bhagavad Gita
to evaluate the quality and accuracy of responses.
"""
import json
import time
import requests
from typing import List, Dict, Any
from tqdm import tqdm
from pathlib import Path

# Import the questions from the expanded set
from top_200_questions import TOP_QUESTIONS

class QATester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ask_endpoint = f"{base_url}/ask"
        
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Send a question to the QA system and return the response."""
        try:
            response = requests.post(
                self.ask_endpoint,
                headers={"Content-Type": "application/json"},
                json={"question": question},
                timeout=30  # 30 second timeout for each request
            )
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": "Request timed out", "answer": "", "sources": []}
        except Exception as e:
            return {"error": str(e), "answer": "", "sources": []}
    
    def test_questions(self, questions: List[Dict[str, Any]], max_questions: int = None) -> List[Dict[str, Any]]:
        """Test a list of questions and return the results."""
        if max_questions:
            questions = questions[:max_questions]
            
        results = []
        
        print(f"\nTesting {len(questions)} questions...\n")
        
        for question_data in tqdm(questions, desc="Testing questions"):
            question = question_data["question"]
            response = self.ask_question(question)
            
            result = {
                "question": question,
                "category": question_data["category"],
                "difficulty": question_data["difficulty"],
                "response": response,
                "has_answer": bool(response.get("answer") and len(response.get("answer", "").strip()) > 0),
                "has_sources": bool(response.get("sources") and len(response.get("sources", [])) > 0),
                "error": response.get("error")
            }
            
            results.append(result)
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)  # Increased delay to be more conservative
            
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary report of the test results."""
        total = len(results)
        answered = sum(1 for r in results if r["has_answer"])
        has_sources = sum(1 for r in results if r["has_sources"])
        errors = sum(1 for r in results if r["error"])
        
        # Categorize by difficulty
        by_difficulty = {}
        for result in results:
            diff = result["difficulty"]
            if diff not in by_difficulty:
                by_difficulty[diff] = {"total": 0, "answered": 0, "with_sources": 0}
            by_difficulty[diff]["total"] += 1
            if result["has_answer"]:
                by_difficulty[diff]["answered"] += 1
            if result["has_sources"]:
                by_difficulty[diff]["with_sources"] += 1
        
        # Categorize by category
        by_category = {}
        for result in results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "answered": 0, "with_sources": 0}
            by_category[cat]["total"] += 1
            if result["has_answer"]:
                by_category[cat]["answered"] += 1
            if result["has_sources"]:
                by_category[cat]["with_sources"] += 1
        
        # Calculate success rates
        for cat, data in by_category.items():
            data["answer_rate"] = (data["answered"] / data["total"]) * 100 if data["total"] > 0 else 0
            data["sources_rate"] = (data["with_sources"] / data["total"]) * 100 if data["total"] > 0 else 0
            
        for diff, data in by_difficulty.items():
            data["answer_rate"] = (data["answered"] / data["total"]) * 100 if data["total"] > 0 else 0
            data["sources_rate"] = (data["with_sources"] / data["total"]) * 100 if data["total"] > 0 else 0
        
        return {
            "total_questions": total,
            "answered_questions": answered,
            "answer_rate": (answered / total) * 100 if total > 0 else 0,
            "questions_with_sources": has_sources,
            "sources_rate": (has_sources / total) * 100 if total > 0 else 0,
            "error_count": errors,
            "error_rate": (errors / total) * 100 if total > 0 else 0,
            "by_category": by_category,
            "by_difficulty": by_difficulty,
            "results": results
        }
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save the report to a JSON file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"gita_qa_test_report_{timestamp}.json"
        
        # Create a results directory if it doesn't exist
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(filepath)

if __name__ == "__main__":
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Test the Bhagavad Gita Q&A system with 200 questions.")
    parser.add_argument("--url", type=str, default="http://localhost:8000",
                       help="Base URL of the Q&A API")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit the number of questions to test (for quick testing)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output filename for the test report")
    
    args = parser.parse_args()
    
    # Initialize the tester
    print(f"Connecting to Q&A system at {args.url}")
    tester = QATester(base_url=args.url)
    
    # Run the tests
    print(f"Testing with {args.limit if args.limit else 'all'} questions...")
    results = tester.test_questions(TOP_QUESTIONS, max_questions=args.limit)
    
    # Generate and save the report
    print("\nGenerating test report...")
    report = tester.generate_report(results)
    output_file = tester.save_report(report, args.output)
    
    # Print a summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total questions: {report['total_questions']}")
    print(f"Answered questions: {report['answered_questions']} ({report['answer_rate']:.1f}%)")
    print(f"Questions with sources: {report['questions_with_sources']} ({report['sources_rate']:.1f}%)")
    print(f"Errors: {report['error_count']} ({report['error_rate']:.1f}%)")
    
    # Print by category
    print("\nBY CATEGORY:")
    for category, data in report["by_category"].items():
        print(f"  {category}: {data['answered']}/{data['total']} answered "
              f"({data['answer_rate']:.1f}%), "
              f"{data['with_sources']}/{data['total']} with sources "
              f"({data['sources_rate']:.1f}%)")
    
    # Print by difficulty
    print("\nBY DIFFICULTY:")
    for difficulty, data in report["by_difficulty"].items():
        print(f"  {difficulty}: {data['answered']}/{data['total']} answered "
              f"({data['answer_rate']:.1f}%), "
              f"{data['with_sources']}/{data['total']} with sources "
              f"({data['sources_rate']:.1f}%)")
    
    print(f"\nDetailed report saved to: {output_file}")
