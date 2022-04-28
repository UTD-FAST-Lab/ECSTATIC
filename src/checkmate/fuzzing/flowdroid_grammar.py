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

from fuzzingbook.Grammars import crange, srange, convert_ebnf_grammar, extend_grammar, is_valid_grammar
from fuzzingbook.Grammars import START_SYMBOL, new_symbol, Grammar

FLOWDROID_EBNF_GRAMMAR: Grammar = {
    '<start>': ['<options>'],
    '<options>': ['<option>', '<options> <option>'],
    '<option>': ['--aliasalgo <aliasalgoopts>',
                 '--aliasflowins <bool>',
                 '--aplength <aplengthopts>',
                 '--cgalgo <cgalgoopts>',
                 '--analyzeframeworks <bool>',
                 '--callbackanalyzer <callbackanalyzeropts>',
                 '--codeelimination <codeeliminationopts>',
                 '--dataflowsolver <dataflowsolveropts>',
                 '--enablereflection <bool>',
                 '--implicit <implicitopts>',
                 '--maxcallbackspercomponent <maxcallbackspercomponentopts>',
                 '--maxcallbacksdepth <maxcallbacksdepthopts>',
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
    '<aplengthopts>' : ['1', '2', '3', '4', '5', '7', '10', '20'],
    '<bool>': ['TRUE', 'FALSE'],
    '<callbackanalyzeropts>': ['DEFAULT', 'FAST'],
    '<codeeliminationopts>': ['NONE', 'DEFAULT', 'REMOVECODE'],
    '<dataflowsolveropts>': ['FLOWINSENSITIVE', 'DEFAULT'],
    '<cgalgoopts>': ['CHA', 'RTA', 'VTA', 'GEOM', 'DEFAULT'],
    '<implicitopts>': ['DEFAULT', 'ARRAYONLY', 'ALL'],
    '<maxcallbackspercomponentopts>': ['1', '50', '80', '90', '100', '110', '120', '150', '600'],
    '<maxcallbacksdepthopts>': ['-1', '1', '50', '80', '90', '100', '110', '120', '150', '600'],
    '<pathalgoopts>': ['DEFAULT', 'CONTEXTINSENSITIVE', 'SOURCESONLY'],
    '<staticmodeopts>': ['CONTEXTFLOWINSENSITIVE', 'DEFAULT', 'NONE'],
    '<taintwrapperopts>': ['DEFAULT', 'DEFAULTFALLBACK', 'NONE', 'EASY']
}

DEFAULT_CONFIG = "--aliasalgo DEFAULT --aliasflowins FALSE --aplength 5 --cgalgo DEFAULT --analyzeframeworks FALSE " \
                 "--callbackanalyzer DEFAULT --codeelimination DEFAULT " \
                 "--dataflowsolver DEFAULT --enablereflection FALSE " \
                 "--implicit DEFAULT --maxcallbackspercomponent 100 --maxcallbacksdepth -1 --nocallbacks FALSE " \
                 "--noexceptions FALSE --nostatic FALSE --nothischainreduction FALSE --onecomponentatatime FALSE " \
                 "--onesourceatatime FALSE --pathalgo DEFAULT --pathspecificresults FALSE " \
                 "--singlejoinpointabstraction FALSE --staticmode DEFAULT --taintwrapper DEFAULT"


class FlowdroidGrammar:

    @staticmethod
    def get_grammar() -> Grammar:
        assert is_valid_grammar(FLOWDROID_EBNF_GRAMMAR)
        return FLOWDROID_EBNF_GRAMMAR

    @staticmethod
    def get_default() -> str:
        return DEFAULT_CONFIG
