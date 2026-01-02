# Technical Challenge: Persistent Chat API with LangChain

## Objective

Develop a REST API that facilitates stateful conversations with a Large Language Model (LLM). The system must persist chat history in a database and provide metadata for individual chat sessions.

## Time Limit

120 Minutes

## Tech Stack

- **Language:** Python (FastAPI or Flask)
    
- **Orchestration:** LangChain
    
- **Database:** SQLite
    
- **LLM Provider:** OpenAI, Anthropic, or Ollama
    

---

## Requirements

### 1. Endpoint: `POST /chat`

- **Payload:**
    
    JSON
    
    ```
    {
      "session_id": "string",
      "message": "string"
    }
    ```
    
- **Logic:**
    
    - If the `session_id` does not exist, initialize a new session and trigger the **Auto-Titling** logic (see below).
        
    - Retrieve the previous message history for the given `session_id`.
        
    - Use LangChain to send the user's message plus the last 5 messages of context to the LLM.
        
    - Persist the user message and the LLM response in the database.
        
- **Response:** The LLM's generated text.
    

### 2. Endpoint: `GET /sessions`

- **Output:** A list of all unique chat sessions stored in the database.
    
- **Data per session:** `session_id`, `title`, and `created_at` timestamp.
    

### 3. Endpoint: `GET /history/{sessionId}`

- **Output:** A list of messages for a session ID 
### 4. Feature: Mandatory Auto-Titling

- When a `session_id` is used for the first time, the application must perform an additional LLM call.
    
- This call should analyze the first message and generate a concise title (3–5 words).
    
- This title must be saved in a `sessions` table and appear in the `/sessions` response.
    

---

## Evaluation Criteria

### Technical Proficiency

- **LangChain Integration**
- **Database Schema** 
- **Prompt Engineering**
    
### Code Quality

- **Error Handling**
- **Efficiency** 
- **Organization** 
    

---

## Setup Instructions (Recommended)

- Use `sqlite3` or `SQLAlchemy` for the database.
    
- Use `pydantic` for request validation (if using FastAPI).
    
- Keep all logic in a single directory; a full production-ready folder structure is not required given the time constraint.
    
