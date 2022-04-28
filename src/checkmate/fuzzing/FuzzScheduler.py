#  CheckMate: A Configuration Tester for Static Analysis
#
#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from multiprocessing import JoinableQueue

from src.checkmate.util.UtilClasses import FuzzingCampaign


class FuzzScheduler:

    def __init__(self, j_queue: JoinableQueue, max_capacity=100):
        self.job_queue = j_queue
        self.max_capacity = max_capacity

    def add_new_job(self, campaign: FuzzingCampaign):
        """
        Submits a new job to the scheduler
        """
        self.job_queue.put(campaign)

    def get_next_job_blocking(self) -> FuzzingCampaign:
        """
        Returns the next job to run (blocks if there is no job).
        """
        return self.job_queue.get(block=True)

    def set_job_as_done(self):
        """
        Marks that a job was done.
        """
        self.job_queue.task_done()