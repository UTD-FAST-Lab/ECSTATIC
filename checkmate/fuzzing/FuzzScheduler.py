from multiprocessing import JoinableQueue

from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.util import FuzzingPairJob


class FuzzScheduler:
    logger = FuzzLogger()

    def __init__(self, j_queue: JoinableQueue, max_capacity=100):
        self.job_queue = j_queue
        self.max_capacity = max_capacity

    def add_new_job(self, job: FuzzingPairJob):
        """
        Submits a new job to the scheduler
        """
        self.job_queue.put(job)

    def get_next_job_blocking(self) -> FuzzingPairJob:
        """
        Returns the next job to run (blocks if there is no job).
        """
        return self.job_queue.get(block=True)

    def set_job_as_done(self):
        """
        Marks that a job was done.
        """
        self.job_queue.task_done()