import os
import sys
import importlib
import subprocess
import pkg_resources
from src.tools.logging import logger

class PackageManager:

    def __init__(self) -> None:
        self.packages = [
            "discord", "beautifulsoup4", "certifi", "mutagen", "requests", "yt_dlp"
        ]

    def install_packages(self) -> None:
        for package in self.packages:
            if not importlib.util.find_spec(package):
                os.system(f"{sys.executable} -m pip install {package}")

    #this takes 2s which can be decreased considerably by using threads or asyncio but I couldnt give less of a fuck
    def _get_newest_package_version(self, package: str) -> str:
        result = subprocess.run([f'{sys.executable}', '-m', 'pip', 'index', 'versions', f"{package}"], capture_output=True, text=True, check=True)
        return result.stdout.split('(')[1].split(')')[0]
    
    def _check_if_uptodate(self, package: str) -> bool:
        return pkg_resources.get_distribution(package).version == self._get_newest_package_version(package)
    
    def update_packages(self) -> None:
        logger.info("Running auto-updater", True)
        for package in self.packages:
            if not self._check_if_uptodate(package):
                logger.info(f"Updating {package}", True)
                os.system(f"{sys.executable} -m pip install --upgrade {package}")
        logger.info("All packages are up to date", True)
    
packageManager = PackageManager()