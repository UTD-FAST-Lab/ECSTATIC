import os
from abc import ABC
from typing import List
import tempfile
import dill as pickle
import logging

from src.ecstatic.debugging.JavaBenchmarkDeltaDebugger import JavaBenchmarkDeltaDebugger
from src.ecstatic.debugging.AbstractDeltaDebugger import DeltaDebuggingJob

logger = logging.getLogger(__name__)

class JSBenchmarkDeltaDebugger(JavaBenchmarkDeltaDebugger, ABC):

    def get_delta_debugger_cmd(self, build_script, directory, potential_violation, script_location):
        # Then, run the delta debugger
        cmd: List[str] = "jsdelta ".split(' ')
        cmd.extend(["--cmd", script_location])
        cmd.extend(["--out", directory + "/os.js"])
        cmd.extend(["--msg", "NonError: Ran Successfully"])
        cmd.extend([potential_violation.job1.job.target.name])
        
        '''sources = [['--sources', s] for s in potential_violation.job1.job.target.sources]
        [cmd.extend(s) for s in sources]
        cmd.extend(["--target", potential_violation.job1.job.target.name])
        cmd.extend(["--bs", os.path.abspath(build_script)])
        cmd.extend(["--vs", os.path.abspath(script_location)])
        cmd.extend(["--logs", os.path.join(directory, "log.txt")])
        cmd.extend(['--hdd'])
        cmd.extend(['--class-reduction'])
        cmd.extend(['--timeout', '120'])'''
        return cmd

    def create_script(self, job: DeltaDebuggingJob, directory: str) -> str:
        """
        :param job: The delta debugging job.
        :param directory: Where to put the script.
        :return: The location of the script.
        """
        job_tmp = tempfile.NamedTemporaryFile(delete=False, dir=directory)
        pickle.dump(job, open(job_tmp.name, 'wb'))
        job_tmp.close()

        with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as f:
            f.write("#!/bin/bash\n")
            cmd = f"deltadebugger {job_tmp.name}"
            f.write(cmd + "\n")
            f.write("error_status = $?\n")
            f.write('if [error_status == 0]; then echo "NonError: Ran Successfully"; fi\n')
            result = f.name
            logger.info(f"Wrote cmd {cmd} to delta debugging script.")
        return result