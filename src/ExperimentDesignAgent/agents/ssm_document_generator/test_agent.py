#!/usr/bin/env python3
"""
Test script for the Systems Manager Document Generator Agent
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_basic_functionality():
    """Test basic functionality of the SSM document generator agent."""
    print("🧪 Testing Systems Manager Document Generator Agent")
    print("=" * 70)
    
    from agent import ssm_document_generator_agent
    
    # Test query for IIS web server disruption with knowledge base integration
    test_query = """
    Create an SSM document to stop and restart IIS web server service on Windows Server instances.
    
    Requirements:
    - Follow AWS best practices from the knowledge base
    - Duration should be configurable (default 5 minutes)
    - Include safety checks before and after the experiment
    - Implement automatic rollback if something goes wrong
    - Add logging for audit purposes
    - Use AWS recommended parameter validation patterns
    - Implement proper error handling as per AWS guidelines
    """
    
    print("📝 Test Query:")
    print(test_query)
    print("\n🚀 Executing agent...")
    
    try:
        result = ssm_document_generator_agent(test_query)
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
    """Test specific SSM document generation scenarios."""
    print("\n🎯 Testing Specific Scenarios")
    print("=" * 40)
    
    from agent import ssm_document_generator_agent
    
    scenarios = [
        {
            "name": "Application Process Termination",
            "query": "Generate an SSM document to kill and restart specific application processes with AWS recommended error handling"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"Query: {scenario['query']}")
        
        try:
            result = ssm_document_generator_agent(scenario['query'])
            print("✅ Success")
            print(f"Result length: {len(result)} characters")
            
            # Check if result contains expected SSM document elements
            if '"schemaVersion"' in result and '"mainSteps"' in result:
                print("✅ Contains valid SSM document structure")
            else:
                print("⚠️ May not contain valid SSM document structure")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def test_windows_iis_interruption():
    """Test creating SSM document to interrupt Windows IIS/web services."""
    print("\n🌐 Testing Windows IIS/Web Services Interruption")
    print("=" * 55)
    
    from agent import ssm_document_generator_agent
    
    # Test query specifically for IIS web service interruption
    iis_test_query = """
    Create an SSM document to interrupt Windows IIS web services for chaos engineering testing.
    
    Requirements:
    1. Target Windows Server instances running IIS
    2. Stop the W3SVC (World Wide Web Publishing Service) 
    3. Optionally stop related services like WAS (Windows Process Activation Service)
    4. Duration should be configurable (default: PT5M for 5 minutes)
    5. Intensity levels: Low (stop W3SVC only), Medium (stop W3SVC + WAS), High (stop all IIS-related services)
    6. Include pre-experiment health checks to verify IIS is running
    7. Implement automatic service restart after experiment duration
    8. Add comprehensive logging for audit and monitoring
    9. Include rollback procedures if experiment fails
    10. Follow AWS best practices for SSM document structure
    11. Add safety timeouts to prevent indefinite service outage
    12. Validate that services restart successfully
    
    The document should be production-ready for testing web application resilience.
    """
    
    print("📝 IIS Interruption Test Query:")
    print(iis_test_query)
    print("\n🚀 Executing agent for IIS service interruption...")
    
    try:
        result = ssm_document_generator_agent(iis_test_query)
        print("✅ IIS interruption SSM document generated successfully")
        
        # Check for production-ready IIS elements
        iis_indicators = [
            "IISAppPoolName",
            "WebAdministration", 
            "Get-IISAppPool",
            "Stop-WebAppPool",
            "Start-WebAppPool",
            "DefaultAppPool"
        ]
        
        found_indicators = [indicator for indicator in iis_indicators if indicator in result]
        print(f"✅ Found production IIS elements: {found_indicators}")
        
        # Check for production-ready features
        production_features = [
            "ValidatePrerequisites",
            "allowedPattern",
            "precondition",
            "platformType",
            "Write-Log",
            "fis_windows_iis_experiment.json",
            "onFailure",
            "timeoutSeconds"
        ]
        
        found_features = [feature for feature in production_features if feature in result]
        print(f"✅ Found production features: {found_features}")
        
        # Check for multi-step architecture
        required_steps = [
            "ValidatePrerequisites",
            "StopIISAppPool", 
            "RestoreIISAppPool"
        ]
        
        found_steps = [step for step in required_steps if step in result]
        print(f"✅ Found required steps: {found_steps}")
        
        # Check for proper SSM document structure
        if '"schemaVersion": "2.2"' in result and '"mainSteps"' in result:
            print("✅ Contains valid SSM document structure")
        else:
            print("⚠️ May not contain valid SSM document structure")
            
        # Production readiness score
        total_checks = len(production_features) + len(required_steps) + len(iis_indicators)
        found_checks = len(found_features) + len(found_steps) + len(found_indicators)
        score = (found_checks / total_checks) * 100
        print(f"📊 Production readiness score: {score:.1f}%")
            
        print(f"📊 Document length: {len(result)} characters")
        
        # Show a preview of the generated document
        print("\n📄 Document Preview (first 500 characters):")
        print("-" * 50)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ IIS interruption test failed: {e}")
        import traceback
        traceback.print_exc()

def test_knowledge_base_integration():
    """Test knowledge base integration for AWS best practices."""
    print("\n📚 Testing Knowledge Base Integration")
    print("=" * 45)
    
    from agent import ssm_document_generator_agent
    
    # Test query that explicitly requires knowledge base consultation
    kb_test_query = """
    Create an SSM document for IIS service disruption that strictly follows AWS best practices.
    
    Requirements:
    1. Consult the knowledge base for SSM document best practices
    2. Apply AWS recommended document structure and schema
    3. Implement AWS recommended parameter validation
    4. Use AWS recommended error handling patterns
    5. Include AWS recommended security measures
    6. Follow AWS recommended logging and monitoring practices
    
    The document should demonstrate adherence to the AWS best practices guide.
    """
    
    print("📝 Knowledge Base Test Query:")
    print(kb_test_query)
    print("\n🚀 Executing agent with knowledge base requirements...")
    
    try:
        result = ssm_document_generator_agent(kb_test_query)
        print("✅ Knowledge base integration test completed")
        
        # Check for indicators of knowledge base usage
        if "retrieve" in result.lower() or "best practices" in result.lower():
            print("✅ Agent appears to be using knowledge base")
        else:
            print("⚠️ May not be fully utilizing knowledge base")
            
        print(f"📄 Result length: {len(result)} characters")
        
    except Exception as e:
        print(f"❌ Knowledge base integration test failed: {e}")

def test_integration_with_parent():
    """Test integration with the parent ExperimentDesignAgent."""
    print("\n🔗 Testing Integration with Parent Agent")
    print("=" * 50)
    
    try:
        # Import the parent agent
        from ExperimentDesignAgent.agent import agent as experiment_design_agent
        
        # Test query that should trigger SSM document generation
        query = """
        Generate an experiment for a hypothesis that requires IIS web server service disruption.
        The experiment should stop the IIS service for 5 minutes and then restart it.
        This is for testing web application resilience on Windows Server instances.
        """
        
        print("📝 Parent agent query:")
        print(query)
        print("\n🚀 Executing parent agent (which should use the sub-agent)...")
        
        result = experiment_design_agent(query)
        print("✅ Parent agent executed successfully")
        print(f"📄 Result preview: {str(result)[:300]}...")
        
    except Exception as e:
        print(f"❌ Error with parent agent integration: {e}")

if __name__ == "__main__":
    print("🔬 Systems Manager Document Generator Agent Test Suite")
    print("=" * 80)
    
    # Run basic functionality test
    test_basic_functionality()
    
    # Run specific scenario tests
    test_specific_scenarios()
    
    # Test Windows IIS interruption (key use case)
    test_windows_iis_interruption()
    
    # Test knowledge base integration
    test_knowledge_base_integration()
    
    # Test integration with parent agent
    test_integration_with_parent()
    
    print("\n🎉 Test suite completed!")