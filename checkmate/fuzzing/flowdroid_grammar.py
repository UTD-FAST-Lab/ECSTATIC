from fuzzingbook.Grammars import crange, srange, convert_ebnf_grammar, extend_grammar, is_valid_grammar
from fuzzingbook.Grammars import START_SYMBOL, new_symbol, Grammar

FLOWDROID_EBNF_GRAMMAR: Grammar = {
    '<start>': ['<options>'],
    '<options>': ['<option>', '<options> <option>'],
    '<option>': ['--aliasalgo <aliasalgoopts>',
                 '--aliasflowins <bool>',
                 '--aplength <int>',
                 '--cgalgo <cgalgoopts>',
                 '--analyzeframeworks <bool>',
                 '--callbackanalyzer <callbackanalyzeropts>',
                 '--codeelimination <codeeliminationopts>',
                 '--dataflowsolver <dataflowsolveropts>',
                 '--enablereflection <bool>',
                 '--implicit <implicitopts>',
                 '--maxcallbackspercomponent <int>',
                 '--maxcallbacksdepth <int-augment>',
                 '--nocallbacks <bool>',
                 '--noexceptions <bool>',
                 '--nostatic <bool>',
                 '--nothischainreduction <bool>',
                 '--onecomponentatatime <bool>',
                 '--onesourceatatime <bool>',
                 '--pathalgo <pathalgoopts>',
                 '--pathspecificresults <bool>',
                 '--singlejoinpointabstraction <bool>',
                 '--staticmode <staticmodeopts>',
                 '--taintwrapper <taintwrapperopts>'
                 ],
    '<aliasalgoopts>': ['NONE', 'LAZY', 'DEFAULT', 'PTSBASED'],
    '<bool>': ['TRUE', 'FALSE'],
    '<callbackanalyzeropts>': ['DEFAULT', 'FAST'],
    '<codeeliminationopts>': ['NONE', 'PROPAGATECONSTS', 'REMOVECODE'],
    '<dataflowsolveropts>': ['FLOWINSENSITIVE', 'DEFAULT'],
    '<cgalgoopts>': ['CHA', 'RTA', 'VTA', 'GEOM', 'SPARK'],
    '<implicitopts>': ['DEFAULT', 'ARRAYONLY', 'ALL'],
    '<pathalgoopts>': ['DEFAULT', 'CONTEXTINSENSITIVE', 'SOURCESONLY'],
    '<staticmodeopts>': ['CONTEXTFLOWINSENSITIVE', 'NONE'],
    '<taintwrapperopts>': ['DEFAULT', 'DEFAULTFALLBACK', 'NONE', 'EASY -t /Users/austin/git/AndroidTAEnvironment/tools/FlowDroid/soot-infoflow/EasyTaintWrapperSource.txt'],
    '<int-augment>': ['<int>', '-1'],
    '<int>': ['<digit>+'],
    '<digit>': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
}

DEFAULT_CONFIG = "--aliasalso DEFAULT --aliasflowins FALSE --aplength 5 --cgalgo SPARK --analyzeframeworks FALSE "\
    "--callbackanalyzer DEFAULT --codeelimination PROPAGATECONSTS --dataflowsolver DEFAULT --enablereflection FALSE "\
    "--implicit DEFAULT --maxcallbackspercomponent 100 --maxcallbacksdepth -1 --nocallbacks FALSE "\
    "--noexceptions FALSE --nostatic FALSE --nothischainreduction FALSE --onecomponentatatime FALSE "\
    "--onesourceatatime FALSE --pathalgo DEFAULT --pathspecificresults FALSE --singlejoinpointabstraction FALSE "\
    "--staticmode NONE --taintwrapper DEFAULT"

class FlowdroidGrammar:

    @staticmethod
    def getGrammar() -> Grammar:
        assert is_valid_grammar(FLOWDROID_EBNF_GRAMMAR)
        return FLOWDROID_EBNF_GRAMMAR

    @staticmethod
    def getDefault() -> str:
        return DEFAULT_CONFIG
