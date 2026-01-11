# LightOS Dev Environment Templates

This directory contains project templates for quick app scaffolding with GLM-4.

## Available Templates

### 1. Fullstack React + FastAPI
**Stack:** React, Vite, Tailwind CSS, FastAPI, PostgreSQL
**Best for:** Data-driven applications, dashboards, admin panels
**Features:**
- React 18 with Vite build tool
- Tailwind CSS for styling
- FastAPI backend with async support
- PostgreSQL database integration
- JWT authentication ready
- API documentation with OpenAPI

**Usage:**
```python
from glm4_app_builder import GLM4AppBuilder

builder = GLM4AppBuilder()
builder.build_app(
    "Build a customer management system with CRUD operations",
    project_path="./my-crm-app"
)
```

### 2. Next.js + Supabase
**Stack:** Next.js, Tailwind CSS, Supabase (Auth + DB)
**Best for:** Content-heavy sites, blogs, e-commerce
**Features:**
- Next.js with App Router
- Server-side rendering (SSR)
- Supabase authentication
- Real-time database subscriptions
- File storage with Supabase Storage
- SEO optimizations

**Usage:**
```python
builder.config['glm4_builder']['default_stack'] = {
    'frontend': 'nextjs',
    'backend': 'supabase',
    'database': 'supabase',
    'auth': 'supabase'
}

builder.build_app(
    "Build a blog with user authentication and comments",
    project_path="./my-blog"
)
```

### 3. Vue + Express
**Stack:** Vue 3, Vite, Tailwind CSS, Express.js, PostgreSQL
**Best for:** Progressive web apps, real-time applications
**Features:**
- Vue 3 Composition API
- Vite for fast development
- Express.js REST API
- WebSocket support
- PostgreSQL with Sequelize ORM
- JWT authentication

**Usage:**
```python
builder.config['glm4_builder']['default_stack'] = {
    'frontend': 'vue',
    'backend': 'express',
    'database': 'postgresql',
    'auth': 'jwt'
}

builder.build_app(
    "Build a real-time chat application",
    project_path="./chat-app"
)
```

### 4. Python Full Stack
**Stack:** Streamlit/Dash, FastAPI, PostgreSQL
**Best for:** Data science apps, analytics dashboards, ML applications
**Features:**
- Streamlit for rapid UI development
- FastAPI for ML model serving
- PostgreSQL for data storage
- Plotly for visualizations
- Pandas integration
- ML model deployment ready

**Usage:**
```python
builder.config['glm4_builder']['default_stack'] = {
    'frontend': 'streamlit',
    'backend': 'fastapi',
    'database': 'postgresql',
    'auth': 'jwt'
}

builder.build_app(
    "Build a data analytics dashboard with chart visualizations",
    project_path="./analytics-dashboard"
)
```

## Template Structure

Each template follows this structure:

```
project-name/
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
├── frontend/             # Frontend application
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx/tsx
│   │   ├── App.jsx/tsx
│   │   ├── pages/
│   │   ├── components/
│   │   └── assets/
│   └── public/
├── backend/              # Backend API
│   ├── main.py or server.js
│   ├── requirements.txt or package.json
│   ├── models/
│   ├── routes/
│   └── utils/
└── database/             # Database schemas
    ├── schema.sql
    └── migrations/
```

## Customizing Templates

You can customize the default stack in `config/dev_config.yaml`:

```yaml
glm4_builder:
  default_stack:
    frontend: "react-vite-tailwind"
    backend: "fastapi"
    database: "postgresql"
    auth: "supabase"
```

## Example Prompts

### E-commerce Store
```
"Build an e-commerce store with product catalog, shopping cart, checkout, and admin panel"
```

### Task Management
```
"Build a project management tool with boards, tasks, assignments, and due dates like Trello"
```

### Social Network
```
"Build a social media platform with user profiles, posts, comments, likes, and followers"
```

### Learning Platform
```
"Build an online learning platform with courses, lessons, quizzes, and progress tracking"
```

### Analytics Dashboard
```
"Build a business analytics dashboard with charts, KPIs, data export, and report generation"
```

## Advanced Features

### Authentication Templates
- **JWT:** Manual token-based auth
- **Supabase:** Managed auth with social logins
- **Auth0:** Enterprise-grade auth
- **Clerk:** Developer-first auth

### Database Templates
- **PostgreSQL:** Full-featured SQL database
- **MongoDB:** NoSQL document database
- **Supabase:** PostgreSQL with real-time
- **Firebase:** NoSQL with offline support

### Deployment Templates
- **Vercel:** Next.js optimized
- **Netlify:** Static + serverless
- **Railway:** Full-stack deployment
- **AWS:** Scalable cloud infrastructure

## Tips for Best Results

1. **Be specific:** Include key features in your prompt
2. **Mention user roles:** If you need admin/user separation
3. **List main entities:** "users, products, orders"
4. **Specify integrations:** "with Stripe payment integration"
5. **Describe workflows:** "users can create, edit, and delete posts"

## Troubleshooting

### Build Failures
If the build fails:
1. Check the build logs in the orchestrator output
2. Verify all dependencies are installed
3. Ensure database is running (for DB-dependent apps)
4. Check port conflicts (3000, 5173, 8000)

### Preview Not Loading
1. Wait 30 seconds for dev server to start
2. Check browser console for errors
3. Verify build completed successfully
4. Check if backend is running (for full-stack apps)

### Auto-fix Not Working
Currently, auto-fix is limited. For complex errors:
1. Review the error logs
2. Manually fix critical issues
3. Re-run the build
4. Future versions will have better auto-fix

## Contributing Templates

To add a new template:
1. Create the template in `templates/`
2. Add generation logic to `glm4_app_builder.py`
3. Update this README
4. Submit a pull request
