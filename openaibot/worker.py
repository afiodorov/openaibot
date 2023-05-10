from dataclasses import dataclass, field
from queue import PriorityQueue
from threading import Thread
from typing import Callable


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    func: Callable = field(compare=False)


class Worker:
    def __init__(self):
        self._q = PriorityQueue()

    def run(self) -> None:
        Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        while True:
            item = self._q.get()
            item.func()
            self._q.task_done()

    def push(self, priority, task) -> None:
        self._q.put(PrioritizedItem(priority=priority, func=task))
