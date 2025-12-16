# Deploy Python Server to GitHub

## Step 1: Navigate to Python Server Directory

```cmd
cd "D:\desktop scripts\airbnb\airbnb next\python server"
```

## Step 2: Initialize Git Repository

```cmd
git init
```

## Step 3: Add All Files

```cmd
git add .
```

## Step 4: Create Initial Commit

```cmd
git commit -m "Initial commit: Python Flask API server for Airbnb price fetching"
```

## Step 5: Add Remote Repository

```cmd
git remote add origin https://github.com/ffaiz01/airbnb-backend.git
```

## Step 6: Push to GitHub

```cmd
git branch -M main
git push -u origin main
```

## Complete Command (All in One)

If you want to do it all at once:

```cmd
cd "D:\desktop scripts\airbnb\airbnb next\python server"
git init
git add .
git commit -m "Initial commit: Python Flask API server for Airbnb price fetching"
git remote add origin https://github.com/ffaiz01/airbnb-backend.git
git branch -M main
git push -u origin main
```

## If You Need to Authenticate

If GitHub asks for authentication:
- Use a Personal Access Token instead of password
- Or use GitHub Desktop
- Or use SSH keys

## Files Included

The following files will be pushed:
- `app.py` - Flask application
- `scheduler.py` - Background scheduler
- `utils.py` - Utility functions
- `requirements.txt` - Dependencies
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose config
- `.dockerignore` - Docker ignore file
- `.gitignore` - Git ignore file
- `README.md` - Documentation
- All deployment guides

## Excluded Files (via .gitignore)

- `__pycache__/` - Python cache
- `.env` - Environment variables (sensitive)
- `*.log` - Log files
- `venv/` - Virtual environment

