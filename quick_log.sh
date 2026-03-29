#!/bin/bash
# Quick conversation logger for Windsurf chats
# Usage: ./quick_log.sh "Your question" "The answer" "Outcome"

LOGFILE="CONVERSATION_LOG.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Check if arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quick_log.sh \"question\" \"answer\" \"outcome\""
    echo ""
    echo "Or run interactively:"
    read -p "Your question: " QUESTION
    read -p "Brief answer: " ANSWER
    read -p "Result/outcome: " OUTCOME
else
    QUESTION="$1"
    ANSWER="$2"
    OUTCOME="${3:-No outcome specified}"
fi

# Append to log file
cat >> "$LOGFILE" << EOF

---

## 💬 Quick Log - $TIMESTAMP

**Q**: $QUESTION

**A**: $ANSWER

**Result**: $OUTCOME

EOF

echo "✅ Logged to $LOGFILE"
