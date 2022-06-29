from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Deque


@dataclass
class Interaction:
    request: str
    response: str


num_interactions_remembered = 5

state: DefaultDict[str, Deque[Interaction]] = defaultdict(
    lambda: deque([], num_interactions_remembered)
)
