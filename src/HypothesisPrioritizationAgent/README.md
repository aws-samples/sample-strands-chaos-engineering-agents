# Hypothesis Prioritization Agent

An intelligent agent that analyzes and prioritizes chaos engineering hypotheses to maximize the value and safety of chaos engineering programs.

## Overview

The Hypothesis Prioritization Agent acts as a senior chaos engineering consultant, analyzing all hypotheses in the database and assigning priority rankings from 1 to N (where 1 is highest priority). Unlike rule-based systems, this agent develops its own prioritization framework based on the specific characteristics of each hypothesis set.

## Key Features

- **Adaptive Prioritization**: Develops custom criteria based on the specific workload and hypothesis characteristics
- **Expert Analysis**: Applies chaos engineering best practices and safety-first principles
- **Contextual Awareness**: Considers AWS service patterns, dependencies, and logical testing sequences
- **Database Integration**: Reads from and updates the hypothesis database seamlessly
- **No Gaps or Duplicates**: Ensures clean priority sequence from 1 to N

## Usage

### Input Format
Simple trigger message:
```json
{
  "message": "Prioritize all hypotheses"
}
```

### Workflow
1. **Discovery**: Retrieves all hypotheses from database using `get_hypotheses()`
2. **Analysis**: Analyzes patterns, services, failure modes, and system components
3. **Framework Development**: Creates custom prioritization criteria for this specific set
4. **Prioritization**: Assigns rankings from 1 to N with expert judgment
5. **Database Update**: Uses `update_hypothesis()` to save priority assignments

### Output
Comprehensive summary including:
- Custom prioritization framework developed
- Analysis insights and patterns identified
- Priority assignment rationale
- Database update confirmation
- Recommendations for the chaos engineering program

## Prioritization Philosophy

The agent follows these core principles:

- **Safety First**: Prioritizes experiments with controlled blast radius
- **Value Maximization**: Focuses on high-learning, reasonable-effort experiments
- **Logical Sequencing**: Considers dependencies and complexity progression
- **Adaptive Thinking**: Develops criteria specific to each workload
- **Expert Judgment**: Applies nuanced chaos engineering expertise

## Integration

This agent fits into the chaos engineering workflow after hypothesis generation:

```
HypothesisGeneratorAgent → HypothesisPrioritizationAgent → ExperimentDesignAgent
```

The prioritized hypotheses help the ExperimentDesignAgent focus on the most valuable experiments first.

## Database Schema

The agent works with the `hypothesis` table, specifically updating the `priority` field:

```sql
UPDATE hypothesis SET priority = :priority WHERE id = :hypothesis_id
```

## Example Prioritization Factors

The agent might consider (but is not limited to):

- **Business Impact**: Critical user-facing services vs. internal tools
- **Safety Profile**: Blast radius and rollback complexity
- **Learning Value**: Insight potential and knowledge gaps
- **Implementation Effort**: Resource requirements and complexity
- **Real-world Likelihood**: Probability of actual occurrence
- **Service Dependencies**: Foundational vs. dependent services
- **Team Readiness**: Skill level and operational maturity

## Safety Considerations

- **Read-First Approach**: Analyzes all data before making changes
- **Atomic Updates**: All priority assignments completed or none
- **Validation**: Ensures no duplicate priorities or gaps
- **Audit Trail**: Provides clear rationale for all decisions

## Advanced Usage

The agent can be called programmatically:

```python
from src.HypothesisPrioritizationAgent.agent import agent

# Prioritize all hypotheses
result = agent("Prioritize all hypotheses based on current database state")
```

## Dependencies

- **AWS Strands**: Agent framework
- **Anthropic Claude**: LLM for intelligent analysis
- **Database Tools**: `shared.hypotheses` module for database operations

## Contributing

To extend the agent's capabilities:

1. **Enhanced Analysis**: Add new pattern recognition capabilities
2. **Custom Criteria**: Extend the framework development logic
3. **Integration Points**: Add hooks for external prioritization factors
4. **Validation**: Improve priority assignment validation
5. **Reporting**: Enhance output formatting and insights
