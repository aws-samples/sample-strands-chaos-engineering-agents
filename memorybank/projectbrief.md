# Chaos Engineering Agent

This project aims to build a set of chaos engineering agents to help software teams use chaos engineering.

## Expected steps

- The user will provide a pointer to the software system of interest. This will include:
    - The Git repository containing the source code
    - The Git repository containing the system documentation
    - The name of the CloudWatch dashboard that monitors the project (without a dashboard, the agent can just try to infer the CloudWatch metrics of interest)
- The first agent will populate a hypothesis backlog according to the principles of chaos engineering. The agent should look at the system from multiple points of view. For example, a typical three-tier software system would have personas for the front-end engineer, the back-end engineer, the database engineer, the operations engineer, and the security engineer. This agent should analyze the CloudWatch dashboard/metrics to determine the steady-state operation of the system.
- The second agent will prioritize the hypothesis backlog.
- The third agent will, upon user request, develop a set of experiments for a specific hypothesis.
- The fourth agent will, upon user request, execute an experiment using AWS FIS. After the experiment completes, it will analyze the results.
- The fifth agent will, upon user request, update the hypothesis backlog based on the results from the experiment.

## Technical choices

- We will use AWS Strands to develop the agents.
- We will use models from Amazon Bedrock, with Claude Sonnet 3.7 as the default model.
- We will assume that all AWS authentication is already handled in the local environment via an AWS profile.
- We will use Amazon Aurora Serverless as a data store for tracking experiment results and other data.
- The agents should make use of AWS blogs and documentation for guidance.
- Wherever possible, the agents should use MCP servers for tools. Agents from the AWSLabs collection (https://github.com/awslabs/mcp?tab=readme-ov-file) are preferred.