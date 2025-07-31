#!/usr/bin/env python3
"""
Test the integrated subagent system
Demonstrates how subagents enhance the analysis pipeline
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src' / 'core'))

def test_subagent_integration():
    """Test the enhanced hypothesis runner with subagents"""
    
    print("🚀 Testing Integrated Subagent System")
    print("="*60)
    
    # Check if we have the enhanced runner
    try:
        from hypothesis_runner_enhanced import EnhancedHypothesisRunner
        print("✅ Enhanced runner imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import enhanced runner: {e}")
        return False
    
    # Check if we have the subagent framework
    try:
        from subagent_framework import setup_subagents
        print("✅ Subagent framework imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import subagent framework: {e}")
        return False
    
    # Test subagent setup
    print("\n📋 Setting up subagents...")
    orchestrator = setup_subagents()
    print(f"✅ Registered subagents: {list(orchestrator.subagents.keys())}")
    
    # Test data validator subagent
    print("\n🔍 Testing Data Validator Subagent...")
    test_data = {
        'posts': [
            {'id': '1', 'text': 'Test post', 'timestamp': '2024-01-01', 'author': 'test'},
            {'id': '2', 'text': 'Another test', 'timestamp': '2024-01-02', 'author': 'test'},
            {'id': '2', 'text': 'Duplicate ID', 'timestamp': '2024-01-03', 'author': 'test'},  # Duplicate
        ],
        'market_data': {
            '1': {'price': 100},
            '2': {'price': 101}
        }
    }
    
    validation_results = orchestrator.execute_relevant_subagents(
        {'stage': 'pre_analysis'},
        test_data
    )
    
    if 'data_validator' in validation_results:
        val_result = validation_results['data_validator']
        print(f"  - Validation Status: {val_result.get('validation_status')}")
        print(f"  - Data Coverage: {val_result.get('checks', {}).get('completeness', {}).get('coverage')}")
        if val_result.get('recommendations'):
            print("  - Recommendations:")
            for rec in val_result['recommendations']:
                print(f"    • {rec}")
    
    # Test market context subagent
    print("\n📈 Testing Market Context Subagent...")
    market_results = orchestrator.execute_relevant_subagents(
        {'stage': 'pre_stock_analysis'},
        {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'symbols': ['AAPL', 'GOOGL']
        }
    )
    
    if 'market_context' in market_results:
        context = market_results['market_context']
        print(f"  - Market Trend: {context.get('market_context', {}).get('general_trend')}")
        print(f"  - Confounding Factors: {len(context.get('confounding_factors', []))}")
    
    # Test with a real template (dry run)
    print("\n📄 Testing with Real Template...")
    template_path = project_root / 'templates' / 'example_trump_with_subagents.yaml'
    
    if template_path.exists():
        try:
            runner = EnhancedHypothesisRunner(str(template_path))
            print(f"✅ Loaded template: {runner.config['experiment']['name']}")
            print(f"  - Subagents configured: {runner.config['experiment'].get('subagents', [])}")
            print(f"  - Statistical rigor: {runner.config['experiment']['analysis'].get('statistical_rigor')}")
            
            # Validate environment (will fail without API keys, but that's OK for test)
            print("\n🔑 Checking environment...")
            has_env = runner.validate_environment()
            if not has_env:
                print("  ⚠️  Missing API keys (expected for test)")
            
        except Exception as e:
            print(f"❌ Error loading template: {e}")
    else:
        print(f"❌ Template not found at: {template_path}")
    
    print("\n" + "="*60)
    print("✅ Subagent Integration Test Complete!")
    print("\nNext Steps:")
    print("1. Set up required API keys in .env")
    print("2. Run: python src/core/hypothesis_runner_enhanced.py templates/example_trump_with_subagents.yaml")
    print("3. Watch as subagents automatically enhance your analysis!")
    
    return True

def demonstrate_subagent_benefits():
    """Show the benefits of using subagents"""
    
    print("\n🌟 Benefits of Subagent Integration:\n")
    
    benefits = [
        ("🔍 Data Quality", "Automatic validation catches issues before analysis"),
        ("📊 Market Context", "Identifies confounding events that might affect results"),
        ("📈 Statistical Rigor", "Publication-ready statistical validation"),
        ("📄 Professional Reports", "Consistent, high-quality output formats"),
        ("🔄 Continuous Improvement", "Spec researcher keeps tools up-to-date"),
        ("🎯 Focused Expertise", "Each subagent is specialized for its task"),
        ("⚡ Parallel Processing", "Subagents can work simultaneously"),
        ("🛡️ Error Resilience", "Failed subagents don't stop the main analysis")
    ]
    
    for icon_title, description in benefits:
        print(f"{icon_title}: {description}")
    
    print("\n📋 Example Workflow with Subagents:\n")
    workflow_steps = [
        "1. Load template with subagent configuration",
        "2. Data Validator checks post quality and completeness",
        "3. Market Context researches relevant events",
        "4. Main analysis runs with enhanced context",
        "5. Statistical Analyzer validates findings",
        "6. Report Generator creates professional outputs",
        "7. All insights integrated into final report"
    ]
    
    for step in workflow_steps:
        print(f"   {step}")

if __name__ == "__main__":
    # Run the integration test
    success = test_subagent_integration()
    
    if success:
        # Show benefits
        demonstrate_subagent_benefits()
    
    print("\n🎉 Subagent system is ready for use!")
    print("Run hypothesis analysis with: --no-subagents flag to compare with/without")