import subprocess

import setuptools


def get_version():
    try:
        return (
            subprocess.check_output(["git", "describe"])
            .decode("utf-8")
            .strip()
            .replace("-", "+", 1)
            .replace("-", ".")
        )
    except subprocess.CalledProcessError:
        return "0.0.0"


setuptools.setup(version=get_version())
