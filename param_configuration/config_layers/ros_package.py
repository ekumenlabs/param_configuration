#  ------------------------------------------------------------------
#   Copyright 2024 Karelics Oy
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#  ------------------------------------------------------------------
import functools
import subprocess
from pathlib import Path
from typing import Dict, List, Union

# ROS
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory

# Parameter Configuration
from param_configuration.config_layer import ConfigLayer
from param_configuration.utils import walk_directory

@functools.lru_cache(maxsize=None, typed=True)
def cached_get_package_share_directory(package: str):
    return get_package_share_directory(package)

class RosParamPackageLayer(ConfigLayer):
    """Configuration layer for getting parameters from a ROS package param directory."""

    def __init__(self, subdir: List[str] = []):
        self._subdir: List[str] = subdir

    @property
    def name(self) -> str:
        return "ros"

    def load(self, path: Path) -> Union[str, Path, None]:
        """Try to load the file from the ROS package."""
        package = str(path).split("/")[2]
        config_file_path = str(path).replace(f"config://{package}/", "")
        full_subdir = Path("config").joinpath(*self._subdir)
        try:
            converted_path = Path(cached_get_package_share_directory(package)) / full_subdir / Path(config_file_path)
            if converted_path.exists():
                return converted_path
        except (PackageNotFoundError, ValueError):
            pass
        return None

    def get_files(self) -> Dict[str, Union[List[Path], str]]:
        packages = subprocess.check_output(["ros2", "pkg", "list"]).decode("utf-8").split("\n")
        res = {"__files": []}
        full_subdir = Path("config").joinpath(*self._subdir)
        for package in packages:
            try:
                package_dir = Path(cached_get_package_share_directory(package)) / full_subdir
                if package_dir.exists():
                    res[package] = walk_directory(directory=package_dir)

            except (PackageNotFoundError, ValueError):
                pass

        return res
