#!/usr/bin/env python3

import sys
import os
import logging
from subprocess import Popen, PIPE
from pathlib import Path

logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(name)s: %(message)s', level=logging.INFO)

MIN_PYTHON_VERSION = (3,7,0)

if sys.version_info < MIN_PYTHON_VERSION:
  logging.getLogger(__name__).error("FHEM_PythonBinding requires Python " + MIN_PYTHON_VERSION[0] + "." + MIN_PYTHON_VERSION[1] + "." + MIN_PYTHON_VERSION[2])
  logging.getLogger(__name__).error("You are running: " + sys.version)
  sys.exit(1)

def is_virtual_env() -> bool:
    """Return if we run in a virtual environment."""
    # Check supports venv && virtualenv
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix or hasattr(
        sys, "real_prefix"
    )


def is_docker_env() -> bool:
    """Return True if we run in a docker env."""
    return Path("/.dockerenv").exists()

def pip_kwargs(config_dir):
    """Return keyword arguments for PIP install."""
    is_docker = is_docker_env()
    kwargs = {
        #"constraints": os.path.join(os.path.dirname(__file__), CONSTRAINT_FILE),
        "no_cache_dir": is_docker,
    }
    if "WHEELS_LINKS" in os.environ:
        kwargs["find_links"] = os.environ["WHEELS_LINKS"]
    if not (config_dir is None or is_virtual_env()) and not is_docker:
        kwargs["target"] = os.path.join(config_dir, "deps")
    return kwargs

def install_package(
    package: str,
    upgrade: bool = True,
    target: [str] = None,
    constraints: [str] = None,
    find_links: [str] = None,
    no_cache_dir: [bool] = False,
) -> bool:
    """Install a package on PyPi. Accepts pip compatible package strings.
    Return boolean if install successful.
    """
    # Not using 'import pip; pip.main([])' because it breaks the logger
    logging.getLogger(__name__).info("Attempting install of %s", package)
    env = os.environ.copy()
    args = [sys.executable, "-m", "pip", "install", "--quiet", package]
    if no_cache_dir:
        args.append("--no-cache-dir")
    if upgrade:
        args.append("--upgrade")
    if constraints is not None:
        args += ["--constraint", constraints]
    if find_links is not None:
        args += ["--find-links", find_links, "--prefer-binary"]
    process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    _, stderr = process.communicate()
    if process.returncode != 0:
        logging.getLogger(__name__).error(
            "Unable to install package %s: %s",
            package,
            stderr.decode("utf-8").lstrip().strip(),
        )
        return False
    else:
      logging.getLogger(__name__).info(f"Successfully installed {package}")

    return True

kwargs = pip_kwargs(None)

try:
  import asyncio
except:
  if install_package("asyncio", **kwargs) == False:
    sys.exit(1)

try:
  import websockets
except:
  if install_package("websockets", **kwargs) == False:
    sys.exit(1)

try:
  if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import (  # pylint: disable=no-name-in-module,import-error
        PackageNotFoundError,
        version,
    )
  else:
      from importlib_metadata import (  # pylint: disable=import-error
          PackageNotFoundError,
          version,
      )
except:
  if install_package("importlib_metadata", **kwargs) == False:
    sys.exit(1)

try:
  import cryptography
except:
  if install_package("cryptography", **kwargs) == False:
    sys.exit(1)


import lib.fhem_pythonbinding as fpb

fpb.run()