#!/bin/bash

# Script to commit Task 2 changes only

echo "🚀 Committing Task 2: Tripletex AI Agent"
echo ""

# Add gitignore changes
git add .gitignore

# Add all Task2 files
git add Task2/

# Show what will be committed
echo "Files to be committed:"
git status --short | grep -E "(\.gitignore|Task2)"
echo ""

# Commit
git commit -m "Add Task 2: Complete Tripletex AI Agent implementation

- FastAPI application with /solve endpoint
- OpenAI GPT-4 integration for prompt interpretation
- Multi-language support (7 languages)
- Tripletex API client with retry logic
- File processing (PDF/images)
- Task execution engine
- Comprehensive documentation
- Docker containerization
- Production-ready deployment"

echo ""
echo "✅ Task 2 committed successfully!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub: git push"
echo "2. Deploy: Follow Task2/GET_STARTED.md"
echo "3. Compete: Submit your URL to https://app.ainm.no/submit/tripletex"

# Made with Bob
