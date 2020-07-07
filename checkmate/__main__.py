from art import text2art
import argparse
import logging
import subprocess
import coloredlogs
from PyInquirer import prompt
from termcolor import colored
from checkmate.models.Option import Option
from checkmate.models.Tool import Tool
from checkmate.models.Constraint import Constraint
from checkmate.models.Tag import Tag
import pickle

coloredlogs.install(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
logging.basicConfig(level=logging.WARNING)
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--call', help="""Full callstring. For example,
'java -jar soot-infoflow-cmd-jar-with-dependencies.jar -a ./TestApk1
-p ~/Android/Sdk/platforms -s ./SourcesAndSinks.txt'""")
parser.add_argument('-t', '--tune', help="Open tuning interface.",
                    action="store_true")
parser.add_argument('-a', '--analyze')
parser.add_argument('--soundness', action='store_true')
parser.add_argument('--tags')
args = parser.parse_args()

HOME="/Users/austin/PycharmProjects/checkmate"

def main():
    title = text2art("checkmate")
    print(title)

    if args.analyze is not None:
        print("Checking soundness with regard to tags (Reflection)\n")
        print("Results:")
        print(f"\tenablereflection is currently {colored('FALSE', 'red')}",
              f", changing it to {colored('TRUE', 'blue')} will make the analysis "
              "more sound.")
    elif args.tune:
        ops = [{'selector': '1', 'prompt': 'FlowDroid', 'return': 'flowdroid'},
               {'selector': '2', 'prompt': 'DroidSafe', 'return': 'droidsafe'}]
        ans = prompt.options("Which tool do you want to tune?", ops)
        ops = [{'selector': '1', 'prompt': 'Default', 'return': 'default'},
               {'selector': '2', 'prompt': 'Most Precise',
                'return': 'most_precise'},
               {'selector': '3', 'prompt': 'Most Sound',
                'return': 'most_sound'},
               {'selector': '4', 'prompt': 'Fastest'}]

        p = ["The current configuration is\n\n",
             "aplength = 5\n",
             "cgalgo = SPARK\n",
             "dataflowsolver = ContextFlowSensitive\n",
             "singlejoinpointabstraction = False\n",
             "nothischainreduction = False\n",
             "onesourceatatime = False\n",
             "onecomponentatatime = False\n",
             "staticmode = ContextFlowSensitive\n",
             "codeelimination = PropagateConstants\n",
             "aliasalgo = FlowSensitive\n",
             "aliasflowins = False\n",
             "callbackanalyzer = Default\n",
             "maxcallbackspercomponent = 100\n",
             "maxcallbackdepth = -1\n",
             "nocallbacks = False\n",
             "analyzeframeworks = False\n",
             "taintwrapper = Default\n",
             "implicit = None\n",
             "noexception = False\n",
             "enablereflection = False\n",
             "pathalgo = ContextSensitive\n", 
             "nostatics = False\n"]
        
        ans = prompt.options("Which configuration do you want to tune?", ops)
        print("\033c", end="")
        print("".join([colored(x, 'blue') for x in p]))
        ops = [{'selector': '1', 'prompt': 'Filter by Tag',
               'return': 'filter'},
               {'selector': '2', 'prompt': 'Increase Precision',
                'return': 'precision'},
               {'selector': '3', 'prompt': 'Increase Soundness',
                'return': 'soundness'},
               {'selector': '4', 'prompt': 'Increase Speed'},
               {'selector': '5', 'prompt': 'Run this configuration',
                'return': 'run'},
               {'selector': '6', 'prompt': 'Save to file',
                'return': 'save'}]
        ans = prompt.options("Choose tuning option:", ops)
        ans = prompt.query("Enter tag:")
        
        p = ["The current (filtered) configuration is\n\n",
             "cgalgo = SPARK\n",
             "enablereflection = False\n"]

        print("\033c", end="")
        print("".join([colored(x, 'blue') for x in p]))
        ops = [{'selector': '1', 'prompt': 'Filter by Tag',
               'return': 'filter'},
               {'selector': '2', 'prompt': 'Increase Precision',
                'return': 'precision'},
               {'selector': '3', 'prompt': 'Increase Soundness',
                'return': 'soundness'},
               {'selector': '4', 'prompt': 'Increase Speed'},
               {'selector': '5', 'prompt': 'Run this configuration',
                'return': 'run'},
               {'selector': '6', 'prompt': 'Save to file',
                'return': 'save'},
               {'selector': '7', 'prompt': 'Clear tags',
                'return': 'clear'}]
        ans = prompt.options("Choose tuning option:", ops)
        
        p = ["The current (filtered) configuration is\n\n",
             "cgalgo = SPARK\n",
             colored("enablereflection = False\n", 'red')]

        print("\033c", end="")
        print(f"Options highlighted in {colored('red', 'red')} "
              "can be made more sound.")
        print("".join([colored(x, 'blue') for x in p]))

        ops = [{'selector': '1', 'prompt': 'Filter by Tag',
               'return': 'filter'},
               {'selector': '2', 'prompt': 'Start Over', 'return': 'start over'}
               ,
               {'selector': '3', 'prompt': 'Change enablereflection to TRUE'},
               
               {'selector': '4', 'prompt': 'Run this configuration',
                'return': 'run'},
               {'selector': '5', 'prompt': 'Save to file',
                'return': 'save'},
               {'selector': '6', 'prompt': 'Clear tags',
                'return': 'clear'}]
        
        ans = prompt.options("Choose tuning option:", ops)

        p = ["The current (filtered) configuration is\n\n",
             "cgalgo = SPARK\n",
             "enablereflection = True\n"]
        
        print("\033c", end="")
        print(f"Options highlighted in {colored('red', 'red')} "
              "can be made more sound.")
        print("".join([colored(x, 'blue') for x in p]))

        ops = [{'selector': '1', 'prompt': 'Filter by Tag',
               'return': 'filter'},
               {'selector': '2', 'prompt': 'Start Over', 'return': 'start over'}
               ,
               {'selector': '3', 'prompt': 'Run this configuration',
                'return': 'run'},
               {'selector': '4', 'prompt': 'Save to file',
                'return': 'save'}]
        ans = prompt.options("Choose tuning option:", ops)

        print("\033c", end="")
        print(colored("Running:\njava -jar soot-infoflow-cmd-jar-with-dependencies.jar -a ~/git/DroidBench/apk/AndroidSpecific/ApplicationModeling1.apk -s ../../soot-infoflow-android/SourcesAndSinks.txt -p ~/Library/Android/sdk/platforms --enablereflection", "blue"))
        subprocess.run("java -jar soot-infoflow-cmd-jar-with-dependencies.jar -a ~/git/DroidBench/apk/AndroidSpecific/ApplicationModeling1.apk -s ../../soot-infoflow-android/SourcesAndSinks.txt -p ~/Library/Android/sdk/platforms --enablereflection", cwd=".", shell=True)
        
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
            

def create_models():
    """Creates the models"""

    am = Tool("Amandroid")
    o = Option("kcontext")
    for k in ["k", "k+1"]:
        o.add_level(k)
    o.is_as_precise("k+1", "k")
    o.add_tag(Tag.OBJECT)
    am.add_option(o)

    with open(f'{HOME}/data/amandroid.model', 'wb') as f:
        pickle.dump(am, f, protocol=0)

    fd = Tool("FlowDroid")

    o = Option("aplength")
    for k in ["k", "k+1"]:
        o.add_level(k)
    o.is_as_precise("k+1", "k")
    o.add_tag(Tag.OBJECT)
    fd.add_option(o)
    
    o = Option("cgalgo")
    for k in ['CHA', 'RTA', 'VTA', 'GEOM', 'SPARK']:
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
    o.is_as_sound('FALSE', 'TRUE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    fd.add_option(o)

    o = Option('dataflowsolver')
    for k in ['CONTEXTFLOWSENSITIVE', 'FLOWINSENSITIVE']:
        o.add_level(k)
    o.is_as_precise('CONTEXTFLOWSENSITIVE',
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
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    fd.add_option(o)
    
    o1 = Option('staticmode')
    for k in ['CONTEXTFLOWSENSITIVE',
              'CONTEXTFLOWINSENSITIVE',
              'NONE']:
        o1.add_level(k)
    o1.add_tag(Tag.STATIC)
    o1.is_as_precise('CONTEXTFLOWSENSITIVE', 'CONTEXTFLOWINSENSITIVE')
    o1.is_as_sound('CONTEXTFLOWSENSITIVE', 'NONE')
    o1.is_as_sound('CONTEXTFLOWINSENSITIVE', 'NONE')

    o = Option('nostatic')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.add_tag(Tag.STATIC)
    o.is_as_sound('FALSE', 'TRUE')
    fd.add_option(o)

    fd.add_subsumes(o1, o)

    o = Option('aliasalgo')
    for k in ['NONE', 'LAZY', 'FLOWSENSITIVE', 'PTSBASED']:
        o.add_level(k)
    o.add_tag(Tag.OBJECT)
    o.is_as_sound('LAZY', 'NONE')
    o.is_as_sound('FLOWSENSITIVE', 'NONE')
    o.is_as_sound('PTSBASED', 'NONE')
    o.is_as_precise('FLOWSENSITIVE', 'LAZY')
    o.is_as_precise('FLOWSENSITIVE', 'PTSBASED')
    fd.add_option(o)
    
    o = Option('codeelimination')
    for k in ['PROPAGATECONSTS', 'NONE', 'REMOVECODE']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('REMOVECODE', 'PROPAGATECONSTS')
    o.is_as_precise('PROPAGATECONSTS', 'NONE')
    fd.add_option(o)

    o1 = Option('implicit')
    for k in ['NONE', 'ARRAYONLY', 'ALL']:
        o1.add_level(k)
    o1.is_as_sound('ALL', 'ARRAYONLY')
    o1.is_as_sound('ARRAYONLY', 'NONE')
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
    for k in ['k', 'k+1']:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.is_as_sound('k+1', 'k')
    fd.add_option(o)

    o = Option('maxcallbacksdepth')
    for k in ['k', 'k+1', -1]:
        o.add_level(k)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.is_as_sound(-1, 'k+1')
    o.is_as_sound('k+1', 'k')
    fd.add_option(o)

    o = Option('enablereflection')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.add_tag(Tag.REFLECTION)
    o.is_as_sound('TRUE', 'FALSE')
    fd.add_option(o)

    o = Option('pathalgo')
    for k in ['CONTEXTSENSITIVE', 'CONTEXTINSENSITIVE', 'SOURCESONLY']:
        o.add_level(k)
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    o.is_as_precise('CONTEXTSENSITIVE', 'CONTEXTINSENSITIVE')
    o.is_as_precise('CONTEXTINSENSITIVE', 'SOURCESONLY')
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
    o.is_as_sound('DEFAULTFALLBACK', 'NONE')
    o.is_as_sound('EASY', 'NONE')
    o.is_as_sound('DEFAULT', 'EASY')
    o.is_as_precise('DEFAULT', 'EASY')
    o.add_tag(Tag.LIBRARY)
    fd.add_option(o)

    o1 = Option('analyzeframeworks')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.LIBRARY)
    o1.is_as_sound('TRUE', 'FALSE')
    fd.add_option(o1)

    fd.add_dominates(o1, 'TRUE', o)

    with open(f'{HOME}/data/flowdroid.model', 'wb') as f:
        pickle.dump(fd, f, protocol=0)

    # droidsafe
    ds = Tool("DroidSafe")

    o = Option('kobjsens')
    for k in ['k', 'k+1']:
        o.add_level(k)
    o.is_as_precise('k+1', 'k')
    o.add_tag(Tag.OBJECT)
    ds.add_option(o)

    o = Option('nova')
    for k in ['TRUE', 'FALSE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.is_as_sound('FALSE', 'TRUE')
    o.add_level(Tag.OBJECT)
    o.add_level(Tag.ANDROID_LIFECYCLE)
    ds.add_option(o)
    
    o1 = Option('nojsa')
    for k in ['TRUE', 'FALSE']:
        o1.add_level(k)
    o.add_tag(Tag.OBJECT)
    o1.is_as_sound('FALSE', 'TRUE')
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

    o = Option('analyzestrings_unfiltered')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.OBJECT)
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('filetransforms')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('TRUE', 'FALSE')
    o.add_tag(Tag.TAINT_ANALYSIS_SPECIFIC)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_precise('FALSE', 'TRUE')
    o.is_as_sound('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o = Option('multipassfb')
    for k in ['FALSE', 'TRUE']:
        o.add_level(k)
    o.is_as_sound('FALSE', 'TRUE')
    o.is_as_sound('TRUE', 'FALSE')
    o.add_tag(Tag.ANDROID_LIFECYCLE)
    o.add_tag(Tag.LIBRARY)
    ds.add_option(o)

    o1 = Option('pta')
    for k in ['SPARK', 'PADDLE', 'GEOM']:
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
    for k in ['k', 'k+1', -1]:
        o.add_level(k)
    o.is_as_sound(-1, 'k+1')
    o.is_as_sound('k+1', 'k')
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
    o.is_as_precise('TRUE', 'FALSE')
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

    with open(f'{HOME}/data/droidsafe.model', 'wb') as f:
        pickle.dump(ds, f, protocol=0)
