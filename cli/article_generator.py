import argparse

from aigen.pipeline import process_actions
from aigen.core.file_handler import FileHandler
from typing import Dict

def build_parser():
    parser = argparse.ArgumentParser(description='Generate an article based on a given instruction.')
    parser.add_argument('instructions', type=str, help='The instruction.')
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    instructions = args.instruction
    print(f"Received instruction: {instructions}")

    _instructions = FileHandler.read_yaml(instructions)
    context: Dict = {}
    process_actions(context, _instructions)
