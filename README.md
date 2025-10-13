# AI Writing Assistant

A single page app that rephrases text into multiple writing styles using OpenAI's API. Built with React (frontend) and FastAPI (backend).

## Quick Start

### Prerequisites

- **Docker Desktop** (recommended)
- OR **Node.js** and **Python**
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd rephraser
```

2. **Set your OpenAI API key**

Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Or set it as an environment variable:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**macOS/Linux:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. **Start the application**
```bash
docker compose up
```
> **Note:** The default `docker-compose.yml` is configured for development. Production Docker files (`Dockerfile.prod` and `docker-compose.prod.yml`) are available but have not yet been tested.

4. **Access the app**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create and activate a virtual environment (recommended)**

> For more details, see the [FastAPI Virtual Environments Guide](https://fastapi.tiangolo.com/virtual-environments/#create-a-project)

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Set your OpenAI API key** (see above)

5. **Run the backend**
```bash
python main.py
```

Backend will be available at http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal)
```bash
cd frontend
```

2. **Install Node dependencies**
```bash
npm install
```

3. **Run the development server**
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

## Usage

1. **Enter your text** in the input field
2. **Click "Process"** to generate rephrased versions
4. **Click "Cancel"** to stop the generation

## Project Structure

### Frontend
- `/src/components/` - React components
- `/src/hooks/` - Custom React hooks
- `/src/styles/` - Global styles and theme
- `/src/test/` - Tests

### Backend
- `/app/routes/` - API endpoints
- `/app/services/` - Business logic
- `/app/security/` - Security features
- `/app/llm/` - OpenAI integration
- `/tests/` - Tests
