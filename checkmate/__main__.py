import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-v", dest='verbosity', action='count', default=0)
subparsers = parser.add_subparsers()
fuzz_parser = subparsers.add_parser('fuzz', help='fuzzing control.')
fuzz_parser.set_defaults(func=lambda r: fuzzer.main(r.model_location, r.threads))
fuzz_parser.add_argument('-m', '--model_location', help='the location of the model to use.',
                         default='data/flowdroid.model')
fuzz_parser.add_argument('-t', '--threads', help='the number of execution threads to generate.',
                         default=8)
generate_models_parser = subparsers.add_parser('generate', help='generate models.')
generate_models_parser.set_defaults(func=lambda r: create_models(r.location))
generate_models_parser.add_argument('--location', '-l', help='where to dump models.',
                                    default='.')
args = parser.parse_args()

if args.verbosity >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbosity == 1:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARN)

from checkmate.fuzzing import fuzzer
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.models.Constraint import Constraint
from checkmate.models.Tag import Tag
import pickle


# noinspection DuplicatedCode
def create_models(location):
    """Creates the models"""

    # am = Tool("Amandroid")
    # o = Option("kcontext")
    # for k in ["k", "k+1"]:
    #     o.add_level(k)
    # o.is_as_precise("k+1", "k")
    # o.add_tag(Tag.OBJECT)
    # am.add_option(o)

    # with open(f'{location}/data/amandroid.model', 'wb') as f:
    #     pickle.dump(am, f, protocol=0)

    fd = Tool("FlowDroid")

    o = Option("aplength")
    ops = ['1', '2', '3', '4', '5', '7', '10', '20']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i + 1], ops[i])
    o.add_tag(Tag.OBJECT)
    o.set_default('5')
    fd.add_option(o)

    o = Option("cgalgo")
    for k in ['CHA', 'RTA', 'VTA', 'GEOM', 'DEFAULT']:
        o.add_level(k)
    o.is_as_precise('RTA', 'CHA')
    o.is_as_precise('VTA', 'RTA')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.REFLECTION)
    o.set_default('DEFAULT')
    fd.add_option(o)

    o = Option("nothischainreduction")
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    o.set_default('FALSE')
    fd.add_option(o)

    o = Option('onesourceatatime')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.set_default('FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o)

    o = Option('dataflowsolver')
    for k in ['DEFAULT', 'FLOWINSENSITIVE']:
        o.add_level(k)
    o.is_as_precise('DEFAULT',
                    'FLOWINSENSITIVE')
    o.set_default('DEFAULT')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o)

    o1 = Option('aliasflowins')
    for k in ['FALSE', 'TRUE']:
        o1.add_level(k)
    o1.is_as_precise('FALSE', 'TRUE')
    o1.add_tag(Tag.OBJECT)
    o1.set_default('FALSE')
    fd.add_option(o1)
    fd.add_dominates(o, 'FLOWINSENSITIVE', o1)

    o = Option('singlejoinpointabstraction')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.set_default('FALSE')
    o.is_as_sound('FALSE', 'TRUE')
    fd.add_option(o)

    o = Option('onecomponentatatime')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
    o.set_default('FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    fd.add_option(o)

    o1 = Option('staticmode')
    for k in ['DEFAULT',
              'CONTEXTFLOWINSENSITIVE',
              'NONE']:
        o1.add_level(k)
    o1.add_tag(Tag.STATIC)
    o1.is_as_precise('DEFAULT', 'CONTEXTFLOWINSENSITIVE')
    o1.is_as_sound('DEFAULT', 'NONE')
    o1.is_as_sound('CONTEXTFLOWINSENSITIVE', 'NONE')
    o1.set_default('DEFAULT')
    fd.add_option(o1)

    o = Option('nostatic')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.STATIC)
    o.is_as_sound('FALSE', 'TRUE')
    o.set_default('FALSE')
    fd.add_option(o)

    fd.add_subsumes(o1, o)

    o = Option('aliasalgo')
    for k in ['NONE', 'LAZY', 'DEFAULT', 'PTSBASED']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.is_as_sound('LAZY', 'NONE')
    o.is_as_sound('DEFAULT', 'NONE')
    o.is_as_sound('PTSBASED', 'NONE')
    o.is_as_precise('DEFAULT', 'LAZY')
    o.is_as_precise('DEFAULT', 'PTSBASED')
    o.set_default('DEFAULT')
    fd.add_option(o)

    o = Option('codeelimination')
    for k in ['DEFAULT', 'NONE', 'REMOVECODE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('REMOVECODE', 'DEFAULT')
    o.is_as_precise('DEFAULT', 'NONE')
    o.set_default('DEFAULT')
    fd.add_option(o)

    o1 = Option('implicit')
    for k in ['DEFAULT', 'ARRAYONLY', 'ALL']:
        o1.add_level(k)
    o1.is_as_sound('ALL', 'ARRAYONLY')
    o1.is_as_sound('ARRAYONLY', 'DEFAULT')
    o1.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o1.set_default('DEFAULT')
    fd.add_option(o1)
    fd.add_constraint(Constraint(o1, 'ALL', o, 'REMOVECODE'))

    o = Option('nocallbacks')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.is_as_sound('FALSE', 'TRUE')
    o.set_default('FALSE')
    fd.add_option(o)

    o1 = Option('callbackanalyzer')
    for k in ['DEFAULT', 'FAST']:
        o1.add_level(k)
    o1.add_tag(Tag.ANDROID_LIFECYCLE)
    o1.is_as_precise('DEFAULT', 'FAST')
    o1.set_default('DEFAULT')
    fd.add_option(o1)

    fd.add_dominates(o, 'TRUE', o1)

    o = Option('maxcallbackspercomponent')
    ops = ['1', '50', '80', '90', '100', '110', '120', '150', '600']
    for k in ops:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i + 1], ops[1])
    o.set_default('100')
    fd.add_option(o)

    o = Option('maxcallbacksdepth')
    ops.append('-1')
    for k in ops:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i + 1], ops[i])
    o.set_default('-1')
    fd.add_option(o)

    o = Option('enablereflection')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.REFLECTION)
    o.is_as_sound('TRUE', 'FALSE')
    o.set_default('FALSE')
    fd.add_option(o)

    o = Option('pathalgo')
    for k in ['DEFAULT', 'CONTEXTINSENSITIVE', 'SOURCESONLY']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('DEFAULT', 'CONTEXTINSENSITIVE')
    o.is_as_precise('DEFAULT', 'SOURCESONLY')
    o.set_default('DEFAULT')
    fd.add_option(o)

    o = Option('pathspecificresults')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('TRUE', 'FALSE')
    o.set_default('FALSE')
    fd.add_option(o)

    o = Option('noexceptions')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.EXCEPTION)
    o.add_tag(Tag.OBJECT)
    o.is_as_sound('FALSE', 'TRUE')
    o.set_default('FALSE')
    fd.add_option(o)

    o = Option('taintwrapper')
    for k in ['DEFAULT', 'DEFAULTFALLBACK', 'EASY', 'NONE']:
        o.add_level(k)
    o.is_as_sound('DEFAULTFALLBACK', 'NONE')
    o.is_as_sound('DEFAULTFALLBACK', 'DEFAULT')
    o.is_as_sound('EASY', 'NONE')
    o.is_as_sound('DEFAULT', 'NONE')
    o.set_default('DEFAULT')
    o.add_tag(Tag.LIBRARY)
    fd.add_option(o)

    o1 = Option('analyzeframeworks')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.LIBRARY)
    o1.is_as_sound('TRUE', 'FALSE')
    o1.set_default('FALSE')
    fd.add_option(o1)

    fd.add_dominates(o1, 'TRUE', o)

    print(f'FlowDroid has {Option.precision} partial orders '
          f'and {Option.soundness} soundness partial orders.')

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
        o.is_as_sound(ops[i + 1], ops[i])
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('nova')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_level(Tag.OBJECT)
    o.add_level(Tag.ANDROID_LIFECYCLE)
    ds.add_option(o)

    o1 = Option('nojsa')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.OBJECT)
    o1.is_as_precise('FALSE', 'TRUE')
    ds.add_option(o1)

    ds.add_dominates(o1, 'TRUE', o)

    o = Option('noclonestatics')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.STATIC)
    o.is_as_precise('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('limitcontextforcomplex')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.is_as_precise('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('ignorenocontextflows')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.is_as_sound('FALSE', 'TRUE')
    ds.add_option(o)

    o = Option('ignoreexceptionflows')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
    o.add_tag(Tag.EXCEPTION)
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('preciseinfoflow')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('analyzestringsunfiltered')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('filetransform')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    #    o.is_as_sound('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_sound('TRUE', 'FALSE')
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
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('noclinitcontext')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.STATIC)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('typesforcontext')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('limitcontextforstrings')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('limitcontextforgui')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('apicalldepth')
    ops = ['0', '1', '50', '80', '90', '100', '110', '120', '150', '200', '600', '-1']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i + 1], ops[i])
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)
    ds.add_dominates(o1, 'PADDLE', o)
    ds.add_dominates(o1, 'GEOM', o)

    o = Option('implicitflow')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_sound('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('noarrayindex')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('nofallback')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('noscalaropts')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('transfertaintfield')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
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
