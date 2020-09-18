import contextlib
import os
import pathlib

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
    import dunamai

    version_pattern = (
        r"^(?P<base>\d+\.\d+\.\d+)(-?((?P<stage>[a-zA-Z]+)\.?(?P<revision>\d+)?))?$"
    )
    version = dunamai.Version.from_git(pattern=version_pattern).serialize()

    try:
        with open(version_filename, "w") as f:
            f.write(version)
        yield version
    finally:
        os.remove(version_filename)


with ensure_version() as version:
    setuptools.setup(version=version)
