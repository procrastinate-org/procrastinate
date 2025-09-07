# Hot-reload Development Worker

During development, manually restarting workers after code changes can slow down the development cycle. Procrastinate provides a hot-reload worker that automatically restarts when Python files change.

## Installation

The hot-reload functionality requires the `watchfiles` package:

```bash
pip install watchfiles
```

## Basic Usage

```python
import asyncio
from procrastinate.contrib.hot_reload import HotReloadWorker
from myapp import app  # Your Procrastinate app

async def main():
    # Create hot-reload worker
    hot_worker = HotReloadWorker(
        app=app,
        watch_paths=["./myapp", "./tasks"],  # Directories to watch
        queues=["default", "high-priority"]   # Queues to process
    )
    
    # Run with hot-reload enabled
    await hot_worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Docker Setup

Hot-reload works particularly well in Docker development environments. Here's how to set it up:

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies including watchfiles
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "-m", "myapp.hot_reload_worker"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  worker:
    build: .
    command: python -m myapp.hot_reload_worker
    environment:
      - WATCHFILES_FORCE_POLLING=false  # Use native file events
    volumes:
      # Mount source code for hot-reload
      - ./myapp:/app/myapp:ro
      - ./tasks:/app/tasks:ro
      - ./data:/app/data  # Persistent data (read-write)
    depends_on:
      - postgres
      
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=procrastinate
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

### Hot-reload Worker Script

Create `myapp/hot_reload_worker.py`:

```python
import asyncio
import logging
from procrastinate.contrib.hot_reload import HotReloadWorker
from .app import app  # Your Procrastinate app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    worker = HotReloadWorker(
        app=app,
        watch_paths=["./myapp", "./tasks"],
        queues=["analysis", "maintenance", "default"]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

The `HotReloadWorker` accepts several configuration options:

```python
worker = HotReloadWorker(
    app=app,
    watch_paths=["./src", "./tasks"],        # Directories to monitor
    queues=["urgent", "default"],            # Worker queues
    wait=True,                               # Wait for jobs (passed to worker)
    concurrency=4                            # Worker concurrency
)
```

### Parameters

- **`app`**: Your Procrastinate App instance
- **`watch_paths`**: List of directories to monitor for changes (default: `["./"]`)
- **`queues`**: List of queues for the worker to process (default: all queues)
- **`**worker_kwargs`**: Additional arguments passed to `run_worker_async()`

## How It Works

The hot-reload worker:

1. **File Monitoring**: Uses `watchfiles` to monitor Python files in specified directories
2. **Process Isolation**: Runs the actual worker in a subprocess for clean restarts
3. **Change Detection**: Triggers restart when `.py` files change (ignores `__pycache__`, `.pyc`, etc.)
4. **Graceful Restart**: Terminates the current worker with SIGTERM, then SIGKILL if needed
5. **Signal Handling**: Responds to SIGINT/SIGTERM for clean shutdown

## Development Workflow

1. Start the hot-reload worker:
   ```bash
   docker compose up worker
   ```

2. Edit your task code:
   ```python
   @app.task
   async def my_task(name: str):
       print(f"Hello, {name}! (updated)")  # Add/modify code
   ```

3. Save the file - the worker automatically restarts:
   ```
   📝 File changes detected: 1 files
     modified: /app/tasks/my_tasks.py
   🔄 Requesting worker restart due to file changes...
   🔄 Restarting Procrastinate worker...
   ✅ Procrastinate worker started
   ```

4. Test your changes immediately without manual restarts

## Production Considerations

⚠️ **Important**: Hot-reload is designed for development only. In production:

- Use the standard `app.run_worker()` or `procrastinate worker` CLI
- Don't mount source code volumes
- Don't install `watchfiles` in production images
- Use proper process managers like systemd or supervisor

## Troubleshooting

### File Changes Not Detected

If changes aren't detected, try:

```yaml
# docker-compose.yml
environment:
  - WATCHFILES_FORCE_POLLING=true  # Force polling mode
```

### High CPU Usage

Polling mode can use more CPU. Optimize by:

```python
# Limit watch paths to only what's needed
worker = HotReloadWorker(
    app=app,
    watch_paths=["./tasks"],  # Only watch task directory
    queues=["important"]       # Only process critical queues
)
```

### Container Permissions

If using Docker with bind mounts, ensure proper permissions:

```bash
# Set ownership to container user
chown -R 1000:1000 ./myapp
```

## Example: Complete Development Setup

Here's a complete example for a typical development setup:

**Project Structure:**
```
myproject/
├── docker-compose.yml
├── Dockerfile  
├── requirements.txt
├── myapp/
│   ├── __init__.py
│   ├── app.py
│   ├── hot_reload_worker.py
│   └── tasks/
│       ├── __init__.py
│       └── analysis.py
└── data/
```

**myapp/app.py:**
```python
import os
from procrastinate import App, PsycopgConnector

# Create app
app = App(
    connector=PsycopgConnector(
        conninfo=os.getenv("DATABASE_URL")
    )
)

# Import tasks to register them
from . import tasks
```

**myapp/tasks/analysis.py:**
```python
from ..app import app

@app.task(queue="analysis", retry=3)
async def analyze_data(dataset_id: int):
    # Your analysis logic here
    print(f"Analyzing dataset {dataset_id}")
    return {"status": "completed", "dataset_id": dataset_id}
```

**myapp/hot_reload_worker.py:**
```python
import asyncio
import logging
from procrastinate.contrib.hot_reload import HotReloadWorker
from .app import app

logging.basicConfig(level=logging.INFO)

async def main():
    worker = HotReloadWorker(
        app=app,
        watch_paths=["./myapp"],
        queues=["analysis", "default"]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**requirements.txt:**
```
procrastinate>=3.5.0
watchfiles>=0.21.0
psycopg2-binary>=2.9.0
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=procrastinate
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=devpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  worker:
    build: .
    command: python -m myapp.hot_reload_worker
    environment:
      - DATABASE_URL=postgresql://dev:devpass@postgres:5432/procrastinate
      - PYTHONPATH=/app
    volumes:
      - ./myapp:/app/myapp:ro  # Hot-reload mount
      - ./data:/app/data       # Persistent data
    depends_on:
      - postgres

volumes:
  postgres_data:
```

Start development:
```bash
# Initialize database schema
docker compose run --rm worker python -c "
import asyncio
from myapp.app import app

async def init():
    async with app.open_async():
        await app._schema_manager.apply_schema()

asyncio.run(init())
"

# Start hot-reload worker
docker compose up worker
```

Now you can edit files in `myapp/` and see the worker restart automatically! 🚀