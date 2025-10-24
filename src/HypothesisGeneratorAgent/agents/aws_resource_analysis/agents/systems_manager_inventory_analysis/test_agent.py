#!/usr/bin/env python3
"""
Test script for the Systems Manager Inventory Analysis Agent
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agent import systems_manager_inventory_analysis_agent

def test_basic_functionality():
    """Test basic functionality of the Systems Manager inventory analysis agent."""
    print("🧪 Testing Systems Manager Inventory Analysis Agent")
    print("=" * 60)
    
    # Test query
    test_query = """
    Analyze all managed instances in the current AWS account and identify:
    1. Critical applications and their versions
    2. Potential security vulnerabilities
    3. System configurations that could impact resilience
    4. Chaos engineering opportunities based on installed software
    
    Focus on providing actionable insights for chaos engineering hypothesis generation.
    """
    
    print("📝 Test Query:")
    print(test_query)
    print("\n🚀 Executing agent...")
    
    try:
        result = systems_manager_inventory_analysis_agent(test_query)
        print("\n✅ Agent executed successfully!")
        print("\n📄 Results:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
    except Exception as e:
        print(f"\n❌ Error executing agent: {e}")
        import traceback
        traceback.print_exc()

def test_specific_scenarios():
    """Test specific analysis scenarios."""
    print("\n🎯 Testing Specific Scenarios")
    print("=" * 40)
    
    scenarios = [
        {
            "name": "Critical Application Analysis",
            "query": "Identify critical applications and their dependencies across all managed instances"
        },
        {
            "name": "Security Vulnerability Assessment", 
            "query": "Assess security vulnerabilities and configuration risks in the managed fleet"
        },
        {
            "name": "Chaos Engineering Hypothesis Generation",
            "query": "Generate chaos engineering hypotheses based on installed software and configurations"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"Query: {scenario['query']}")
        
        try:
            result = systems_manager_inventory_analysis_agent(scenario['query'])
            print("✅ Success")
            print(f"Result length: {len(result)} characters")
            
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("🔬 Systems Manager Inventory Analysis Agent Test Suite")
    print("=" * 70)
    
    # Run basic functionality test
    test_basic_functionality()
    
    # Run specific scenario tests
    test_specific_scenarios()
    
    print("\n🎉 Test suite completed!")