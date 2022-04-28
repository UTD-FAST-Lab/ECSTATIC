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

def fix_file_output(file: str) -> None:
    content = ""
    with open(file) as f:
        for l in f:
            content += l

    content = content.replace('soot.jimple.infoflow.android.SetupApplication$InPlaceInfoflow',
                              'soot.jimple.infoflow.Infoflow')

    with open(args.file, 'w') as f:
        f.write(content)
