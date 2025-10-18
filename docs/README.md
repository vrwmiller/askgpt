# askgpt Workflow Visualization

This directory contains visual representations of the askgpt application workflow using popular diagram formats.

## Files

### 1. `askgpt-workflow.erd`
An Entity Relationship Diagram (ERD) that models the data structures and relationships within the askgpt application. This diagram shows:

- **Entities**: Major components like SESSION, USER_INPUT, MODEL_DISCOVERY, etc.
- **Attributes**: Key properties and data fields for each entity
- **Relationships**: How different components interact and relate to each other

**Best for**: Understanding the data model, component relationships, and system architecture.

### 2. `askgpt-flowchart.md`
A comprehensive flowchart showing the complete execution flow of the askgpt application. This diagram illustrates:

- **Process Flow**: Step-by-step execution from start to finish
- **Decision Points**: All conditional logic and branching
- **Error Handling**: Fallback mechanisms and error paths
- **API Interactions**: How the system communicates with OpenAI

**Best for**: Understanding program execution, debugging, and following the logical flow.

## Key Workflow Components

### 🚀 **Initialization Phase**
1. **Command Line Parsing** - Process user arguments and options
2. **Logging Setup** - Configure file and console logging based on debug mode
3. **Model Discovery** - Fetch available models from OpenAI API with fallback
4. **Validation** - Ensure model availability, token limits, and operation modes

### 🤖 **Question Phase**
- **Direct Question**: User provides question via `--question`
- **Random Generation**: AI generates question on any topic via `--random`
- **Topic Generation**: AI generates question about specific topic via `--topic`

### 💬 **Answer Phase**
- **API Call**: Send question to OpenAI model for answer generation
- **Fallback Logic**: Try alternative models if primary model fails
- **Response Validation**: Ensure answer quality and length

### 🔄 **Resilience Features**
- **Model Fallback**: Automatic retry with different models on failure
- **API Discovery**: Dynamic model list with static fallback
- **Parameter Adaptation**: Automatic parameter selection based on model capabilities
- **Error Handling**: Graceful degradation and informative error messages

## Usage Examples

### View ERD in VS Code
```bash
# Install Mermaid extension for VS Code
# Open askgpt-workflow.erd to see the entity relationships
```

### Render Flowchart
```bash
# View askgpt-flowchart.md in VS Code with Mermaid preview
# Or use any Mermaid-compatible renderer
```

### Generate PNG/SVG from Command Line
```bash
# Using mermaid-cli (if installed)
mmdc -i docs/askgpt-flowchart.md -o docs/askgpt-flowchart.png
mmdc -i docs/askgpt-workflow.erd -o docs/askgpt-workflow.png
```

## Understanding the Diagrams

### ERD Relationships
- **SESSION** is the central entity that coordinates all operations
- **USER_INPUT** captures command-line arguments and user preferences
- **MODEL_DISCOVERY** handles dynamic model fetching and validation
- **QUESTION_GENERATION** and **ANSWER_GENERATION** represent the core AI operations
- **API_CALL** tracks all interactions with OpenAI services
- **FALLBACK_ATTEMPT** documents resilience mechanisms
- **LOG_EVENT** captures comprehensive audit trail

### Flowchart Flow
- **Blue nodes**: Entry and success exit points
- **Green nodes**: Successful completion states
- **Red nodes**: Error conditions and failed exits
- **Orange nodes**: User interruption handling
- **Diamond shapes**: Decision points requiring conditional logic
- **Rectangle shapes**: Process steps and actions

## Benefits

### For Developers
- **System Understanding**: Clear view of component interactions
- **Debugging Aid**: Visual representation of execution paths
- **Architecture Planning**: Reference for system design decisions
- **Documentation**: Living documentation that stays current with code

### For Users
- **Transparency**: Understanding of how the tool works internally
- **Troubleshooting**: Visual guide for understanding error conditions
- **Feature Discovery**: See all available capabilities and options

### For Maintenance
- **Impact Analysis**: Understand downstream effects of changes
- **Testing Strategy**: Identify critical paths and edge cases
- **Performance Optimization**: Spot bottlenecks and inefficiencies

This visualization approach follows modern software documentation practices, making the askgpt workflow accessible to both technical and non-technical stakeholders.