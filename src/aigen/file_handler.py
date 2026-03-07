import os
import glob
from pathlib import Path
from re import match
import yaml
from typing import Any, Optional, List, Dict, Union

from aigen.models import ImageType
from aigen.image_encoder import ImageEncoder

class FileHandler:
    """Handles reading and writing of files."""

    @staticmethod
    def read_text(file_path: Path) -> str:
        with open(file_path,"r") as f:
            return f.read().rstrip('\n')

    @staticmethod
    def write_text(file_path: Path, text: str) -> None:
        _file_path = Path(file_path)
        _file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(_file_path,"w") as f:
            f.write(text)

    @staticmethod
    def read_yaml(file_path: Path) -> Any:
        with open(file_path,"r") as f:
            return yaml.safe_load(f)

    @staticmethod
    def write_yaml(file_path: Path, data: Any) -> None:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    @staticmethod
    def search_images(image_path: Path) -> List[Path]:
        """Find image files in a directory"""
        images = sorted(image_path.glob("*"))
        return [img for img in images if ImageType.validate(img.suffix)]
