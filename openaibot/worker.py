from dataclasses import dataclass, field
from logging import Logger
from queue import PriorityQueue
from threading import Thread
from typing import Callable


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    func: Callable = field(compare=False)


class Worker:
    def __init__(self, logger: Logger):
        self.logger = logger
        self._q: PriorityQueue = PriorityQueue()

    def run(self) -> None:
        Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        while True:
            item = self._q.get()
            try:
                item.func()
            except Exception:
                self.logger.exception("Exception occurred")
            finally:
                self._q.task_done()

    def push(self, priority, task) -> None:
        self._q.put(PrioritizedItem(priority=priority, func=task))
