# Active Context

## Current Work Focus

The project is currently in the initialization phase. We are setting up the memory bank to document the project's requirements, architecture, and technical context. This will serve as the foundation for developing the chaos engineering agents.

The immediate focus is on:

1. Establishing a clear understanding of the project requirements and goals
2. Defining the system architecture and component relationships
3. Documenting the technical context and dependencies
4. Planning the development approach for the five agents

## Recent Changes

- Created the initial memory bank structure with core documentation files:
  - `projectbrief.md`: Defining the project scope and technical choices
  - `productContext.md`: Explaining why the project exists and how it should work
  - `systemPatterns.md`: Documenting the system architecture and design patterns
  - `techContext.md`: Detailing the technologies and development setup
  - `activeContext.md`: Tracking current work and decisions (this file)
  - `progress.md`: Monitoring project progress and status

- Fixed database infrastructure deployment issue:
  - Switched from Aurora MySQL to Aurora PostgreSQL (version 13.9) with Serverless v2
  - Configured Serverless v2 scaling with 0.5-4.0 ACU capacity range
  - Enabled Data API for PostgreSQL to support the postgres-mcp-server MCP server
  - Updated database schema to use PostgreSQL syntax (SERIAL, JSONB, custom ENUM types)
  - Configured security group to use PostgreSQL port (5432)

- Consolidated database schema initialization:
  - Moved hypothesis_evaluation table creation from HypothesisEvaluatorAgent to schema-init Lambda
  - Added proper indexes and comments for the hypothesis_evaluation table
  - Ensured consistent timestamp handling with other tables (TIMESTAMP WITH TIME ZONE)
  - All schema initialization now happens in a single place for better maintainability

## Next Steps

1. **Research and Learning**:
   - Explore AWS Strands documentation and examples
   - Study AWS FIS capabilities and limitations
   - Investigate CloudWatch integration options
   - Review existing chaos engineering methodologies and best practices

2. **Development Environment Setup**:
   - Configure AWS profile and permissions
   - Set up development tools for AWS Strands
   - Create test environment for agent development

3. **Agent Development Planning**:
   - Define detailed requirements for each agent
   - Design agent interfaces and data structures
   - Plan development sequence and milestones

4. **Initial Implementation**:
   - Start with the Hypothesis Generation Agent
   - Implement basic functionality for analyzing system components
   - Create data structures for the hypothesis backlog

## Active Decisions and Considerations

1. **Agent Granularity**:
   - Decision to use five specialized agents rather than a monolithic approach
   - Each agent focuses on a specific phase of the chaos engineering workflow
   - Considering how to manage state and data sharing between agents

2. **Technology Stack**:
   - Selected AWS Strands as the agent development framework
   - Chosen Claude Sonnet 3.7 as the default model
   - Considering options for local development and testing

3. **Data Storage**:
   - Selected Aurora Serverless for persistent storage
   - Need to design database schema for hypothesis backlog and experiment results
   - Considering data access patterns and performance requirements

4. **User Experience**:
   - Focusing on making chaos engineering accessible to teams without specialized expertise
   - Balancing automation with user control and transparency
   - Considering how to present complex information in an understandable way

## Important Patterns and Preferences

1. **AWS-Native Integration**:
   - Preference for AWS services and tools
   - Leveraging existing AWS infrastructure and authentication
   - Following AWS best practices for service integration

2. **Agent Collaboration Model**:
   - Pipeline pattern for agent workflow
   - Repository pattern for shared data
   - Clear interfaces between agents

3. **Development Approach**:
   - Iterative development with focus on one agent at a time
   - Test-driven development for agent functionality
   - Documentation-first approach for clarity and knowledge sharing

4. **Tool Integration**:
   - Preference for AWSLabs MCP servers
   - Structured approach to tool integration
   - Consistent patterns for service access

## Learnings and Project Insights

1. **Chaos Engineering Principles**:
   - Importance of steady-state identification before experimentation
   - Need for multiple perspectives (personas) when analyzing systems
   - Value of hypothesis-driven approach to resilience testing

2. **Agent Architecture**:
   - Benefits of specialized agents for different phases
   - Challenges of state management across agent boundaries
   - Importance of clear data structures and interfaces

3. **AWS Integration**:
   - Advantages of AWS-native approach for seamless integration
   - Considerations for authentication and permissions
   - Potential for leveraging AWS services for enhanced functionality

4. **Project Scope**:
   - Focus on AWS-hosted systems as targets
   - Requirement for CloudWatch monitoring
   - Need for Git repositories for source code and documentation access
