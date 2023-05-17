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
from typing import List

from src.ecstatic.runners.WALARunner import WALARunner
from src.ecstatic.util.UtilClasses import BenchmarkRecord


class WALAJSRunner(WALARunner):
    def get_input_option(self, benchmark_record: BenchmarkRecord) -> List[str]:
        return f"--scripts {benchmark_record.name}".split(" ")

    def get_output_option(self, output_file: str) -> List[str]:
        return f"--cgoutput {output_file}".split(" ")


    def get_base_command(self) -> List[str]:
        return "java -jar /WalaJSCallgraph/target/jscallgraph-0.0.1-SNAPSHOT-jar-with-dependencies.jar".split(" ")