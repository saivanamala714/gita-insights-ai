#!/usr/bin/env python3
"""
Script to easily append conversations to CONVERSATION_LOG.md
Usage: python update_conversation_log.py
"""

import sys
from datetime import datetime
from pathlib import Path


def get_multiline_input(prompt: str) -> str:
    """Get multiline input from user"""
    print(f"\n{prompt}")
    print("(Enter your text. Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done)")
    print("-" * 60)
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    return "\n".join(lines)


def append_conversation(
    question: str,
    answer: str,
    actions: list = None,
    files: list = None,
    decisions: list = None,
    outcome: str = None
):
    """Append a conversation to CONVERSATION_LOG.md"""
    
    log_file = Path("CONVERSATION_LOG.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build the entry
    entry = f"\n---\n\n"
    entry += f"## 💬 Windsurf Chat - {timestamp}\n\n"
    
    # Question
    entry += f"### 🙋 User Question/Request\n"
    entry += f"{question}\n\n"
    
    # Answer
    entry += f"### 💡 LLM Response\n"
    entry += f"{answer}\n\n"
    
    # Actions
    if actions:
        entry += f"### 🔧 Actions Taken\n"
        for action in actions:
            entry += f"- ✅ {action}\n"
        entry += "\n"
    
    # Files
    if files:
        entry += f"### 📁 Files Created/Modified\n"
        for file_info in files:
            entry += f"- `{file_info}`\n"
        entry += "\n"
    
    # Decisions
    if decisions:
        entry += f"### 🎯 Key Decisions\n"
        for decision in decisions:
            entry += f"- {decision}\n"
        entry += "\n"
    
    # Outcome
    if outcome:
        entry += f"### ✅ Outcome\n"
        entry += f"{outcome}\n\n"
    
    # Append to file
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"\n✅ Conversation logged to {log_file}")


def quick_log():
    """Quick logging mode - just Q&A"""
    print("\n" + "=" * 60)
    print("QUICK LOG MODE")
    print("=" * 60)
    
    question = input("\nYour question: ").strip()
    answer = input("Brief answer: ").strip()
    result = input("Result/outcome: ").strip()
    
    log_file = Path("CONVERSATION_LOG.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = f"\n---\n\n"
    entry += f"## 💬 Quick Log - {timestamp}\n\n"
    entry += f"**Q**: {question}\n\n"
    entry += f"**A**: {answer}\n\n"
    entry += f"**Result**: {result}\n\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"\n✅ Quick log added to {log_file}")


def detailed_log():
    """Detailed logging mode - full conversation"""
    print("\n" + "=" * 60)
    print("DETAILED LOG MODE")
    print("=" * 60)
    
    question = get_multiline_input("\n📝 Enter your question/request:")
    answer = get_multiline_input("\n💡 Enter the LLM response:")
    
    # Optional fields
    print("\n" + "-" * 60)
    print("Optional fields (press Enter to skip)")
    print("-" * 60)
    
    actions = []
    print("\nActions taken (one per line, empty line to finish):")
    while True:
        action = input("  - ").strip()
        if not action:
            break
        actions.append(action)
    
    files = []
    print("\nFiles created/modified (one per line, empty line to finish):")
    while True:
        file_info = input("  - ").strip()
        if not file_info:
            break
        files.append(file_info)
    
    decisions = []
    print("\nKey decisions (one per line, empty line to finish):")
    while True:
        decision = input("  - ").strip()
        if not decision:
            break
        decisions.append(decision)
    
    outcome = input("\nOutcome (optional): ").strip() or None
    
    # Append to log
    append_conversation(
        question=question,
        answer=answer,
        actions=actions if actions else None,
        files=files if files else None,
        decisions=decisions if decisions else None,
        outcome=outcome
    )


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("CONVERSATION LOG UPDATER")
    print("=" * 60)
    print("\nChoose logging mode:")
    print("1. Quick log (Q&A only)")
    print("2. Detailed log (full conversation)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        quick_log()
    elif choice == "2":
        detailed_log()
    elif choice == "3":
        print("\nExiting...")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
