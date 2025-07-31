#!/bin/bash
# Repository Cleanup Script
# Removes temporary files and organizes the repository

echo "🧹 Cleaning up repository..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type f -name ".coverage" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove OS-specific files
echo "Removing OS-specific files..."
find . -type f -name ".DS_Store" -delete
find . -type f -name "Thumbs.db" -delete
find . -type f -name "*~" -delete

# Remove temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete
find . -type f -name "*.temp" -delete
find . -type f -name "*.log" -delete 2>/dev/null

# Clean up empty directories (except those with .gitkeep)
echo "Cleaning empty directories..."
find . -type d -empty ! -path "./.git/*" ! -exec test -e {}/.gitkeep \; -delete 2>/dev/null

# Run organization script
echo "Running organization script..."
if [ -f "scripts/organize_repo.py" ]; then
    python3 scripts/organize_repo.py
else
    echo "Organization script not found!"
fi

# Update directory tree
echo "Updating directory tree..."
tree -I '__pycache__|*.pyc|.git|.DS_Store' > docs/directory_tree.txt 2>/dev/null || {
    echo "Tree command not found. Skipping directory tree generation."
}

echo "✅ Cleanup complete!"

# Optional: Show repository statistics
echo ""
echo "📊 Repository Statistics:"
echo "Python files: $(find src -name "*.py" -type f | wc -l)"
echo "Test files: $(find tests -name "test_*.py" -type f | wc -l)"
echo "Template files: $(find templates -name "*.yaml" -type f | wc -l)"
echo "Documentation files: $(find . -name "*.md" -type f | wc -l)"
echo "Data files: $(find data -name "*.json" -o -name "*.csv" -type f | wc -l)"