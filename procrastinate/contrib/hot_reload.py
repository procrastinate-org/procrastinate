"""
Hot-reloadable Procrastinate Worker for Development

This contrib module provides hot-reload functionality for Procrastinate workers
during development, automatically restarting when Python files change.

Usage:
    from procrastinate.contrib.hot_reload import HotReloadWorker

    # Create hot-reload worker
    worker = HotReloadWorker(
        app=your_procrastinate_app,
        watch_paths=["./app", "./tasks"],
        queues=["default", "high-priority"]
    )

    # Run with hot-reload
    await worker.run()

Docker Example:
    # docker-compose.yml
    services:
      worker:
        build: .
        command: python -m your_app.hot_reload_worker
        volumes:
          - ./app:/app/app:ro  # Mount for hot-reload
        environment:
          - WATCHFILES_FORCE_POLLING=false
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

try:
    from watchfiles import awatch  # type: ignore[import-untyped]

    HAS_WATCHFILES = True
except ImportError:
    HAS_WATCHFILES = False
    awatch = None  # type: ignore[assignment]

from .. import App

logger = logging.getLogger(__name__)


class HotReloadWorker:
    """
    Hot-reloadable Procrastinate worker for development.

    Automatically restarts the worker process when Python files change,
    enabling rapid development and testing of background tasks.

    Warning:
        This is intended for development use only. Do not use in production.
    """

    def __init__(
        self,
        app: App,
        *,
        watch_paths: Sequence[str | Path] | None = None,
        queues: Sequence[str] | None = None,
        **worker_kwargs: Any,
    ) -> None:
        """
        Initialize hot-reload worker.

        Args:
            app: Procrastinate App instance
            watch_paths: Directories to watch for changes (default: ["./"])
            queues: Queues for worker to process (default: all queues)
            **worker_kwargs: Additional kwargs for run_worker_async()

        Raises:
            ImportError: If watchfiles is not installed
        """
        if not HAS_WATCHFILES:
            raise ImportError(
                "watchfiles is required for hot-reload functionality. "
                "Install with: pip install watchfiles"
            )

        self.app = app
        self.watch_paths = [Path(p) for p in (watch_paths or ["./"])]
        self.queues = queues
        self.worker_kwargs = worker_kwargs

        self.worker_process: asyncio.subprocess.Process | None = None
        self.shutdown_event = asyncio.Event()
        self.restart_requested = asyncio.Event()

    async def start_worker(self) -> None:
        """Start the Procrastinate worker process."""
        try:
            logger.info("🔄 Starting Procrastinate worker...")

            # Create worker subprocess for isolation
            cmd = [sys.executable, "-c", self._get_worker_script()]

            self.worker_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={"PYTHONPATH": ":".join(sys.path)},
            )

            logger.info("✅ Procrastinate worker started")

            # Monitor worker output
            output_task = asyncio.create_task(self._stream_worker_output())
            restart_task = asyncio.create_task(self.restart_requested.wait())

            # Wait for completion or restart
            done, pending = await asyncio.wait(
                [output_task, restart_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            if restart_task in done:
                logger.info("🔄 Restart requested")
            elif self.worker_process and self.worker_process.returncode is not None:
                logger.info(
                    f"🛑 Worker process exited with code {self.worker_process.returncode}"
                )

        except Exception as e:
            logger.error(f"❌ Error in worker process: {e}")
        finally:
            await self._terminate_worker()

    def _get_worker_script(self) -> str:
        """Generate Python script to run the worker."""
        # Import the app module path
        app_module = self.app.__module__
        app_attr = getattr(self.app, "_name", "app")

        # Handle cases where app might be imported differently
        if hasattr(self.app, "__qualname__"):
            app_attr = self.app.__qualname__

        script = f"""
import asyncio
import sys
import importlib

# Import the app
try:
    module = importlib.import_module('{app_module}')
    app = getattr(module, '{app_attr}')
except (ImportError, AttributeError) as e:
    print(f"Failed to import app: {{e}}", file=sys.stderr)
    sys.exit(1)

async def main():
    try:
        async with app.open_async():
            await app.run_worker_async(
                queues={self.queues!r},
                **{self.worker_kwargs!r}
            )
    except Exception as e:
        print(f"Worker error: {{e}}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
"""
        return script

    async def _stream_worker_output(self) -> None:
        """Stream worker process output to logger."""
        if not self.worker_process or not self.worker_process.stdout:
            return

        try:
            async for line in self.worker_process.stdout:
                logger.info(f"Worker: {line.decode().rstrip()}")
        except Exception as e:
            logger.warning(f"Error streaming worker output: {e}")

    async def _terminate_worker(self) -> None:
        """Terminate the worker process gracefully."""
        if self.worker_process and self.worker_process.returncode is None:
            logger.info("🔄 Terminating worker process...")
            self.worker_process.terminate()
            try:
                await asyncio.wait_for(self.worker_process.wait(), timeout=10)
            except asyncio.TimeoutError:
                logger.warning("⚠️  Worker didn't terminate, killing...")
                self.worker_process.kill()
                if self.worker_process:
                    await self.worker_process.wait()

    async def watch_files(self) -> None:
        """Watch for file changes and trigger restarts."""
        # Filter to existing paths
        existing_paths = [str(p) for p in self.watch_paths if p.exists()]

        if not existing_paths:
            logger.warning("⚠️  No watch paths found, file watching disabled")
            return

        logger.info(f"👁️  Watching for changes in: {existing_paths}")

        try:
            # mypy: awatch is conditionally imported but guaranteed available here
            async for changes in awatch(
                *existing_paths, watch_filter=self._should_reload
            ):
                if self.shutdown_event.is_set():
                    break

                logger.info(f"📝 File changes detected: {len(changes)} files")
                for change_type, path in changes:
                    logger.info(f"  {change_type.name}: {path}")

                # Request restart
                logger.info("🔄 Requesting worker restart due to file changes...")
                self.restart_requested.set()

                # Debounce rapid changes
                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"❌ Error in file watcher: {e}")

    def _should_reload(self, change_type: Any, path: str) -> bool:
        """Determine if a file change should trigger reload."""
        path_obj = Path(path)

        # Only watch Python files
        if path_obj.suffix != ".py":
            return False

        # Skip cache and temp files
        if (
            "__pycache__" in path
            or path.endswith(".pyc")
            or path_obj.name.startswith(".")
        ):
            return False

        return True

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, frame: Any) -> None:
            logger.info(f"📡 Received signal {signum}, initiating shutdown...")
            # Store task to satisfy linter, but we don't need to track it
            _ = asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def shutdown(self) -> None:
        """Gracefully shutdown the hot-reload worker."""
        logger.info("🔄 Shutting down hot-reload worker...")
        self.shutdown_event.set()
        self.restart_requested.set()
        await self._terminate_worker()
        logger.info("✅ Hot-reload worker shutdown complete")

    async def run(self) -> None:
        """Main run loop with hot-reloading."""
        logger.info("🌟 Starting Hot-Reload Procrastinate Worker...")

        try:
            self._setup_signal_handlers()

            # Start file watcher
            file_watcher_task = asyncio.create_task(self.watch_files())

            # Main worker loop
            while not self.shutdown_event.is_set():
                try:
                    # Clear restart flag
                    self.restart_requested.clear()

                    # Start worker
                    await self.start_worker()

                    # Check why we exited
                    if (
                        not self.restart_requested.is_set()
                        and not self.shutdown_event.is_set()
                    ):
                        logger.info(
                            "⏸️  Worker exited, waiting 5 seconds before restart..."
                        )
                        await asyncio.sleep(5)

                except Exception as e:
                    logger.error(f"💥 Error in worker loop: {e}")
                    if not self.shutdown_event.is_set():
                        logger.info("⏸️  Waiting 5 seconds before retry...")
                        await asyncio.sleep(5)

            # Cancel file watcher
            file_watcher_task.cancel()
            try:
                await file_watcher_task
            except asyncio.CancelledError:
                pass

        except KeyboardInterrupt:
            logger.info("⌨️  Keyboard interrupt received")
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            raise
        finally:
            await self.shutdown()


def create_hot_reload_worker(app: App, **kwargs: Any) -> HotReloadWorker:
    """
    Create a hot-reload worker with sensible defaults.

    Args:
        app: Procrastinate App instance
        **kwargs: Additional arguments for HotReloadWorker

    Returns:
        Configured HotReloadWorker instance
    """
    return HotReloadWorker(app=app, **kwargs)
