import os
import glob
from pathlib import Path
import yaml
from typing import Any, Optional, List, Dict, Union

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

class FileHandler:
    """Handles reading and writing of files and YAML."""
    @staticmethod
    def read_text(file_path: str) -> str:
        result: str = ""
        with open(file_path,"r") as f:
            return f.read().rstrip('\n') # Removes trailing \n (newline).
    
    @staticmethod
    def wrtie_text(file_path: str, data: str) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path,"w") as f:
            return f.write(data)
        
    @staticmethod
    def read_yaml(file_path: str) -> Any:
        with open(file_path,"r") as f:
            return yaml.safe_load(f)
        
    @staticmethod
    def write_yaml(file_path: str, data: Any) -> None:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    @staticmethod
    def expand_images(image_path: str) -> List[str]:
        """Find files using path with /*"""
        files = []
        if isinstance(image_path, str):
            if "*" in image_path:
                return sorted(glob.glob(image_path))
        elif isinstance(image_path, list):
            files = []
            for item in image_path:
                files.extend(FileHandler.expand_images(item))
        else:
            files = []
        return [f for f in files if FileHandler.is_supported_image(f)]
    
    @staticmethod
    def is_supported_image(image_path: str) -> bool:
        ext = os.path.splitext(image_path)[1].lower()
        return ext in SUPPORTED_IMAGE_EXTENSIONS
    
    @staticmethod
    def replace_var(data, ):
        var_name = match.group(1)  # e.g. "name" or "project"
        return params.get(var_name, match.group(0))
