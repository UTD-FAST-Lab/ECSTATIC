#  ECSTATIC: Extensible, Customizable STatic Analysis Tester Informed by Configuration
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

from abc import ABC

from src.ecstatic.debugging.AbstractDeltaDebugger import AbstractDeltaDebugger


class JavaDeltaDebugger(AbstractDeltaDebugger, ABC):
    def get_delta_debugger_cmd(self, build_script, directory, potential_violation, script_location):
        # Then, run the delta debugger
        cmd: List[str] = "java -jar /SADeltaDebugger/ViolationDeltaDebugger/target/ViolationDeltaDebugger-1.0" \
                         "-SNAPSHOT-jar-with-dependencies.jar".split(' ')
        sources = [['--sources', s] for s in potential_violation.job1.job.target.sources]
        [cmd.extend(s) for s in sources]
        cmd.extend(["--target", potential_violation.job1.job.target.name])
        cmd.extend(["--bs", os.path.abspath(build_script)])
        cmd.extend(["--vs", os.path.abspath(script_location)])
        cmd.extend(["--logs", os.path.join(directory, "log.txt")])
        cmd.extend(['--hdd'])
        cmd.extend(['--class-reduction'])
        cmd.extend(['--timeout', '120'])
        return cmd
