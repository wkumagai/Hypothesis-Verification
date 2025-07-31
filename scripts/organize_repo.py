#!/usr/bin/env python3
"""
Repository Organization Script
Automatically organizes files in the Hypothesis Verification repository
"""

import os
import shutil
from pathlib import Path
import json
import yaml
from datetime import datetime

class RepoOrganizer:
    def __init__(self, repo_root=None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        
        # Define directory mappings
        self.directories = {
            'src/core': ['hypothesis_runner.py', 'universal_sentiment_analyzer.py'],
            'src/analyzers': ['*_analysis.py', '*_analyzer.py'],
            'src/utils': ['utils.py', 'helpers.py', '*_helper.py'],
            'data/raw': ['*_raw_*.json', '*_raw_*.csv', 'raw_*.json'],
            'data/processed': ['*_results.csv', '*_analysis.csv', '*_details.json'],
            'results/reports': ['*_report.md', '*_methodology_report.md'],
            'assets/images': ['*.png', '*.jpg', '*.svg'],
            'tests': ['test_*.py'],
            'templates': ['*.yaml', '*.yml'],
            'scripts': ['*.sh', '*.py'],
            'docs': ['*.md', '!README.md', '!test_file.md'],
        }
        
        # Files to keep in root
        self.root_files = [
            'README.md',
            'requirements.txt',
            '.env',
            '.env.example',
            '.gitignore',
            'setup.py',
            'LICENSE'
        ]
    
    def ensure_directories(self):
        """Create all necessary directories"""
        print("Ensuring directory structure...")
        
        dirs = [
            'src/core', 'src/analyzers', 'src/utils',
            'data/raw', 'data/processed',
            'results/elon_tesla', 'results/trump_tech', 'results/reports',
            'assets/images',
            'tests', 'scripts', 'docs', 'config',
            '.github/workflows'
        ]
        
        for dir_path in dirs:
            full_path = self.repo_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Add .gitkeep for empty directories
            gitkeep = full_path / '.gitkeep'
            if not any(full_path.iterdir()) and not gitkeep.exists():
                gitkeep.touch()
    
    def organize_files(self):
        """Move files to their appropriate directories"""
        print("\nOrganizing files...")
        
        moved_count = 0
        
        # Get all files in root directory
        for item in self.repo_root.iterdir():
            if item.is_file() and item.name not in self.root_files:
                moved = self.move_file(item)
                if moved:
                    moved_count += 1
        
        # Organize files in subdirectories
        for subdir in ['results', 'data', 'src']:
            subdir_path = self.repo_root / subdir
            if subdir_path.exists():
                for item in subdir_path.rglob('*'):
                    if item.is_file() and item.parent == subdir_path:
                        moved = self.move_file(item)
                        if moved:
                            moved_count += 1
        
        print(f"Moved {moved_count} files")
    
    def move_file(self, file_path: Path) -> bool:
        """Move a single file to its appropriate directory"""
        filename = file_path.name
        
        # Skip if file is in correct location
        for target_dir, patterns in self.directories.items():
            for pattern in patterns:
                if pattern.startswith('!'):
                    # Exclusion pattern
                    continue
                    
                if self.matches_pattern(filename, pattern):
                    target_path = self.repo_root / target_dir / filename
                    
                    # Skip if already in correct location
                    if file_path.parent == target_path.parent:
                        return False
                    
                    # Move file
                    try:
                        print(f"  Moving {file_path.relative_to(self.repo_root)} -> {target_dir}/")
                        shutil.move(str(file_path), str(target_path))
                        return True
                    except Exception as e:
                        print(f"  Error moving {filename}: {e}")
                        return False
        
        return False
    
    def matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern"""
        if pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        elif '*' in pattern:
            prefix, suffix = pattern.split('*', 1)
            return filename.startswith(prefix) and filename.endswith(suffix)
        else:
            return filename == pattern
    
    def categorize_results(self):
        """Categorize results by analysis type"""
        print("\nCategorizing results...")
        
        results_dir = self.repo_root / 'results'
        
        # Define categorization rules
        categories = {
            'elon_tesla': ['*elon*', '*tesla*sentiment*', 'sentiment_*'],
            'trump_tech': ['*trump*', 'trump_*'],
        }
        
        for category, patterns in categories.items():
            category_dir = results_dir / category
            
            # Move matching files
            for pattern in patterns:
                for file_path in results_dir.glob(pattern):
                    if file_path.is_file() and file_path.parent == results_dir:
                        try:
                            shutil.move(str(file_path), str(category_dir))
                            print(f"  Categorized {file_path.name} -> {category}/")
                        except Exception as e:
                            print(f"  Error categorizing {file_path.name}: {e}")
    
    def clean_empty_directories(self):
        """Remove empty directories (except those with .gitkeep)"""
        print("\nCleaning empty directories...")
        
        for dirpath, dirnames, filenames in os.walk(self.repo_root, topdown=False):
            dirpath = Path(dirpath)
            
            # Skip .git directory
            if '.git' in dirpath.parts:
                continue
            
            # Check if directory is empty (only has .gitkeep)
            if not dirnames and len(filenames) <= 1:
                if not filenames or filenames[0] == '.gitkeep':
                    # Keep certain directories even if empty
                    keep_dirs = ['data/raw', 'data/processed', 'results/elon_tesla', 
                               'results/trump_tech', 'docs', 'scripts', 'config']
                    
                    relative_path = dirpath.relative_to(self.repo_root)
                    if str(relative_path) not in keep_dirs:
                        try:
                            shutil.rmtree(dirpath)
                            print(f"  Removed empty directory: {relative_path}")
                        except Exception as e:
                            print(f"  Error removing {relative_path}: {e}")
    
    def generate_tree(self):
        """Generate directory tree for documentation"""
        print("\nGenerating directory tree...")
        
        tree_lines = ["```", "Hypothesis-Verification/"]
        
        for root, dirs, files in os.walk(self.repo_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            level = root.replace(str(self.repo_root), '').count(os.sep)
            indent = "│   " * level
            
            if level > 0:
                dirname = os.path.basename(root)
                tree_lines.append(f"{indent[:-4]}├── {dirname}/")
            
            # Add files
            subindent = "│   " * (level + 1)
            for i, filename in enumerate(sorted(files)):
                if not filename.startswith('.'):
                    connector = "├──" if i < len(files) - 1 else "└──"
                    tree_lines.append(f"{subindent[:-4]}{connector} {filename}")
        
        tree_lines.append("```")
        return "\n".join(tree_lines)
    
    def create_index_files(self):
        """Create __init__.py files for Python packages"""
        print("\nCreating package index files...")
        
        python_dirs = ['src', 'src/core', 'src/analyzers', 'src/utils', 'tests']
        
        for dir_name in python_dirs:
            dir_path = self.repo_root / dir_name
            if dir_path.exists():
                init_file = dir_path / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
                    print(f"  Created {dir_name}/__init__.py")
    
    def run(self):
        """Run the complete organization process"""
        print(f"Organizing repository at: {self.repo_root}")
        print("=" * 50)
        
        self.ensure_directories()
        self.organize_files()
        self.categorize_results()
        self.create_index_files()
        self.clean_empty_directories()
        
        # Generate and save tree
        tree = self.generate_tree()
        tree_file = self.repo_root / 'docs' / 'directory_tree.txt'
        tree_file.write_text(tree)
        print(f"\nDirectory tree saved to: docs/directory_tree.txt")
        
        print("\n✅ Repository organization complete!")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize Hypothesis Verification repository')
    parser.add_argument('--path', help='Repository path', default='.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    organizer = RepoOrganizer(args.path)
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        # TODO: Implement dry run logic
    else:
        organizer.run()

if __name__ == "__main__":
    main()