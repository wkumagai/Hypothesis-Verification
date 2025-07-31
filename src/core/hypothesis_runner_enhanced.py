#!/usr/bin/env python3
"""
Enhanced Hypothesis Runner with Subagent Integration
Automatically triggers specialized subagents at appropriate stages
"""

import os
import sys
import yaml
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path

# Import subagent framework
from subagent_framework import setup_subagents, SubagentOrchestrator

class EnhancedHypothesisRunner:
    def __init__(self, template_path: str, enable_subagents: bool = True):
        """Initialize with a template file and optional subagent support"""
        self.template_path = template_path
        self.config = self.load_template()
        self.output_dir = Path.cwd()
        self.enable_subagents = enable_subagents
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize subagent orchestrator if enabled
        if self.enable_subagents:
            self.orchestrator = self._setup_all_subagents()
            self.logger.info("Subagent system initialized")
        else:
            self.orchestrator = None
            self.logger.info("Running without subagents")
    
    def _setup_all_subagents(self) -> SubagentOrchestrator:
        """Set up all available subagents"""
        orchestrator = setup_subagents()
        
        # Register additional subagents that weren't in the basic setup
        try:
            from statistical_analyzer_subagent import StatisticalAnalyzerSubagent
            orchestrator.register_subagent(StatisticalAnalyzerSubagent("statistical_analyzer"))
        except ImportError:
            self.logger.warning("Statistical analyzer subagent not available")
        
        try:
            from report_generator_subagent import ReportGeneratorSubagent
            orchestrator.register_subagent(ReportGeneratorSubagent("report_generator"))
        except ImportError:
            self.logger.warning("Report generator subagent not available")
        
        try:
            from spec_researcher_subagent import SpecResearcherSubagent
            orchestrator.register_subagent(SpecResearcherSubagent("spec_researcher"))
        except ImportError:
            self.logger.warning("Spec researcher subagent not available")
        
        return orchestrator
    
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
            self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
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
        
        # Add subagent configuration if present
        if 'subagents' in exp:
            config['subagents'] = exp['subagents']
        
        return config
    
    def run_experiment(self) -> Dict[str, Any]:
        """Run the experiment with integrated subagent support"""
        print(f"\n{'='*60}")
        print(f"Running Experiment: {self.config['experiment']['name']}")
        if self.enable_subagents:
            print("🤖 Subagent System: ENABLED")
        print(f"{'='*60}\n")
        
        # Validate environment
        if not self.validate_environment():
            return {'status': 'failed', 'error': 'Environment validation failed'}
        
        # Create analyzer configuration
        config = self.create_analyzer_config()
        
        # Run spec researcher subagent (if enabled) for quarterly review
        if self.orchestrator and self._should_run_spec_research():
            self.logger.info("Running spec researcher for quarterly review...")
            spec_results = self.orchestrator.execute_relevant_subagents(
                {'stage': 'quarterly_review'}, 
                {'config': config}
            )
            self._log_subagent_results('spec_researcher', spec_results)
        
        try:
            # Import and create analyzer
            from universal_sentiment_analyzer import UniversalSentimentAnalyzer
            analyzer = UniversalSentimentAnalyzer(config)
            
            # Pre-analysis: Data collection
            self.logger.info("Collecting data...")
            posts = analyzer.collect_social_media_posts()
            market_data = analyzer.collect_market_data()
            
            # Trigger data validator subagent
            validation_results = None
            if self.orchestrator:
                self.logger.info("Running data validation subagent...")
                validation_results = self.orchestrator.execute_relevant_subagents(
                    {'stage': 'pre_analysis'},
                    {'posts': posts, 'market_data': market_data}
                )
                self._log_subagent_results('data_validator', validation_results)
                
                # Check if validation passed
                if validation_results.get('data_validator', {}).get('validation_status') == 'failed':
                    return {
                        'status': 'failed', 
                        'error': 'Data validation failed',
                        'validation_details': validation_results['data_validator']
                    }
            
            # Trigger market context subagent
            market_context = None
            if self.orchestrator:
                self.logger.info("Running market context subagent...")
                market_context = self.orchestrator.execute_relevant_subagents(
                    {'stage': 'pre_stock_analysis'},
                    {
                        'start_date': config['social_media']['start_date'],
                        'end_date': config['social_media']['end_date'],
                        'symbols': config['market_data']['symbols']
                    }
                )
                self._log_subagent_results('market_context', market_context)
            
            # Run main analysis
            self.logger.info("Running sentiment analysis...")
            analyzer.posts = posts
            analyzer.market_data = market_data
            
            # Add context from subagents if available
            if market_context:
                analyzer.market_context = market_context.get('market_context', {})
            
            results = analyzer.analyze_sentiment()
            
            # Trigger statistical analyzer subagent
            statistical_results = None
            if self.orchestrator and self._should_run_statistical_analysis(config):
                self.logger.info("Running statistical analysis subagent...")
                statistical_results = self.orchestrator.execute_relevant_subagents(
                    {'stage': 'post_analysis'},
                    {'analysis_results': results}
                )
                self._log_subagent_results('statistical_analyzer', statistical_results)
                
                # Enhance results with statistical analysis
                if 'statistical_analyzer' in statistical_results:
                    results['statistical_analysis'] = statistical_results['statistical_analyzer']
            
            # Generate outputs with report generator subagent
            if self.orchestrator and self._should_generate_reports(config):
                self.logger.info("Running report generator subagent...")
                report_results = self.orchestrator.execute_relevant_subagents(
                    {'stage': 'report_generation'},
                    {
                        'results': results,
                        'config': config,
                        'validation_results': validation_results,
                        'market_context': market_context,
                        'statistical_results': statistical_results
                    }
                )
                self._log_subagent_results('report_generator', report_results)
            
            # Standard output generation
            self.generate_outputs(results, config)
            
            # Compile comprehensive results
            comprehensive_results = {
                'status': 'success',
                'experiment_name': config['experiment_name'],
                'posts_analyzed': len(results.get('posts', [])),
                'outputs_generated': config['output'],
                'subagent_reports': {
                    'validation': validation_results,
                    'market_context': market_context,
                    'statistical_analysis': statistical_results
                }
            }
            
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"Error running experiment: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _should_run_spec_research(self) -> bool:
        """Determine if spec research should run (quarterly)"""
        # Check if last run was more than 90 days ago
        last_run_file = self.output_dir / '.last_spec_research'
        if last_run_file.exists():
            last_run = datetime.fromtimestamp(last_run_file.stat().st_mtime)
            if (datetime.now() - last_run).days < 90:
                return False
        return True
    
    def _should_run_statistical_analysis(self, config: Dict[str, Any]) -> bool:
        """Determine if statistical analysis should run"""
        # Run if explicitly requested in config or for academic reports
        if 'subagents' in config and 'statistical_analyzer' in config.get('subagents', []):
            return True
        # Also run for reports marked as 'academic' or 'publication'
        for report in config.get('output', {}).get('reports', []):
            if report.get('style') in ['academic', 'publication']:
                return True
        return False
    
    def _should_generate_reports(self, config: Dict[str, Any]) -> bool:
        """Determine if report generator should run"""
        # Run if reports are specified in output
        return bool(config.get('output', {}).get('reports', []))
    
    def _log_subagent_results(self, subagent_name: str, results: Dict[str, Any]):
        """Log subagent execution results"""
        if subagent_name in results:
            result = results[subagent_name]
            if result.get('status') == 'error':
                self.logger.error(f"{subagent_name}: {result.get('error')}")
            else:
                self.logger.info(f"{subagent_name}: Completed successfully")
                if 'recommendations' in result:
                    for rec in result['recommendations']:
                        self.logger.info(f"  - Recommendation: {rec}")
    
    def generate_outputs(self, results: Dict[str, Any], config: Dict[str, Any]):
        """Generate all specified outputs"""
        # Create output directory if needed
        output_dir = self.output_dir / 'results' / config['experiment_name'].replace(' ', '_').lower()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save data exports
        for export in config['output']['data_exports']:
            if export['type'] == 'csv':
                df = pd.DataFrame(results.get('analysis', []))
                df.to_csv(output_dir / f"{export['filename']}.csv", index=False)
                self.logger.info(f"Saved CSV: {export['filename']}.csv")
            
            elif export['type'] == 'json':
                with open(output_dir / f"{export['filename']}.json", 'w') as f:
                    json.dump(results.get('posts', []), f, indent=2, default=str)
                self.logger.info(f"Saved JSON: {export['filename']}.json")
        
        # Generate report
        for report in config['output']['reports']:
            if report['type'] == 'markdown':
                self.generate_markdown_report(results, config, output_dir / f"{report['filename']}.md")
                self.logger.info(f"Generated report: {report['filename']}.md")
        
        self.logger.info(f"All outputs saved to: {output_dir}")
    
    def generate_markdown_report(self, results: Dict[str, Any], config: Dict[str, Any], output_path: Path):
        """Generate enhanced markdown report with subagent insights"""
        with open(output_path, 'w') as f:
            f.write(f"# {config['experiment_name']} Results\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Hypothesis**: {self.config['experiment']['hypothesis']}\n")
            f.write(f"**Subagent System**: {'Enabled' if self.enable_subagents else 'Disabled'}\n\n")
            
            # Summary statistics
            f.write("## Summary\n\n")
            f.write(f"- Total posts analyzed: {len(results.get('posts', []))}\n")
            f.write(f"- Date range: {config['social_media']['start_date']} to {config['social_media']['end_date']}\n")
            f.write(f"- Symbols tracked: {', '.join(config['market_data']['symbols'])}\n\n")
            
            # Data validation summary (if available)
            if 'validation' in results.get('subagent_reports', {}):
                validation = results['subagent_reports']['validation'].get('data_validator', {})
                if validation:
                    f.write("## Data Quality\n\n")
                    f.write(f"- Validation Status: **{validation.get('validation_status', 'Unknown')}**\n")
                    checks = validation.get('checks', {})
                    if 'completeness' in checks:
                        f.write(f"- Data Coverage: {checks['completeness'].get('coverage', 'N/A')}\n")
                    if validation.get('recommendations'):
                        f.write("\n### Data Quality Recommendations:\n")
                        for rec in validation['recommendations']:
                            f.write(f"- {rec}\n")
                    f.write("\n")
            
            # Market context summary (if available)
            if 'market_context' in results.get('subagent_reports', {}):
                context = results['subagent_reports']['market_context'].get('market_context', {})
                if context:
                    f.write("## Market Context\n\n")
                    market_info = context.get('market_context', {})
                    f.write(f"- General Trend: {market_info.get('general_trend', 'N/A')}\n")
                    f.write(f"- S&P 500 Change: {market_info.get('sp500_change', 'N/A')}\n")
                    f.write(f"- Sector Performance: {market_info.get('sector_performance', 'N/A')}\n")
                    if context.get('confounding_factors'):
                        f.write("\n### Confounding Factors:\n")
                        for factor in context['confounding_factors']:
                            f.write(f"- {factor}\n")
                    f.write("\n")
            
            # Sentiment distribution
            if 'sentiment_distribution' in results:
                f.write("## Sentiment Distribution\n\n")
                f.write("| Sentiment | Count | Percentage |\n")
                f.write("|-----------|-------|------------|\n")
                total_posts = sum(results['sentiment_distribution'].values())
                for sentiment, count in results['sentiment_distribution'].items():
                    pct = (count / total_posts) * 100 if total_posts > 0 else 0
                    f.write(f"| {sentiment} | {count} | {pct:.1f}% |\n")
                f.write("\n")
            
            # Statistical analysis (if available)
            if 'statistical_analysis' in results:
                stats = results['statistical_analysis']
                f.write("## Statistical Analysis\n\n")
                if 'correlation_results' in stats:
                    f.write("### Correlations\n\n")
                    for key, val in stats['correlation_results'].items():
                        f.write(f"- **{key}**: r={val.get('correlation', 'N/A')}, ")
                        f.write(f"p={val.get('p_value', 'N/A')}, ")
                        f.write(f"Significant: {val.get('significant', 'N/A')}\n")
                f.write("\n")
            
            # Methodology
            f.write("## Methodology\n\n")
            f.write(f"- Sentiment Model: {config['sentiment']['model']}\n")
            f.write(f"- Temperature: {config['sentiment']['temperature']}\n")
            f.write(f"- Time intervals analyzed: {config['analysis']['time_intervals']} hours\n")
            
            if self.enable_subagents:
                f.write("\n### Subagents Used\n")
                f.write("- Data Validator: Quality assurance\n")
                f.write("- Market Context: External factor analysis\n")
                f.write("- Statistical Analyzer: Rigorous validation\n")
                f.write("- Report Generator: Professional outputs\n")

def main():
    parser = argparse.ArgumentParser(description='Run hypothesis verification experiments with subagent support')
    parser.add_argument('template', help='Path to YAML template file')
    parser.add_argument('--output-dir', help='Output directory', default='.')
    parser.add_argument('--dry-run', action='store_true', help='Validate template without running')
    parser.add_argument('--no-subagents', action='store_true', help='Disable subagent system')
    parser.add_argument('--subagents-only', nargs='+', help='Run only specific subagents')
    
    args = parser.parse_args()
    
    # Create runner
    runner = EnhancedHypothesisRunner(
        args.template, 
        enable_subagents=not args.no_subagents
    )
    
    if args.output_dir:
        runner.output_dir = Path(args.output_dir)
    
    # Dry run mode
    if args.dry_run:
        print("Template loaded successfully!")
        print(f"Experiment: {runner.config['experiment']['name']}")
        print(f"Would analyze {runner.config['experiment']['data_sources']['social_media']['max_posts']} posts")
        if runner.enable_subagents:
            print("Subagents: ENABLED")
        return
    
    # Run experiment
    result = runner.run_experiment()
    
    if result['status'] == 'success':
        print(f"\n✅ Experiment completed successfully!")
        print(f"Analyzed {result['posts_analyzed']} posts")
        if runner.enable_subagents:
            print("\n📊 Subagent Reports Generated:")
            for subagent, report in result.get('subagent_reports', {}).items():
                if report:
                    print(f"  - {subagent}: ✓")
    else:
        print(f"\n❌ Experiment failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()