# HypothesisGeneratorAgent

A chaos engineering hypothesis generation expert agent built with Strands Agents SDK. This agent specializes in analyzing AWS workloads and generating structured, testable chaos engineering hypotheses that describe potential failure scenarios.

## Features

- **Workload Analysis**: Analyzes AWS workloads through source code and deployed resources
- **Hypothesis Generation**: Creates structured, testable hypotheses covering different failure domains
- **Multi-Service Support**: Generates hypotheses for ECS, EKS, Lambda, EC2, RDS, and other AWS services
- **Failure Domain Coverage**: Covers compute, data layer, network, dependency, and resource constraint failures
- **JSON Output**: Returns clean JSON arrays ready for experiment design agents
- **Safety-First Approach**: Focuses on realistic failure scenarios with limited blast radius

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have proper AWS credentials configured and access to Amazon Bedrock models.

## Usage

### Running the Agent

```python
from agent import agent

# Example: Generate hypotheses for an ECS-based API
message = "Analyze this ECS-based API workload and generate chaos engineering hypotheses"

response = agent(message)
print(response.message)
```

### Running from Command Line

```bash
python agent.py
```

### Interactive Usage

```python
# Generate hypotheses for a microservices architecture
result = agent("Generate hypotheses for a microservices architecture running on EKS with RDS backend")

# Generate hypotheses with repository context
result = agent("Analyze https://github.com/example/app and generate chaos hypotheses")
```

## Architecture

The agent follows the Strands "Agents as Tools" pattern with specialized sub-agents:

### Specialized Agents
- **`workload_analysis_agent`**: Coordinates source code analysis and AWS resource discovery
- **`source_code_analysis_agent`**: Analyzes repository code for infrastructure patterns and AWS service usage
- **`aws_resource_analysis_agent`**: Discovers and analyzes deployed AWS resources
- **`hypothesis_builder_agent`**: Generates structured chaos engineering hypotheses from analysis results

### Agent Workflow

The main orchestrator agent coordinates these specialized agents in a 2-step workflow:

1. **Workload Analysis**: Uses `workload_analysis_agent` to understand system architecture
   - Analyzes source code repositories when provided
   - Discovers deployed AWS resources
   - Identifies potential failure points and dependencies

2. **Hypothesis Generation**: Uses `hypothesis_builder_agent` to create testable hypotheses
   - Generates 3-5 focused hypotheses covering different failure domains
   - Ensures hypotheses are FIS-compatible and production-safe
   - Returns structured JSON output ready for experiment design

### Example Workflow

Input: *"Generate hypotheses for an ECS-based API with RDS backend"*

1. **Workload Analysis**: 
   - Identifies ECS services, ALB, RDS instances
   - Maps service dependencies and data flow
   - Identifies potential failure points

2. **Hypothesis Building**:
   - Analyzes failure scenarios for each component
   - Validates FIS implementation feasibility
   - Creates detailed recommendations

3. **Hypothesis Generation**:
   ```json
   [
     {
       "title": "ECS Task Termination Test",
       "description": "Validate application resilience when ECS tasks are terminated",
       "steady_state": "All services respond within 500ms with 99.9% availability",
       "hypothesis_statement": "We believe that if 50% of ECS tasks are terminated then the application will maintain availability because auto-scaling will replace failed tasks",
       "aws_services": ["ECS", "ALB"],
       "created_at": "2025-06-18T00:00:00+00:00"
     }
   ]
   ```

## Hypothesis Focus Areas

The agent generates hypotheses covering these failure domains:

1. **Compute Failures**: Container/instance termination, resource exhaustion
2. **Data Layer Failures**: Database failover, connection pool exhaustion, replication lag
3. **Network Failures**: Service communication, load balancer issues, DNS resolution
4. **Dependency Failures**: External service timeouts, API rate limiting
5. **Resource Constraints**: Auto-scaling delays, capacity limits

## Hypothesis Quality Criteria

Every generated hypothesis meets these standards:
- ✅ **Testable**: Can be implemented using AWS FIS or similar tools
- ✅ **Realistic**: Based on actual failure modes that occur in production
- ✅ **Specific**: Target specific AWS services and failure conditions
- ✅ **Safe**: Describe failures with limited blast radius
- ✅ **Learning-focused**: Test specific resilience assumptions

## Output Format

The agent returns ONLY valid JSON in this exact format:
```json
[
  {
    "title": "Brief descriptive title",
    "description": "What could fail and why",
    "steady_state": "Normal system behavior description", 
    "hypothesis_statement": "We believe that if [condition] then [outcome]",
    "aws_services": ["service1", "service2"],
    "created_at": "ISO timestamp"
  }
]
```

## Hypothesis Statement Format

Always uses this structure: "We believe that if [specific failure condition] then [expected system behavior] because [underlying assumption about system design]"

Examples:
- "We believe that if 50% of ECS tasks are terminated then the application will maintain availability because auto-scaling will replace failed tasks within 2 minutes"
- "We believe that if the primary RDS instance fails then read operations will continue normally because read replicas will handle the load"

## Supported Services

The agent generates hypotheses for various AWS services:

- **ECS**: Task termination, service scaling, resource constraints
- **EKS**: Pod failures, node termination, cluster scaling
- **Lambda**: Function errors, timeout scenarios, concurrency limits
- **EC2**: Instance failures, auto-scaling scenarios, resource exhaustion
- **RDS**: Database failover, connection limits, replication lag
- **ALB/NLB**: Load balancer failures, target health issues
- **S3**: Access failures, eventual consistency scenarios
- **DynamoDB**: Throttling, partition key distribution issues

## Safety Guidelines

- **Limited Blast Radius**: Hypotheses focus on controlled failure scenarios
- **Production-Safe**: Designed for gradual rollout and safe testing
- **Measurable Outcomes**: Clear success criteria and steady state definitions
- **Realistic Scenarios**: Based on actual production failure patterns
- **FIS-Compatible**: All hypotheses can be implemented with AWS FIS

## Requirements

- Python 3.8+
- AWS credentials configured with appropriate permissions
- Amazon Bedrock access
- Strands Agents SDK:
  ```bash
  pip install strands-agents strands-agents-tools
  ```

## File Structure

```
src/HypothesisGeneratorAgent/
├── agent.py                           # Main orchestrator agent
├── system_prompt.md                   # Main agent system prompt
├── requirements.txt                   # Python dependencies
├── README.md                         # This documentation
└── agents/                           # Specialized agents directory
    ├── workload_analysis/
    │   ├── agent.py                  # @tool decorated workload analysis agent
    │   └── system_prompt.md          # Workload analysis system prompt
    ├── source_code_analysis/
    │   ├── agent.py                  # @tool decorated source code analysis agent
    │   └── system_prompt.md          # Source code analysis system prompt
    ├── aws_resource_analysis/
    │   ├── agent.py                  # @tool decorated AWS resource analysis agent
    │   └── system_prompt.md          # AWS resource analysis system prompt
    └── hypothesis_builder/
        ├── agent.py                  # @tool decorated hypothesis builder agent
        └── system_prompt.md          # Hypothesis builder system prompt
```

## Contributing

To extend the agent:

1. Add new AWS services to the analysis tools
2. Update system_prompt.md with new service examples
3. Test with various workload types and architectures
4. Ensure generated hypotheses are testable and safe
5. Maintain focus on the core 3-step workflow
