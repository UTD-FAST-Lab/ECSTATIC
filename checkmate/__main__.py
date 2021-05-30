from art import text2art
import argparse
import logging
import subprocess
import coloredlogs
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.models.Constraint import Constraint
from checkmate.models.Tag import Tag
import pickle

logging.basicConfig(level=logging.WARNING)
parser = argparse.ArgumentParser()
parser.add_argument('--generate-models', help="Generate models.",
                    action="store_true")
parser.add_argument('-c', '--call', help="""Full callstring. For example,
'java -jar soot-infoflow-cmd-jar-with-dependencies.jar -a ./TestApk1
-p ~/Android/Sdk/platforms -s ./SourcesAndSinks.txt'""")
parser.add_argument('-t', '--tune', help="Open tuning interface.",
                    action="store_true")
parser.add_argument('-a', '--analyze')
parser.add_argument('--soundness', action='store_true')
parser.add_argument('--tags')
args = parser.parse_args()

HOME="."
def create_models():
    """Creates the models"""

    # am = Tool("Amandroid")
    # o = Option("kcontext")
    # for k in ["k", "k+1"]:
    #     o.add_level(k)
    # o.is_as_precise("k+1", "k")
    # o.add_tag(Tag.OBJECT)
    # am.add_option(o)

    # with open(f'{HOME}/data/amandroid.model', 'wb') as f:
    #     pickle.dump(am, f, protocol=0)

    fd = Tool("FlowDroid")

    o = Option("aplength")
    ops = ['1', '2', '3', '4', '5', '7', '10', '20']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i+1], ops[i])
    o.add_tag(Tag.OBJECT)
    fd.add_option(o)
    
    o = Option("cgalgo")
    for k in ['CHA', 'RTA', 'VTA', 'GEOM', 'DEFAULT']:
        o.add_level(k)
    o.is_as_precise('RTA', 'CHA')
    o.is_as_precise('VTA', 'RTA')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.REFLECTION)
    fd.add_option(o)
    
    o = Option("nothischainreduction")
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.add_tag(Tag.OBJECT)
    fd.add_option(o)
    
    o = Option('onesourceatatime')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o)

    o = Option('dataflowsolver')
    for k in ['DEFAULT', 'FLOWINSENSITIVE']:
        o.add_level(k)
    o.is_as_precise('DEFAULT',
                    'FLOWINSENSITIVE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o)

    o1 = Option('aliasflowins')
    for k in ['FALSE', 'TRUE']:
        o1.add_level(k)
    o1.is_as_precise('FALSE', 'TRUE')
    o1.add_tag(Tag.OBJECT)
    fd.add_option(o1)
    fd.add_dominates(o, 'FLOWINSENSITIVE', o1)
    
    o = Option('singlejoinpointabstraction')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_sound('FALSE', 'TRUE')
    fd.add_option(o)

    o = Option('onecomponentatatime')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
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
    fd.add_option(o1)
    
    o = Option('nostatic')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.STATIC)
    o.is_as_sound('FALSE', 'TRUE')
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
    fd.add_option(o)
    
    o = Option('codeelimination')
    for k in ['DEFAULT', 'NONE', 'REMOVECODE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('REMOVECODE', 'DEFAULT')
    o.is_as_precise('DEFAULT', 'NONE')
    fd.add_option(o)

    o1 = Option('implicit')
    for k in ['DEFAULT', 'ARRAYONLY', 'ALL']:
        o1.add_level(k)
    o1.is_as_sound('ALL', 'ARRAYONLY')
    o1.is_as_sound('ARRAYONLY', 'DEFAULT')
    o1.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o1)
    fd.add_constraint(Constraint(o1, 'ALL', o, 'REMOVECODE'))

    o = Option('nocallbacks')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.is_as_sound('FALSE', 'TRUE')
    fd.add_option(o)

    o1 = Option('callbackanalyzer')
    for k in ['DEFAULT', 'FAST']:
        o1.add_level(k)
    o1.add_tag(Tag.ANDROID_LIFECYCLE)
    o1.is_as_precise('DEFAULT', 'FAST')
    fd.add_option(o1)
    
    fd.add_dominates(o, 'TRUE', o1)

    o = Option('maxcallbackspercomponent')
    ops = ['1', '50', '80', '90', '100', '110', '120', '150', '600']
    for k in ops:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    for i in range(len(ops)-1):
        o.is_as_sound(ops[i+1], ops[1])
    fd.add_option(o)

    o = Option('maxcallbacksdepth')
    ops.append('-1')
    for k in ops:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i+1], ops[i])
    fd.add_option(o)

    o = Option('enablereflection')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.REFLECTION)
    o.is_as_sound('TRUE', 'FALSE')
    fd.add_option(o)

    o = Option('pathalgo')
    for k in ['DEFAULT', 'CONTEXTINSENSITIVE', 'SOURCESONLY']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('DEFAULT', 'CONTEXTINSENSITIVE')
    o.is_as_precise('DEFAULT', 'SOURCESONLY')
    fd.add_option(o)

    o = Option('pathspecificresults')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('TRUE', 'FALSE')
    fd.add_option(o)

    o = Option('noexceptions')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.EXCEPTION)
    o.add_tag(Tag.OBJECT)
    o.is_as_sound('FALSE', 'TRUE')
    fd.add_option(o)

    o = Option('taintwrapper')
    for k in ['DEFAULT', 'DEFAULTFALLBACK', 'EASY', 'NONE']:
        o.add_level(k)
    o.is_as_sound('DEFAULTFALLBACK', 'NONE')
    o.is_as_sound('DEFAULTFALLBACK', 'DEFAULT')
    o.is_as_sound('EASY', 'NONE')
    o.is_as_sound('DEFAULT', 'NONE')
    o.add_tag(Tag.LIBRARY)
    fd.add_option(o)

    o1 = Option('analyzeframeworks')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.LIBRARY)
    o1.is_as_sound('TRUE', 'FALSE')
    fd.add_option(o1)

    fd.add_dominates(o1, 'TRUE', o)

    print(f'FlowDroid has {Option.precision} partial orders '
          f'and {Option.soundness} soundness partial orders.')

    Option.precision = 0
    Option.soundness = 0
    with open(f'{HOME}/data/flowdroid.model', 'wb') as f:
        pickle.dump(fd, f, protocol=0)

    print(f'Flowdroid model generated and stored in {HOME}/data/flowdroid.model')

    # droidsafe
    ds = Tool("DroidSafe")

    o = Option('kobjsens')
    ops = ['1', '2', '3', '4', '5', '6', '18']
    for k in ops:
        o.add_level(k)
    for i in range(len(ops) - 1):
        o.is_as_sound(ops[i+1], ops[i])
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
        o.is_as_sound(ops[i+1], ops[i])
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
    o.is_as_sound('FALSE','TRUE')
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
    
    with open(f'{HOME}/data/droidsafe.model', 'wb') as f:
        pickle.dump(ds, f, protocol=0)

    print(f'DroidSafe model stored in {HOME}/data/droidsafe.model.')

def main():
    title = text2art("checkmate")
    print(title)
    if args.generate_models:
        create_models()
        exit(0)
    
    if args.call is not None:
        if args.call.startswith('java'):
            ##load flowdroid model
            call = args.call
            with open(f'{HOME}/data/flowdroid.model', 'rb') as f:
                model = pickle.load(f)
            skip = ['-s', '--sourcesandsinks',
                    '-a', '--apkfile',
                    '-p', '--platformsdir',
                    '-jar']
        else:
            with open('./Makefile') as f:
                content = f.readlines()
                # need to 
                call = [c for c in content if c.startswith("DSARGS")][0]
            with open(f'{HOME}/data/droidsafe.model', 'b') as f:
                model = pickle.load(f)
            skip = []
        # Go through each option
        i = 0
        toks = call.split()
        conf = list()
        while i < len(toks):
            if toks[i].startswith('--'):
                if toks[i] in skip:
                    continue
                # the setting of it should be next, otherwise it's true
                try:
                    if not toks[i+1].startswith('--'):
                        setting = toks[i+1]
                    else:
                        setting = 'TRUE'
                except IndexError:
                    # i+1 overflowed
                    setting = 'TRUE'
                conf.append(toks[i].lstrip('-'))
                try:
                    conf.append(int(setting))
                except ValueError:
                    conf.append(setting) # setting wasn't an int
            elif toks[i].startswith('-') and toks[i] not in skip:
                logging.warning(f'checkmate does not support short options.'
                                'Please use the long option format instead.')
            i += 1
        # check configuration against each of the constraints.
        for c in model.constraints:
            if c.o1.name in conf and\
               conf[conf.index(c.o1.name) + 1] == c.l1 and\
               c.o2.name in conf and\
               conf[conf.index(c.o2.name) + 1] == c.l2:
                logging.warning(f"{c.o1.name} with setting {c.l1} "
                                f"disables {c.o2.name} "
                                f"with setting {c.l2}.")
                            
        subprocess.run(args.call, cwd=".", shell=True)
        

if __name__ == "__main__":
    main()

def interpret_call(call):
    """Interprets a call and returns a configuration list."""
    if call.startswith('java'):
        logging.debug(f'{call} is a flowdroid call.')
        ## load flowdroid model
        with open(f'{HOME}/data/flowdroid.model', 'b') as f:
            fd = pickle.load(f)

        return parse_call(call, fd)
                    

def parse_call(call, model):
    toks = call.split()
    for i in range(len(toks)):
        if toks[i].startswith('-'):
            logging.warning(f'checkmate only understands options supplied in '
                            'long form (e.g., --aplength rather than -a). '
                            'Skipping {toks[i]}')
            continue
        elif toks[i].startswith('--'):
            op = toks[i].lstrip('-')
            model_ops = [o.name for o in model.options]
