"""Start the local Django preview, including packages from the project venv."""

import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
WINDOWS_SITE_PACKAGES = PROJECT_DIR / ".venv" / "Lib" / "site-packages"
if WINDOWS_SITE_PACKAGES.exists():
    sys.path.insert(0, str(WINDOWS_SITE_PACKAGES))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.management import execute_from_command_line


if __name__ == "__main__":
    execute_from_command_line(
        [
            "manage.py",
            "runserver",
            "127.0.0.1:8000",
            "--noreload",
            "--skip-checks",
        ]
    )
