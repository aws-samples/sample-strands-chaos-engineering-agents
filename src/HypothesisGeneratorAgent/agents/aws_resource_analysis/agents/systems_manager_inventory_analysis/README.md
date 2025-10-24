# Systems Manager Inventory Analysis Agent

A specialized sub-agent that analyzes AWS Systems Manager inventory data to catalog what software, applications, and configurations are installed on **online EC2 instances only**. This agent focuses exclusively on instances that are currently online and actively reporting to Systems Manager (PingStatus=Online).

## Overview

This agent is part of the AWS Resource Analysis Agent and focuses specifically on cataloging Systems Manager inventory data from online EC2 instances to:

- **Catalog installed software and applications** on online EC2 instances
- **Document system configurations** and installed packages on active instances
- **Report running services** and their current status on online instances
- **List installed components** and their versions on managed EC2 instances
- **Provide inventory data** from online instances only for use by other analysis agents

## Key Features

### 🔍 **Comprehensive Software Inventory**
- Catalogs all installed applications and their versions
- Lists running services and their status
- Documents installed packages and components
- Reports custom or third-party applications
- Identifies runtime environments (Java, Python, Node.js, .NET)

### ⚙️ **Configuration Inventory**
- Documents OS configurations and parameters
- Reports network settings and interfaces
- Lists security settings and policies
- Documents resource configurations (memory, CPU, disk)
- Reports environment variables and application settings

### 🔗 **Service Documentation**
- Lists all running services and their status
- Documents service configurations
- Reports service startup dependencies
- Lists database clients and drivers
- Documents network services and configurations

## Usage

### As a Sub-Agent (Recommended)

The agent is automatically available as a tool within the parent AWS Resource Analysis Agent:

```python
from HypothesisGeneratorAgent.agents.aws_resource_analysis.agent import aws_resource_analysis_agent

# The parent agent will automatically use the Systems Manager inventory analysis
# when it discovers managed instances
result = aws_resource_analysis_agent(
    "Analyze AWS resources including Systems Manager inventory data"
)
```

### Direct Usage

You can also use the agent directly:

```python
from systems_manager_inventory_analysis.agent import systems_manager_inventory_analysis_agent

# Complete inventory report
result = systems_manager_inventory_analysis_agent(
    "Provide a complete inventory of all software installed on managed instances"
)

# Application inventory
result = systems_manager_inventory_analysis_agent(
    "List all applications and their versions across all managed instances"
)

# Service inventory
result = systems_manager_inventory_analysis_agent(
    "Report on all running services and their configurations in the managed fleet"
)
```

## Analysis Process

### 1. **Online EC2 Instance Discovery**
- Lists online EC2 instances using `describe-instance-information` with PingStatus=Online filter
- **Excludes offline, stopped, or unreachable instances**
- Filters instances based on workload tags if provided
- Identifies instance types, operating systems, and SSM agent versions for online instances only
- Verifies instances have recent contact times

### 2. **Inventory Collection**
- Collects application inventory using `get-inventory` with `AWS:Application` type
- Gathers service inventory using `AWS:Service` type
- Collects network configuration using `AWS:Network` type
- Collects custom inventory types if configured

### 3. **Analysis & Risk Assessment**
- Analyzes critical applications and their versions
- Identifies security vulnerabilities and outdated software
- Maps service dependencies and potential failure points
- Assesses configuration risks and compliance gaps
- Generates chaos engineering opportunities

## Output Format

The agent provides structured analysis including:

### **Instance Summary**
- Total managed instances by OS type
- Instance types and last contact status
- SSM agent health and version information

### **Software Inventory**
- Critical applications with versions and risk levels
- Detected vulnerabilities with CVE information
- Service dependencies and startup requirements
- Runtime environments and their configurations

### **Configuration Analysis**
- System resource utilization and limits
- Network configuration and security groups
- Security settings and compliance status
- Environment variables and application settings

### **Chaos Engineering Insights**
- Specific failure scenarios based on installed software
- Application failure testing opportunities
- Resource exhaustion testing targets
- Dependency failure testing scenarios

## Prerequisites

### AWS Permissions
The agent requires the following AWS permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetInventory",
                "ssm:DescribeInstanceInformation",
                "ssm:ListInventoryEntries",
                "ssm:ListComplianceItems",
                "ssm:ListComplianceSummaries",
                "ssm:DescribeInstancePatchStates",
                "ssm:ListAssociations"
            ],
            "Resource": "*"
        }
    ]
}
```

### Systems Manager Setup - Online EC2 Instances Only
- **EC2 instances must be online** with PingStatus=Online in Systems Manager
- EC2 instances must have the SSM agent installed and running
- Instances must have appropriate IAM roles for Systems Manager
- Inventory collection must be configured (automatic or manual)
- **Only instances showing as "Online" will be analyzed** - offline instances are skipped
- Instances should have recent contact times (within 24 hours recommended)

## Integration with Chaos Engineering

The analysis directly feeds into chaos engineering hypothesis generation by:

1. **Identifying Critical Applications**: Pinpoints applications whose failure would impact the system
2. **Mapping Dependencies**: Shows which services depend on others for failure cascade testing
3. **Finding Vulnerabilities**: Identifies security weaknesses that could be exploited in tests
4. **Resource Constraints**: Identifies systems under resource pressure for stress testing
5. **Configuration Risks**: Finds misconfigurations that could cause failures

## Example Analysis Output

```
SYSTEMS MANAGER INVENTORY ANALYSIS - ONLINE EC2 INSTANCES ONLY
==============================================================

Online EC2 Instances: 12 total (PingStatus=Online)
- Linux: 8 instances
- Windows: 4 instances  
- All instances reporting within last 24 hours

CRITICAL APPLICATIONS DETECTED
==============================
Instance: i-1234567890abcdef0 (web-server-1)
- Apache HTTP Server 2.4.41 (Critical - Web Service)
- MySQL Client 8.0.25 (High - Database Connectivity)
- Node.js 14.17.0 (High - Application Runtime)
- PM2 5.1.0 (Medium - Process Manager)

POTENTIAL VULNERABILITIES
========================
- Apache HTTP Server 2.4.41: CVE-2021-44790 (High)
- Node.js 14.17.0: End of Life, upgrade recommended

CHAOS ENGINEERING OPPORTUNITIES
===============================
1. Application Failure Testing
   - Target: Apache HTTP Server process termination
   - Impact: Web service unavailability
   - Recovery: PM2 auto-restart capability

2. Resource Exhaustion Testing
   - Target: Memory pressure on high-utilization instances
   - Impact: Application performance degradation
   - Recovery: Auto-scaling group response
```

## Testing

Run the test suite to verify functionality:

```bash
cd src/HypothesisGeneratorAgent/agents/aws_resource_analysis/agents/systems_manager_inventory_analysis
python test_agent.py
```

## Online Instance Filtering and Error Handling

The agent focuses exclusively on online EC2 instances and:
- **Skips offline, stopped, or unreachable instances entirely**
- Only processes instances with PingStatus=Online and ResourceType=EC2Instance
- Gracefully handles missing inventory data for online instances
- Provides partial results when some online instance data is unavailable
- Handles AWS API rate limiting and service quotas
- Validates inventory data before reporting
- Logs when instances are skipped due to offline status

## Contributing

When extending this agent:

1. **Add new inventory types** by extending the analysis logic
2. **Enhance vulnerability detection** by integrating with security databases
3. **Improve dependency mapping** by analyzing configuration files
4. **Add compliance checks** for specific regulatory requirements
5. **Extend chaos engineering scenarios** based on new software patterns

## Related Documentation

- [AWS Systems Manager Inventory](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-inventory.html)
- [AWS Systems Manager Agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html)
- [Chaos Engineering Best Practices](https://principlesofchaos.org/)
- [AWS Fault Injection Service](https://docs.aws.amazon.com/fis/latest/userguide/what-is.html)