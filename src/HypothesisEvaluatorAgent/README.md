# Hypothesis Evaluator Agent

This agent evaluates the quality of chaos engineering hypotheses using the LLM Judge Evaluation pattern from the Strands SDK.

## Features

- Evaluates hypotheses against five quality criteria
- Provides numerical scores from 1-5 for each criterion
- Calculates an overall quality score
- Stores evaluation results in the database
- Provides summary statistics and individual evaluations

## Quality Criteria

The agent evaluates hypotheses on five criteria:

1. **Testability (1-5)**: Can the hypothesis be implemented with AWS FIS?
2. **Specificity (1-5)**: How precise are the failure conditions and expected behavior?
3. **Realism (1-5)**: Is this a realistic failure scenario in production?
4. **Safety (1-5)**: Is the blast radius clearly bounded with minimal risk?
5. **Learning Value (1-5)**: Will testing provide valuable insights?

The overall score is calculated as the average of these five scores.

## Usage

### Running the Agent

```python
from HypothesisEvaluatorAgent.agent import hypothesis_evaluator_agent

# Evaluate specific hypotheses
result = hypothesis_evaluator_agent("""
{
  "hypothesis_ids": [1, 2, 3, 4, 5],
  "message": "Evaluate these hypotheses for quality"
}
""")

# Evaluate hypotheses by status
result = hypothesis_evaluator_agent("""
{
  "status_filter": "proposed",
  "limit": 20,
  "message": "Evaluate all proposed hypotheses"
}
""")

print(result)
```

## Database Schema

Evaluations are stored in the `hypothesis_evaluation` table:

```sql
CREATE TABLE hypothesis_evaluation (
    id SERIAL PRIMARY KEY,
    hypothesis_id INTEGER NOT NULL REFERENCES hypothesis(id),
    testability_score INTEGER NOT NULL CHECK (testability_score BETWEEN 1 AND 5),
    specificity_score INTEGER NOT NULL CHECK (specificity_score BETWEEN 1 AND 5),
    realism_score INTEGER NOT NULL CHECK (realism_score BETWEEN 1 AND 5),
    safety_score INTEGER NOT NULL CHECK (safety_score BETWEEN 1 AND 5),
    learning_value_score INTEGER NOT NULL CHECK (learning_value_score BETWEEN 1 AND 5),
    overall_score NUMERIC(3,2) NOT NULL,
    evaluation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (hypothesis_id)
);
```

## Available Tools

- **`get_hypotheses(...)`**: Retrieves hypotheses from the database
- **`insert_hypothesis_evaluation(...)`**: Inserts a single evaluation
- **`batch_insert_hypothesis_evaluations(...)`**: Inserts multiple evaluations
- **`get_hypothesis_evaluations(...)`**: Retrieves evaluations with filtering options
- **`display_hypothesis_evaluation_chart(...)`**: Generates charts for hypothesis evaluations

## Visualization Tools

The agent includes tools for visualizing hypothesis evaluation results in various chart formats:

### Chart Types

1. **Radar Charts**: Show all 5 criteria scores for each hypothesis in a radar/spider plot
2. **Bar Charts**: Compare scores across hypotheses for each criterion
3. **Heatmaps**: Show scores for all hypotheses and criteria in a color-coded grid
4. **Comparison Charts**: Show overall scores for all hypotheses in a ranked order
5. **Statistics Chart**: Show mean and standard deviation for each quality score across all evaluations

### Statistics Functionality

The agent includes functionality to calculate and display statistics for hypothesis evaluations:

```python
from HypothesisEvaluatorAgent.evaluation_charts import display_evaluation_statistics

# Get statistics for all evaluations
stats_result = display_evaluation_statistics()

# Access the statistics
if stats_result["success"]:
    stats = stats_result["statistics"]
    print(f"Mean testability score: {stats['average_scores']['testability']}")
    print(f"Standard deviation of testability: {stats['standard_deviations']['testability']}")
    
    # Generate a chart showing mean and standard deviation
    stats_chart = display_evaluation_statistics(output_path="stats_chart.png")
```

The statistics include:
- Mean scores for each criterion
- Standard deviations for each criterion
- Score distribution across ranges (1-2, 2-3, 3-4, 4-5)
- Highest and lowest overall scores

### Using the Chart Generation Tool

```python
from HypothesisEvaluatorAgent.evaluation_charts import display_hypothesis_evaluation_chart

# Generate a radar chart
radar_chart = display_hypothesis_evaluation_chart(
    chart_type="radar",
    hypothesis_ids=[1, 2, 3],  # Optional: specific hypothesis IDs
    min_overall_score=3.0,     # Optional: minimum score filter
    max_overall_score=5.0,     # Optional: maximum score filter
    limit=10,                  # Optional: maximum number of hypotheses
    output_path="charts/radar_chart.png"  # Optional: save to file
)

# Chart types: "radar", "bar", "heatmap", "comparison"
```

### Example Notebook

See `src/hypothesis_evaluation_charts_example.ipynb` for a complete example of how to use the chart generation functionality in a Jupyter notebook.

### Command-Line Chart Generation

A command-line script is provided for generating charts without using a notebook:

```bash
# Generate a radar chart (default)
python src/HypothesisEvaluatorAgent/generate_charts.py

# Generate a specific chart type
python src/HypothesisEvaluatorAgent/generate_charts.py --chart-type heatmap

# Filter by hypothesis IDs
python src/HypothesisEvaluatorAgent/generate_charts.py --hypothesis-ids 1 2 3

# Filter by score range
python src/HypothesisEvaluatorAgent/generate_charts.py --min-score 3.5 --max-score 5.0

# Generate all chart types
python src/HypothesisEvaluatorAgent/generate_charts.py --all-types

# Generate statistics chart with mean and standard deviation
python src/HypothesisEvaluatorAgent/generate_charts.py --statistics

# Generate statistics and all chart types
python src/HypothesisEvaluatorAgent/generate_charts.py --statistics --all-types

# Specify output directory
python src/HypothesisEvaluatorAgent/generate_charts.py --output-dir ./my-charts
```

The script can also be run directly if it has execute permissions:

```bash
chmod +x src/HypothesisEvaluatorAgent/generate_charts.py
./src/HypothesisEvaluatorAgent/generate_charts.py --all-types
```

### Dependencies

The chart generation functionality requires the following dependencies:
- matplotlib
- numpy

These dependencies can be installed using pip:
```
pip install matplotlib numpy
```

## Implementation Details

This agent implements the "LLM Judge Evaluation" pattern from the Strands SDK, which uses an LLM to evaluate the quality of generated content. In this case, it evaluates the quality of chaos engineering hypotheses generated by the HypothesisGeneratorAgent.

The evaluation process:

1. Retrieves hypotheses from the database using the provided filters
2. Evaluates each hypothesis against the five quality criteria
3. Calculates an overall quality score for each hypothesis
4. Stores the evaluation results in the database
5. Returns a summary of the evaluation results

## Example Response

```json
{
  "summary": {
    "hypotheses_evaluated": 5,
    "average_scores": {
      "testability": 4.2,
      "specificity": 3.8,
      "realism": 4.0,
      "safety": 3.6,
      "learning_value": 4.4,
      "overall": 4.0
    },
    "score_distribution": {
      "1-2": 0,
      "2-3": 1,
      "3-4": 2,
      "4-5": 2
    }
  },
  "evaluations": [
    {
      "hypothesis_id": 1,
      "title": "We believe that if 50% of ECS tasks are terminated then the application will maintain availability because auto-scaling will replace failed tasks within 2 minutes",
      "scores": {
        "testability": 5,
        "specificity": 5,
        "realism": 4,
        "safety": 3,
        "learning_value": 4,
        "overall": 4.2
      },
      "rationale": "This hypothesis is highly testable with AWS FIS, has clear failure conditions and expectations, represents a common failure mode, has a moderate blast radius, and would provide valuable insights about auto-scaling behavior."
    },
    // Additional evaluations...
  ],
  "database_status": {
    "evaluations_stored": 5,
    "message": "All evaluations successfully stored in the database"
  }
}
