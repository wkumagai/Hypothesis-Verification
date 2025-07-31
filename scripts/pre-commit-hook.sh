#!/bin/bash
# Git pre-commit hook to organize repository before each commit
# Install by copying to .git/hooks/pre-commit

echo "🗂️ Organizing repository before commit..."

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Run the organization script
if [ -f "$REPO_ROOT/scripts/organize_repo.py" ]; then
    python3 "$REPO_ROOT/scripts/organize_repo.py"
    
    # Add any newly organized files to the commit
    git add -A
    
    echo "✅ Repository organized"
else
    echo "⚠️  Organization script not found"
fi

# Run basic cleanup
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name ".DS_Store" -delete 2>/dev/null

exit 0