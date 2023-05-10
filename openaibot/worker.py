import heapq
from threading import Condition, Thread


class Task:
    def __init__(self, priority, func):
        self.priority = priority
        self.func = func

    def __lt__(self, other):
        return self.priority < other.priority

    def __call__(self):
        return self.func()


class Worker:
    def __init__(self):
        self._task_queue: [Task] = []
        self._queue_condition: Condition = Condition()

    def run(self) -> Thread:
        worker_thread = Thread(target=self._run)
        worker_thread.start()

        return worker_thread

    def _run(self):
        while True:
            with self._queue_condition:
                while not self._task_queue:
                    self._queue_condition.wait()
                task = heapq.heappop(self._task_queue)
            if task is None:
                break
            task()

    def push(self, priority, task) -> None:
        heapq.heappush(self._task_queue, Task(priority, task))
        with self._queue_condition:
            self._queue_condition.notify()
