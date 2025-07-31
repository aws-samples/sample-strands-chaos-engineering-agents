# Shared Database Tools

Centralized database tools for all Chaos Agent components.

## Available Tools

### System Components
```python
from shared.system_components import insert_system_component, update_system_component, get_system_components

# Insert new system component (returns ID or None)
component_id = insert_system_component(
    name="Web API",
    component_type="ECS Service", 
    description="Main web API service"
)

# Update existing system component (returns True/False)
success = update_system_component(
    component_id=1,
    component_type="ECS Fargate Service",
    description="Updated description"
)

# Get with optional filtering
components = get_system_components(component_type="ECS Service", limit=50)
```

### Hypotheses
```python
from shared.hypotheses import insert_hypothesis, update_hypothesis, get_hypotheses

# Insert new hypothesis (returns ID or None)
hypothesis_id = insert_hypothesis(
    title="API maintains performance during high load",
    description="Test API resilience under load",
    persona="End User",
    status="proposed",
    priority=2,
    system_component_id=1
)

# Update existing hypothesis (returns True/False)
success = update_hypothesis(
    hypothesis_id=1,
    status="prioritized",
    priority=1
)

# Get with filtering
hypotheses = get_hypotheses(status_filter="proposed", limit=25)
```

### Experiments
```python
from shared.experiments import insert_experiment, get_experiments, update_experiment

# Insert experiment (returns ID or None)
experiment_id = insert_experiment(
    experiment_name="Load Test Experiment",
    hypothesis_id=1,
    description="Test system under load",
    experiment_plan="1. Baseline\n2. Apply load\n3. Monitor",
    fis_configuration={"actions": {...}},
    status="draft"
)

# Get with filtering
experiments = get_experiments(status_filter="draft", limit=10)

# Update experiment (returns True/False)
success = update_experiment(
    experiment_id=1,
    status="planned",
    fis_experiment_id="fis-123",
    experiment_notes="Ready for execution"
)
```

### Database Views
```python
from shared.views import get_experiments_with_context

# Get experiments with full context (hypothesis + system component info)
result = get_experiments_with_context(
    status_filter="draft",
    hypothesis_status_filter="prioritized",
    component_type_filter="ECS Service",
    limit=5
)
```

## Import Everything
```python
from shared import (
    insert_system_component, update_system_component, get_system_components,
    insert_hypothesis, update_hypothesis, get_hypotheses,
    insert_experiment, get_experiments, update_experiment,
    get_experiments_with_context
)
```

## Function Types
- **`insert_*`**: INSERT operations for creating new records
- **`update_*`**: UPDATE operations for modifying existing records
- **`get_*`**: Retrieve with filtering and pagination
