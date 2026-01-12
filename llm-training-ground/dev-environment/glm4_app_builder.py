#!/usr/bin/env python3
"""
GLM-4 Autonomous App Builder
Turns single natural-language prompts into fully working web applications.
Integrates with LightOS build server for real-time preview and iteration.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import yaml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# System meta-prompt for GLM-4 App Builder
SYSTEM_META_PROMPT = """You are an autonomous App-Builder Agent powered by GLM-4.
Your job is to turn a single natural-language idea into a fully working web application, not just isolated code snippets.
The app must be production-structured: clear frontend, backend, database schema, and deployment configuration.

1. Overall behavior
Always follow this loop:

UNDERSTAND the user's idea and restate the requirements.

PLAN the app as tasks and files.

BUILD an initial end-to-end vertical slice (frontend + backend + DB).

CHECK & FIX by running tests, linters, and any available dev server logs.

ITERATE until the app starts, loads in a browser, and basic flows work.

Prefer small, safe changes over huge rewrites.

Always keep the project in a runnable state after each change.

2. Architecture constraints
Default stack:

Frontend: React + Tailwind + Vite (or Lovable's default web stack).

Backend: Node/TypeScript or Python (use the environment default).

Database: Supabase/PostgreSQL or the platform's default DB integration.

Every app must include:

Routing (multiple pages or views as needed).

A persistent data model (tables or collections) for the main entities.

Authentication if the user's idea implies personal or multi-user data.

Basic error handling and loading states.

3. Planning step (required)
Before touching code, output a JSON "PLAN" with:

{
  "app_summary": "...",
  "pages": ["..."],
  "data_models": ["..."],
  "api_endpoints": ["..."],
  "key_flows": ["..."]
}

Think through the entities, user flows, and non-functional requirements (auth, rate limits, etc.).

Only after emitting "PLAN" may you start editing files.

4. File & code editing behavior
Use minimal, targeted edits to existing files rather than rewriting whole projects.

When adding or editing code, always:

Keep imports, types, and styles consistent with the rest of the project.

Avoid pseudocode; write real, executable code.

Keep secrets and keys out of the repo; assume they come from environment variables.

When you create new files, update all relevant imports and routes.

5. Running & debugging
After significant changes:

Run the test or dev command provided by the environment (npm test, npm run dev, etc.).

If there are errors, read the logs and prioritize fixing runtime errors before adding features.

Use structured reasoning:

Explain briefly what broke, why, and how the fix will work.

6. Interaction model
Treat a single user prompt as a feature spec, not a one-off request.

When the user later asks for changes ("add dark mode", "add a dashboard"), treat them as incremental feature requests and extend the existing app in place.

Ask clarifying questions only when required to avoid guessing critical business logic.

7. Output discipline
When planning or summarizing, output valid JSON or Markdown as requested.

When editing code, output only the necessary file diffs or full file contents according to the tool protocol.

Do not include explanations inside source files except short comments.

Your goal: behave like a full-stack coding agent that can repeatedly turn high-level prompts into real, runnable applications and then evolve them over time.
"""


class BuildPhase(Enum):
    """Build phases"""
    UNDERSTAND = "understand"
    PLAN = "plan"
    BUILD = "build"
    CHECK = "check"
    FIX = "fix"
    ITERATE = "iterate"
    COMPLETE = "complete"


@dataclass
class AppPlan:
    """Application plan structure"""
    app_summary: str
    pages: List[str]
    data_models: List[str]
    api_endpoints: List[str]
    key_flows: List[str]
    tech_stack: Dict[str, str]
    requirements: List[str]

    def to_dict(self):
        return {
            "app_summary": self.app_summary,
            "pages": self.pages,
            "data_models": self.data_models,
            "api_endpoints": self.api_endpoints,
            "key_flows": self.key_flows,
            "tech_stack": self.tech_stack,
            "requirements": self.requirements
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class BuildIteration:
    """Single build iteration"""
    phase: BuildPhase
    timestamp: float
    actions: List[str]
    errors: List[str]
    fixes: List[str]
    success: bool


class GLM4AppBuilder:
    """Autonomous app builder using GLM-4"""

    def __init__(
        self,
        model_size: str = "9b",
        config_path: Optional[Path] = None,
        device: Optional[str] = None
    ):
        self.model_size = model_size
        self.model_name = f"THUDM/glm-4-{model_size}"

        # Load config
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "dev_config.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Determine device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.device = device
        logger.info(f"Using device: {self.device}")

        # Load model and tokenizer
        logger.info(f"Loading GLM-4 {model_size} model...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            device_map="auto" if self.device == "cuda" else None,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )

        if self.device != "cuda":
            self.model = self.model.to(self.device)

        self.model.eval()

        # Build state
        self.current_phase = BuildPhase.UNDERSTAND
        self.current_plan: Optional[AppPlan] = None
        self.iterations: List[BuildIteration] = []
        self.project_path: Optional[Path] = None

        logger.info("GLM-4 App Builder initialized")

    def _generate(
        self,
        messages: List[Dict[str, str]],
        max_length: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Generate response from GLM-4"""
        # Add system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_META_PROMPT}
        ] + messages

        # Apply chat template
        inputs = self.tokenizer.apply_chat_template(
            full_messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode
        response = self.tokenizer.decode(
            outputs[0][inputs.shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()

    def understand_requirement(self, user_prompt: str) -> str:
        """Phase 1: Understand the user's idea"""
        logger.info("Phase 1: Understanding requirement...")
        self.current_phase = BuildPhase.UNDERSTAND

        messages = [
            {
                "role": "user",
                "content": f"""I want to build: {user_prompt}

Please restate the requirements and ask any critical clarifying questions needed to avoid guessing business logic."""
            }
        ]

        response = self._generate(messages)
        logger.info(f"Understanding: {response}")
        return response

    def create_plan(self, user_prompt: str, understanding: str) -> AppPlan:
        """Phase 2: Create application plan"""
        logger.info("Phase 2: Creating plan...")
        self.current_phase = BuildPhase.PLAN

        # Get default stack from config
        default_stack = self.config.get('glm4_builder', {}).get('default_stack', {})

        messages = [
            {
                "role": "user",
                "content": f"""Original request: {user_prompt}

Understanding: {understanding}

Create a detailed JSON PLAN for this application. Use this default stack:
- Frontend: {default_stack.get('frontend', 'react-vite-tailwind')}
- Backend: {default_stack.get('backend', 'fastapi')}
- Database: {default_stack.get('database', 'postgresql')}
- Auth: {default_stack.get('auth', 'supabase')}

Output ONLY the JSON plan in this exact format:
{{
  "app_summary": "Brief description",
  "pages": ["list of pages/views"],
  "data_models": ["list of entities/tables"],
  "api_endpoints": ["list of API routes"],
  "key_flows": ["list of main user flows"],
  "tech_stack": {{"frontend": "...", "backend": "...", "database": "...", "auth": "..."}},
  "requirements": ["list of functional and non-functional requirements"]
}}"""
            }
        ]

        response = self._generate(messages, temperature=0.3)

        # Extract JSON from response
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                plan_dict = json.loads(json_str)

                self.current_plan = AppPlan(
                    app_summary=plan_dict.get('app_summary', ''),
                    pages=plan_dict.get('pages', []),
                    data_models=plan_dict.get('data_models', []),
                    api_endpoints=plan_dict.get('api_endpoints', []),
                    key_flows=plan_dict.get('key_flows', []),
                    tech_stack=plan_dict.get('tech_stack', default_stack),
                    requirements=plan_dict.get('requirements', [])
                )

                logger.info(f"Plan created: {self.current_plan.app_summary}")
                return self.current_plan

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            logger.error(f"Response: {response}")

            # Create a basic plan
            self.current_plan = AppPlan(
                app_summary=user_prompt,
                pages=["Home", "Dashboard"],
                data_models=["User"],
                api_endpoints=["/api/health"],
                key_flows=["User visits home page"],
                tech_stack=default_stack,
                requirements=["Build a working application"]
            )

            return self.current_plan

    def generate_project_structure(self, plan: AppPlan) -> Dict[str, str]:
        """Generate initial project structure and files"""
        logger.info("Generating project structure...")
        self.current_phase = BuildPhase.BUILD

        # Determine template based on tech stack
        frontend = plan.tech_stack.get('frontend', 'react-vite-tailwind')
        backend = plan.tech_stack.get('backend', 'fastapi')

        files = {}

        # Frontend files
        if 'react' in frontend.lower():
            files.update(self._generate_react_vite_files(plan))

        # Backend files
        if 'fastapi' in backend.lower():
            files.update(self._generate_fastapi_files(plan))
        elif 'express' in backend.lower():
            files.update(self._generate_express_files(plan))

        # Configuration files
        files.update(self._generate_config_files(plan))

        return files

    def _generate_react_vite_files(self, plan: AppPlan) -> Dict[str, str]:
        """Generate React + Vite frontend files"""
        files = {}

        # package.json
        files['package.json'] = json.dumps({
            "name": plan.app_summary.lower().replace(' ', '-'),
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.21.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.43",
                "@types/react-dom": "^18.2.17",
                "@vitejs/plugin-react": "^4.2.1",
                "autoprefixer": "^10.4.16",
                "eslint": "^8.55.0",
                "eslint-plugin-react": "^7.33.2",
                "eslint-plugin-react-hooks": "^4.6.0",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.4.0",
                "vite": "^5.0.8"
            }
        }, indent=2)

        # vite.config.js
        files['vite.config.js'] = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0'
  }
})
"""

        # tailwind.config.js
        files['tailwind.config.js'] = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5',
        secondary: '#06B6D4',
      }
    },
  },
  plugins: [],
}
"""

        # index.html
        files['index.html'] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{plan.app_summary}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

        # src/main.jsx
        files['src/main.jsx'] = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

        # src/index.css
        files['src/index.css'] = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
"""

        # src/App.jsx
        pages_components = '\n'.join([
            f"import {page.replace(' ', '')} from './pages/{page.replace(' ', '')}';"
            for page in plan.pages
        ])

        pages_routes = '\n'.join([
            f"        <Route path=\"/{page.lower().replace(' ', '-')}\" element={{<{page.replace(' ', '')} />}} />"
            for page in plan.pages
        ])

        files['src/App.jsx'] = f"""import React from 'react';
import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';
{pages_components}

function App() {{
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
{pages_routes}
        </Routes>
      </div>
    </Router>
  );
}}

export default App;
"""

        # Generate page components
        for page in plan.pages:
            page_name = page.replace(' ', '')
            files[f'src/pages/{page_name}.jsx'] = f"""import React from 'react';

function {page_name}() {{
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">{page}</h1>
      <p className="text-gray-600">Welcome to the {page} page.</p>
    </div>
  );
}}

export default {page_name};
"""

        return files

    def _generate_fastapi_files(self, plan: AppPlan) -> Dict[str, str]:
        """Generate FastAPI backend files"""
        files = {}

        # requirements.txt
        files['backend/requirements.txt'] = """fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
"""

        # main.py
        models_imports = '\n'.join([
            f"from models import {model}"
            for model in plan.data_models
        ])

        api_routes = '\n'.join([
            f'@app.{endpoint.split()[0].lower() if " " in endpoint else "get"}("{endpoint.split()[1] if " " in endpoint else endpoint}")\nasync def {endpoint.replace("/", "_").replace("-", "_").split()[1] if " " in endpoint else "handler"}():\n    return {{"message": "Not implemented"}}\n'
            for endpoint in plan.api_endpoints
        ])

        files['backend/main.py'] = f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="{plan.app_summary}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "{plan.app_summary} API", "status": "running"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

{api_routes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

        # models.py
        model_classes = '\n\n'.join([
            f"""class {model}(BaseModel):
    id: int
    name: str
    created_at: datetime = Field(default_factory=datetime.now)"""
            for model in plan.data_models
        ])

        files['backend/models.py'] = f"""from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

{model_classes}
"""

        # .env.example
        files['backend/.env.example'] = """DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
"""

        return files

    def _generate_express_files(self, plan: AppPlan) -> Dict[str, str]:
        """Generate Express.js backend files"""
        files = {}

        # package.json
        files['backend/package.json'] = json.dumps({
            "name": f"{plan.app_summary.lower().replace(' ', '-')}-api",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "nodemon server.js",
                "start": "node server.js"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "dotenv": "^16.3.1",
                "pg": "^8.11.3"
            },
            "devDependencies": {
                "nodemon": "^3.0.2"
            }
        }, indent=2)

        # server.js
        files['backend/server.js'] = f"""import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {{
  res.json({{ message: '{plan.app_summary} API', status: 'running' }});
}});

app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy' }});
}});

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
"""

        return files

    def _generate_config_files(self, plan: AppPlan) -> Dict[str, str]:
        """Generate configuration files"""
        files = {}

        # README.md
        files['README.md'] = f"""# {plan.app_summary}

## Overview
{plan.app_summary}

## Tech Stack
- Frontend: {plan.tech_stack.get('frontend', 'React + Vite + Tailwind')}
- Backend: {plan.tech_stack.get('backend', 'FastAPI')}
- Database: {plan.tech_stack.get('database', 'PostgreSQL')}
- Auth: {plan.tech_stack.get('auth', 'Supabase')}

## Getting Started

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Features
{chr(10).join([f'- {flow}' for flow in plan.key_flows])}

## Pages
{chr(10).join([f'- {page}' for page in plan.pages])}

## API Endpoints
{chr(10).join([f'- {endpoint}' for endpoint in plan.api_endpoints])}

## Data Models
{chr(10).join([f'- {model}' for model in plan.data_models])}
"""

        # .gitignore
        files['.gitignore'] = """node_modules/
dist/
build/
.env
.env.local
*.log
.DS_Store
__pycache__/
*.py[cod]
venv/
"""

        return files

    def write_project_files(self, project_path: Path, files: Dict[str, str]):
        """Write generated files to disk"""
        logger.info(f"Writing {len(files)} files to {project_path}")

        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)

        logger.info("Project files written successfully")

    def build_app(
        self,
        user_prompt: str,
        project_path: Path,
        max_iterations: int = 10
    ) -> bool:
        """Main build loop"""
        self.project_path = project_path
        max_iter = self.config.get('glm4_builder', {}).get('max_iterations', max_iterations)

        logger.info(f"Building app: {user_prompt}")
        logger.info(f"Project path: {project_path}")

        # Phase 1: Understand
        understanding = self.understand_requirement(user_prompt)

        # Phase 2: Plan
        plan = self.create_plan(user_prompt, understanding)
        logger.info(f"Plan:\n{plan.to_json()}")

        # Phase 3: Build
        files = self.generate_project_structure(plan)
        self.write_project_files(project_path, files)

        logger.info(f"Initial project created with {len(files)} files")

        return True


def main():
    """Example usage"""
    # Initialize builder
    builder = GLM4AppBuilder(model_size="9b")

    # Build an app
    user_prompt = "Build a LightOS training job dashboard with run list, job details, and S3-backed artifacts"
    project_path = Path("./projects/lightos-dashboard")

    success = builder.build_app(user_prompt, project_path)

    if success:
        logger.info(f"App built successfully at {project_path}")
    else:
        logger.error("App build failed")


if __name__ == "__main__":
    main()
