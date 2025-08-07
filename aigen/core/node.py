from abc import ABC, abstractmethod
from typing import Any, Optional, Union, List, Dict

class Node(ABC):
    def __init__(self, name: str, params: Dict) -> None:
        self.name = name
        self.params = params

    @abstractmethod
    def run(self, context):
        ...
