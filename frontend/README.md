# Frontend - AI Writing Assistant

### Project Structure

```
frontend/
├── src/
│   ├── main.jsx           # App entry point
│   ├── App.jsx            # Main app component
│   ├── App.module.css     # App styles
│   ├── components/        # Reusable UI components
│   │   ├── ThemeToggle/   # Light/dark mode switcher
│   │   ├── PromptForm/    # Text input form
│   │   ├── ResultsGrid/   # Results display
│   │   ├── StyleCard/     # Individual style result card
│   │   └── ShinyText/     # Animated text effect
│   ├── hooks/             # Custom React hooks
│   │   └── useRephrase.js # Main rephrasing logic
│   ├── styles/            # Global styles
│   └── test/              # Tests
├── public/                # Static assets
├── index.html             # HTML template
└── vite.config.js         # Vite configuration
```

> **Note on Tests:** In preference of time and due to the simplicity and large number of tests, the tests were LLM-generated. They all passed and were quickly reviewed to confirm they made sense.

## How It Works

### 1. User Flow

```
User Input → Submit → Backend Request → SSE Stream → Display Results
```

### 2. Streaming

#### Step 1: Create Request
```javascript
const response = await fetch('/v1/rephrase', {
  method: 'POST',
  body: JSON.stringify({ text, styles: ['professional', 'casual', 'polite', 'social'] })
});
const { request_id } = await response.json();
```

#### Step 2: Stream Results
```javascript
const eventSource = new EventSource(`/v1/rephrase/stream?request_id=${request_id}`);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'delta') {
    // Append text chunk to the appropriate style
    setOutputs(prev => ({
      ...prev,
      [data.style]: prev[data.style] + data.text
    }));
  }
};
```