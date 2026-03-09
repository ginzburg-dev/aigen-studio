from pathlib import Path
import yaml
from typing import Any

from aigen.models import ImageType


class FileHandler:
    """Handles reading and writing of files."""

    @staticmethod
    def read_text(file_path: str) -> str:
        with open(file_path, "r") as f:
            return f.read().rstrip("\n")

    @staticmethod
    def write_text(file_path: str, text: str) -> None:
        _file_path = Path(file_path)
        _file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(_file_path, "w") as f:
            f.write(text)

    @staticmethod
    def read_yaml(file_path: str) -> Any:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    @staticmethod
    def write_yaml(file_path: str, data: Any) -> None:
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    @staticmethod
    def search_images(image_dir_path: str) -> list[str]:
        """Find image files in a directory"""
        images = sorted(
            Path(image_dir_path).rglob("*"),
            key=lambda p: str(p),
            reverse=True,
        )
        return [
            str(img)
            for img in images
            if img.is_file() and ImageType.validate(img.suffix.lstrip(".").lower())
        ]
