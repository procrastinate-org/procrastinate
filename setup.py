import contextlib
import os
import pathlib
import subprocess

import setuptools


@contextlib.contextmanager
def ensure_version():
    version_filename = pathlib.Path(__file__).parent / "VERSION.txt"

    # If installing from a sdist
    try:
        with open(version_filename) as f:
            yield f.read().strip()
        return
    except IOError:
        pass

    # If running from the git repository
    try:
        version = (
            subprocess.check_output(["git", "describe", "--tags"])
            .decode("utf-8")
            .strip()
            .replace("-", "+", 1)
            .replace("-", ".")
        )
    except subprocess.CalledProcessError:
        # This might happen in some rare cases, like when running check-manifest.
        # We'll update this to something better if it ever proves problematic.
        yield "0.0.0"
        return

    try:
        with open(version_filename, "w") as f:
            f.write(version)
        yield version
    finally:
        os.remove(version_filename)


with ensure_version() as version:
    setuptools.setup(version=version)
