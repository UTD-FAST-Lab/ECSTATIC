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


from xml.etree import ElementTree
import argparse

from src.ecstatic.models.Flow import Flow

p = argparse.ArgumentParser()
p.add_argument('groundtruths')
args = p.parse_args()

def main():
    tree = ElementTree.parse(args.groundtruths)
    flows = [Flow(f) for f in tree.getroot() if 'flowdroid' in f.get('generating_config').lower()]

    apk_dict = dict()
    for f in flows:
        f: Flow
        if 'flowdroid' in f.element.get('generating_config').lower():
            if f.get_file() not in apk_dict:
                apk_dict[f.get_file()] = {'tp': 0, 'fp': 0}
            if f.get_classification().lower() == 'true':
                apk_dict[f.get_file()]['tp'] += 1
            else:
                apk_dict[f.get_file()]['fp'] += 1

    root = ElementTree.Element('flows')
    [root.append(f.element) for f in flows]
    tree = ElementTree.ElementTree(root)
    tree.write(f'{args.groundtruths}_flowdroidonly')
    print(apk_dict)

if __name__ == '__main__':
    main()