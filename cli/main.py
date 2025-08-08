# load cfg
# main loop

from aigen.core.file_handler import FileHandler
from aigen.pipeline import process_actions
from typing import Any, Optional, Union, List, Dict

def main():
    instructions = FileHandler.read_yaml("././config/example_pipeline.yaml")
    context: Dict = []
    process_actions(context, instructions)

if __name__ == "__main__":
    main()
