# ExperimentDesignAgent

An AWS Fault Injection Service (FIS) expert agent built with Strands Agents SDK. This agent specializes in generating production-ready, validated FIS experiment templates by fetching live AWS documentation and saving experiments to a database for tracking and hypothesis validation.

## Features

- **Live Documentation Access**: Fetches current AWS FIS documentation from official sources to ensure accuracy
- **Hypothesis-Driven Design**: Generates experiments based on specific hypotheses and testing goals
- **Database Integration**: Saves all experiments to database for tracking and traceability  
- **Multi-Service Support**: Generates experiments for ECS, EKS, Lambda, EC2, and other AWS services
- **Production-Ready Templates**: Templates include all required fields and follow AWS best practices
- **Safety-First Approach**: Automatically applies appropriate targeting limits and stop conditions

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have proper AWS credentials configured and access to Amazon Bedrock models.

3. Set up the database infrastructure (see SETUP.md for details).

## Usage

### Running the Agent with Database-First Approach

The agent now uses a database-first approach where it fetches hypotheses from the database and generates experiments based on natural language requests:

```python
from agent import agent

# Example: Generate experiment for a specific hypothesis
response = agent("Generate experiment for hypothesis ID 1")
print(response.message)

# Example: Generate experiments for multiple hypotheses
response = agent("Generate experiments for hypothesis IDs 1, 2, 3")
print(response.message)

# Example: Generate experiments for all ECS hypotheses
response = agent("Generate experiments for all ECS hypotheses")
print(response.message)

# Example: Generate experiments for high priority hypotheses
response = agent("Generate experiments for high priority hypotheses")
print(response.message)
```

### Running from Command Line

```bash
python agent.py
```

### JSON Input Structure

The agent expects a structured JSON input with the following fields:

```json
{
  "hypothesis_id": 123,                    // Required: Database ID of the hypothesis
  "hypothesis_text": "string",             // Required: Human-readable description
  "target_service": "ECS|EC2|RDS|Lambda",  // Required: AWS service being tested
  "expected_behavior": "string",           // Required: What should remain stable
  "failure_mode": "string",                // Required: What failure is being simulated
  "success_criteria": {                     // Required: Metrics and thresholds
    "metric": "string",
    "threshold": number,
    "unit": "string"
  },
  "target_resources": {                     // Required: Resource targeting info
    "resource_type": "aws:service:resource", // AWS resource type
    "tags": {"key": "value"},              // Resource tags for targeting
    "selection_criteria": "string"          // How many resources to target
  }
}
```

### Example JSON Inputs

**ECS Container Restart:**
```json
{
  "hypothesis_id": 1,
  "hypothesis_text": "API maintains performance during ECS task restarts",
  "target_service": "ECS",
  "expected_behavior": "Response time < 500ms",
  "failure_mode": "Container restarts",
  "success_criteria": {
    "metric": "response_time",
    "threshold": 500,
    "unit": "ms"
  },
  "target_resources": {
    "resource_type": "aws:ecs:task",
    "tags": {"Environment": "test"},
    "selection_criteria": "50% of containers"
  }
}
```

**EC2 Instance Failure:**
```json
{
  "hypothesis_id": 2,
  "hypothesis_text": "Database remains available when one EC2 instance fails",
  "target_service": "EC2",
  "expected_behavior": "Database connections maintained",
  "failure_mode": "Instance termination",
  "success_criteria": {
    "metric": "database_connections",
    "threshold": 95,
    "unit": "percent"
  },
  "target_resources": {
    "resource_type": "aws:ec2:instance",
    "tags": {"Environment": "test", "Role": "database"},
    "selection_criteria": "1 instance"
  }
}
```



## Available Tools

The agent uses focused tools for documentation lookup and database persistence:

### FIS Documentation Tool
- **`get_fis_documentation(service)`**: Get URLs for current AWS FIS documentation
  - Supports: general, ecs, eks, lambda, ec2, ssm
  - Returns documentation URLs to fetch with http_request

### Database Tool  
- **`save_experiment_to_database(...)`**: Save experiments to database for tracking
  - Links experiments to hypotheses for traceability
  - Stores complete FIS configuration and experiment plan
  - Returns experiment ID for tracking

### Core Tools
- **`http_request`**: Fetch live AWS documentation content
- **`current_time`**: Get current timestamp for experiment metadata

## Agent Workflow

The agent follows a focused 4-step workflow:

1. **Understand Hypothesis**: Parse what the user wants to test and extract key parameters
2. **Check Documentation**: Fetch current AWS FIS documentation to find valid actions and parameters  
3. **Generate Template**: Create complete FIS experiment JSON with appropriate targeting and actions
4. **Save to Database**: Persist experiment for tracking and hypothesis validation

### Example Workflow

Input: *"API maintains performance during ECS task restarts"*

1. **Hypothesis Analysis**: 
   - Target service: ECS
   - Goal: Test API performance during task restarts
   - Selection mode: Based on restart scenario

2. **Documentation Check**:
   - Fetch AWS FIS ECS documentation
   - Find actions like `aws:ecs:task-kill-process` for task restarts

3. **Template Generation**:
   ```json
   {
     "description": "Test API performance during ECS task restarts",
     "targets": {
       "ecsTargets": {
         "resourceType": "aws:ecs:task",
         "resourceTags": {"Environment": "test"},
         "selectionMode": "PERCENT(50)"
       }
     },
     "actions": {
       "killTasks": {
         "actionId": "aws:ecs:task-kill-process",
         "parameters": {"processName": "api-process"},
         "targets": {"Tasks": "ecsTargets"}
       }
     },
     "stopConditions": [{"source": "none"}],
     "roleArn": "arn:aws:iam::ACCOUNT_ID:role/FISExperimentRole",
     "tags": {
       "Name": "ECS-Task-Restart-Test",
       "Purpose": "Performance-Testing"
     }
   }
   ```

4. **Database Persistence**: Save experiment with tracking ID

## Intelligent Selection Modes

The agent analyzes hypotheses to determine appropriate targeting instead of using defaults:

- **"when half the containers are restarted"** → `PERCENT(50)`
- **"when one instance fails"** → `COUNT(1)`  
- **"when 20% of pods are terminated"** → `PERCENT(20)`
- **"when all instances in one AZ fail"** → target by AZ tags
- **"when a single Lambda function fails"** → `COUNT(1)`

## Supported Services

The agent generates experiments for various AWS services by checking their specific documentation:

- **ECS**: Task-level actions (kill-process, cpu-stress, network-latency, etc.)
- **EKS**: Pod-level actions (terminate instances, cpu-stress, etc.)  
- **Lambda**: Function-level actions (invocation-error, invocation-timeout, etc.)
- **EC2**: Instance-level actions (stop-instances, reboot-instances, etc.)
- **SSM**: Agent-based actions for custom fault injection

## Quality Standards

Every generated template includes:
- ✅ **Valid JSON**: Proper syntax with correct data types
- ✅ **Complete Structure**: All required fields (description, targets, actions, stopConditions, roleArn)
- ✅ **Hypothesis-Driven**: Selection modes and parameters match the testing hypothesis
- ✅ **Safe Defaults**: Conservative targeting and `[{"source": "none"}]` stop conditions  
- ✅ **Current Actions**: Action IDs verified from live AWS documentation
- ✅ **Database Tracked**: Saved for experiment tracking and hypothesis validation

## Safety Guidelines

- **Documentation-First**: Always checks current AWS documentation for valid actions
- **Hypothesis-Driven Targeting**: Selection modes derived from user intent
- **Safe Stop Conditions**: Defaults to `[{"source": "none"}]` unless specific alarms verified
- **Conservative Selection**: Reasonable targeting percentages based on hypothesis
- **Environment Tags**: Uses appropriate resource tags for targeting
- **Non-Production First**: Recommends testing in non-production environments

## Database Integration

All experiments are saved to a PostgreSQL database with:
- **Experiment Tracking**: Each experiment gets a unique ID
- **Hypothesis Linking**: Experiments linked to hypotheses for validation tracking  
- **Complete Configuration**: Full FIS template stored as JSONB
- **Experiment Plan**: Detailed text plan with safety considerations
- **Status Tracking**: Draft status with ability to update lifecycle

## Requirements

- Python 3.8+
- AWS credentials configured with appropriate permissions
- Amazon Bedrock access
- PostgreSQL database (Aurora Serverless recommended)
- Strands Agents SDK:
  ```bash
  pip install strands-agents strands-agents-tools
  ```

## File Structure

```
src/ExperimentDesignAgent/
├── agent.py              # Main agent implementation
├── fis_tools.py          # FIS documentation tools
├── database_tools.py     # Database persistence tools
├── system_prompt.md      # Agent system prompt and capabilities
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
├── SETUP.md             # Database setup instructions
└── repl_state/          # Agent state persistence
```

## Contributing

To extend the agent:

1. Add new services to FIS_DOCS_URLS in fis_tools.py
2. Update system_prompt.md with new service examples  
3. Test with various hypothesis formats
4. Ensure generated templates are valid and safe
5. Maintain focus on the core 4-step workflow
