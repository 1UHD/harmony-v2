import os
import sys
import shutil
import requests
import importlib
import subprocess
import pkg_resources
from src.tools.logging import logger, Colors

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

class ProjectUpdater:

    def __init__(self) -> None:
        self.author = "1UHD"
        self.repo = "harmony-v2"

        self.latest_update = f"https://api.github.com/repos/{self.author}/{self.repo}/releases/latest"
        self.latest_version = self._get_latest_version()

        self.project_path = __file__.replace("src/tools/PackageManager.py", "")

    def _get_current_version(self) -> str:
        from src.settings import VERSION
        return VERSION
    
    def _get_latest_version(self) -> str:
        response = requests.get(self.latest_update)
        if response.status_code == 200:
            return response.json()["tag_name"]
        else:
            logger.error("Failed to fetch latest release.")
            return None
        
    def _download_latest_release(self) -> None:
        if self.latest_version is None:
            return
        
        download_url = f"https://github.com/{self.author}/{self.repo}/archive/refs/tags/{self.latest_version}.zip"
        zip_path = os.path.join(self.project_path, "latest.zip")

        logger.info("Downloading latest release", True)
        with requests.get(download_url, stream=True) as r:
            with open("latest.zip", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        shutil.unpack_archive(zip_path, "latest_release")

        extracted_folder = os.path.join(self.project_path, f"{self.repo}-{self.latest_version}")
        for item in os.listdir(extracted_folder):
            shutil.move(os.path.join(extracted_folder, item), self.project_path)

        os.remove(zip_path)
        shutil.rmtree(extracted_folder)

    def check_for_update(self) -> None:
        if self.latest_version is None:
            return

        if self._get_current_version() > self.latest_version:
            logger.info(f"{Colors.CYAN}A new release of Harmony is available:{Colors.END} {Colors.BOLD}{self.latest_version}{Colors.END}! Run {Colors.BOLD}python launch.py --update{Colors.END} to update!", True)

    def update_project(self) -> None:
        if self.latest_version is None:
            return
        
        if self._get_current_version() > self.latest_version:
            logger.info("Updating Harmony...", True)
            self._download_latest_release()
            logger.info("Update complete! You can now restart the bot.", True)

        else:
            logger.info("No updates available.", True)

projectUpdater = ProjectUpdater()