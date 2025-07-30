#!/usr/bin/env python3
"""
Hypothesis Runner - Automated Verification System
Runs hypothesis verification experiments from YAML templates
"""

import os
import sys
import yaml
import json
import argparse
import importlib.util
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

class HypothesisRunner:
    def __init__(self, template_path: str):
        """Initialize with a template file"""
        self.template_path = template_path
        self.config = self.load_template()
        self.output_dir = Path.cwd()
        
    def load_template(self) -> Dict[str, Any]:
        """Load and parse YAML template"""
        with open(self.template_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_environment(self) -> bool:
        """Validate required environment variables"""
        required_vars = self.config['validation']['required_env_vars']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def process_date_range(self, date_str: str) -> str:
        """Convert relative dates to absolute dates"""
        if '_days_ago' in date_str:
            days = int(date_str.split('_')[0])
            return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        elif date_str == 'now':
            return datetime.now().strftime('%Y-%m-%d')
        else:
            return date_str
    
    def create_analyzer_config(self) -> Dict[str, Any]:
        """Create configuration for the analyzer"""
        exp = self.config['experiment']
        
        # Process dates
        start_date = self.process_date_range(exp['data_sources']['social_media']['date_range']['start'])
        end_date = self.process_date_range(exp['data_sources']['social_media']['date_range']['end'])
        
        config = {
            'experiment_name': exp['name'],
            'social_media': {
                'platform': exp['data_sources']['social_media']['platform'],
                'accounts': exp['data_sources']['social_media']['accounts'],
                'keywords': exp['data_sources']['social_media']['keywords'],
                'start_date': start_date,
                'end_date': end_date,
                'max_posts': exp['data_sources']['social_media']['max_posts']
            },
            'market_data': {
                'symbols': [s['symbol'] for s in exp['data_sources']['market_data']['symbols']],
                'feed': exp['data_sources']['market_data']['data_feed']
            },
            'sentiment': {
                'provider': exp['sentiment_analysis']['llm_provider'],
                'model': exp['sentiment_analysis']['model'],
                'temperature': exp['sentiment_analysis']['temperature'],
                'categories': exp['sentiment_analysis']['categories']
            },
            'analysis': {
                'time_intervals': exp['analysis']['time_intervals'],
                'conditions': exp['analysis']['conditions']
            },
            'output': exp['output']
        }
        
        # Add custom prompt if present
        if 'custom_prompt' in exp['sentiment_analysis']:
            config['sentiment']['custom_prompt'] = exp['sentiment_analysis']['custom_prompt']
        
        return config
    
    def run_experiment(self) -> Dict[str, Any]:
        """Run the experiment based on the template"""
        print(f"\n{'='*60}")
        print(f"Running Experiment: {self.config['experiment']['name']}")
        print(f"{'='*60}\n")
        
        # Validate environment
        if not self.validate_environment():
            return {'status': 'failed', 'error': 'Environment validation failed'}
        
        # Create analyzer configuration
        config = self.create_analyzer_config()
        
        # Import and run the appropriate analyzer
        try:
            # Dynamically import the analyzer module
            from universal_sentiment_analyzer import UniversalSentimentAnalyzer
            
            # Create analyzer instance
            analyzer = UniversalSentimentAnalyzer(config)
            
            # Run analysis
            results = analyzer.run_analysis()
            
            # Generate outputs
            self.generate_outputs(results, config)
            
            return {
                'status': 'success',
                'experiment_name': config['experiment_name'],
                'posts_analyzed': len(results['posts']),
                'outputs_generated': config['output']
            }
            
        except Exception as e:
            print(f"Error running experiment: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def generate_outputs(self, results: Dict[str, Any], config: Dict[str, Any]):
        """Generate all specified outputs"""
        # Create output directory if needed
        output_dir = self.output_dir / 'results' / config['experiment_name'].replace(' ', '_').lower()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save data exports
        for export in config['output']['data_exports']:
            if export['type'] == 'csv':
                df = pd.DataFrame(results['analysis'])
                df.to_csv(output_dir / f"{export['filename']}.csv", index=False)
                print(f"Saved CSV: {export['filename']}.csv")
            
            elif export['type'] == 'json':
                with open(output_dir / f"{export['filename']}.json", 'w') as f:
                    json.dump(results['posts'], f, indent=2, default=str)
                print(f"Saved JSON: {export['filename']}.json")
        
        # Generate report
        for report in config['output']['reports']:
            if report['type'] == 'markdown':
                self.generate_markdown_report(results, config, output_dir / f"{report['filename']}.md")
                print(f"Generated report: {report['filename']}.md")
        
        print(f"\nAll outputs saved to: {output_dir}")
    
    def generate_markdown_report(self, results: Dict[str, Any], config: Dict[str, Any], output_path: Path):
        """Generate markdown report from results"""
        with open(output_path, 'w') as f:
            f.write(f"# {config['experiment_name']} Results\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Hypothesis**: {self.config['experiment']['hypothesis']}\n\n")
            
            # Summary statistics
            f.write("## Summary\n\n")
            f.write(f"- Total posts analyzed: {len(results['posts'])}\n")
            f.write(f"- Date range: {config['social_media']['start_date']} to {config['social_media']['end_date']}\n")
            f.write(f"- Symbols tracked: {', '.join(config['market_data']['symbols'])}\n\n")
            
            # Sentiment distribution
            if 'sentiment_distribution' in results:
                f.write("## Sentiment Distribution\n\n")
                f.write("| Sentiment | Count | Percentage |\n")
                f.write("|-----------|-------|------------|\n")
                for sentiment, count in results['sentiment_distribution'].items():
                    pct = (count / len(results['posts'])) * 100
                    f.write(f"| {sentiment} | {count} | {pct:.1f}% |\n")
                f.write("\n")
            
            # Add more sections as specified in the template
            f.write("\n## Methodology\n\n")
            f.write(f"- Sentiment Model: {config['sentiment']['model']}\n")
            f.write(f"- Temperature: {config['sentiment']['temperature']}\n")
            f.write(f"- Time intervals analyzed: {config['analysis']['time_intervals']} hours\n")

def main():
    parser = argparse.ArgumentParser(description='Run hypothesis verification experiments')
    parser.add_argument('template', help='Path to YAML template file')
    parser.add_argument('--output-dir', help='Output directory', default='.')
    parser.add_argument('--dry-run', action='store_true', help='Validate template without running')
    
    args = parser.parse_args()
    
    # Create runner
    runner = HypothesisRunner(args.template)
    
    if args.output_dir:
        runner.output_dir = Path(args.output_dir)
    
    # Dry run mode
    if args.dry_run:
        print("Template loaded successfully!")
        print(f"Experiment: {runner.config['experiment']['name']}")
        print(f"Would analyze {runner.config['experiment']['data_sources']['social_media']['max_posts']} posts")
        return
    
    # Run experiment
    result = runner.run_experiment()
    
    if result['status'] == 'success':
        print(f"\n✅ Experiment completed successfully!")
        print(f"Analyzed {result['posts_analyzed']} posts")
    else:
        print(f"\n❌ Experiment failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()