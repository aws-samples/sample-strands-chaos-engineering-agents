# Systems Manager Document Generator Agent

A specialized sub-agent that creates AWS Systems Manager (SSM) documents for executing chaos engineering experiments directly on EC2 operating systems. This agent enables OS-level chaos experiments that go beyond what AWS FIS can provide.

## Overview

This agent is part of the ExperimentDesignAgent and focuses specifically on creating SSM documents for:

- **Operating system level experiments** (CPU stress, memory pressure, disk I/O)
- **Application service manipulation** (stop/start services, kill processes)
- **Network disruption at OS level** (disable adapters, firewall rules)
- **File system experiments** (disk space exhaustion, file corruption)
- **Custom chaos scenarios** not available in standard FIS actions

## Key Features

### 🖥️ **Multi-Platform Support**
- **Windows Server**: PowerShell-based experiments for IIS, SQL Server, .NET applications
- **Linux**: Bash/shell script experiments for Apache, MySQL, containerized applications
- **Cross-platform**: Generic experiments that work on both platforms

### ⚡ **Experiment Types**
- **Resource Exhaustion**: CPU stress, memory pressure, disk I/O saturation
- **Service Disruption**: Stop/start critical services (IIS, Apache, databases)
- **Process Management**: Kill/restart application processes
- **Network Chaos**: Network adapter manipulation, firewall rules
- **File System**: Disk space exhaustion, file corruption, permission changes

### 🛡️ **Safety Mechanisms**
- **Timeout controls** to prevent runaway experiments
- **Health checks** before and after experiments
- **Automatic rollback** procedures to restore system state
- **Resource limits** to prevent permanent system damage
- **Protected service exclusions** (SSM agent, critical system services)

## Usage

### As a Sub-Agent (Recommended)

The agent is automatically available as a tool within the parent ExperimentDesignAgent:

```python
from ExperimentDesignAgent.agent import agent as experiment_design_agent

# The parent agent will automatically use the SSM document generator
# when it detects the need for OS-level experiments
result = experiment_design_agent(
    "Generate experiments for IIS web server disruption hypotheses"
)
```

### Direct Usage

You can also use the agent directly:

```python
from ssm_document_generator.agent import ssm_document_generator_agent

# Windows IIS service disruption
result = ssm_document_generator_agent(
    "Create an SSM document to stop and restart IIS web server service on Windows Server instances for 5 minutes"
)

# Linux CPU stress testing
result = ssm_document_generator_agent(
    "Generate an SSM document for CPU stress testing on Linux instances with configurable intensity"
)

# Memory pressure testing
result = ssm_document_generator_agent(
    "Create an SSM document for memory pressure testing on Windows instances"
)
```

## Document Structure

### Standard SSM Document Format

```json
{
  "schemaVersion": "2.2",
  "description": "Chaos Engineering: CPU Stress Test",
  "parameters": {
    "Duration": {
      "type": "String",
      "description": "Experiment duration (e.g., PT5M for 5 minutes)",
      "default": "PT5M"
    },
    "Intensity": {
      "type": "String", 
      "description": "Experiment intensity (Low, Medium, High)",
      "default": "Low"
    }
  },
  "mainSteps": [
    {
      "action": "aws:runPowerShellScript",
      "name": "ExecuteExperiment",
      "inputs": {
        "timeoutSeconds": "600",
        "runCommand": ["# PowerShell experiment logic"]
      }
    }
  ]
}
```

### Safety Features

- **Pre-experiment health checks**
- **Configurable timeouts**
- **Automatic system restoration**
- **Resource usage limits**
- **Error handling and logging**

## Experiment Examples

### 1. IIS Web Server Disruption (Windows)

```powershell
# Stop IIS service for chaos testing
Write-Output "Starting IIS disruption experiment"
Stop-Service -Name W3SVC -Force
Start-Sleep -Seconds ([System.TimeSpan]::Parse($env:Duration).TotalSeconds)
Write-Output "Restoring IIS service"
Start-Service -Name W3SVC
```

### 2. CPU Stress Testing (Cross-Platform)

**Windows:**
```powershell
# CPU stress using PowerShell
$duration = [System.TimeSpan]::Parse($env:Duration)
$endTime = (Get-Date).Add($duration)
while ((Get-Date) -lt $endTime) {
    Start-Job -ScriptBlock { while ($true) { $result = 1..1000000 | ForEach-Object { $_ * $_ } } }
}
```

**Linux:**
```bash
# CPU stress using stress-ng
duration_seconds=$(echo $Duration | sed 's/PT\([0-9]*\)M/\1/' | awk '{print $1*60}')
stress-ng --cpu 0 --timeout ${duration_seconds}s
```

### 3. Memory Pressure Testing

```powershell
# Allocate memory to create pressure
$memoryMB = if ($env:Intensity -eq "High") { 2048 } elseif ($env:Intensity -eq "Medium") { 1024 } else { 512 }
$memoryArray = @()
for ($i = 0; $i -lt $memoryMB; $i++) {
    $memoryArray += New-Object byte[] 1MB
}
Start-Sleep -Seconds ([System.TimeSpan]::Parse($env:Duration).TotalSeconds)
```

## Integration with FIS

SSM documents can be executed through FIS using the `aws:ssm:send-command` action:

```json
{
  "experimentTemplateId": "EXT123456789",
  "actions": {
    "CPUStressTest": {
      "actionId": "aws:ssm:send-command",
      "parameters": {
        "documentArn": "arn:aws:ssm:us-east-1:123456789012:document/ChaosEngineering-CPUStress",
        "documentParameters": "{\"Duration\":\"PT5M\",\"Intensity\":\"Medium\"}",
        "duration": "PT10M"
      },
      "targets": {
        "WebServers": {
          "resourceType": "aws:ec2:instance",
          "resourceTags": {
            "Environment": "test",
            "Application": "web-server"
          },
          "selectionMode": "PERCENT(50)"
        }
      }
    }
  }
}
```

## Safety Guidelines

### Protected Resources (Never Target)

- ❌ **AWS SSM Agent** - Required for document execution
- ❌ **Critical system services** - Core OS functionality
- ❌ **Security services** - Antivirus, monitoring agents
- ❌ **Network connectivity to AWS** - Required for SSM communication

### Safe Targets

- ✅ **Business applications** - Web servers, databases, custom apps
- ✅ **Application services** - IIS, Apache, application-specific services
- ✅ **User processes** - Application processes, user sessions
- ✅ **Temporary resources** - Cache files, temporary directories

## Prerequisites

### AWS Permissions

The agent requires these AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:CreateDocument",
                "ssm:UpdateDocument",
                "ssm:GetDocument",
                "ssm:SendCommand",
                "ssm:ListCommandInvocations",
                "ssm:DescribeInstanceInformation"
            ],
            "Resource": "*"
        }
    ]
}
```

### EC2 Instance Requirements

- **SSM Agent installed** and running
- **Appropriate IAM role** for Systems Manager
- **Network connectivity** to AWS Systems Manager endpoints
- **Target instances tagged** appropriately for experiment targeting

## Best Practices

1. **Start Small**: Begin with low-intensity, short-duration experiments
2. **Test in Non-Production**: Always validate documents in development first
3. **Use Parameters**: Make experiments configurable through parameters
4. **Implement Timeouts**: Always include timeout mechanisms
5. **Monitor Continuously**: Ensure monitoring during experiments
6. **Document Everything**: Comprehensive logging for audit and debugging
7. **Gradual Rollout**: Test on single instances before broader deployment

## Error Handling

The agent handles common scenarios:

- **Instance offline or unreachable**
- **SSM agent not responding**
- **Insufficient permissions**
- **Resource constraints preventing execution**
- **Experiment timeout or failure**
- **Automatic rollback on errors**

## Testing

Run the test suite to verify functionality:

```bash
cd src/ExperimentDesignAgent/agents/ssm_document_generator
python test_agent.py
```

## Contributing

When extending this agent:

1. **Add new experiment types** by extending the system prompt
2. **Enhance safety mechanisms** with additional health checks
3. **Improve cross-platform support** with better OS detection
4. **Add new application targets** with specific service handling
5. **Extend monitoring capabilities** with better logging and metrics

## Related Documentation

- [AWS Systems Manager Documents](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html)
- [AWS Systems Manager Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html)
- [AWS FIS SSM Integration](https://docs.aws.amazon.com/fis/latest/userguide/actions-ssm-agent.html)
- [Chaos Engineering Best Practices](https://principlesofchaos.org/)