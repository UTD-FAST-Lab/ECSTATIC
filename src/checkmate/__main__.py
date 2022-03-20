import argparse
import importlib.resources
import logging
import os.path
from typing import List

from src.checkmate.fuzzing.fuzzer import Fuzzer
from src.checkmate.readers.callgraph.AbstractCallGraphReader import AbstractCallGraphTransformer
from src.checkmate.readers.callgraph.DOOPCallGraphReader import DOOPCallGraphTransformer
from src.checkmate.readers.callgraph.WALACallGraphReader import WALACallGraphTransformer

logging.basicConfig(format='%(levelname)s[%(asctime)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

parser = argparse.ArgumentParser()
parser.add_argument("-v", dest='verbosity', action='count', default=0)
subparsers = parser.add_subparsers()
fuzz_parser = subparsers.add_parser('fuzz', help='fuzzing control.')
fuzz_parser.set_defaults(
    func=lambda r: Fuzzer(r.model_location, r.processes, r.number_campaigns, not r.no_validate).main())
fuzz_parser.add_argument('-m', '--model_location', help='the location of the model to use.',
                         default='data/flowdroid.model')
fuzz_parser.add_argument('-p', '--processes', help='the number of processes to generate.',
                         default=64, type=int)
fuzz_parser.add_argument('-n', '--number_campaigns', help='the number of campaigns',
                         default=1, type=int)
fuzz_parser.add_argument('--no_validate', help='do not perform validation', action="store_true")
generate_models_parser = subparsers.add_parser('generate', help='generate models.')
generate_models_parser.set_defaults(func=lambda r: create_models(r.location, r.transitive))
generate_models_parser.add_argument('-t', '--transitive', help='generate transitive partial orders.',
                                    action='store_true')
generate_models_parser.add_argument('--location', '-l', help='where to dump models.',
                                    default='.')
transformation_parser = subparsers.add_parser('transform', help='transform outputs')
transformation_parser.add_argument('--type', choices=['callgraph'], default='callgraph')
transformation_parser.add_argument('--doop', nargs='+', help='DOOP input files.')
transformation_parser.add_argument('--soot', nargs='+', help='SOOT input files.')
transformation_parser.add_argument('--wala', nargs='+', help='WALA input files.')
transformation_parser.set_defaults(func=lambda r: transform_inputs(r.type, r.doop, r.soot, r.wala))
args = parser.parse_args()

if args.verbosity >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbosity == 1:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARN)

from src.checkmate.models.Option import Option
from src.checkmate.models.Tool import Tool
from src.checkmate.models.Tag import Tag
import pickle


def transform_inputs(type: str, doop: List[str], soot: List[str], wala: List[str]):
    if type.lower() == 'callgraph':
        for transformer, files in [(DOOPCallGraphTransformer(), doop), (WALACallGraphTransformer(), wala)]:
            if files is not None:
                for f in files:
                    transformer: AbstractCallGraphTransformer
                    print(f'Transforming file {f}')
                    transformer.transform(f, str(importlib.resources.path('generated', f'{os.path.basename(f)}.out')))
    else:
        raise NotImplementedError('Other types of inputs not accepted.')


# noinspection DuplicatedCode
def make_amandroid_model():
    pass


def make_flowdroid_model():
    pass


def make_droidbench_model():
    pass


def create_models(location, transitive):
    """Creates the models"""

    amandroid: Tool = make_amandroid_model()
    flowdroid: Tool = make_flowdroid_model()
    droidbench: Tool = make_droidbench_model()
    # am = Tool("Amandroid")
    # o = Option("kcontext")
    # for k in ["k", "k+1"]:
    #     o.add_level(k)
    # o.is_as_precise("k+1", "k")
    # o.add_tag(Tag.OBJECT)
    # am.add_option(o)

    # with open(f'{location}/data/amandroid.model', 'wb') as f:
    #     pickle.dump(am, f, protocol=0)

    Option.precision = 0
    Option.soundness = 0
    with open(f'{location}/data/flowdroid.model', 'wb') as f:
        pickle.dump(fd, f, protocol=0)

    print(f'Flowdroid model generated and stored in {location}/data/flowdroid.model')

    # droidsafe
    ds = Tool("DroidSafe")

    o = Option('kobjsens')
    ops = ['1', '2', '3', '4', '5', '6', '18']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.set_more_sound_than(ops[i + 1], ops[i])
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('nova')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_level(Tag.OBJECT)
    o.add_level(Tag.ANDROID_LIFECYCLE)
    ds.add_option(o)

    o1 = Option('nojsa')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.OBJECT)
    o1.set_more_precise_than('FALSE', 'TRUE')
    ds.add_option(o1)

    ds.add_dominates(o1, 'TRUE', o)

    o = Option('noclonestatics')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.STATIC)
    o.set_more_precise_than('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('limitcontextforcomplex')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.set_more_precise_than('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('ignorenocontextflows')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.set_more_sound_than('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('ignoreexceptionflows')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_sound_than('FALSE', 'TRUE')
    o.add_tag(Tag.EXCEPTION)
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('preciseinfoflow')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_precise_than('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('analyzestringsunfiltered')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_precise_than('TRUE', 'FALSE')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('filetransform')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_precise_than('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    #    o.is_as_sound('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.set_more_sound_than('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o1 = Option('pta')
    for k in ['DEFAULT', 'PADDLE', 'GEOM']:
        o1.add_level(k)
    o1.add_tag(Tag.OBJECT)
    ds.add_option(o1)

    o = Option('imprecisestrings')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('noclinitcontext')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.STATIC)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('typesforcontext')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('limitcontextforstrings')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('limitcontextforgui')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('apicalldepth')
    ops = ['0', '1', '50', '80', '90', '100', '110', '120', '150', '200', '600', '-1']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.set_more_sound_than(ops[i + 1], ops[i])
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('implicitflow')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_sound_than('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('noarrayindex')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_sound_than('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('nofallback')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_sound_than('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('noscalaropts')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('transfertaintfield')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.set_more_precise_than('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    print(f'DroidSafe has {Option.precision} partial orders '
          f'and {Option.soundness} soundness partial orders.')

    with open(f'{location}/data/droidsafe.model', 'wb') as f:
        pickle.dump(ds, f, protocol=0)

    print(f'DroidSafe model stored in {location}/data/droidsafe.model.')


def main():
    args.func(args)


if __name__ == '__main__':
    main()
