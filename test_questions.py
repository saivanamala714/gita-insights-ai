"""
Test Script for Bhagavad Gita Q&A System

This script tests the application with the top questions about the Bhagavad Gita
to evaluate the quality and accuracy of responses.
"""
import json
import time
import requests
from typing import List, Dict, Any
from tqdm import tqdm

# Import the questions
from top_bg_questions import TOP_QUESTIONS

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
                json={"question": question}
            )
            return response.json()
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
            time.sleep(0.5)
            
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
                by_difficulty[diff] = {"total": 0, "answered": 0}
            by_difficulty[diff]["total"] += 1
            if result["has_answer"]:
                by_difficulty[diff]["answered"] += 1
        
        # Categorize by category
        by_category = {}
        for result in results:
            cat = result["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "answered": 0}
            by_category[cat]["total"] += 1
            if result["has_answer"]:
                by_category[cat]["answered"] += 1
        
        # Calculate success rates
        for cat, data in by_category.items():
            data["success_rate"] = (data["answered"] / data["total"]) * 100 if data["total"] > 0 else 0
            
        for diff, data in by_difficulty.items():
            data["success_rate"] = (data["answered"] / data["total"]) * 100 if data["total"] > 0 else 0
        
        return {
            "total_questions": total,
            "answered_questions": answered,
            "answer_rate": (answered / total) * 100 if total > 0 else 0,
            "has_sources": has_sources,
            "source_rate": (has_sources / total) * 100 if total > 0 else 0,
            "errors": errors,
            "by_difficulty": by_difficulty,
            "by_category": by_category,
            "sample_questions": {
                "answered": [r for r in results if r["has_answer"]][:3],
                "unanswered": [r for r in results if not r["has_answer"]][:3]
            }
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted report of the test results."""
        print("\n" + "="*60)
        print("BHAGAVAD GITA Q&A SYSTEM - TEST REPORT")
        print("="*60)
        
        print(f"\n📊 SUMMARY")
        print(f"Total Questions: {report['total_questions']}")
        print(f"Answered: {report['answered_questions']} ({report['answer_rate']:.1f}%)")
        print(f"With Sources: {report['has_sources']} ({report['source_rate']:.1f}%)")
        print(f"Errors: {report['errors']}")
        
        print("\n📈 BY DIFFICULTY")
        for diff, data in report["by_difficulty"].items():
            print(f"{diff.title()}: {data['answered']}/{data['total']} ({data['success_rate']:.1f}%)")
        
        print("\n📚 BY CATEGORY")
        for cat, data in sorted(report["by_category"].items(), key=lambda x: x[1]["success_rate"], reverse=True):
            print(f"{cat}: {data['answered']}/{data['total']} ({data['success_rate']:.1f}%)")
        
        print("\n✅ SAMPLE ANSWERED QUESTIONS")
        for i, q in enumerate(report["sample_questions"]["answered"][:5], 1):
            print(f"{i}. {q['question']}")
            print(f"   Answer: {q['response']['answer'][:100]}..." if q['has_answer'] else "   No answer")
            print()
        
        if report["sample_questions"]["unanswered"]:
            print("\n❌ SAMPLE UNANSWERED QUESTIONS")
            for i, q in enumerate(report["sample_questions"]["unanswered"][:5], 1):
                print(f"{i}. {q['question']}")
                if q['error']:
                    print(f"   Error: {q['error']}")
                print()
        
        print("="*60)

if __name__ == "__main__":
    # Initialize the tester
    tester = QATester()
    
    # Test all questions (or a subset)
    test_questions = TOP_QUESTIONS  # Can use [:10] to test just the first 10
    
    print(f"Starting test with {len(test_questions)} questions...")
    
    # Run the tests
    results = tester.test_questions(test_questions)
    
    # Generate and print the report
    report = tester.generate_report(results)
    tester.print_report(report)
    
    # Save detailed results to a file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"test_results_{timestamp}.json", "w") as f:
        json.dump({"report": report, "results": results}, f, indent=2)
    
    print(f"\nDetailed results saved to test_results_{timestamp}.json")
