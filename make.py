import shutil
import sys

from denverapi.autopyb import *

auto = BuildTasks()


@auto.task()
def clean(args):
    """Clean up"""
    run_command([sys.executable, "setup.py", "clean"])
    try:
        shutil.rmtree("dist")
    except:
        pass
    try:
        shutil.rmtree("build")
    except:
        pass
    try:
        shutil.rmtree("PiOS.egg-info")
    except:
        pass


@auto.task(clean)
def sdist(args):
    """Build Source Distribution"""
    run_command([sys.executable, "setup.py", "sdist"])


@auto.task(clean)
def wheel(args):
    """Build wheel package"""
    ensure_pip_package("wheel")
    run_command([sys.executable, "setup.py", "bdist_wheel"])


@auto.task(wheel, sdist)
def publish(args):
    """publish packages to PyPI"""
    ensure_pip_package("twine")
    run_command([sys.executable, "-m", "twine", "upload", "dist/*"])


@auto.task()
def precommit(args):
    """pre-commit run to make required changes"""
    ensure_pip_package("pre-commit")
    run_command(["pre-commit", "run", "-a"])


auto.interact()
