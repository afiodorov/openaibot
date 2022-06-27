from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class Interaction:
    request: str
    response: str


num_interactions_remembered = 5

state = defaultdict(lambda: deque([], num_interactions_remembered))
