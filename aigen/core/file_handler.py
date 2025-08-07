from pathlib import Path
import yaml
from typing import Any, Optional, List, Dict

class FileHandler:
    """Handles reading and writing of files and YAML."""
    @staticmethod
    def read_text(file_path: str) -> str:
        with open(file_path,"r") as f:
            return f.read()
    
    @staticmethod
    def wrtie_text(file_path: str, data: str) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path,"w") as f:
            return f.write(data)

    def read_yaml(file_path: str) -> Any:
        with open(file_path,"r") as f:
            return yaml.safe_load(f)

    def write_yaml(file_path: str, data: Any) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
