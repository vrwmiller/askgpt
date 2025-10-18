# askgpt Workflow - Text Visualization

This document provides a comprehensive text-based visualization of the askgpt workflow using only Markdown formatting.

## 📋 **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Command Line   │───▶│   Core Engine   │───▶│    OpenAI API   │
│   Interface     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Logging System │    │ Fallback Logic  │    │  Response Data  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 **Complete Execution Flow**

### **Phase 1: Initialization**
```
START
  ↓
Parse Command Line Arguments
  ↓
Setup Logging System
  ├─ File Handler (always active) → logs/askgpt.log
  └─ Console Handler (debug mode only)
  ↓
Initialize Random Seed
  ↓
Fetch Available Models from OpenAI API
  ├─ SUCCESS → Use API Model List
  └─ FAILURE → Use Fallback Model List
  ↓
Validate Requested Model
  ├─ INVALID → Display Error & EXIT
  └─ VALID → Continue
  ↓
Validate Token Counts & Operation Mode
  ├─ INVALID → Display Error & EXIT
  └─ VALID → Initialize OpenAI Client
```

### **Phase 2: Question Determination**
```
Question Source Decision
  ├─ --question → Use Direct Question
  ├─ --random → Generate Random Question
  └─ --topic → Generate Topic-Specific Question
  ↓
[IF GENERATION NEEDED]
Call OpenAI API for Question Generation
  ├─ SUCCESS → Use Generated Question
  └─ FAILURE → Try Fallback Models
      ├─ gpt-4o → Try Next
      ├─ gpt-4o-mini → Try Next
      ├─ gpt-4-turbo → Try Next
      ├─ gpt-4 → Try Next
      └─ gpt-3.5-turbo → Last Resort
  ↓
Display Question to User
```

### **Phase 3: Answer Generation**
```
Call OpenAI API for Answer Generation
  ├─ SUCCESS → Use Generated Answer
  └─ FAILURE → Try Fallback Models
      ├─ Same fallback sequence as above
      └─ All failed → EXIT with error
  ↓
Display Answer to User
  ↓
Log Session Complete
  ↓
END (Success)
```

## 🏗️ **Data Structures & Relationships**

### **Core Entities**

#### **SESSION**
- `session_id` (Primary Key)
- `start_time`
- `command_args`
- `debug_mode`
- `log_file_path`
- `status`

**Relationships:**
- Has one USER_INPUT
- Has one MODEL_DISCOVERY
- Has zero or one QUESTION_GENERATION
- Has one ANSWER_GENERATION
- Has many API_CALLs
- Has many LOG_EVENTs
- Has zero or many FALLBACK_ATTEMPTs

#### **USER_INPUT**
- `operation_mode` (random|topic|question)
- `topic` (if topic mode)
- `direct_question` (if question mode)
- `model_requested`
- `question_tokens`
- `answer_tokens`

#### **MODEL_DISCOVERY**
- `api_success` (boolean)
- `available_models[]`
- `selected_model`

#### **QUESTION_GENERATION** (optional)
- `source_type` (random|topic)
- `model_used`
- `temperature` (0.9 for creativity)
- `generated_question`
- `generation_time`
- `fallback_used`

#### **ANSWER_GENERATION**
- `question_text`
- `model_used`
- `temperature` (0.7 for balance)
- `generated_answer`
- `generation_time`
- `fallback_used`

## 🔧 **API Interaction Patterns**

### **Model Compatibility Logic**
```
For each API call:
  ↓
Check Model Type
  ├─ Newer Models (gpt-5, gpt-4o, o1, o3, o4)
  │   ├─ Use: max_completion_tokens
  │   └─ Temperature: Default only (1.0)
  └─ Legacy Models (gpt-4, gpt-3.5-turbo)
      ├─ Use: max_tokens
      └─ Temperature: Custom allowed
  ↓
Execute API Call
  ├─ SUCCESS → Return response
  └─ FAILURE → Trigger fallback
```

### **Fallback Sequence**
```
Primary Model Fails
  ↓
Try: gpt-5
  ├─ SUCCESS → Use result
  └─ FAIL → Try: gpt-4o
      ├─ SUCCESS → Use result
      └─ FAIL → Try: gpt-4o-mini
          ├─ SUCCESS → Use result
          └─ FAIL → Try: gpt-4-turbo
              ├─ SUCCESS → Use result
              └─ FAIL → Try: gpt-4
                  ├─ SUCCESS → Use result
                  └─ FAIL → Try: gpt-3.5-turbo
                      ├─ SUCCESS → Use result
                      └─ FAIL → EXIT with error
```

## 🚨 **Error Handling Matrix**

| Error Type | Detection Point | Action | Exit Code |
|------------|----------------|---------|-----------|
| Missing API Key | Client Init | Display error message | 1 |
| Invalid Model | Validation | Show available models | 1 |
| Invalid Tokens | Validation | Show error message | 1 |
| No Operation Mode | Validation | Show usage help | 1 |
| Multiple Modes | Validation | Show conflict error | 1 |
| API Failure | Runtime | Try fallback models | 1 (if all fail) |
| User Interrupt | Runtime | Graceful cancellation | 1 |
| Unexpected Error | Runtime | Log error & exit | 1 |

## 📊 **Logging Strategy**

### **File Logging (Always Active)**
- **Location**: `logs/askgpt.log`
- **Level**: INFO (or DEBUG if debug mode)
- **Format**: `YYYY-MM-DD HH:MM:SS - askgpt - LEVEL - MESSAGE`

### **Console Logging (Debug Mode Only)**
- **Trigger**: `--debug` flag
- **Content**: Same as file + additional debug info
- **Purpose**: Real-time troubleshooting

### **Key Log Events**
```
Session Start
  ├─ Command line arguments
  ├─ Model discovery results
  ├─ Question generation attempts
  ├─ API call timing & results
  ├─ Fallback attempts & outcomes
  └─ Session completion status
```

## 🎯 **Operation Modes Comparison**

| Mode | Input Required | Question Source | Use Case |
|------|---------------|-----------------|----------|
| `--random` | None | AI Generated | Explore random topics |
| `--topic "X"` | Topic string | AI Generated | Focus on specific area |
| `--question "Y"` | Full question | User Provided | Direct Q&A |

## 🔄 **State Transitions**

```
IDLE
  ↓ (command execution)
INITIALIZING
  ↓ (validation complete)
DISCOVERING_MODELS
  ↓ (models fetched)
GENERATING_QUESTION (if needed)
  ↓ (question ready)
GENERATING_ANSWER
  ↓ (answer ready)
DISPLAYING_RESULTS
  ↓ (output complete)
COMPLETED
```

## 💡 **Key Design Principles**

1. **Resilience**: Multiple fallback models ensure reliability
2. **Flexibility**: Three operation modes serve different use cases
3. **Transparency**: Comprehensive logging for debugging
4. **Compatibility**: Automatic parameter adaptation for different models
5. **Usability**: Clear error messages and helpful usage information

This text-based visualization captures the complete askgpt workflow using only standard Markdown formatting, making it universally readable without any special tools or software!