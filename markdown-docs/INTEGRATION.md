# Integration with markdown-builder

This documentation is designed to work with the markdown-builder at https://github.com/Lightiam/markdown-builder

## Quick Setup

### Option 1: Deploy to Lovable

```bash
# 1. Ensure this is pushed to your repo
git add markdown-docs/
git commit -m "Add LightOS documentation in markdown format"
git push

# 2. In Lovable, point markdown-builder to this directory:
# Source directory: markdown-docs/
# Config file: markdown-docs/mkdocs.yml

# 3. Deploy!
```

### Option 2: Local Build

```bash
# Install markdown-builder dependencies
npm install -g markdown-builder
# or
pip install mkdocs mkdocs-material

# Build documentation
cd markdown-docs/
mkdocs build

# Serve locally
mkdocs serve
# Visit http://localhost:8000
```

### Option 3: Integrate with Main Site

```bash
# Copy to your main site
cp -r markdown-docs/* /path/to/your/site/docs/

# Or use as submodule
git submodule add https://github.com/Lightiam/LightOS docs/lightos
```

## Directory Structure

```
markdown-docs/
├── README.md                  # Home page
├── mkdocs.yml                 # markdown-builder config
├── getting-started/           # Installation & quickstart
├── guides/                    # User guides
├── api/                       # API reference
├── examples/                  # Code examples
└── INTEGRATION.md            # This file
```

## Configuration

The `mkdocs.yml` file configures:
- Site metadata (title, description, URL)
- Theme (Material Design)
- Navigation structure
- Markdown extensions
- Social links

### Customization

Edit `mkdocs.yml` to match your site:

```yaml
# Update these
site_name: Your Site Name
site_url: https://lighrail.ink/docs
repo_url: https://github.com/Lightiam/LightOS

# Theme colors
theme:
  palette:
    primary: your-color
    accent: your-accent

# Add your analytics
google_analytics:
  - UA-XXXXXXXX-X
  - auto
```

## markdown-builder Features

This documentation uses:
- ✅ Material Design theme
- ✅ Syntax highlighting
- ✅ Code copy buttons
- ✅ Search functionality
- ✅ Mobile responsive
- ✅ Dark/light mode
- ✅ Navigation tabs
- ✅ Table of contents

## Deployment Options

### Lovable Integration

```yaml
# In your Lovable config
documentation:
  source: markdown-docs/
  builder: mkdocs
  output: public/docs
```

### Netlify

```toml
# netlify.toml
[build]
  command = "cd markdown-docs && mkdocs build"
  publish = "markdown-docs/site"
```

### GitHub Pages

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Docs
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install mkdocs-material
      - run: cd markdown-docs && mkdocs gh-deploy --force
```

## Content Updates

### Adding New Pages

1. Create markdown file in appropriate directory
2. Add to navigation in `mkdocs.yml`
3. Commit and push

Example:
```bash
# Create new guide
echo "# My Guide" > markdown-docs/guides/my-guide.md

# Add to mkdocs.yml under nav:
#   - Guides:
#       - My Guide: guides/my-guide.md

git add markdown-docs/
git commit -m "Add new guide"
git push
```

### Updating Existing Pages

Simply edit the markdown files and push:
```bash
vim markdown-docs/getting-started/installation.md
git add markdown-docs/
git commit -m "Update installation guide"
git push
```

## Support

- **markdown-builder**: https://github.com/Lightiam/markdown-builder
- **MkDocs**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/

## Next Steps

1. Review and customize `mkdocs.yml`
2. Add remaining guide pages
3. Deploy to Lovable or your preferred platform
4. Link from main site (https://lighrail.ink)
