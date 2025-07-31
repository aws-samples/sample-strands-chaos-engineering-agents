# Technical Context

## Technologies Used

### Core Technologies

1. **AWS Strands**
   - Primary framework for developing the AI agents
   - Provides structured approach to building agents with tool access
   - Handles agent orchestration and communication

2. **Amazon Bedrock**
   - AI model platform for powering the agents
   - Default model: Claude Sonnet 3.7
   - Provides natural language understanding and generation capabilities

3. **AWS Fault Injection Service (FIS)**
   - Used for executing chaos experiments
   - Provides controlled fault injection into AWS resources
   - Supports various fault types (CPU stress, memory stress, network latency, etc.)

4. **Amazon Aurora Serverless**
   - Database for storing hypothesis backlog, experiment results, and other data
   - Serverless architecture scales automatically
   - SQL-compatible for flexible querying

5. **AWS CloudWatch**
   - Monitoring service for observing system behavior
   - Used to determine steady-state operation
   - Tracks system metrics during experiments

### Supporting Technologies

1. **Git**
   - Source code version control
   - Used for accessing system source code and documentation
   - Required for agent analysis of target systems

2. **AWS SDK**
   - Programmatic access to AWS services
   - Used for interacting with FIS, CloudWatch, Aurora, etc.
   - Available in multiple languages (likely Python for this project)

3. **MCP Servers**
   - Model Context Protocol servers for extending agent capabilities
   - Preference for AWSLabs collection
   - Provides specialized tools for agents

## Development Setup

### Prerequisites

1. **AWS Account**
   - Access to AWS services (Bedrock, FIS, Aurora, CloudWatch)
   - Appropriate IAM permissions for service access

2. **AWS CLI**
   - Configured with appropriate credentials
   - Used for service interaction during development

3. **AWS Profile**
   - Pre-configured authentication
   - Assumed to be set up in the local environment

### Development Environment

1. **Local Development**
   - Standard development tools for Python/AWS Strands
   - IDE with AWS integration support
   - Git client for repository access

2. **Testing Environment**
   - Isolated AWS resources for testing
   - Test target systems for experiment validation
   - CloudWatch dashboards for monitoring test systems

## Technical Constraints

1. **AWS Ecosystem Dependency**
   - System is tightly coupled with AWS services
   - Requires AWS account and permissions
   - Limited portability to other cloud providers

2. **Authentication Requirements**
   - Relies on pre-configured AWS authentication
   - Needs appropriate permissions for service access
   - Security considerations for accessing target systems

3. **Target System Compatibility**
   - Target systems must be running on AWS
   - Requires CloudWatch monitoring
   - Needs Git repositories for source code and documentation

4. **Model Limitations**
   - Dependent on Claude Sonnet 3.7 capabilities
   - Subject to model token limits and latency
   - May require optimization for complex analyses

## Dependencies

### External Dependencies

1. **AWS Services**
   - Bedrock: AI model hosting and inference
   - FIS: Fault injection capabilities
   - Aurora Serverless: Data storage
   - CloudWatch: System monitoring
   - IAM: Authentication and authorization

2. **Target System**
   - Source code repository
   - Documentation repository
   - CloudWatch dashboard
   - AWS infrastructure components

### Internal Dependencies

1. **Agent Interdependencies**
   - Hypothesis Generation → Prioritization → Experiment Design → Execution → Learning
   - Shared data structures for hypothesis and experiment information
   - Consistent interfaces between agents

2. **Data Flow Dependencies**
   - Hypothesis backlog as central data store
   - Experiment results database
   - System state monitoring data

## Tool Usage Patterns

1. **AWS Strands Agent Development**
   - Agent definition and configuration
   - Tool integration for specialized capabilities
   - State management and persistence

2. **AWS Service Integration**
   - SDK-based service access
   - IAM role-based authentication
   - Event-driven architecture where appropriate

3. **Data Management**
   - SQL queries for hypothesis and experiment data
   - Structured data formats for agent communication
   - Persistent storage for long-running experiments

4. **MCP Server Integration**
   - Tool extension through MCP servers
   - Preference for AWSLabs collection
   - Custom tool development when needed

5. **Monitoring and Observability**
   - CloudWatch metrics and dashboards
   - Experiment result tracking
   - System state comparison (before/during/after experiments)
