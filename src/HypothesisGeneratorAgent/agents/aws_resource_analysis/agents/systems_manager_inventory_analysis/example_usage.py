#!/usr/bin/env python3
"""
Example usage of the Systems Manager Inventory Analysis Agent

This script demonstrates how to use the agent both directly and as part of 
the parent AWS Resource Analysis Agent workflow.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def example_direct_usage():
    """Example of using the Systems Manager inventory analysis agent directly."""
    print("🔍 Direct Usage Example")
    print("=" * 50)
    
    from agent import systems_manager_inventory_analysis_agent
    
    # Example 1: Complete inventory report
    print("\n📋 Example 1: Complete Inventory Report")
    query1 = """
    Provide a complete inventory report for all managed instances in the current AWS account:
    1. A summary of all managed instances and their status
    2. All applications installed across the fleet with versions
    3. All running services and their configurations
    4. All installed packages and components
    5. System configurations and environment settings
    
    Focus on providing comprehensive inventory data.
    """
    
    try:
        result1 = systems_manager_inventory_analysis_agent(query1)
        print("✅ Analysis completed successfully")
        print(f"📄 Result preview: {result1[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Service inventory report
    print("\n⚙️ Example 2: Service Inventory Report")
    query2 = """
    Focus on service inventory of managed instances:
    1. List all running services and their status
    2. Document service configurations and parameters
    3. Report service startup dependencies
    4. List database clients and network services
    
    Provide detailed service inventory information.
    """
    
    try:
        result2 = systems_manager_inventory_analysis_agent(query2)
        print("✅ Security analysis completed successfully")
        print(f"📄 Result preview: {result2[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

def example_parent_agent_integration():
    """Example of how the parent AWS Resource Analysis Agent uses this sub-agent."""
    print("\n🏗️ Parent Agent Integration Example")
    print("=" * 50)
    
    try:
        # Import the parent agent using the correct relative import
        # We need to go up to the project root and then import properly
        sys.path.insert(0, str(project_root / "src"))
        
        from HypothesisGeneratorAgent.agents.aws_resource_analysis.agent import aws_resource_analysis_agent
        
        # The parent agent will automatically use the Systems Manager sub-agent
        # when it discovers managed instances
        query = """
        {
            "message": "Perform comprehensive AWS resource analysis including Systems Manager inventory",
            "workload_description": "Multi-tier web application with database backend",
            "aws_region": "us-east-1"
        }
        """
        
        print("📝 Parent agent query:")
        print(query)
        print("\n🚀 Executing parent agent (which will use the sub-agent)...")
        
        result = aws_resource_analysis_agent(query)
        print("✅ Parent agent analysis completed successfully")
        print(f"📄 Result preview: {result[:300]}...")
        
    except Exception as e:
        print(f"❌ Error with parent agent: {e}")

def example_specific_scenarios():
    """Examples of specific analysis scenarios."""
    print("\n🎯 Specific Scenario Examples")
    print("=" * 40)
    
    from agent import systems_manager_inventory_analysis_agent
    
    scenarios = [
        {
            "name": "Database Server Analysis",
            "description": "Focus on database-related software and configurations",
            "query": """
            Analyze managed instances for database-related software and configurations:
            1. Identify database clients and drivers (MySQL, PostgreSQL, Oracle, etc.)
            2. Check database connection configurations
            3. Assess database security settings
            4. Generate chaos engineering scenarios for database connectivity failures
            """
        },
        {
            "name": "Web Server Analysis", 
            "description": "Focus on web server software and configurations",
            "query": """
            Analyze managed instances for web server software and configurations:
            1. Identify web servers (Apache, Nginx, IIS, etc.) and their versions
            2. Check web server configurations and modules
            3. Assess SSL/TLS configurations
            4. Generate chaos engineering scenarios for web server failures
            """
        },
        {
            "name": "Container Runtime Analysis",
            "description": "Focus on container-related software",
            "query": """
            Analyze managed instances for container runtime software:
            1. Identify Docker, containerd, or other container runtimes
            2. Check container orchestration tools (Kubernetes agents, etc.)
            3. Assess container security configurations
            4. Generate chaos engineering scenarios for container failures
            """
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        
        try:
            result = systems_manager_inventory_analysis_agent(scenario['query'])
            print("✅ Analysis completed")
            print(f"📊 Result length: {len(result)} characters")
            
            # Show a snippet of the result
            lines = result.split('\n')[:5]
            print("📄 Result preview:")
            for line in lines:
                print(f"   {line}")
            if len(result.split('\n')) > 5:
                print("   ...")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function to run all examples."""
    print("🚀 Systems Manager Inventory Analysis Agent - Usage Examples")
    print("=" * 80)
    
    # Run direct usage examples
    example_direct_usage()
    
    # Run parent agent integration example
    example_parent_agent_integration()
    
    # Run specific scenario examples
    example_specific_scenarios()
    
    print("\n🎉 All examples completed!")
    print("\n💡 Tips for using this agent:")
    print("   • Ensure EC2 instances have SSM agent installed and running")
    print("   • Configure Systems Manager inventory collection")
    print("   • Use workload tags to filter analysis to specific applications")
    print("   • Review AWS permissions for Systems Manager access")
    print("   • Start with comprehensive analysis, then focus on specific areas")

if __name__ == "__main__":
    main()