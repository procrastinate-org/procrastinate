"""
Auto-reload functionality for Procrastinate CLI worker command.

This module provides file watching and worker restarting capabilities
similar to uvicorn's --reload functionality, using watchfiles with inotify
for efficient file system monitoring.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

try:
    from watchfiles import awatch  # type: ignore[import-untyped]

    HAS_WATCHFILES = True
except ImportError:
    HAS_WATCHFILES = False
    awatch = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class ChangeReloader:
    """
    Auto-reload supervisor for Procrastinate worker CLI.

    Monitors file changes and restarts worker processes,
    similar to uvicorn's reload functionality.
    """

    def __init__(
        self,
        target_cmd: list[str],
        *,
        reload_dirs: list[str] | None = None,
        reload_includes: list[str] | None = None,
        reload_excludes: list[str] | None = None,
        reload_delay: float = 0.25,
    ) -> None:
        """
        Initialize the change reloader.

        Args:
            target_cmd: Command and arguments to run as subprocess
            reload_dirs: Directories to watch (default: current directory)
            reload_includes: Glob patterns to include (default: ['*.py'])
            reload_excludes: Glob patterns to exclude
            reload_delay: Delay between file change and restart
        """
        if not HAS_WATCHFILES:
            raise RuntimeError(
                "watchfiles is required for --reload functionality. "
                "Install with: pip install 'procrastinate[reload]'"
            )

        self.target_cmd = target_cmd
        self.reload_dirs = reload_dirs or [os.getcwd()]
        self.reload_includes = reload_includes or ["*.py"]
        self.reload_excludes = reload_excludes or []
        self.reload_delay = reload_delay

        self.should_exit = asyncio.Event()
        self.process: asyncio.subprocess.Process | None = None

    def startup_message(self) -> None:
        """Print startup information about file watching."""
        dirs = ", ".join(self.reload_dirs)
        includes = (
            ", ".join(self.reload_includes) if self.reload_includes else "all files"
        )

        logger.info("🔄 Started reloader process using watchfiles")
        logger.info(f"👁️  Watching for file changes in: {dirs}")
        logger.info(f"📄 Including patterns: {includes}")

        if self.reload_excludes:
            excludes = ", ".join(self.reload_excludes)
            logger.info(f"🚫 Excluding patterns: {excludes}")

    def should_reload(self, path: str) -> bool:
        """
        Check if a file change should trigger a reload.

        Args:
            path: Path to the changed file

        Returns:
            True if the change should trigger a reload
        """
        from fnmatch import fnmatch

        path_obj = Path(path)

        # Check excludes first (more restrictive)
        for exclude_pattern in self.reload_excludes:
            if fnmatch(str(path_obj), exclude_pattern):
                return False

        # Check includes
        for include_pattern in self.reload_includes:
            if fnmatch(str(path_obj), include_pattern):
                return True

        # Default: don't reload if no patterns matched
        return False

    async def start_process(self) -> None:
        """Start the target process."""
        logger.info(f"🚀 Starting process: {' '.join(self.target_cmd)}")

        self.process = await asyncio.create_subprocess_exec(
            *self.target_cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin,
        )

        logger.info(f"✅ Process started with PID {self.process.pid}")

    async def restart_process(self) -> None:
        """Restart the target process."""
        if self.process:
            logger.info("🔄 Stopping current process...")

            # Try graceful shutdown first
            self.process.terminate()

            try:
                await asyncio.wait_for(self.process.wait(), timeout=10.0)
                logger.info("✅ Process stopped gracefully")
            except asyncio.TimeoutError:
                logger.warning("⚠️  Process didn't stop gracefully, killing...")
                self.process.kill()
                await self.process.wait()
                logger.info("💀 Process killed")

        # Start new process
        await self.start_process()

    async def watch_files(self) -> None:
        """Watch for file changes and trigger restarts."""
        if awatch is None:
            raise RuntimeError("watchfiles not available")

        # Convert string paths to Path objects for validation
        watch_paths = [
            str(Path(d).resolve()) for d in self.reload_dirs if Path(d).exists()
        ]

        if not watch_paths:
            logger.warning("⚠️  No valid watch directories found")
            return

        logger.info(f"👁️  Watching for changes in: {watch_paths}")

        try:
            async for changes in awatch(*watch_paths):
                if self.should_exit.is_set():
                    break

                # Filter changes based on patterns
                relevant_changes = [
                    (change_type, path)
                    for change_type, path in changes
                    if self.should_reload(path)
                ]

                if not relevant_changes:
                    continue

                logger.info(
                    f"📝 Detected {len(relevant_changes)} relevant file changes:"
                )
                for change_type, path in relevant_changes:
                    logger.info(f"  {change_type.name}: {path}")

                # Debounce rapid changes
                if self.reload_delay > 0:
                    logger.info(f"⏳ Waiting {self.reload_delay}s before restart...")
                    await asyncio.sleep(self.reload_delay)

                # Check if we should still exit (in case signal came during delay)
                if not self.should_exit.is_set():
                    await self.restart_process()

        except Exception as e:
            logger.error(f"❌ Error watching files: {e}")

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int) -> None:
            logger.info(f"📡 Received signal {signum}, shutting down...")
            self.should_exit.set()

        # Handle common termination signals
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))

        # Handle additional signals on Unix
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, lambda s, f: signal_handler(s))

    async def run(self) -> int:
        """
        Main run loop for the reloader.

        Returns:
            Exit code from the target process
        """
        self.setup_signal_handlers()
        self.startup_message()

        try:
            # Start initial process
            await self.start_process()

            # Start file watching
            watch_task = asyncio.create_task(self.watch_files())

            # Wait for either process completion or shutdown signal
            if self.process:
                process_task = asyncio.create_task(self.process.wait())

                done, pending = await asyncio.wait(
                    [process_task, asyncio.create_task(self.should_exit.wait())],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Get exit code if process completed
                if process_task in done:
                    exit_code = process_task.result()
                    logger.info(f"🛑 Process exited with code {exit_code}")
                else:
                    exit_code = 0  # Shutdown signal received
            else:
                exit_code = 1  # Process failed to start

            # Cancel file watcher
            watch_task.cancel()
            try:
                await watch_task
            except asyncio.CancelledError:
                pass

            # Cleanup process if still running
            if self.process and self.process.returncode is None:
                logger.info("🧹 Cleaning up process...")
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    self.process.kill()
                    await self.process.wait()

            return exit_code

        except KeyboardInterrupt:
            logger.info("⌨️  Keyboard interrupt received")
            return 0
        except Exception as e:
            logger.error(f"💥 Unexpected error in reloader: {e}")
            return 1


def run_with_reload(
    target_cmd: list[str],
    **reload_config: Any,
) -> int:
    """
    Run a command with auto-reload functionality.

    Args:
        target_cmd: Command and arguments to execute
        **reload_config: Configuration for reload behavior

    Returns:
        Exit code from the target process
    """
    reloader = ChangeReloader(target_cmd, **reload_config)

    try:
        return asyncio.run(reloader.run())
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        logger.error(f"💥 Failed to run with reload: {e}")
        return 1
