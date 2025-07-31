from shared.config import get_default_model
# Import Strands-native observability
from shared.observability import get_callback
"""
Hypothesis Prioritization Agent

Agent that analyzes and prioritizes chaos engineering hypotheses based on expert evaluation.
Reads all hypotheses from the database, develops a prioritization framework, and updates
the database with priority rankings from 1 to N (1 = highest priority).

Input format: Simple trigger message
{
  "message": "Prioritize all hypotheses"
}
"""
from pathlib import Path
from strands import Agent
from strands_tools import file_write, file_read

# Import shared database tools
from shared.hypotheses import get_hypotheses, batch_update_hypothesis_priorities

# Load system prompt
current_file = Path(__file__)
prompt_file = current_file.parent / "system_prompt.md"

with open(prompt_file, 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

# Define the hypothesis prioritization agent
agent = Agent(
    model=get_default_model(),
    tools=[
        get_hypotheses,
        batch_update_hypothesis_priorities,
        file_write,
        file_read
    ],
    system_prompt=SYSTEM_PROMPT,
    callback_handler=get_callback("hypothesis-prioritization")
)
