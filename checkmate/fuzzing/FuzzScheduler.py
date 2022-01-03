from checkmate.fuzzing.FuzzLogger import FuzzLogger
from checkmate.util import FuzzingPairJob


class FuzzScheduler:
    jobQueue = list()
    logger = FuzzLogger()

    def __init__(self, max_capacity=100):
        self.max_capacity = max_capacity

    def add_new_job(self, job: FuzzingPairJob):
        """
        Submits a new job to the scheduler
        """
        while len(self.jobQueue) >= self.max_capacity:
            pass

        self.jobQueue.append(job)

    def get_next_job_non_blocking(self) -> FuzzingPairJob:
        """
        Returns the next job to run.
        """
        if len(self.jobQueue) > 0:
            return self.jobQueue.pop(0)
        else:
            return None

    def get_next_job_blocking(self) -> FuzzingPairJob:
        """
        Returns the next job to run (blocks if there is no job).
        """
        while len(self.jobQueue) == 0:
            pass
        return self.jobQueue.pop(0)