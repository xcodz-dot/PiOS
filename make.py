import shutil

from denverapi.autopyb import *

auto = BuildTasks()


@auto.task()
def clean():
    """Clean up"""
    terminal.run_command([sys.executable, "setup.py", "clean"])
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
def sdist():
    """Build Source Distribution"""
    terminal.run_command([sys.executable, "setup.py", "sdist"])


@auto.task(clean)
def wheel():
    """Build wheel package"""
    pip.ensure_pip_package("wheel")
    terminal.run_command([sys.executable, "setup.py", "bdist_wheel"])


@auto.task(wheel, sdist)
def publish():
    """publish packages to PyPI"""
    pip.ensure_pip_package("twine")
    terminal.run_command([sys.executable, "-m", "twine", "upload", "dist/*"])


@auto.task()
def precommit():
    """pre-commit run to make required changes"""
    pip.ensure_pip_package("pre-commit")
    terminal.run_command(["pre-commit", "run", "-a"])


auto.interact()
