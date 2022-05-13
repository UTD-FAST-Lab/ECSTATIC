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

import logging
import os

from src.ecstatic.util.ApplicationCodeFilter import ApplicationCodeFilter
from src.ecstatic.util.UtilClasses import BenchmarkRecord

logger = logging.getLogger(__name__)


class JavaApplicationCodeFilter(ApplicationCodeFilter):
    """
    Iterates through sources and tries to find packages.
    """

    def find_application_packages(self, br: BenchmarkRecord) -> BenchmarkRecord:
        packages = set()
        for source in br.sources:
            for root, dirs, files in os.walk(source):
                for f in [f for f in files if f.endswith('.java')]:
                    with open(os.path.join(root, f), 'r') as infile:
                        try:
                            lines = infile.readlines()
                            package_decls = [l for l in lines if l.startswith("package")]
                            packages.update([p.split(' ')[1].split(';')[0] for p in package_decls])
                        except UnicodeDecodeError:
                            logging.critical(f"Could not read in file {os.path.join(root, f)}")
        br.packages = frozenset(packages)
        logging.info(f"Resolved packages as {packages})")
        return br
