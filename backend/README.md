# Backend - AI Writing Assistant

### Project Structure

```
backend/
├── main.py                # Application entry point
├── app/
│   ├── main.py            # FastAPI app configuration
│   ├── config.py          # Environment and settings
│   ├── routes/            # API endpoints
│   │   └── rephrase.py    # Rephrase API routes
│   ├── services/          # Business logic
│   │   └── rephrase.py    # Rephrase service
│   ├── llm/               # LLM integration
│   │   └── openai_client.py
│   ├── security/          # Security components
│   │   ├── prompt_injection_filter.py
│   │   ├── output_validator.py
│   │   └── secure_llm_pipeline.py
│   └── models/            # Request/response models
│       └── requests.py
└── tests/                 # Tests
```

> **Note on Tests:** In preference of time and due to the simplicity and large number of tests, the tests were LLM-generated. They all passed and were quickly reviewed to confirm they made sense.

## How It Works

### 1. Request Flow

```
Client Request → Security Filter → LLM Processing → Validation → Stream Response
```

### 2. API Endpoints

#### `POST /v1/rephrase`
Creates a rephrase request and returns a unique `request_id`.

**Request:**
```json
{
  "text": "Your text here",
  "styles": ["professional", "casual", "polite", "social"]
}
```

**Response:**
```json
{
  "request_id": "uuid-string"
}
```

#### `GET /v1/rephrase/stream?request_id={id}`
Opens SSE connection to stream rephrased text.

**SSE Events:**
- `delta`: Partial text chunks as they're generated
- `complete`: Style completion notification
- `error`: Security or validation errors
- `end`: All styles processed

#### `DELETE /v1/rephrase/{request_id}`
Cancels an active rephrase request.
