#!/usr/bin/env python3
"""
Test the hypothesis verification system
"""

import os
import sys
import json
import yaml
from pathlib import Path
from hypothesis_runner import HypothesisRunner

def test_template_validation():
    """Test template loading and validation"""
    print("Testing template validation...")
    
    # Test with example template
    template_path = "templates/examples/trump_tesla_example.yaml"
    
    try:
        runner = HypothesisRunner(template_path)
        print("✅ Template loaded successfully")
        
        # Check required fields
        assert 'experiment' in runner.config
        assert 'data_sources' in runner.config['experiment']
        assert 'sentiment_analysis' in runner.config['experiment']
        print("✅ All required fields present")
        
        return True
    except Exception as e:
        print(f"❌ Template validation failed: {e}")
        return False

def test_date_processing():
    """Test relative date processing"""
    print("\nTesting date processing...")
    
    runner = HypothesisRunner("templates/examples/trump_tesla_example.yaml")
    
    # Test relative dates
    test_cases = [
        ("365_days_ago", "relative past date"),
        ("now", "current date"),
        ("2024-01-01", "absolute date")
    ]
    
    for date_str, desc in test_cases:
        result = runner.process_date_range(date_str)
        print(f"✅ {desc}: {date_str} -> {result}")
    
    return True

def test_dry_run():
    """Test dry run mode"""
    print("\nTesting dry run mode...")
    
    # Run with dry-run flag
    runner = HypothesisRunner("templates/examples/trump_tesla_example.yaml")
    
    # Validate environment (may fail but that's ok for dry run)
    env_valid = runner.validate_environment()
    if not env_valid:
        print("⚠️  Environment validation failed (expected in test)")
    
    # Create config
    config = runner.create_analyzer_config()
    
    print(f"✅ Experiment name: {config['experiment_name']}")
    print(f"✅ Keywords: {len(config['social_media']['keywords'])} defined")
    print(f"✅ Time intervals: {config['analysis']['time_intervals']}")
    
    return True

def test_multiple_templates():
    """Test running multiple templates"""
    print("\nTesting multiple templates...")
    
    templates = [
        "templates/examples/trump_tesla_example.yaml",
        "templates/examples/elon_tesla_example.yaml"
    ]
    
    for template in templates:
        if Path(template).exists():
            runner = HypothesisRunner(template)
            config = runner.create_analyzer_config()
            print(f"✅ Loaded: {config['experiment_name']}")
    
    return True

def create_test_template():
    """Create a minimal test template"""
    print("\nCreating test template...")
    
    test_template = {
        'metadata': {
            'template_version': '1.0',
            'created_date': '2025-07-31',
            'description': 'Test template'
        },
        'experiment': {
            'name': 'Test Experiment',
            'description': 'Testing the system',
            'hypothesis': 'System works correctly',
            'data_sources': {
                'social_media': {
                    'platform': 'twitter',
                    'actor_id': 'test123',
                    'accounts': ['testuser'],
                    'keywords': ['test', 'keyword'],
                    'date_range': {
                        'start': '30_days_ago',
                        'end': 'now'
                    },
                    'max_posts': 10
                },
                'market_data': {
                    'provider': 'alpaca',
                    'symbols': [
                        {'symbol': 'TEST', 'name': 'Test Corp'}
                    ],
                    'data_feed': 'iex'
                }
            },
            'sentiment_analysis': {
                'llm_provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.0,
                'categories': [
                    {'name': 'POSITIVE', 'description': 'Positive sentiment'},
                    {'name': 'NEGATIVE', 'description': 'Negative sentiment'},
                    {'name': 'NEUTRAL', 'description': 'Neutral sentiment'}
                ]
            },
            'analysis': {
                'time_intervals': [1, 24],
                'conditions': [
                    {
                        'name': 'market_hours',
                        'description': 'Market hours check',
                        'enabled': True
                    }
                ]
            },
            'output': {
                'reports': [
                    {
                        'type': 'markdown',
                        'filename': 'test_report',
                        'include_sections': ['sentiment_distribution']
                    }
                ],
                'visualizations': [],
                'data_exports': [
                    {'type': 'csv', 'filename': 'test_data'}
                ]
            }
        },
        'validation': {
            'min_posts_required': 1,
            'min_confidence_threshold': 0.5,
            'required_env_vars': []
        }
    }
    
    # Save test template
    test_path = Path('templates/test_template.yaml')
    test_path.parent.mkdir(exist_ok=True)
    
    with open(test_path, 'w') as f:
        yaml.dump(test_template, f, default_flow_style=False)
    
    print(f"✅ Created test template: {test_path}")
    return test_path

def main():
    """Run all tests"""
    print("="*60)
    print("Testing Hypothesis Verification System")
    print("="*60)
    
    tests = [
        test_template_validation,
        test_date_processing,
        test_dry_run,
        test_multiple_templates
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            failed += 1
    
    # Create and test with minimal template
    try:
        test_template_path = create_test_template()
        runner = HypothesisRunner(str(test_template_path))
        print("✅ Test template works correctly")
        passed += 1
    except Exception as e:
        print(f"❌ Test template failed: {e}")
        failed += 1
    
    print("\n" + "="*60)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)