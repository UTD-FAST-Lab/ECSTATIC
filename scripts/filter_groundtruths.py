from xml.etree import ElementTree
import argparse

from src.checkmate import Flow

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