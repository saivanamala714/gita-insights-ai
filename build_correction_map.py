import os
import sys
from text_utils import TextProcessor

def main():
    # Path to the PDF file
    pdf_path = "11-Bhagavad-gita_As_It_Is.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    # Initialize the text processor
    print("Initializing TextProcessor...")
    processor = TextProcessor(pdf_path)
    
    # Build the correction map
    print("Building correction map from PDF...")
    correction_map = processor.build_correction_map()
    
    # Print some statistics
    print(f"\nCorrection map created with {len(correction_map)} entries")
    print("\nSample corrections:")
    for i, (wrong, correct) in enumerate(correction_map.items()):
        print(f"{wrong} -> {correct}")
        if i >= 9:  # Show first 10 examples
            break
    
    print("\nCorrection map saved to 'correction_map.json'")

if __name__ == "__main__":
    main()
