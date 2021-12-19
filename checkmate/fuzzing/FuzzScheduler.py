from checkmate.util import FuzzingPairJob


class FuzzScheduler:

    jobQueue = list()

    def __init__(self, max_capacity = 1000):
        self.max_capacity = 1000

    def addNewJob(self, job: FuzzingPairJob):
        """
        Submits a new job to the scheduler
        """
        while(len(self.jobQueue) >= self.max_capacity)
            pass
        
        self.jobQueue.append(job)


    def getNextJobNonBlocking(self) -> FuzzingPairJob:
        """
        Returns the next job to run.
        """
        if len(self.jobQueue) > 0:
            return self.jobQueue.pop()
        else:
            return None

    def getNextJobBlocking(self) -> FuzzingPairJob:
        """
        Returns the next job to run (blocks if there is no job).
        """
        while (len(self.jobQueue) == 0):
            pass
        return self.jobQueue.pop()