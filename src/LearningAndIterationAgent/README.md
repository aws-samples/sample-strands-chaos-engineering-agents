# Learning and Iteration Agent

An AI-powered agent focused on learning from chaos engineering experiments and iterating on hypotheses to build organizational resilience knowledge.

## Overview

The Learning and Iteration Agent analyzes experiment results, extracts insights, and provides recommendations for improving chaos engineering practices. It helps organizations build a knowledge base of system resilience patterns and continuously refine their understanding of system behavior.

## Features

### Core Capabilities

- **Experiment Analysis**: Analyze completed chaos engineering experiments to extract patterns and insights
- **Learning Extraction**: Identify key learnings from successful and failed experiments
- **Hypothesis Refinement**: Refine existing hypotheses based on experiment outcomes
- **Knowledge Management**: Build and maintain organizational knowledge base from experiments
- **Continuous Improvement**: Recommend improvements to chaos engineering practices

### Key Tools

#### Database Tools (`database_tools.py`)
- `get_experiment_results()`: Retrieve experiment results for analysis
- `save_learning_insights()`: Save learning insights and recommendations
- `get_learning_history()`: Retrieve historical learning insights
- `update_hypothesis_status()`: Update hypothesis status based on learnings

#### Analysis Tools (`analysis_tools.py`)
- `analyze_experiment_outcomes()`: Analyze experiment outcomes to extract patterns
- `generate_improvement_recommendations()`: Generate actionable improvement recommendations
- `identify_knowledge_gaps()`: Identify areas needing further investigation

#### Iteration Tools (`iteration_tools.py`)
- `refine_hypothesis()`: Refine hypotheses based on experiment results
- `suggest_follow_up_experiments()`: Suggest follow-up experiments based on analysis
- `generate_hypothesis_variations()`: Generate variations of hypotheses for broader testing

## Usage

### Basic Usage

```python
from LearningAndIterationAgent import agent

# Analyze experiment results and get insights
message = """
Analyze the results from our recent ECS task restart experiments and provide insights 
on what we learned about system resilience. Suggest improvements for future experiments.
"""

result = agent(message)
print(result.message)
```

### Advanced Usage Examples

#### Analyze Specific Experiment Results

```python
# Analyze results from a specific experiment
message = """
Please analyze experiment EXP-2024-001 results and provide:
1. Key learnings about system behavior
2. Recommendations for system improvements
3. Suggestions for follow-up experiments
4. Updated risk assessment
"""

result = agent(message)
```

#### Refine Hypotheses Based on Results

```python
# Refine a hypothesis based on experiment outcomes
message = """
Based on the results from experiments EXP-2024-001 through EXP-2024-005, 
please refine hypothesis HYP-001 about API performance during ECS restarts.
The experiments showed mixed results - some confirmed the hypothesis while others contradicted it.
"""

result = agent(message)
```

#### Generate Learning Insights Report

```python
# Generate comprehensive learning insights
message = """
Generate a learning insights report for all experiments conducted in the last 30 days.
Include:
- Overall success patterns
- Common failure modes
- System resilience improvements identified
- Knowledge gaps that need attention
- Recommendations for the next quarter
"""

result = agent(message)
```

## Input Format

The agent accepts natural language requests for:

- Experiment result analysis
- Hypothesis refinement requests
- Learning insight generation
- Improvement recommendations
- Knowledge gap identification
- Follow-up experiment suggestions

## Output Format

The agent provides structured responses including:

- **Key Learnings**: Main insights extracted from analysis
- **Recommendations**: Actionable next steps and improvements
- **Refined Hypotheses**: Updated or new hypotheses based on learnings
- **Follow-up Experiments**: Suggested experiments to fill knowledge gaps
- **Risk Assessment**: Updated understanding of system risks
- **Knowledge Gaps**: Areas requiring further investigation

## Integration

### Database Schema

The agent expects the following Aurora MySQL tables (created by the infrastructure):

#### experiment
- `id` (INT, Primary Key, Auto Increment)
- `hypothesis_id` (INT, Foreign Key to hypothesis.id)
- `title` (VARCHAR)
- `description` (TEXT)
- `experiment_plan` (TEXT)
- `fis_configuration` (JSONB)
- `status` (VARCHAR)
- `scheduled_for` (TIMESTAMP)
- `executed_at` (TIMESTAMP)
- `completed_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

#### hypothesis
- `id` (INT, Primary Key, Auto Increment)
- `title` (VARCHAR)
- `description` (TEXT)
- `status` (VARCHAR)
- `priority` (INT)
- `notes` (TEXT)
- `system_component_id` (INT, Foreign Key)
- `created_at` (TIMESTAMP)

#### learning_insights (created by agent)
- `id` (INT, Primary Key, Auto Increment)
- `experiment_ids` (JSON)
- `key_learnings` (JSON)
- `recommendations` (JSON)
- `refined_hypotheses` (JSON)
- `risk_assessment` (JSON)
- `knowledge_gaps` (JSON)
- `created_at` (TIMESTAMP)

### Integration with Other Agents

- **HypothesisGeneratorAgent**: Refines hypotheses generated by the hypothesis generator
- **ExperimentDesignAgent**: Informs experiment design with learnings and recommendations
- **ExperimentsAgent**: Analyzes results from experiments executed by the experiments agent

## Configuration

### Environment Variables

- `AWS_REGION`: AWS region for DynamoDB access
- `AWS_PROFILE`: AWS profile for authentication (optional)

### Required Permissions

The agent requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds-data:ExecuteStatement",
                "rds-data:BatchExecuteStatement"
            ],
            "Resource": [
                "arn:aws:rds:*:*:cluster:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": [
                "arn:aws:secretsmanager:*:*:secret:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:DescribeStacks"
            ],
            "Resource": [
                "arn:aws:cloudformation:*:*:stack/ChaosAgentDatabaseStack/*"
            ]
        }
    ]
}
```

## Best Practices

### Analysis Best Practices

1. **Evidence-Based**: Base all recommendations on data and evidence from experiments
2. **Actionable**: Provide specific, implementable recommendations
3. **Prioritized**: Rank recommendations by impact and feasibility
4. **Comprehensive**: Consider both technical and organizational aspects

### Learning Management

1. **Systematic**: Follow consistent patterns for extracting and documenting learnings
2. **Traceable**: Maintain clear links between experiments, hypotheses, and insights
3. **Iterative**: Continuously refine understanding based on new evidence
4. **Shareable**: Document insights in a way that benefits the entire organization

### Hypothesis Refinement

1. **Data-Driven**: Use experiment results to guide hypothesis refinement
2. **Specific**: Make hypotheses more specific and testable based on learnings
3. **Validated**: Ensure refined hypotheses can be validated through experiments
4. **Evolutionary**: Allow hypotheses to evolve as understanding improves

## Error Handling

The agent includes comprehensive error handling for:

- Database connection issues
- Invalid experiment data formats
- Missing required parameters
- AWS service limitations
- Data parsing errors

## Monitoring and Observability

The agent logs key activities including:

- Experiment analysis completion
- Learning insights generation
- Hypothesis refinement actions
- Recommendation generation
- Knowledge gap identification

## Contributing

When extending the Learning and Iteration Agent:

1. Follow the established tool pattern in existing files
2. Add comprehensive error handling
3. Include detailed docstrings
4. Update this README with new capabilities
5. Add example usage for new features

## Dependencies

- `boto3`: AWS SDK for Python
- `strands`: Core agent framework
- `strands-tools`: Additional tools for agent capabilities

## License

This project follows the same license as the parent chaos-agent project.
