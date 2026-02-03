# Deep Dive: FlowEngine

## Overview

The `FlowEngine` is the core orchestrator of the conversation. It handles the "Iron Logic" of moving a candidate through the recruitment funnel, from the initial greeting to the final data submission.

## Architecture: Dispatch Pattern

The `FlowEngine` uses a **Dispatch Pattern** instead of long conditional chains. This improves readability and makes it easier to add or modify states.

```python
self._handlers = {
    self.STATE_IDLE: self._handle_idle,
    self.STATE_GREETED: self._handle_greeted,
    # ...
}
```

### Key Components

- **State Discovery**: The engine retrieves the current state of a lead from the database (`conversation_stage`).
- **Handler Execution**: It fetches the corresponding handler from the dispatch table and executes it with the user's message.
- **State Transition**: Handlers return a tuple containing the `next_state` and the `response_message`.
- **Persistence**: The engine automatically commits the new state to the database after each interaction.

## State Definitions

| State Constant | ID | Description |
|----------------|----|-------------|
| `STATE_IDLE` | 0 | Initial state before any interaction. |
| `STATE_GREETED` | 1 | Greeting sent, waiting for candidate to choose Job or Info. |
| `STATE_JOB_SELECTED` | 2 | Job list shown, waiting for specific job selection. |
| `STATE_REQ_1..3` | 3-5 | Screening questions (Experience, Tech, Mindset). |
| `STATE_NAME/PHONE` | 6-7 | Personal data collection. |
| `STATE_CV/COVER` | 8-9 | Document upload monitoring. |
| `STATE_COMPLETED` | 99 | Application finished. |

## AI Integration

The `FlowEngine` delegates complex decisions to the `OpenAI Service`:
1. **Intention Parsing**: "Did they mean Job 1 or Job 2?"
2. **Sentiment/Logic Check**: "Did they answer 'Yes' or 'No' to the experience question?"
3. **Response Generation**: Creating human-like transitions between screening steps.

## Implementation Details

### Handling Reset
The engine intercepts "reset" or "start" commands at the beginning of `process_message` to allow candidates to restart their application at any time.

### Error Handling
Each handler is responsible for its own validation logic (e.g., checking if a name is long enough or if a PDF was uploaded). If validation fails, the handler returns the *current* state to stay on the same step.
