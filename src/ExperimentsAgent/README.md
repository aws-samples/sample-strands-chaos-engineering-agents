# ExperimentsAgent

An AWS Fault Injection Service (FIS) experiments creation agent built with Strands Agents SDK. This agent specializes in taking designed chaos engineering experiments from the database, creating IAM roles, discovering and validating AWS resources, and creating production-ready FIS experiments that are ready for execution.

## Features

- **Role-First Creation**: Creates IAM roles first using configurations from experiment design
- **Built-in AWS Integration**: Uses the built-in `use_aws` tool for seamless AWS resource discovery
- **Target Correction**: Updates placeholder or incorrect targets with real AWS resource identifiers
- **Safety-First Approach**: Only uses read-only AWS operations for resource discovery
- **Database Integration**: Retrieves experiments and updates status throughout the process
- **Comprehensive Resource Support**: Supports all AWS resource types supported by FIS

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have proper AWS credentials configured and access to Amazon Bedrock models.

3. Set up the database infrastructure with the required schema including `fis_experiment_id` and `experiment_notes` columns.

## Usage

### Running the Agent

```python
from agent import agent

# Create FIS experiments for draft experiments
result = agent("Create FIS experiments for all draft experiments in the database")
print(result.message)
```

### Running from Command Line

```bash
python agent.py
```

### Interactive Usage

```python
# Create FIS experiment for a specific experiment ID
result = agent("Get experiment ID 39 from the database and create the FIS experiment with role creation")

# Process all validation failed experiments
result = agent("Retry creating FIS experiments for validation_failed experiments")
```

## Available Tools

The agent uses focused tools for IAM role creation, resource discovery, FIS creation, and database management:

### Database Tools
- **`get_experiments_from_database(...)`**: Retrieve experiments ready for creation from database
  - Supports status filtering (draft, planned, validation_failed, etc.)
  - Returns experiment details including FIS configuration and role configuration
- **`update_experiment_status(...)`**: Update experiment status and store FIS experiment IDs
  - Tracks experiment lifecycle and stores results

### IAM Role Tools
- **`create_fis_execution_role(...)`**: Create IAM roles for FIS experiment execution
  - Uses standardized FIS trust policy
  - Attaches required managed policies
  - Handles role propagation and error cases
- **`delete_fis_execution_role(...)`**: Clean up IAM roles when experiment creation fails

### AWS Integration Tools
- **`use_aws`**: Built-in tool for comprehensive AWS service interaction
  - Supports all AWS services and APIs
  - Provides direct access to EC2, ECS, RDS, Lambda, Auto Scaling, EKS, and more
  - Handles authentication and region management automatically



### Core Tools
- **`current_time`**: Get current timestamp for experiment metadata

## Agent Workflow

The agent follows a comprehensive 7-step workflow:

1. **Experiment Retrieval**: Gets experiments with status "draft", "planned", etc. from database
2. **IAM Role Creation**: Creates FIS execution role if `fis_role_configuration` exists
3. **Resource Discovery**: Uses the built-in `use_aws` tool to discover matching AWS resources
4. **Target Validation**: Ensures sufficient resources exist for experiment requirements
5. **Target Correction**: Updates FIS configuration with actual resource ARNs/IDs
6. **FIS Creation**: Creates experiment template in AWS FIS (does not execute)
7. **Status Update**: Updates database with "created" status and FIS experiment ID

### Example Workflow

Input: *"Get experiment ID 39 from the database and create the FIS experiment with role creation"*

1. **Experiment Retrieval**:
   - Query database for experiment ID 39
   - Extract FIS configuration and role configuration

2. **IAM Role Creation**:
   - Generate unique role name: `FIS-EC2-Instance-Stop-Test-Role`
   - Create role with FIS trust policy and required permissions
   - Return role ARN for FIS configuration

3. **Resource Discovery**:
   - Use `use_aws` tool to find EC2 instances with Environment=test tag
   - Return structured resource data with ARNs, states, tags

4. **Target Validation**:
   - Verify sufficient resources exist for selection mode (COUNT, PERCENT, ALL)
   - Check resource states and accessibility

5. **Target Correction**:
   - Replace placeholder ARNs with real resource identifiers
   - Update FIS configuration with validated targets

6. **FIS Creation**:
   - Create experiment template: `EXT417RFphqsJ32x`
   - Validate template structure and permissions

7. **Database Update**:
   - Update status to "created"
   - Store FIS experiment ID for tracking

## Resource Discovery Examples

The agent uses the built-in `use_aws` tool for seamless resource discovery:

### EC2 Instances
```python
# Use use_aws tool to discover EC2 instances
use_aws(service="ec2", action="describe_instances", region="us-west-2")
# Returns structured data with instance details, tags, states, ARNs
```

### ECS Tasks
```python
# Use use_aws tool to discover ECS tasks
use_aws(service="ecs", action="list_clusters", region="us-west-2")
use_aws(service="ecs", action="list_tasks", region="us-west-2")
use_aws(service="ecs", action="describe_tasks", region="us-west-2")
# Returns task details with cluster information, status, and ARNs
```

### Lambda Functions
```python
# Use use_aws tool to discover Lambda functions
use_aws(service="lambda", action="list_functions", region="us-west-2")
# Returns function configurations, tags, runtime information
```

### RDS Instances
```python
# Use use_aws tool to discover RDS instances
use_aws(service="rds", action="describe_db_instances", region="us-west-2")
# Returns database details, engine info, availability zones
```

## Agent Architecture

```
Database → ExperimentsAgent → AWS IAM → AWS FIS
    ↑                                      ↓
    └──── Status Updates ─────────────────┘
```

## Database Status Flow

```
draft → validating → created
   ↓         ↓           ↓
validation_failed  →  ready_for_execution
permission_error
resource_unavailable  
creation_failed
```

## Safety Guidelines

- **Read-Only Resource Operations**: Only uses `describe_*`, `list_*`, `get_*` AWS API calls for resource discovery
- **No Resource Modification**: Cannot create, delete, or modify existing AWS resources
- **IAM Role Creation**: Only creates IAM roles required for FIS execution
- **FIS Creation Only**: The only "create" operations allowed are IAM roles and FIS experiment templates
- **No Experiment Execution**: Creates experiments but does not execute them
- **Role-First Pattern**: Always creates IAM roles before experiment templates
- **Conservative Validation**: Ensures sufficient resources exist before creation

## Error Handling

The agent handles various error scenarios:

- **Insufficient Resources**: Not enough resources found for experiment requirements
- **Permission Issues**: FIS role lacks permissions for discovered resources
- **Resource Unavailable**: Target resources are not in appropriate states
- **FIS API Errors**: Issues with AWS FIS service during creation
- **Template Invalid**: Problems with experiment template structure
- **IAM Role Issues**: Role creation or attachment failures

## Configuration

### AWS Permissions Required

The agent needs AWS permissions for:
- **IAM Role Management**: `iam:CreateRole`, `iam:AttachRolePolicy`, `iam:GetRole` permissions
- **Resource Discovery**: Read access to all services referenced in experiments
- **FIS Creation**: `fis:CreateExperimentTemplate` permission
- **Database Access**: RDS Data API access for experiment retrieval and updates

### Environment Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials with appropriate permissions

3. Ensure database is accessible via RDS Data API with proper schema

## Integration

The ExperimentsAgent works in conjunction with:

- **ExperimentDesignAgent**: Consumes experiment templates created by the design agent
- **Database**: Retrieves experiments and updates status throughout lifecycle
- **AWS IAM**: Creates execution roles for FIS experiments  
- **AWS FIS**: Creates experiment templates ready for execution
- **Monitoring Systems**: Can be integrated for experiment lifecycle tracking

## Requirements

- Python 3.8+
- AWS credentials configured with appropriate permissions
- Amazon Bedrock access
- PostgreSQL database (Aurora Serverless recommended) with required schema
- Strands Agents SDK:
  ```bash
  pip install strands-agents strands-agents-tools
  ```

## File Structure

```
src/ExperimentsAgent/
├── agent.py                        # Main agent implementation
├── database_tools.py               # Database interaction tools
├── iam_role_tools.py              # IAM role creation and management

├── system_prompt.md               # Agent system prompt and capabilities
├── requirements.txt               # Python dependencies
├── README.md                      # This documentation
└── repl_state/                    # Agent state persistence
```

## Contributing

To extend the agent:

1. Leverage the built-in `use_aws` tool for additional AWS services as needed
2. Update error handling for new resource types and scenarios
3. Enhance target correction logic for complex experiment requirements
4. Add new status types as needed for workflow tracking
5. Implement additional safety checks for new resource types
6. Maintain focus on the role-first creation workflow
