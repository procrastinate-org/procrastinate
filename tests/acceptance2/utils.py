from __future__ import annotations

import asyncio
import pathlib
import signal


class SubprocessException(Exception):
    def __init__(self, stdout: str, stderr: str, exit_code: int | None):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        super().__init__(
            f"Subprocess failed (code {exit_code}) with "
            f"stdout: {stdout} and stderr: {stderr}"
        )


class InterruptedSubprocess(SubprocessException):
    pass


async def subprocess(
    *args: str | pathlib.Path, env: dict[str, str] | None = None
) -> tuple[str, str]:
    env = env or {}
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    task = asyncio.create_task(process.communicate())
    try:
        stdout, stderr = await asyncio.shield(task)
    except asyncio.CancelledError as exc:
        process.send_signal(signal=signal.SIGINT)
        stdout, stderr = await task
        raise InterruptedSubprocess(
            stdout=stdout.decode("utf-8"),
            stderr=stderr.decode("utf-8"),
            exit_code=process.returncode,
        ) from exc

    if process.returncode != 0:
        raise SubprocessException(
            stdout=stdout.decode("utf-8"),
            stderr=stderr.decode("utf-8"),
            exit_code=process.returncode,
        )
    return stdout.decode("utf-8"), stderr.decode("utf-8")
