# LightOS Dev Environment - Quick Start

Get your first app running in under 5 minutes!

## Installation

```bash
# Navigate to dev environment
cd /opt/lightos/llm-training-ground/dev-environment

# Install dependencies
pip install -r requirements.txt

# Verify installation
lightos-dev --help
```

## Build Your First App

### Option 1: Interactive (Easiest)

```bash
lightos-dev build
```

Then type your app idea:
```
Build a todo app with create, edit, delete, and complete tasks
```

Press Enter and watch the magic happen! ✨

### Option 2: One-Liner

```bash
lightos-dev build "Build a blog with posts and comments"
```

### Option 3: From File

```bash
cat > my-app.txt << EOF
Build an analytics dashboard with:
- Real-time metrics
- Line and bar charts
- Date range filtering
- CSV export
EOF

lightos-dev build --file my-app.txt
```

## What Happens Next

```
╔═══════════════════════════════════════════════════════════╗
║  1. 🤖 GLM-4 analyzes your prompt                         ║
║  2. 📋 Creates detailed plan (pages, APIs, data models)   ║
║  3. 🏗️  Generates React frontend + FastAPI backend        ║
║  4. 📦 Installs all dependencies automatically            ║
║  5. 🔨 Builds the app with Vite                           ║
║  6. 🧪 Runs tests (if configured)                         ║
║  7. 🚀 Starts dev server with hot-reload                  ║
║  8. ✅ App is live!                                        ║
╚═══════════════════════════════════════════════════════════╝

⏱️  Total Time: 3-5 minutes
```

## Access Your App

Once built, your app is running at:

- **Frontend Preview:** http://localhost:5173
- **API Backend:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Try Examples

Run pre-built examples to see the system in action:

```bash
# List available examples
lightos-dev examples --list

# Build a todo app
lightos-dev examples todo_app

# Build an analytics dashboard
lightos-dev examples dashboard
```

## Hot-Reload Demo

1. Build an app (any app)
2. Open http://localhost:5173 in your browser
3. Edit `src/App.jsx` in your project
4. Save the file
5. **Watch the browser update instantly!** ⚡

No manual refresh needed!

## Common Commands

```bash
# Build an app
lightos-dev build "Your app idea"

# Build with custom name
lightos-dev build "CRM system" --name my-crm

# Start build server only
lightos-dev server

# List examples
lightos-dev examples --list

# Run an example
lightos-dev examples todo_app

# View templates
lightos-dev templates

# Edit configuration
lightos-dev config --edit
```

## Example Prompts

### Simple Apps (1-2 min build)
- "Todo app with add, edit, delete tasks"
- "Calculator with basic operations"
- "Weather app with city search"
- "Note-taking app with markdown support"

### Medium Apps (3-4 min build)
- "Blog with user auth, posts, comments"
- "E-commerce store with products and cart"
- "Task management like Trello with boards"
- "Social media feed with posts and likes"

### Complex Apps (5-7 min build)
- "CRM with contacts, deals, pipeline, reports"
- "Analytics dashboard with charts and export"
- "Project management with teams and tasks"
- "Marketplace with sellers, products, orders"

## Project Structure

Your generated app will look like:

```
your-app/
├── package.json              # Frontend dependencies
├── vite.config.js           # Vite config
├── tailwind.config.js       # Tailwind CSS
├── index.html               # HTML entry
├── src/                     # React app
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css
│   └── pages/
│       ├── Home.jsx
│       └── Dashboard.jsx
├── backend/                 # FastAPI
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Tips for Best Results

### ✅ DO:
- Be specific about features
- Mention key entities ("users, products, orders")
- Specify interactions ("users can like posts")
- Include auth if needed ("with user authentication")

### ❌ DON'T:
- Be too vague ("build an app")
- Use technical jargon unnecessarily
- Request impossible features
- Assume complex integrations work out of the box

### Good Prompts:
```
✅ "Build a todo app with user auth, task creation, editing,
   deletion, and marking complete. Include filtering by status."

✅ "Build an e-commerce store with product catalog, shopping cart,
   checkout, and admin panel for managing products."
```

### Bad Prompts:
```
❌ "Build an app"
❌ "Make me something cool"
❌ "Create a fully scalable microservices architecture"
```

## Troubleshooting

### Build Fails

**Check:**
1. Is GLM-4 model downloaded? (happens on first run)
2. Enough disk space? (need ~10 GB for model + node_modules)
3. Ports available? (3000, 5173, 8000)

**Fix:**
```bash
# Retry the build
lightos-dev build "Your prompt"

# Or start fresh
rm -rf dev-environment/projects/*
lightos-dev build "Your prompt"
```

### Preview Not Loading

**Wait 30 seconds** - dev server takes time to start

**Then check:**
```bash
# Is build server running?
curl http://localhost:3000/

# Check build status
curl http://localhost:3000/api/build/status

# View logs
curl http://localhost:3000/api/server/logs
```

### Out of Memory

**Use smaller model:**
Edit `config/dev_config.yaml`:
```yaml
glm4_builder:
  model_size: "9b"  # Smaller, faster
```

Or use CPU (slower but less memory):
```python
builder = GLM4AppBuilder(device="cpu")
```

## Next Steps

### 1. Edit Your App
Navigate to your project and start editing:
```bash
cd dev-environment/projects/your-app
code .  # Or use your favorite editor
```

Changes auto-reload in browser!

### 2. Add Features
Just run build again with updated prompt:
```bash
lightos-dev build "Add dark mode to my todo app"
```

GLM-4 will extend the existing app!

### 3. Deploy
Your app is production-ready. Deploy to:

**Vercel:**
```bash
cd your-app
vercel deploy
```

**Netlify:**
```bash
netlify deploy --prod
```

**Railway:**
```bash
railway up
```

## Get Help

- **Docs:** `llm-training-ground/dev-environment/README.md`
- **Examples:** `lightos-dev examples --list`
- **Config:** `lightos-dev config --edit`
- **Templates:** `llm-training-ground/dev-environment/templates/`

## What's Next?

Try building:
1. **Your actual product idea** - why not?
2. **A tool you need** - scratch your own itch
3. **A side project** - start that idea you've been thinking about
4. **A prototype** - validate before building manually

**The limit is your imagination!** 🚀

---

Ready to build? Run:
```bash
lightos-dev build
```

*Turn your ideas into reality, instantly.*
